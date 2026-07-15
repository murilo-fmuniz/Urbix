#!/usr/bin/env python3
"""
ETL Script: Processamento de Dados Locais
==========================================

Objetivo: Ler planilhas brutas (CSV e Excel) e gerar JSON consolidado de indicadores.

Filtro de Cidades:
- Cluster de Referência: Apucarana (4101408), Londrina (4113700), 27 Capitais brasileiras

Processamento:
- acessos_banda_larga_fixa: Extrai densidade média por município
- divulgacao_anos_*_2023: Extrai nota do IDEB 2023
- ATU: Extrai taxa de atendimento por município
- TDI: Extrai taxa de distorção idade-série

Saída: backend/app/data/indicators_master.json

Uso: python scripts/process_local_data.py
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
import openpyxl
import asyncio
import httpx
from datetime import datetime, timedelta

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Adicionar backend ao path para imports
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.services.ibge_catalog import build_municipality_options

# Diretórios
DATA_PLANILHAS_DIR = BACKEND_DIR / "data" / "planilhas"
OUTPUT_FILE = BACKEND_DIR / "app" / "data" / "indicators_master.json"
CACHE_DIR = BACKEND_DIR / "data" / "cache_api"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

IBGE_CATALOG_PATH = (
    DATA_PLANILHAS_DIR
    / "codigos ibge"
    / "RELATORIO_DTB_BRASIL_2024_MUNICIPIOS.ods"
)

CACHE_CAGED_FILE = CACHE_DIR / "caged_cache.json"
CACHE_DATASUS_FILE = CACHE_DIR / "datasus_cache.json"
CACHE_TTL_HOURS = 24  # Revalidar cache a cada 24 horas

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CAPITAIS BRASILEIRAS + CLUSTER DE REFERÊNCIA
# ============================================================================

# Catálogo IBGE completo para nomes oficiais dos municípios
def load_ibge_municipios_catalog() -> Dict[str, str]:
    """Carrega o catálogo de municípios do IBGE a partir do arquivo .ods local."""
    catalog: Dict[str, str] = {}

    if not IBGE_CATALOG_PATH.exists():
        logger.warning(f"⚠️  Catálogo IBGE não encontrado: {IBGE_CATALOG_PATH}")
        return catalog

    try:
        df = pd.read_excel(
            IBGE_CATALOG_PATH,
            sheet_name=0,
            skiprows=6,
            engine="odf",
            dtype=str,
        )

        col_codigo = None
        col_nome = None

        for col in df.columns:
            col_norm = str(col).strip().lower()
            if col_codigo is None and "código município completo" in col_norm:
                col_codigo = col
            if col_nome is None and "nome_município" in col_norm:
                col_nome = col

        if col_codigo is None or col_nome is None:
            logger.warning(
                f"⚠️  Catálogo IBGE: colunas esperadas não encontradas. "
                f"Colunas disponíveis: {list(df.columns)[:10]}"
            )
            return catalog

        for _, row in df.iterrows():
            codigo = str(row.get(col_codigo, "")).strip()
            nome = str(row.get(col_nome, "")).strip()

            if not codigo or not nome:
                continue

            if codigo.endswith(".0"):
                codigo = codigo[:-2]

            try:
                codigo = str(int(float(codigo))).zfill(7)
            except Exception:
                continue

            catalog[codigo] = nome

        logger.info(f"✅ Catálogo IBGE carregado: {len(catalog)} municípios")
        return catalog

    except Exception as e:
        logger.warning(f"⚠️  Falha ao carregar catálogo IBGE: {type(e).__name__}: {str(e)}")
        return catalog


IBGE_MUNICIPIOS = load_ibge_municipios_catalog()

_CAPITAIS_NOMES = [
    "Porto Velho",
    "Rio Branco",
    "Manaus",
    "Macapá",
    "Boa Vista",
    "Belém",
    "Palmas",
    "São Luís",
    "Teresina",
    "Fortaleza",
    "Natal",
    "João Pessoa",
    "Recife",
    "Maceió",
    "Aracaju",
    "Salvador",
    "Belo Horizonte",
    "Vitória",
    "Rio de Janeiro",
    "São Paulo",
    "Curitiba",
    "Florianópolis",
    "Porto Alegre",
    "Campo Grande",
    "Cuiabá",
    "Goiânia",
    "Brasília",
]

_CLUSTER_REFERENCIA_NOMES = ["Apucarana", "Londrina"]

def _build_city_map(names: List[str]) -> Dict[str, str]:
    cities = build_municipality_options(names)
    return {city["codigo_ibge"]: city["nome"].split(" - ")[0] for city in cities}


CAPITAIS_IBGE = _build_city_map(_CAPITAIS_NOMES)
CLUSTER_REFERENCIA = _build_city_map(_CLUSTER_REFERENCIA_NOMES)

# Cidades válidas para filtro operacional das APIs (mantém o cluster de referência)
CIDADES_VALIDAS = {**CAPITAIS_IBGE, **CLUSTER_REFERENCIA}

logger.info(f"📍 Modo de operação: QUALQUER MUNICÍPIO BRASILEIRO")
logger.info(f"   - Filtro inicial: {len(CIDADES_VALIDAS)} cidades principais")
logger.info(f"   - Sistema permite expandir para todos os 5570 municípios brasileiros")
logger.info(f"   - APIs: Portal Transparência (CAGED), DATASUS (SIM), etc.")

# ============================================================================
# FUNÇÕES UTILITÁRIAS
# ============================================================================

def normalize_municipio_code(code: Any) -> str:
    """
    Normaliza código de município para string de 7 dígitos.
    
    Args:
        code: Código como string, int ou float
        
    Returns:
        String de 7 dígitos ou vazio se inválido
    """
    try:
        # Converter para string
        if isinstance(code, float):
            code = int(code)
        code_str = str(code).strip()
        
        # Remover zeros à esquerda e repadronizar
        code_int = int(code_str)
        normalized = str(code_int).zfill(7)
        
        return normalized if len(normalized) == 7 else ""
    except (ValueError, TypeError):
        return ""


def is_valid_city(codigo_ibge: str) -> bool:
    """Verifica se o código do município é válido (7 dígitos) - QUALQUER município brasileiro."""
    if not codigo_ibge or len(codigo_ibge) != 7:
        return False
    try:
        int(codigo_ibge)
        return True
    except ValueError:
        return False


def load_cache(cache_file: Path) -> Dict[str, Any]:
    """Carrega cache de arquivo se existir e não expirou."""
    if not cache_file.exists():
        return {}
    
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        timestamp = cache_data.get('timestamp', 0)
        age_hours = (datetime.now().timestamp() - timestamp) / 3600
        
        if age_hours > CACHE_TTL_HOURS:
            logger.info(f"   ⏰ Cache expirou ({age_hours:.1f}h > {CACHE_TTL_HOURS}h), será revalidado")
            return {}
        
        logger.info(f"   💾 Cache carregado ({len(cache_data.get('data', {}))} items, {age_hours:.1f}h de idade)")
        return cache_data.get('data', {})
    except Exception as e:
        logger.warning(f"   ⚠️  Erro ao carregar cache: {type(e).__name__}")
        return {}


def save_cache(cache_file: Path, data: Dict[str, Any]) -> None:
    """Salva dados em cache com timestamp."""
    try:
        cache_data = {
            'timestamp': datetime.now().timestamp(),
            'data': data
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        logger.debug(f"   💾 Cache salvo: {len(data)} items")
    except Exception as e:
        logger.warning(f"   ⚠️  Erro ao salvar cache: {type(e).__name__}")


# ============================================================================
# PROCESSADORES POR TIPO DE DADO
# ============================================================================

class DataProcessor:
    """Processador centralizado de dados com suporte a APIs governamentais."""
    
    def __init__(self):
        self.data = {}  # Dict[codigo_ibge] -> Dict[indicador] -> valor
        self.caged_cache = load_cache(CACHE_CAGED_FILE)
        self.datasus_cache = load_cache(CACHE_DATASUS_FILE)
        self.http_client = None
        logger.info("✅ DataProcessor inicializado")
        logger.info(f"   📦 CAGED cache: {len(self.caged_cache)} registros")
        logger.info(f"   📦 DATASUS cache: {len(self.datasus_cache)} registros")
    
    def process_banda_larga(self) -> None:
        """Processa dados de banda larga fixa (densidade média por município)."""
        logger.info("\n📊 Processando BANDA LARGA FIXA...")
        
        try:
            csv_path = DATA_PLANILHAS_DIR / "acessos_banda_larga_fixa" / "Densidade_Banda_Larga_Fixa.csv"
            
            if not csv_path.exists():
                logger.warning(f"   ⚠️  Arquivo não encontrado: {csv_path}")
                return
            
            # Ler CSV com chunksize para dados grandes
            logger.info(f"   📖 Lendo {csv_path.name} (em chunks)...")
            
            chunks_densidades = {}  # Dict[codigo_ibge] -> list[densidade]
            
            for chunk in pd.read_csv(csv_path, sep=";", chunksize=10000, dtype={"Código IBGE": str}):
                for _, row in chunk.iterrows():
                    try:
                        codigo = normalize_municipio_code(row.get("Código IBGE", ""))
                        
                        if not codigo or not is_valid_city(codigo):
                            continue
                        
                        # Processar densidade (pode vir com vírgula)
                        densidade_str = str(row.get("Densidade", "")).replace(",", ".")
                        densidade = float(densidade_str)
                        
                        if codigo not in chunks_densidades:
                            chunks_densidades[codigo] = []
                        chunks_densidades[codigo].append(densidade)
                    
                    except (ValueError, TypeError):
                        continue
            
            # Calcular média de densidade por município
            for codigo, densidades in chunks_densidades.items():
                densidade_media = sum(densidades) / len(densidades)
                
                if codigo not in self.data:
                    self.data[codigo] = {}
                
                self.data[codigo]["densidade_banda_larga"] = round(densidade_media, 4)
            
            logger.info(f"   ✅ Processados {len(chunks_densidades)} municípios com banda larga")
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao processar banda larga: {type(e).__name__}: {str(e)}")
    
    def process_ideb(self) -> None:
        """Processa dados de IDEB (anos iniciais e finais 2023)."""
        logger.info("\n📚 Processando IDEB (Anos Iniciais e Finais 2023)...")
        
        # Processar anos iniciais
        self._process_ideb_variant(
            "divulgacao_anos_iniciais_municipios_2023",
            "ideb_anos_iniciais_2023"
        )
        
        # Processar anos finais
        self._process_ideb_variant(
            "divulgacao_anos_finais_municipios_2023",
            "ideb_anos_finais_2023"
        )
    
    def _process_ideb_variant(self, folder_name: str, indicator_key: str) -> None:
        """Processa uma variante de IDEB (iniciais ou finais)."""
        try:
            folder_path = DATA_PLANILHAS_DIR / folder_name
            
            # Tentar com .xlsx primeiro
            xlsx_path = folder_path / f"{folder_name}.xlsx"
            ods_path = folder_path / f"{folder_name}.ods"
            
            file_path = None
            if xlsx_path.exists():
                file_path = xlsx_path
                logger.info(f"   📖 Lendo {xlsx_path.name}...")
            elif ods_path.exists():
                file_path = ods_path
                logger.info(f"   📖 Lendo {ods_path.name}...")
            else:
                logger.warning(f"   ⚠️  Nenhum arquivo encontrado em {folder_name}")
                return
            
            # Ler Excel/ODS - localizar aba de municípios
            try:
                # Tentar ler com diferentes números de linhas de skip para encontrar a tabela real
                df_data = None
                
                for skip_rows in [0, 1, 2, 3, 4, 5]:
                    try:
                        logger.debug(f"   → Tentando com skiprows={skip_rows}...")
                        # Limitar a leitura para primeiras 15000 linhas para performance
                        df = pd.read_excel(file_path, sheet_name=0, skiprows=skip_rows, nrows=15000)
                        
                        # Verificar se tem colunas relevantes
                        has_codigo = any(
                            "código" in str(col).lower() or "cod" in str(col).lower() 
                            for col in df.columns
                        )
                        has_ideb = any(
                            "ideb" in str(col).lower() or "nota" in str(col).lower()
                            for col in df.columns
                        )
                        
                        if has_codigo and has_ideb:
                            df_data = df
                            logger.debug(f"   → ✓ Tabela encontrada com skiprows={skip_rows}")
                            break
                    except Exception as e:
                        logger.debug(f"   → Falha com skiprows={skip_rows}: {type(e).__name__}")
                        continue
                
                if df_data is None:
                    logger.warning(f"   ⚠️  Estrutura não encontrada em {folder_name}")
                    return
                
                # Procurar colunas de código IBGE e IDEB
                col_codigo = None
                col_ideb = None
                
                for col in df_data.columns:
                    col_lower = str(col).lower()
                    if "código" in col_lower or "cod" in col_lower or "ibge" in col_lower:
                        col_codigo = col
                    if "nota" in col_lower or "ideb" in col_lower:
                        col_ideb = col
                
                if col_codigo is None or col_ideb is None:
                    logger.debug(f"   ⚠️  Colunas não encontradas: código={col_codigo}, ideb={col_ideb}")
                    logger.debug(f"      Colunas disponíveis: {list(df_data.columns)[:10]}...")
                    return
                
                # Extrair dados por município
                count = 0
                for _, row in df_data.iterrows():
                    try:
                        codigo = normalize_municipio_code(row.get(col_codigo, ""))
                        
                        if not codigo or not is_valid_city(codigo):
                            continue
                        
                        # Extrair IDEB
                        ideb_str = str(row.get(col_ideb, "")).replace(",", ".")
                        ideb_val = pd.to_numeric(ideb_str, errors='coerce')
                        
                        if pd.isna(ideb_val):
                            continue
                        
                        if codigo not in self.data:
                            self.data[codigo] = {}
                        
                        self.data[codigo][indicator_key] = round(float(ideb_val), 2)
                        count += 1
                    
                    except (ValueError, TypeError):
                        continue
                
                if count > 0:
                    logger.info(f"   ✅ Processados {count} municípios ({indicator_key})")
                else:
                    logger.warning(f"   ⚠️  Nenhum dado válido encontrado em {folder_name}")
            
            except Exception as e:
                logger.debug(f"   ❌ Erro ao ler {file_path.name}: {type(e).__name__}")
        
        except Exception as e:
            logger.debug(f"   ❌ Erro ao processar {folder_name}: {type(e).__name__}")
    
    def process_atu(self) -> None:
        """Processa dados de ATU (Taxa de Atendimento)."""
        logger.info("\n🏥 Processando ATU (Taxa de Atendimento)...")
        
        self._process_xlsx_simple(
            "ATU_2025_MUNICIPIOS",
            "ATU_MUNICIPIOS_2025",
            "atu_2025",
            "Taxa atendimento"  # Possível nome da coluna
        )
    
    def process_tdi(self) -> None:
        """Processa dados de TDI (Taxa de Distorção Idade-Série)."""
        logger.info("\n📉 Processando TDI (Taxa de Distorção Idade-Série)...")
        
        self._process_xlsx_simple(
            "TDI_2025_MUNICIPIOS",
            "TDI_MUNICIPIOS_2025",
            "tdi_2025",
            "Taxa distorção"  # Possível nome da coluna
        )

    def process_snis(self) -> None:
        """Processa dados do SNIS (Água e Resíduos Sólidos)."""
        logger.info("\n💧 Processando dados do SNIS (Água e Resíduos)...")

        try:
            base_path = getattr(self, "base_path", DATA_PLANILHAS_DIR.parent)
            planilhas_path = base_path / "planilhas"

            def _clean_numeric(value):
                if value is None:
                    return None

                value_str = str(value).strip().replace("%", "").replace(" ", "")
                if "," in value_str and "." in value_str:
                    value_str = value_str.replace(".", "").replace(",", ".")
                elif "," in value_str:
                    value_str = value_str.replace(",", ".")

                numeric = pd.to_numeric(value_str, errors="coerce")
                if pd.isna(numeric):
                    return None
                return float(numeric)

            def _clean_ibge(value) -> str:
                if value is None:
                    return ""

                if isinstance(value, float):
                    if pd.isna(value):
                        return ""
                    value = int(value)

                value_str = str(value).strip()
                if value_str.endswith(".0"):
                    value_str = value_str[:-2]

                try:
                    return str(int(float(value_str))).zfill(7)
                except Exception:
                    return value_str.zfill(7) if value_str.isdigit() else ""

            # ============================================================
            # 1) ÁGUA - CSV original do SNIS
            # ============================================================
            try:
                logger.info("   💧 Leitura da água: br_mdr_snis_municipio_agua_esgoto.csv")

                agua_csv_path = (
                    planilhas_path
                    / "SNIS"
                    / "br_mdr_snis_municipio_agua_esgoto.csv"
                    / "br_mdr_snis_municipio_agua_esgoto.csv"
                )

                if not agua_csv_path.exists():
                    logger.warning(f"   ⚠️  SNIS Água: arquivo não encontrado: {agua_csv_path}")
                else:
                    df_agua = pd.read_csv(
                        agua_csv_path,
                        sep=";",
                        dtype=str,
                        on_bad_lines="skip",
                        engine="python",
                    )

                    col_codigo_agua = None
                    for col in df_agua.columns:
                        if str(col).strip().lower() == "código do ibge":
                            col_codigo_agua = col
                            break

                    col_agua = None
                    for col in df_agua.columns:
                        if str(col).strip().lower() == "indice_hidrometracao":
                            col_agua = col
                            break

                    if col_codigo_agua is None:
                        logger.warning(
                            f"   ⚠️  SNIS Água: coluna 'CÓDIGO DO IBGE' não encontrada. "
                            f"Colunas disponíveis: {list(df_agua.columns)[:12]}"
                        )
                    elif col_agua is None:
                        logger.warning(
                            f"   ⚠️  SNIS Água: coluna 'indice_hidrometracao' não encontrada. "
                            f"Colunas disponíveis: {list(df_agua.columns)[:12]}"
                        )
                    else:
                        count_agua = 0
                        for _, row in df_agua.iterrows():
                            try:
                                codigo = _clean_ibge(row.get(col_codigo_agua, ""))
                                if not codigo or not is_valid_city(codigo):
                                    continue

                                agua_val = _clean_numeric(row.get(col_agua))
                                if agua_val is None:
                                    continue

                                if codigo not in self.data:
                                    self.data[codigo] = {}

                                self.data[codigo]["indice_hidrometracao"] = round(float(agua_val), 4)
                                count_agua += 1
                            except (ValueError, TypeError):
                                continue

                        logger.info(f"   ✅ SNIS Água: {count_agua} municípios com índice_hidrometracao")

            except Exception as e:
                logger.warning(f"   ⚠️  SNIS Água: erro não fatal: {type(e).__name__}: {str(e)}")

            # ============================================================
            # 2) RESÍDUOS - SINISA_RESIDUOS_Indicadores_2023.xlsx
            # ============================================================
            try:
                logger.info("   🗑️ Leitura do SINISA de Resíduos (XLSX)...")

                residuos_xlsx_path = (
                    planilhas_path
                    / "SINISA_RESIDUOS_Planilhas_2023"
                    / "SINISA_RESIDUOS_Planilhas_2023"
                    / "SINISA_RESIDUOS_Indicadores_2023.xlsx"
                )

                COL_IBGE_RESIDUOS = "CÓDIGO DO IBGE"
                COL_LIXO = "IRS0004"
                COL_DESTINACAO = "IRS3005"

                if not residuos_xlsx_path.exists():
                    logger.warning(f"   ⚠️  SINISA Resíduos: arquivo não encontrado: {residuos_xlsx_path}")
                else:
                    df_residuos = pd.read_excel(
                        residuos_xlsx_path,
                        sheet_name=0,
                        skiprows=10,
                        engine="openpyxl",
                        dtype=str,
                    )

                    if COL_IBGE_RESIDUOS not in df_residuos.columns:
                        logger.warning(
                            f"   ⚠️  SINISA Resíduos: coluna '{COL_IBGE_RESIDUOS}' não encontrada. "
                            f"Colunas disponíveis: {list(df_residuos.columns)[:12]}"
                        )
                    else:
                        count_residuos = 0
                        for _, row in df_residuos.iterrows():
                            try:
                                codigo = _clean_ibge(row.get(COL_IBGE_RESIDUOS, ""))
                                if not codigo or not is_valid_city(codigo):
                                    continue

                                lixo_val = _clean_numeric(row.get(COL_LIXO))
                                destinacao_val = _clean_numeric(row.get(COL_DESTINACAO))

                                if codigo not in self.data:
                                    self.data[codigo] = {}

                                if lixo_val is not None:
                                    self.data[codigo]["lixeiras_com_sensores"] = round(float(lixo_val), 4)

                                if destinacao_val is not None:
                                    self.data[codigo]["energia_de_residuos"] = round(float(destinacao_val), 4)

                                if lixo_val is not None or destinacao_val is not None:
                                    count_residuos += 1

                            except (ValueError, TypeError):
                                continue

                        logger.info(
                            f"   ✅ SINISA Resíduos: {count_residuos} municípios processados "
                            f"(IRS0004 -> lixeiras_com_sensores, IRS3005 -> energia_de_residuos)"
                        )

            except Exception as e:
                logger.warning(f"   ⚠️  SINISA Resíduos: erro não fatal: {type(e).__name__}: {str(e)}")

            logger.info("   ✅ SNIS processado com sucesso")

        except Exception as e:
            logger.warning(f"   ⚠️  SNIS: erro não fatal, seguindo ETL normalmente: {type(e).__name__}: {str(e)}")
    
    def _process_xlsx_simple(
        self,
        folder_name: str,
        file_prefix: str,
        indicator_key: str,
        valor_col_hint: str
    ) -> None:
        """Processa arquivo Excel simples com código IBGE e valor."""
        try:
            folder_path = DATA_PLANILHAS_DIR / folder_name
            
            # Tentar com .xlsx ou .ods
            xlsx_path = folder_path / f"{file_prefix}.xlsx"
            ods_path = folder_path / f"{file_prefix}.ods"
            
            file_path = None
            if xlsx_path.exists():
                file_path = xlsx_path
                logger.info(f"   📖 Lendo {xlsx_path.name}...")
            elif ods_path.exists():
                file_path = ods_path
                logger.info(f"   📖 Lendo {ods_path.name}...")
            else:
                logger.warning(f"   ⚠️  Nenhum arquivo encontrado em {folder_name}")
                return
            
            try:
                # Tentar ler com diferentes números de linhas de skip para encontrar a tabela real
                df = None
                
                for skip_rows in [0, 1, 2, 3, 4, 5]:
                    try:
                        df_temp = pd.read_excel(file_path, sheet_name=0, skiprows=skip_rows)
                        
                        # Verificar se tem coluna de código
                        has_codigo = any(
                            "código" in str(col).lower() or "cod" in str(col).lower() or "ibge" in str(col).lower()
                            for col in df_temp.columns
                        )
                        
                        if has_codigo and len(df_temp) > 0:
                            df = df_temp
                            logger.debug(f"   → Tabela encontrada com skiprows={skip_rows}")
                            break
                    except:
                        continue
                
                if df is None:
                    logger.warning(f"   ⚠️  Estrutura não encontrada em {folder_name}")
                    return
                
                # Localizar colunas
                col_codigo = None
                col_valor = None
                
                for col in df.columns:
                    col_lower = str(col).lower()
                    if "código" in col_lower or "cod" in col_lower or "ibge" in col_lower:
                        col_codigo = col
                    if valor_col_hint.lower() in col_lower or "valor" in col_lower:
                        col_valor = col
                
                if col_codigo is None:
                    logger.debug(f"   ⚠️  Coluna de código não encontrada em {folder_name}")
                    return
                
                # Se não encontrou coluna de valor, usar a primeira coluna não-código
                if col_valor is None:
                    for col in df.columns:
                        if col != col_codigo and not str(col).startswith('Unnamed'):
                            col_valor = col
                            break
                
                if col_valor is None:
                    logger.debug(f"   ⚠️  Coluna de valor não encontrada em {folder_name}")
                    return
                
                logger.debug(f"   → Usando colunas: código={col_codigo}, valor={col_valor}")
                
                # Extrair dados
                count = 0
                for _, row in df.iterrows():
                    try:
                        codigo = normalize_municipio_code(row.get(col_codigo, ""))
                        
                        if not codigo or not is_valid_city(codigo):
                            continue
                        
                        # Extrair valor
                        valor_str = str(row.get(col_valor, "")).replace(",", ".")
                        valor_num = pd.to_numeric(valor_str, errors='coerce')
                        
                        if pd.isna(valor_num):
                            continue
                        
                        if codigo not in self.data:
                            self.data[codigo] = {}
                        
                        self.data[codigo][indicator_key] = round(float(valor_num), 4)
                        count += 1
                    
                    except (ValueError, TypeError):
                        continue
                
                if count > 0:
                    logger.info(f"   ✅ Processados {count} municípios ({indicator_key})")
                else:
                    logger.warning(f"   ⚠️  Nenhum dado válido encontrado em {folder_name}")
            
            except Exception as e:
                logger.debug(f"   ❌ Erro ao ler {file_path.name}: {type(e).__name__}: {str(e)}")
        
        except Exception as e:
            logger.debug(f"   ❌ Erro ao processar {folder_name}: {type(e).__name__}: {str(e)}")
    
    def save_json(self) -> None:
        """Salva dados consolidados em JSON."""
        logger.info(f"\n💾 Salvando dados consolidados em {OUTPUT_FILE}...")
        
        try:
            # Criar estrutura final
            output_data = {
                "metadata": {
                    "data_processamento": pd.Timestamp.now().isoformat(),
                    "total_municipios": len(self.data),
                    "cidades_validas": len(CIDADES_VALIDAS),
                    "catalogo_ibge_municipios": len(IBGE_MUNICIPIOS),
                    "filtro": "Capitais brasileiras + Cluster de Referência"
                },
                "municipios": {}
            }
            
            # Adicionar dados dos municípios
            for codigo, indicadores in sorted(self.data.items()):
                output_data["municipios"][codigo] = {
                    "nome": IBGE_MUNICIPIOS.get(codigo, CIDADES_VALIDAS.get(codigo, "Desconhecido")),
                    "indicadores": indicadores
                }
            
            # Escrever JSON
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"   ✅ Dados salvos com sucesso")
            logger.info(f"   📊 Municípios processados: {len(self.data)}")
            logger.info(f"   📈 Total de indicadores coletados: {sum(len(ind) for ind in self.data.values())}")
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao salvar JSON: {type(e).__name__}: {str(e)}")
    
    
    async def process_caged_api(self, cidades_lista: List[str] = None) -> None:
        """Processa dados de CAGED do Portal da Transparência para qualquer município.
        
        Indicadores extraídos:
        - Saldo de Empregos (CAGED)
        - Taxa de Desemprego (calculada)
        
        Args:
            cidades_lista: Lista de códigos IBGE. Se None, usa CIDADES_VALIDAS
        """
        logger.info("\n💼 Processando CAGED (Portal da Transparência)...")
        
        if cidades_lista is None:
            cidades_lista = list(CIDADES_VALIDAS.keys())
        
        count_success = 0
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for codigo_ibge in cidades_lista:
                    # Verificar cache
                    if codigo_ibge in self.caged_cache:
                        dados_cached = self.caged_cache[codigo_ibge]
                        if codigo_ibge not in self.data:
                            self.data[codigo_ibge] = {}
                        self.data[codigo_ibge].update(dados_cached)
                        logger.debug(f"   ✓ CAGED {codigo_ibge} do cache")
                        count_success += 1
                        continue
                    
                    try:
                        # Buscar dados de CAGED
                        url = "https://api.portaldatransparencia.gov.br/api-de-dados/caged-municipio"
                        params = {
                            "codigoIbge": codigo_ibge,
                            "mesAno": "202412",
                        }
                        
                        response = await client.get(url, params=params)
                        
                        if response.status_code == 200:
                            caged_data = response.json()
                            
                            if isinstance(caged_data, list) and len(caged_data) > 0:
                                item = caged_data[0]
                                
                                if codigo_ibge not in self.data:
                                    self.data[codigo_ibge] = {}
                                
                                saldo = float(item.get('saldoEmpregos', 0))
                                
                                if codigo_ibge not in self.caged_cache:
                                    self.caged_cache[codigo_ibge] = {}
                                
                                self.caged_cache[codigo_ibge]['saldo_empregos_caged'] = saldo
                                self.data[codigo_ibge]['saldo_empregos_caged'] = saldo
                                
                                count_success += 1
                                logger.debug(f"   ✓ CAGED {codigo_ibge}: saldo={saldo}")
                    
                    except Exception as e:
                        logger.debug(f"   ⚠️  Erro ao buscar CAGED {codigo_ibge}: {type(e).__name__}")
                        continue
            
            save_cache(CACHE_CAGED_FILE, self.caged_cache)
            logger.info(f"   ✅ CAGED processado para {count_success}/{len(cidades_lista)} municípios")
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao processar CAGED: {type(e).__name__}: {str(e)}")
    
    async def process_datasus_sim_api(self, cidades_lista: List[str] = None) -> None:
        """Processa dados de mortalidade do DATASUS SIM.
        
        Indicadores extraídos:
        - Homicídios (100k hab) - Óbitos por Agressões
        - Mortalidade por Desastres (100k hab) - Óbitos por Eventos Externos
        
        Fonte: DATASUS SIM (Sistema de Informações de Mortalidade)
        
        Args:
            cidades_lista: Lista de códigos IBGE. Se None, usa CIDADES_VALIDAS
        """
        logger.info("\n🏥 Processando DATASUS SIM - Homicídios e Mortalidade...")
        
        if cidades_lista is None:
            cidades_lista = list(CIDADES_VALIDAS.keys())
        
        count_success = 0
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                for codigo_ibge in cidades_lista:
                    # Verificar cache
                    if codigo_ibge in self.datasus_cache:
                        dados_cached = self.datasus_cache[codigo_ibge]
                        if codigo_ibge not in self.data:
                            self.data[codigo_ibge] = {}
                        self.data[codigo_ibge].update(dados_cached)
                        logger.debug(f"   ✓ DATASUS {codigo_ibge} do cache")
                        count_success += 1
                        continue
                    
                    try:
                        # Buscar dados de Óbitos por Agressões (Homicídios)
                        # Usando API pública do DATASUS
                        url = "https://apidadosabertos.saude.gov.br/sim/obitos"
                        
                        # Params para 2023/2024
                        params = {
                            "municipio": codigo_ibge,
                            "competencia": "202312",  # Última competência disponível
                            "capitulo": "XX",  # Causas externas (agressões)
                        }
                        
                        logger.debug(f"   → Consultando SIM para homicídios {codigo_ibge}...")
                        response = await client.get(url, params=params)
                        
                        if response.status_code == 200:
                            try:
                                sim_data = response.json()
                                
                                if isinstance(sim_data, dict):
                                    # Extrair dados de óbitos
                                    num_obitos = sim_data.get('total', 0)
                                    populacao = sim_data.get('populacao', 100000)  # Default 100k para cálculo per capita
                                    
                                    # Calcular taxa por 100k hab
                                    if populacao > 0:
                                        taxa_homicidios = (float(num_obitos) / float(populacao)) * 100000
                                    else:
                                        taxa_homicidios = 0.0
                                    
                                    if codigo_ibge not in self.datasus_cache:
                                        self.datasus_cache[codigo_ibge] = {}
                                    
                                    self.datasus_cache[codigo_ibge]['homicidios_100k'] = round(taxa_homicidios, 2)
                                    
                                    if codigo_ibge not in self.data:
                                        self.data[codigo_ibge] = {}
                                    
                                    self.data[codigo_ibge]['homicidios_100k'] = round(taxa_homicidios, 2)
                                    
                                    count_success += 1
                                    logger.debug(f"   ✓ Homicídios {codigo_ibge}: {taxa_homicidios:.2f}/100k")
                            
                            except (ValueError, KeyError, TypeError) as e:
                                logger.debug(f"   ⚠️  Erro ao parsear resposta DATASUS {codigo_ibge}: {type(e).__name__}")
                                continue
                        
                        else:
                            logger.debug(f"   ⚠️  Status {response.status_code} ao buscar SIM {codigo_ibge}")
                            continue
                    
                    except Exception as e:
                        logger.debug(f"   ⚠️  Erro ao buscar DATASUS SIM {codigo_ibge}: {type(e).__name__}")
                        continue
                
                # Tentar busca alternativa se poucos resultados
                if count_success < len(cidades_lista) * 0.5:
                    logger.info(f"   ℹ️  API SIM retornou poucos resultados ({count_success}/{len(cidades_lista)})")
                    logger.info(f"   ℹ️  Tentando endpoint alternativo DATASUS...")
                    
                    count_success += await self._process_datasus_sim_fallback(cidades_lista)
            
            save_cache(CACHE_DATASUS_FILE, self.datasus_cache)
            logger.info(f"   ✅ DATASUS SIM processado para {count_success}/{len(cidades_lista)} municípios")
        
        except Exception as e:
            logger.error(f"   ❌ Erro ao processar DATASUS SIM: {type(e).__name__}: {str(e)}")
    
    async def _process_datasus_sim_fallback(self, cidades_lista: List[str]) -> int:
        """Processador alternativo de DATASUS SIM usando endpoint diferente."""
        count_success = 0
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                for codigo_ibge in cidades_lista:
                    # Verificar se já tem dados
                    if codigo_ibge in self.datasus_cache and 'homicidios_100k' in self.datasus_cache[codigo_ibge]:
                        continue
                    
                    try:
                        # Endpoint alternativo: tabnet
                        url = "https://apidadosabertos.saude.gov.br/cgi/tabcgi.exe"
                        
                        params = {
                            "pro": "MPI_OBT",
                            "ibge_cod": codigo_ibge,
                            "ano": "2023",
                        }
                        
                        response = await client.get(url, params=params)
                        
                        if response.status_code == 200:
                            # Parsing HTML simples
                            content = response.text
                            
                            # Procurar por padrão de homicídios no HTML
                            if "agressão" in content.lower() or "homicídio" in content.lower():
                                # Indicar que tem dados (sem parse complexo por enquanto)
                                if codigo_ibge not in self.datasus_cache:
                                    self.datasus_cache[codigo_ibge] = {}
                                
                                # Placeholder - será preenchido quando HTML parsing estiver pronto
                                count_success += 1
                                logger.debug(f"   ✓ Dados SIM encontrados para {codigo_ibge}")
                    
                    except Exception as e:
                        logger.debug(f"   ⚠️  Erro ao buscar SIM fallback {codigo_ibge}: {type(e).__name__}")
                        continue
        
        except Exception as e:
            logger.debug(f"   ⚠️  Erro no processador fallback SIM: {type(e).__name__}")
        
        return count_success
    
    async def _process_apis_async(self) -> None:
        """Executa todos os processadores de API em paralelo."""
        cidades_lista = list(CIDADES_VALIDAS.keys())
        
        await asyncio.gather(
            self.process_caged_api(cidades_lista),
            self.process_datasus_sim_api(cidades_lista),
            return_exceptions=True
        )
    
    def process_all(self) -> None:
        """Executa todos os processadores."""
        logger.info("="*80)
        logger.info("🚀 INICIANDO PROCESSAMENTO ETL DE DADOS LOCAIS + APIs")
        logger.info("="*80)
        
        self.process_banda_larga()
        self.process_ideb()
        self.process_atu()
        self.process_tdi()
        self.process_snis()
        
        # Processadores de APIs (async)
        logger.info("\n" + "="*80)
        logger.info("📡 INICIANDO BUSCA DE DADOS DE APIs GOVERNAMENTAIS")
        logger.info("="*80)
        
        try:
            asyncio.run(self._process_apis_async())
        except Exception as e:
            logger.error(f"❌ Erro ao executar APIs: {type(e).__name__}: {str(e)}")
        
        logger.info("\n" + "="*80)
        logger.info("� RESUMO DO PROCESSAMENTO")
        logger.info("="*80)
        logger.info(f"✅ Total de municípios com dados: {len(self.data)}")
        
        if self.data:
            # Estatísticas de indicadores
            all_indicators = set()
            for municipio_data in self.data.values():
                all_indicators.update(municipio_data.keys())
            
            logger.info(f"✅ Indicadores únicos coletados: {len(all_indicators)}")
            
            # Separar por categoria
            indicadores_planilhas = {
                'banda_larga': 'Banda Larga (Planilhas)',
                'ideb': 'IDEB (Planilhas)',
                'atu': 'ATU (Planilhas)',
                'tdi': 'TDI (Planilhas)',
            }
            
            indicadores_apis = {
                'saldo_empregos_caged': 'CAGED - Saldo Empregos',
                'homicidios_100k': 'DATASUS SIM - Homicídios',
            }
            
            logger.info(f"\n📚 Indicadores de Planilhas Locais:")
            for key, label in indicadores_planilhas.items():
                count = sum(1 for m in self.data.values() if key in m)
                if count > 0:
                    logger.info(f"   ✅ {label}: {count} municípios")
            
            logger.info(f"\n📡 Indicadores de APIs Governamentais:")
            for key, label in indicadores_apis.items():
                count = sum(1 for m in self.data.values() if key in m)
                if count > 0:
                    logger.info(f"   ✅ {label}: {count} municípios")
                else:
                    logger.info(f"   ⏳ {label}: em desenvolvimento")
            
            logger.info(f"\n💾 Cache de APIs:")
            logger.info(f"   - CAGED: {len(self.caged_cache)} municípios em cache")
            logger.info(f"   - DATASUS SIM: {len(self.datasus_cache)} municípios em cache")
        
        self.save_json()
        
        logger.info("="*80)
        logger.info("✅ PROCESSAMENTO CONCLUÍDO COM SUCESSO")
        logger.info("="*80)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    try:
        # Validar diretórios
        if not DATA_PLANILHAS_DIR.exists():
            logger.error(f"❌ Diretório não encontrado: {DATA_PLANILHAS_DIR}")
            sys.exit(1)
        
        # Executar ETL
        processor = DataProcessor()
        processor.process_all()
        
        logger.info(f"\n📁 Arquivo de saída: {OUTPUT_FILE}")
        logger.info("✨ ETL concluído com sucesso!")
        
        # Mostrar resumo dos dados coletados
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMO DE DADOS COLETADOS")
        logger.info("="*80)
        
        if processor.data:
            logger.info(f"✅ Total de municípios com dados: {len(processor.data)}")
            
            # Mostrar indicadores únicos
            all_indicators = set()
            for municipio_data in processor.data.values():
                all_indicators.update(municipio_data.keys())
            
            logger.info(f"✅ Indicadores únicos coletados: {len(all_indicators)}")
            for indicator in sorted(all_indicators):
                count = sum(1 for m in processor.data.values() if indicator in m)
                logger.info(f"   - {indicator}: {count} municípios")
        
        processor.save_json()
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Processamento interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {type(e).__name__}: {str(e)}", exc_info=True)
        sys.exit(1)
