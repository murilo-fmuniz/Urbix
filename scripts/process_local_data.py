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

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

# Adicionar backend ao path para imports
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

# Diretórios
DATA_PLANILHAS_DIR = BACKEND_DIR / "data" / "planilhas"
OUTPUT_FILE = BACKEND_DIR / "app" / "data" / "indicators_master.json"

# Garantir que o diretório de saída existe
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# CAPITAIS BRASILEIRAS (27 + referência)
# ============================================================================

# Lista das 27 capitais + 2 do cluster de referência (Londrina, Apucarana não são capitais)
CAPITAIS_IBGE = {
    "1100015": "Porto Velho",           # Rondônia
    "1200060": "Rio Branco",            # Acre
    "1302603": "Manaus",                # Amazonas
    "1400100": "Macapá",                # Amapá
    "1500029": "Boa Vista",             # Roraima
    "1600055": "Belém",                 # Pará
    "1500138": "Palmas",                # Tocantins
    "2100044": "São Luís",              # Maranhão
    "2211001": "Teresina",              # Piauí
    "2304400": "Fortaleza",             # Ceará
    "2408102": "Natal",                 # Rio Grande do Norte
    "2507507": "João Pessoa",           # Paraíba
    "2611606": "Recife",                # Pernambuco
    "2704302": "Maceió",                # Alagoas
    "2800308": "Aracaju",               # Sergipe
    "2927408": "Salvador",              # Bahia
    "3100104": "Brasília",              # Distrito Federal
    "3106200": "Goiânia",               # Goiás
    "3018402": "Belo Horizonte",        # Minas Gerais
    "3500105": "São Paulo",             # São Paulo
    "3304557": "Rio de Janeiro",        # Rio de Janeiro
    "4106902": "Curitiba",              # Paraná
    "4204402": "Florianópolis",         # Santa Catarina
    "4305108": "Porto Alegre",          # Rio Grande do Sul
    "5002704": "Campo Grande",          # Mato Grosso do Sul
    "5103403": "Cuiabá",                # Mato Grosso
    "5208707": "Brasília",              # Brasília (duplicado, ajuste conforme needed)
}

# Cluster de Referência (adicional ao de capitais)
CLUSTER_REFERENCIA = {
    "4101408": "Apucarana",
    "4113700": "Londrina",
}

# Cidades válidas para filtro
CIDADES_VALIDAS = {**CAPITAIS_IBGE, **CLUSTER_REFERENCIA}

logger.info(f"📍 Cidades válidas para filtro: {len(CIDADES_VALIDAS)}")
logger.info(f"   - 27 Capitais brasileiras")
logger.info(f"   - 2 Cluster de Referência (Apucarana, Londrina)")

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
    """Verifica se o código do município está na lista de cidades válidas."""
    return codigo_ibge in CIDADES_VALIDAS


# ============================================================================
# PROCESSADORES POR TIPO DE DADO
# ============================================================================

class DataProcessor:
    """Processador centralizado de dados."""
    
    def __init__(self):
        self.data = {}  # Dict[codigo_ibge] -> Dict[indicador] -> valor
        logger.info("✅ DataProcessor inicializado")
    
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
                    "filtro": "Capitais brasileiras + Cluster de Referência"
                },
                "municipios": {}
            }
            
            # Adicionar dados dos municípios
            for codigo, indicadores in sorted(self.data.items()):
                output_data["municipios"][codigo] = {
                    "nome": CIDADES_VALIDAS.get(codigo, "Desconhecido"),
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
    
    def process_all(self) -> None:
        """Executa todos os processadores."""
        logger.info("="*80)
        logger.info("🚀 INICIANDO PROCESSAMENTO ETL DE DADOS LOCAIS")
        logger.info("="*80)
        
        self.process_banda_larga()
        self.process_ideb()
        self.process_atu()
        self.process_tdi()
        
        logger.info("\n" + "="*80)
        logger.info("📝 RESUMO DO PROCESSAMENTO")
        logger.info("="*80)
        logger.info(f"✅ Total de municípios com dados: {len(self.data)}")
        
        if self.data:
            # Estatísticas de indicadores
            all_indicators = set()
            for municipio_data in self.data.values():
                all_indicators.update(municipio_data.keys())
            
            logger.info(f"✅ Indicadores únicos coletados: {len(all_indicators)}")
            for indicator in sorted(all_indicators):
                count = sum(1 for m in self.data.values() if indicator in m)
                logger.info(f"   - {indicator}: {count} municípios")
        
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
    
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Processamento interrompido pelo usuário")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {type(e).__name__}: {str(e)}", exc_info=True)
        sys.exit(1)
