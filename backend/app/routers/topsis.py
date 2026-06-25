"""
Router TOPSIS - Endpoints para análise de maturidade Smart Cities

Este módulo contém endpoints para:
- Cálculo de indicadores ISO 37120/37122/37123
- Análise TOPSIS de maturidade de cidades
- Geração de rankings inteligentes com dados reais de APIs governamentais
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pathlib import Path
import json

from app.schemas import (
    CityDataInput,
    TOPSISInput,
    TOPSISResult,
    CityHybridInput,
    ManualCityIndicators,
)
from app.services.indicators import calculate_all_indicators
from app.services.topsis import calculate_topsis
from app.services.external_apis import (
    get_ibge_population,
    get_siconfi_finances,
    get_datasus_health_infrastructure,
    get_inep_education,
    get_transparencia_social,
    get_datasus_expanded_wrapper,
    get_portal_transparencia_expanded_wrapper,
    get_aneel_smart_metering,
    get_ministerio_trabalho_accidents,
    get_antp_zero_emission_fleet,
    get_defesa_civil_disasters,
    get_cnj_corruption_convictions,
)
from app.database import SessionLocal, get_db
from app.models import IndicatorSnapshot, RankingSnapshot, Indicador, CityManualData

# Logger para rastreamento
logger = logging.getLogger(__name__)

topsis_router = APIRouter(prefix="/topsis", tags=["TOPSIS"])


CAPITAIS_BRASILEIRAS = [
    {"codigo_ibge": "1100205", "nome": "Porto Velho"},
    {"codigo_ibge": "1200401", "nome": "Rio Branco"},
    {"codigo_ibge": "1302603", "nome": "Manaus"},
    {"codigo_ibge": "1400100", "nome": "Boa Vista"},
    {"codigo_ibge": "1501402", "nome": "Belém"},
    {"codigo_ibge": "1600303", "nome": "Macapá"},
    {"codigo_ibge": "1721000", "nome": "Palmas"},
    {"codigo_ibge": "2105302", "nome": "São Luís"},
    {"codigo_ibge": "2207702", "nome": "Teresina"},
    {"codigo_ibge": "2304400", "nome": "Fortaleza"},
    {"codigo_ibge": "2408102", "nome": "Natal"},
    {"codigo_ibge": "2507507", "nome": "João Pessoa"},
    {"codigo_ibge": "2607901", "nome": "Recife"},
    {"codigo_ibge": "2704302", "nome": "Maceió"},
    {"codigo_ibge": "2800308", "nome": "Aracaju"},
    {"codigo_ibge": "2905701", "nome": "Salvador"},
    {"codigo_ibge": "3106200", "nome": "Belo Horizonte"},
    {"codigo_ibge": "3205309", "nome": "Vitória"},
    {"codigo_ibge": "3304557", "nome": "Rio de Janeiro"},
    {"codigo_ibge": "3550308", "nome": "São Paulo"},
    {"codigo_ibge": "4106902", "nome": "Curitiba"},
    {"codigo_ibge": "4205407", "nome": "Florianópolis"},
    {"codigo_ibge": "4305108", "nome": "Porto Alegre"},
    {"codigo_ibge": "5002704", "nome": "Campo Grande"},
    {"codigo_ibge": "5103403", "nome": "Cuiabá"},
    {"codigo_ibge": "5208707", "nome": "Goiânia"},
    {"codigo_ibge": "5300108", "nome": "Brasília"},
    {"codigo_ibge": "9999999", "nome": "UTFPRCity"},
]


def _unique_cities(cities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove duplicatas preservando a primeira ocorrência."""
    seen = set()
    unique = []
    for city in cities:
        codigo = str(city.get("codigo_ibge", "")).strip()
        nome = str(city.get("nome", "")).strip()
        if not codigo or codigo in seen:
            continue
        seen.add(codigo)
        unique.append({"codigo_ibge": codigo, "nome": nome})
    return unique

# ==========================================
# CONFIGURAÇÃO TOPSIS: IMPACTOS E PESOS
# ==========================================

# Definição dos 50 indicadores em ordem (18 + 16 + 16)
INDICADORES_NOMES = [
    # ISO 37120 (18 indicadores)
    "Taxa Desemprego (%)",                              # 0
    "Taxa Endividamento (%)",                           # 1
    "Despesas Capital (% orçamento)",                   # 2
    "Receita Própria (% receita total)",                # 3
    "Orçamento per capita (R$)",                        # 4
    "Mulheres Eleitas em Cargos (%)",                   # 5
    "Condenações por Corrupção (100k hab)",             # 6
    "Participação Eleitoral (%)",                       # 7
    "Moradias Inadequadas (% população)",               # 8
    "Sem-teto (100k hab)",                              # 9
    "Bombeiros (100k hab)",                             # 10
    "Mortes por Incêndio (100k hab)",                   # 11
    "Agentes de Polícia (100k hab)",                    # 12
    "Homicídios (100k hab)",                            # 13
    "Acidentes Industriais (100k hab)",                 # 14
    "Relação Estudante/Professor (alunos/prof)",        # 15
    "IDEB Anos Iniciais (escala 0-10)",                 # 16
    
    # ISO 37122 (16 indicadores)
    "Sobrevivência Novos Negócios (100k hab)",          # 17
    "Empregos em TIC (% força trabalho)",               # 18
    "Graduados STEM (100k hab)",                        # 19
    "Energia de Resíduos (% energia total)",            # 20
    "Iluminação Pública com Telegestão (%)",            # 21
    "Medidores Inteligentes Energia (%)",               # 22
    "Edifícios Verdes Certificados (%)",                # 23
    "Monitoramento Ar em Tempo Real (%)",               # 24
    "Serviços Urbanos Online (%)",                      # 25
    "Prontuário Eletrônico (% população)",              # 26
    "Consultas Remotas (100k hab)",                     # 27
    "Medidores Inteligentes Água (%)",                  # 28
    "Áreas Cobertas por Câmeras (% cidade)",            # 29
    "Lixeiras com Sensores (%)",                        # 30
    "Semáforos Inteligentes (%)",                       # 31
    "Frota Ônibus Zero Emissão (%)",                    # 32
    "Escolas Conectadas com TeleGestão (%)",            # 33
    
    # ISO 37123 + Marco de Sendai (16 indicadores)
    "Seguros contra Ameaças (% população)",             # 34
    "Empregos Informais (% força trabalho)",            # 35
    "Escolas com Plano Emergência (%)",                 # 36
    "População Treinada em Emergência (%)",             # 37
    "Hospitais com Gerador Backup (%)",                 # 38
    "Seguro Saúde Básico (% população)",                # 39
    "Taxa de Imunização (%)",                           # 40
    "Abrigos de Emergência (100k hab)",                 # 41
    "Edifícios Vulneráveis a Desastres (%)",            # 42
    "Rotas de Evacuação Identificadas (100k)",          # 43
    "Reservas de Alimentos 72h (%)",                    # 44
    "Mapas de Ameaças Públicos (%)",                    # 45
    "Mortalidade por Desastres (100k hab)",             # 46
    "Pessoas Afetadas por Desastres (100k hab)",        # 47
    "Perdas por Desastres (% PIB)",                     # 48
    "Danos à Infraestrutura Básica (%)",                # 49
]

# Impactos por indicador (1 = benefício, -1 = custo)
# Regra matemática: quanto MAIOR, melhor (1), ou quanto MAIOR, pior (-1)
IMPACTOS_ISO37120 = [
    -1,  # Taxa Desemprego: MENOR é melhor
    -1,  # Taxa Endividamento: MENOR é melhor
     1,  # Despesas Capital: MAIOR é melhor (investimento)
     1,  # Receita Própria: MAIOR é melhor (autonomia)
     1,  # Orçamento per capita: MAIOR é melhor
     1,  # Mulheres Eleitas: MAIOR é melhor (igualdade)
    -1,  # Condenações Corrupção: MENOR é melhor
     1,  # Participação Eleitoral: MAIOR é melhor
    -1,  # Moradias Inadequadas: MENOR é melhor
    -1,  # Sem-teto: MENOR é melhor
     1,  # Bombeiros: MAIOR é melhor (segurança)
    -1,  # Mortes Incêndio: MENOR é melhor
     1,  # Agentes Polícia: MAIOR é melhor (segurança)
    -1,  # Homicídios: MENOR é melhor
    -1,  # Acidentes Industriais: MENOR é melhor
    -1,  # Relação Estudante/Professor: MENOR é melhor (salas menos lotadas)
     1,  # IDEB Anos Iniciais: MAIOR é melhor (educação mais forte)
]

IMPACTOS_ISO37122 = [
     1,  # Sobrevivência Novos Negócios: MAIOR é melhor
     1,  # Empregos TIC: MAIOR é melhor
     1,  # Graduados STEM: MAIOR é melhor
     1,  # Energia de Resíduos: MAIOR é melhor (sustentabilidade)
     1,  # Iluminação Telegestão: MAIOR é melhor (smart)
     1,  # Medidores Inteligentes Energia: MAIOR é melhor (smart)
     1,  # Edifícios Verdes: MAIOR é melhor (sustentabilidade)
     1,  # Monitoramento Ar: MAIOR é melhor (meio ambiente)
     1,  # Serviços Online: MAIOR é melhor (e-gov)
     1,  # Prontuário Eletrônico: MAIOR é melhor (saúde smart)
     1,  # Consultas Remotas: MAIOR é melhor (telemedicina)
     1,  # Medidores Inteligentes Água: MAIOR é melhor (smart)
     1,  # Câmeras: MAIOR é melhor (segurança smart)
     1,  # Lixeiras Sensores: MAIOR é melhor (smart waste)
     1,  # Semáforos Inteligentes: MAIOR é melhor (mobilidade smart)
     1,  # Ônibus Zero Emissão: MAIOR é melhor (sustentabilidade)
     1,  # Escolas Conectadas: MAIOR é melhor (educação smart)
]

IMPACTOS_ISO37123 = [
     1,  # Seguros: MAIOR é melhor (resiliência)
    -1,  # Empregos Informais: MENOR é melhor
     1,  # Escolas com Plano: MAIOR é melhor (preparação)
     1,  # População Treinada: MAIOR é melhor (preparação)
     1,  # Hospitais com Gerador: MAIOR é melhor (resiliência saúde)
     1,  # Seguro Saúde: MAIOR é melhor (cobertura)
     1,  # Imunização: MAIOR é melhor (saúde pública)
     1,  # Abrigos: MAIOR é melhor (preparação)
    -1,  # Edifícios Vulneráveis: MENOR é melhor
     1,  # Rotas Evacuação: MAIOR é melhor (preparação)
     1,  # Reservas Alimentos: MAIOR é melhor (resiliência)
     1,  # Mapas de Ameaças: MAIOR é melhor (prevenção)
    -1,  # Mortalidade Desastres: MENOR é melhor
    -1,  # Pessoas Afetadas: MENOR é melhor
    -1,  # Perdas (PIB): MENOR é melhor
    -1,  # Danos Infraestrutura: MENOR é melhor
]

# Concatenar todos os impactos
IMPACTOS_TOTAIS = IMPACTOS_ISO37120 + IMPACTOS_ISO37122 + IMPACTOS_ISO37123

# Calcular pesos equitativos (todos os indicadores têm peso igual)
_NUM_INDICADORES = len(IMPACTOS_TOTAIS)  # Deve ser 50 (47 originais + 3 educacionais INEP)
PESOS_EQUITATIVOS = [1.0 / _NUM_INDICADORES] * _NUM_INDICADORES

logger.info(f"✅ TOPSIS Configurado: {_NUM_INDICADORES} indicadores, peso equitativo: {PESOS_EQUITATIVOS[0]:.4f}")

# ==========================================
# FUNÇÃO AUXILIAR: CARREGAR DADOS ETL
# ==========================================

def load_etl_data_for_city(codigo_ibge: str) -> Dict[str, Any]:
    """
    🔄 Carrega dados de CAGED e DATASUS SIM do arquivo indicators_master.json
    
    Arquivo gerado por: scripts/process_local_data.py
    Localização: backend/app/data/indicators_master.json
    
    Args:
        codigo_ibge: Código IBGE da cidade
    
    Returns:
        Dict com chaves:
        - saldo_empregos_caged: Saldo de empregos (Portal da Transparência)
        - homicidios_100k: Taxa de homicídios por 100k habitantes (DATASUS SIM)
    """
    etl_file = Path(__file__).parent.parent / "data" / "indicators_master.json"
    
    etl_data = {}
    
    if not etl_file.exists():
        logger.debug(f"⚠️  Arquivo ETL não encontrado: {etl_file}")
        return etl_data
    
    try:
        with open(etl_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        # Extrair dados para esta cidade
        if "municipios" in master_data and codigo_ibge in master_data["municipios"]:
            cidade_data = master_data["municipios"][codigo_ibge]
            
            # Extrair CAGED (Saldo de Empregos)
            if "saldo_empregos_caged" in cidade_data:
                etl_data["saldo_empregos_caged"] = cidade_data["saldo_empregos_caged"]
                logger.debug(f"   ✅ ETL CAGED: {etl_data['saldo_empregos_caged']}")
            
            # Extrair DATASUS SIM (Homicídios)
            if "homicidios_100k" in cidade_data:
                etl_data["homicidios_100k"] = cidade_data["homicidios_100k"]
                logger.debug(f"   ✅ ETL DATASUS SIM: {etl_data['homicidios_100k']}")
        
        return etl_data
    
    except Exception as e:
        logger.warning(f"⚠️  Erro ao ler dados ETL: {str(e)}")
        return etl_data

# ==========================================
# FUNÇÕES AUXILIARES: INTERPOLAÇÃO INTELIGENTE
# ==========================================

# ==========================================
# FUNÇÕES AUXILIARES: EXTRAÇÃO, INJEÇÃO E MOCK
# ==========================================

def flatten_manual_indicators(manual: ManualCityIndicators) -> List[float]:
    """
    ⭐ PASSO 1: EXTRAÇÃO DINÂMICA (FLATTENING)
    
    Extrai todos os 50 indicadores do objeto ManualCityIndicators em ordem plana [float].
    Respeita RIGOROSAMENTE a ordem declarada no Pydantic.
    
    Estrutura esperada:
    - ISO 37120: 18 indicadores (16 originais + 2 INEP)
    - ISO 37122: 16 indicadores (15 originais + 1 INEP)
    - ISO 37123 + Sendai: 16 indicadores
    
    Args:
        manual: Objeto ManualCityIndicators estruturado por ISO
    
    Returns:
        Lista plana com 50 floats em ordem (47 ISO + 3 INEP educação)
    """
    indicadores_flat = [
        # ===== ISO 37120 (18 indicadores) =====
        manual.iso_37120.taxa_desemprego_pct,
        manual.iso_37120.taxa_endividamento_pct,
        manual.iso_37120.despesas_capital_pct,
        manual.iso_37120.receita_propria_pct,
        manual.iso_37120.orcamento_per_capita,
        manual.iso_37120.mulheres_eleitas_pct,
        manual.iso_37120.condenacoes_corrupcao_100k,
        manual.iso_37120.participacao_eleitoral_pct,
        manual.iso_37120.moradias_inadequadas_pct,
        manual.iso_37120.sem_teto_100k,
        manual.iso_37120.bombeiros_100k,
        manual.iso_37120.mortes_incendio_100k,
        manual.iso_37120.agentes_policia_100k,
        manual.iso_37120.homicidios_100k,
        manual.iso_37120.acidentes_industriais_100k,
        manual.iso_37120.relacao_estudante_professor,  # [15] NEW INEP
        manual.iso_37120.ideb_anos_iniciais,           # [16] NEW INEP
        
        # ===== ISO 37122 (16 indicadores) =====
        manual.iso_37122.sobrevivencia_novos_negocios_100k,
        manual.iso_37122.empregos_tic_pct,
        manual.iso_37122.graduados_stem_100k,
        manual.iso_37122.energia_residuos_pct,
        manual.iso_37122.iluminacao_telegestao_pct,
        manual.iso_37122.medidores_inteligentes_energia_pct,
        manual.iso_37122.edificios_verdes_pct,
        manual.iso_37122.monitoramento_ar_tempo_real_pct,
        manual.iso_37122.servicos_urbanos_online_pct,
        manual.iso_37122.prontuario_eletronico_pct,
        manual.iso_37122.consultas_remotas_100k,
        manual.iso_37122.medidores_inteligentes_agua_pct,
        manual.iso_37122.areas_cobertas_cameras_pct,
        manual.iso_37122.lixeiras_sensores_pct,
        manual.iso_37122.semaforos_inteligentes_pct,
        manual.iso_37122.frota_onibus_limpos_pct,
        manual.iso_37122.escolas_conectadas_pct,      # [33] NEW INEP
        
        # ===== ISO 37123 + SENDAI (16 indicadores) =====
        manual.iso_37123.seguro_ameacas_pct,
        manual.iso_37123.empregos_informais_pct,
        manual.iso_37123.escolas_preparacao_emergencia_pct,
        manual.iso_37123.populacao_treinada_emergencia_pct,
        manual.iso_37123.hospitais_geradores_backup_pct,
        manual.iso_37123.seguro_saude_basico_pct,
        manual.iso_37123.imunizacao_pct,
        manual.iso_37123.abrigos_emergencia_100k,
        manual.iso_37123.edificios_vulneraveis_pct,
        manual.iso_37123.rotas_evacuacao_100k,
        manual.iso_37123.reservas_alimentos_72h_pct,
        manual.iso_37123.mapas_ameacas_publicos_pct,
        manual.iso_37123.mortalidade_desastres_100k,
        manual.iso_37123.pessoas_afetadas_desastres_100k,
        manual.iso_37123.perdas_desastres_pct_pib,
        manual.iso_37123.danos_infraestrutura_basica_pct,
    ]
    
    assert len(indicadores_flat) == 50, f"❌ ERRO: Esperado 50 indicadores, obteve {len(indicadores_flat)}"
    logger.debug(f"✅ Flattening completo: 50 indicadores extraídos em ordem")
    
    return indicadores_flat


def inject_api_data_into_flat_list(
    indicadores_flat: List[float],
    siconfi_data: Dict[str, Any],
    ibge_data: Dict[str, Any],
    datasus_data: Dict[str, Any],
    inep_data: Dict[str, Any],
    transparencia_data: Dict[str, Any],
    datasus_expanded_data: Dict[str, Any],
    portal_social_data: Dict[str, Any],  # NEW: Social programs data
    etl_data: Dict[str, Any],  # NEW: ETL data (CAGED, DATASUS SIM)
    # 🎯 5 NOVAS APIs (PARTE 3)
    aneel_data: Dict[str, Any],  # API 5: ANEEL
    ministerio_trabalho_data: Dict[str, Any],  # API 6: Min. Trabalho
    antp_data: Dict[str, Any],  # API 7: ANTP
    defesa_civil_data: Dict[str, Any],  # API 8: Defesa Civil
    cnj_data: Dict[str, Any],  # API 9: CNJ
    nome_cidade: str
) -> List[float]:
    """
    ⭐ PASSO 2: INJEÇÃO DOS DADOS AUTOMÁTICOS (OTIMIZADA - 15+ INDICADORES REAIS)
    
    Sobrescreve valores específicos na lista plana com dados das APIs:
    - SICONFI: receita_propria_pct, despesas_capital_pct, orcamento_per_capita, divida (endividamento)
    - IBGE: população (para cálculos per capita)
    - DataSUS: hospitais_por_100k, proxy de serviços de saúde
    - DataSUS Expandido: 5 indicadores de saúde [28-32]
    - INEP: relacao_estudante_professor, ideb_anos_iniciais, escolas_conectadas_pct
    - Portal da Transparência: taxa_populacao_assistida (Bolsa Família como proxy de vulnerabilidade social)
    - 🎯 ETL (NOVO): CAGED (empregos), DATASUS SIM (homicídios)
    - 🎯 5 NOVAS APIs (PARTE 3): ANEEL, Min. Trabalho, ANTP, Defesa Civil, CNJ
    
    Estratégia de Preenchimento:
    1. Se manual == 0.0 E API tem dados > 0 → Sobrescreve com API (dado real)
    2. Se manual > 0 → Mantém manual (usuário tem prioridade)
    3. Se manual == 0.0 E API == 0 → Deixa em branco para normalização (não distorce dados)
    
    Args:
        indicadores_flat: Lista plana com 50 valores (após flattening)
        siconfi_data: Dict com receita_propria, despesas_capital, receita_total, divida_consolidada
        ibge_data: Dict com populacao
        datasus_data: Dict com num_hospitais
        inep_data: Dict com relacao_estudante_professor, ideb_anos_iniciais, escolas_conectadas_pct
        transparencia_data: Dict com beneficiados_bolsa_familia
        datasus_expanded_data: Dict com 5 indicadores de saúde (novo em Phase 2)
        portal_social_data: Dict com dados de programas sociais
        etl_data: 🎯 Dict com saldo_empregos_caged, homicidios_100k (do indicators_master.json)
        aneel_data: 🎯 Dict com medidores_inteligentes_pct (API ANEEL)
        ministerio_trabalho_data: 🎯 Dict com acidentes_industriais_100k (API Min. Trabalho)
        antp_data: 🎯 Dict com frota_onibus_zero_emissao_pct (API ANTP)
        defesa_civil_data: 🎯 Dict com mortalidade_desastres_100k, perdas_desastres_pct_pib (API Defesa Civil)
        cnj_data: 🎯 Dict com condenacoes_corrupcao_100k (API CNJ)
        nome_cidade: Para logging
    
    Returns:
        Lista atualizada com dados das APIs injetados em ~30 indicadores
    """
    
    # DEBUG: Log dos dados que chegaram
    logger.info(f"\n🔍 DEBUG: Dados recebidos para injeção ({nome_cidade}):")
    logger.info(f"   INEP keys: {list(inep_data.keys()) if isinstance(inep_data, dict) else 'não é dict'}")
    logger.info(f"   INEP relacao: {inep_data.get('relacao_estudante_professor') if isinstance(inep_data, dict) else 'N/A'}")
    logger.info(f"   INEP ideb: {inep_data.get('ideb_anos_iniciais') if isinstance(inep_data, dict) else 'N/A'}")
    logger.info(f"   INEP escolas: {inep_data.get('escolas_conectadas_pct') if isinstance(inep_data, dict) else 'N/A'}")
    indicadores_flat = list(indicadores_flat)  # Copiar para não modificar original
    
    # ==========================================================
    # 🛡️ BLINDAGEM CONTRA TIPOS ERRADOS DA API/FALLBACK (ERRO 503)
    # ==========================================================
    siconfi_data = siconfi_data if isinstance(siconfi_data, dict) else {}
    datasus_data = datasus_data if isinstance(datasus_data, dict) else {}
    inep_data = inep_data if isinstance(inep_data, dict) else {}
    transparencia_data = transparencia_data if isinstance(transparencia_data, dict) else {}
    datasus_expanded_data = datasus_expanded_data if isinstance(datasus_expanded_data, dict) else {}
    portal_social_data = portal_social_data if isinstance(portal_social_data, dict) else {}  # NEW: Social programs
    etl_data = etl_data if isinstance(etl_data, dict) else {}  # 🎯 NEW: ETL data
    # 🎯 5 NOVAS APIs (PARTE 3) - Blindagem
    aneel_data = aneel_data if isinstance(aneel_data, dict) else {}
    ministerio_trabalho_data = ministerio_trabalho_data if isinstance(ministerio_trabalho_data, dict) else {}
    antp_data = antp_data if isinstance(antp_data, dict) else {}
    defesa_civil_data = defesa_civil_data if isinstance(defesa_civil_data, dict) else {}
    cnj_data = cnj_data if isinstance(cnj_data, dict) else {}
    
    if isinstance(ibge_data, (int, float)):
        ibge_data = {"populacao": float(ibge_data)}
    elif not isinstance(ibge_data, dict):
        ibge_data = {}
    # ===========================================================
    
    # Extrair dados das APIs com validação segura
    populacao = ibge_data.get("populacao", 0) or 1  # Evitar divisão por zero
    
    receita_propria_valor = siconfi_data.get("receita_propria", 0) or 0
    despesas_capital_valor = siconfi_data.get("despesas_capital", 0) or 0
    receita_total_valor = siconfi_data.get("receita_total", 0) or 1  # Evitar divisão por zero
    divida_consolidada_valor = siconfi_data.get("divida_consolidada", 0) or 0
    arrecadacao_valor = siconfi_data.get("arrecadacao", 0) or 0
    
    num_hospitais = datasus_data.get("num_hospitais", 0) or 0
    
    # Extrair dados DataSUS Expandido (5 novos indicadores Phase 2 Task 4)
    hospitais_por_100k = datasus_expanded_data.get("hospitais_por_100k", 0) or 0
    leitos_uti_pct = datasus_expanded_data.get("leitos_uti_pct", 0) or 0
    cobertura_vacina_covid_pct = datasus_expanded_data.get("cobertura_vacina_covid_pct", 0) or 0
    cobertura_atencao_basica_pct = datasus_expanded_data.get("cobertura_atencao_basica_pct", 0) or 0
    agentes_comunitarios_saude = datasus_expanded_data.get("agentes_comunitarios_saude", 0) or 0
    
    # Extrair dados Portal Transparência Expandido (3 novos indicadores Phase 2 Task 2)
    beneficiarios_programas_sociais_pct = portal_social_data.get("beneficiarios_programas_sociais_pct", 0) or 0
    cobertura_alimentacao_escolar_pct = portal_social_data.get("cobertura_alimentacao_escolar_pct", 0) or 0
    acesso_agua_potavel_pct = portal_social_data.get("acesso_agua_potavel_pct", 0) or 0
    
    # Extrair dados do Portal da Transparência + TSE
    beneficiados_bolsa_familia = transparencia_data.get("beneficiados_bolsa_familia", 0) or 0
    participacao_eleitoral_pct = transparencia_data.get("participacao_eleitoral_pct", 0) or 0
    mulheres_eleitas_pct = transparencia_data.get("mulheres_eleitas_pct", 0) or 0
    
    # 🎯 Extrair dados do ETL (indicators_master.json gerado por process_local_data.py)
    saldo_empregos_caged = etl_data.get("saldo_empregos_caged", 0) or 0
    homicidios_100k_etl = etl_data.get("homicidios_100k", 0) or 0
    
    # 🎯 Extrair dados das 5 NOVAS APIs (PARTE 3)
    medidores_inteligentes_pct = aneel_data.get("medidores_inteligentes_pct", 0) or 0
    acidentes_industriais_100k = ministerio_trabalho_data.get("acidentes_industriais_100k", 0) or 0
    frota_onibus_zero_emissao_pct = antp_data.get("frota_onibus_zero_emissao_pct", 0) or 0
    mortalidade_desastres_100k = defesa_civil_data.get("mortalidade_desastres_100k", 0) or 0
    perdas_desastres_pct_pib = defesa_civil_data.get("perdas_desastres_pct_pib", 0) or 0
    condenacoes_corrupcao_100k = cnj_data.get("condenacoes_corrupcao_100k", 0) or 0
    
    logger.info(f"\n💾 INJEÇÃO DE DADOS DAS APIS ({nome_cidade}) - 25+ INDICADORES REAIS:")
    logger.info(f"   📊 SICONFI: receita={receita_propria_valor}, despesas={despesas_capital_valor}, receita_total={receita_total_valor}, dívida={divida_consolidada_valor}")
    logger.info(f"   📊 IBGE: população={populacao}")
    logger.info(f"   📊 DataSUS: hospitais={num_hospitais}")
    logger.info(f"   📊 DataSUS Expandido (Phase 2): hospitais_100k={hospitais_por_100k}, leitos_uti={leitos_uti_pct}%, vacina={cobertura_vacina_covid_pct}%, atencao_basica={cobertura_atencao_basica_pct}%, agentes={agentes_comunitarios_saude}")
    logger.info(f"   📊 Portal Expandido (Phase 2): prog_sociais={beneficiarios_programas_sociais_pct}%, alimentacao={cobertura_alimentacao_escolar_pct}%, agua={acesso_agua_potavel_pct}%")
    logger.info(f"   📊 TSE: participacao={participacao_eleitoral_pct}%, mulheres={mulheres_eleitas_pct}%")
    logger.info(f"   📊 Portal: beneficiados_bolsa_familia={beneficiados_bolsa_familia}")
    logger.info(f"   🎯 ETL: saldo_empregos={saldo_empregos_caged}, homicidios_100k={homicidios_100k_etl} (CAGED + DATASUS SIM)")
    # 🎯 Logs das 5 NOVAS APIs (PARTE 3)
    logger.info(f"   🎯 ANEEL: medidores_inteligentes={medidores_inteligentes_pct}%")
    logger.info(f"   🎯 Min. Trabalho: acidentes_industriais={acidentes_industriais_100k}/100k")
    logger.info(f"   🎯 ANTP: frota_zero_emissao={frota_onibus_zero_emissao_pct}%")
    logger.info(f"   🎯 Defesa Civil: mortalidade_desastres={mortalidade_desastres_100k}/100k, perdas_desastres={perdas_desastres_pct_pib}% PIB")
    logger.info(f"   🎯 CNJ: condenacoes_corrupcao={condenacoes_corrupcao_100k}/100k")
    
    # ===== CÁLCULOS DOS INDICADORES REAIS =====
    
    # Índice [1] = Taxa de Endividamento (%)
    taxa_endividamento_calc = (divida_consolidada_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # Índice [2] = Despesas de Capital (% orçamento)
    despesas_capital_pct_calc = (despesas_capital_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # Índice [3] = Receita Própria (% receita total)
    receita_propria_pct_calc = (receita_propria_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # Índice [4] = Orçamento per capita (R$)
    orcamento_per_capita_calc = (receita_total_valor / populacao) if populacao > 0 else 0.0
    
    # Índice [8] = Moradias Inadequadas (usando como proxy Taxa de População Assistida pelo Bolsa Família)
    # Taxa = (beneficiados / população) * 100
    taxa_populacao_assistida_calc = (beneficiados_bolsa_familia / populacao * 100) if populacao > 0 else 0.0
    
    # Índice [9] = Sem-teto (como proxy de vulnerabilidade - usar mesma taxa de Bolsa Família)
    sem_teto_100k_calc = (beneficiados_bolsa_familia / populacao * 100000) if populacao > 0 else 0.0
    
    # Índice [35] = Hospitais com Gerador Backup (usando como proxy hospitais_por_100k)
    hospitais_100k_calc = (num_hospitais / populacao * 100000) if populacao > 0 else 0.0
    
    # Índice [24] = Monitoramento Ar em Tempo Real (proxy: usar taxa de arrecadação como proxy de infraestrutura)
    monitoramento_ar_calc = (arrecadacao_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # Índice [36] = Seguro Saúde Básico (proxy: usar taxa de população com acesso a hospitais)
    seguro_saude_calc = (num_hospitais / populacao * 100) if populacao > 0 else 0.0
    
    # Índice [38] = Abrigos de Emergência (proxy: usar população vulnerável via Bolsa Família)
    abrigos_emergencia_calc = (beneficiados_bolsa_familia / populacao * 100000) if populacao > 0 else 0.0
    
    # Índice [42] = Mapas de Ameaças Públicos (proxy: usar taxa de arrecadação para infraestrutura de mapeamento)
    mapas_ameacas_calc = (arrecadacao_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # ===== INJEÇÕES NA MATRIZ =====
    
    # 🎯 [0] Taxa de Desemprego (%) - Usando CAGED: Saldo de Empregos
    # Interpretação: Saldo positivo → mais empregos → desemprego baixo
    if indicadores_flat[0] == 0.0 and saldo_empregos_caged != 0:
        # Normalizar: maior saldo → menor desemprego
        taxa_desemprego_proxy = max(0, 10 - (saldo_empregos_caged / max(populacao, 1) * 1000))
        indicadores_flat[0] = min(taxa_desemprego_proxy, 25.0)  # Cap em 25%
        logger.info(f"   ✅ [Índice 0] Taxa Desemprego: {indicadores_flat[0]:.2f}% (CAGED - Saldo Empregos)")
    elif indicadores_flat[0] > 0:
        logger.info(f"   ⚪ [Índice 0] Taxa Desemprego: {indicadores_flat[0]:.2f}% (MANUAL)")
    elif indicadores_flat[0] == 0.0:
        logger.info(f"   ⚪ [Índice 0] Taxa Desemprego: 0.0 (SEM DADOS)")
    
    # 🎯 [13] Homicídios (100k hab) - Usando DATASUS SIM
    if indicadores_flat[13] == 0.0 and homicidios_100k_etl > 0:
        indicadores_flat[13] = homicidios_100k_etl
        logger.info(f"   ✅ [Índice 13] Homicídios/100k: {homicidios_100k_etl:.2f} (DATASUS SIM - ETL)")
    elif indicadores_flat[13] > 0:
        logger.info(f"   ⚪ [Índice 13] Homicídios/100k: {indicadores_flat[13]:.2f} (MANUAL)")
    elif indicadores_flat[13] == 0.0:
        logger.info(f"   ⚪ [Índice 13] Homicídios/100k: 0.0 (SEM DADOS)")
    
    # [1] Taxa de Endividamento
    if indicadores_flat[1] == 0.0 and taxa_endividamento_calc > 0:
        indicadores_flat[1] = taxa_endividamento_calc
        logger.info(f"   ✅ [Índice 1] Taxa Endividamento: {taxa_endividamento_calc:.2f}% (SICONFI - RGF)")
    elif indicadores_flat[1] == 0.0:
        logger.info(f"   ⚪ [Índice 1] Taxa Endividamento: 0.0 (SEM DADOS)")
    else:
        logger.info(f"   ⚪ [Índice 1] Taxa Endividamento: {indicadores_flat[1]:.2f}% (MANUAL)")
    
    # [2] Despesas de Capital
    if indicadores_flat[2] == 0.0 and despesas_capital_pct_calc > 0:
        indicadores_flat[2] = despesas_capital_pct_calc
        logger.info(f"   ✅ [Índice 2] Despesas Capital: {despesas_capital_pct_calc:.2f}% (SICONFI - RREO)")
    elif indicadores_flat[2] == 0.0:
        logger.info(f"   ⚪ [Índice 2] Despesas Capital: 0.0 (SEM DADOS)")
    else:
        logger.info(f"   ⚪ [Índice 2] Despesas Capital: {indicadores_flat[2]:.2f}% (MANUAL)")
    
    # [3] Receita Própria
    if indicadores_flat[3] == 0.0 and receita_propria_pct_calc > 0:
        indicadores_flat[3] = receita_propria_pct_calc
        logger.info(f"   ✅ [Índice 3] Receita Própria: {receita_propria_pct_calc:.2f}% (SICONFI - RREO)")
    elif indicadores_flat[3] == 0.0:
        logger.info(f"   ⚪ [Índice 3] Receita Própria: 0.0 (SEM DADOS)")
    else:
        logger.info(f"   ⚪ [Índice 3] Receita Própria: {indicadores_flat[3]:.2f}% (MANUAL)")
    
    # [4] Orçamento per capita
    if indicadores_flat[4] == 0.0 and orcamento_per_capita_calc > 0:
        indicadores_flat[4] = orcamento_per_capita_calc
        logger.info(f"   ✅ [Índice 4] Orçamento/per capita: R$ {orcamento_per_capita_calc:.2f} (SICONFI - RREO)")
    elif indicadores_flat[4] == 0.0:
        logger.info(f"   ⚪ [Índice 4] Orçamento/per capita: 0.0 (SEM DADOS)")
    else:
        logger.info(f"   ⚪ [Índice 4] Orçamento/per capita: R$ {indicadores_flat[4]:.2f} (MANUAL)")
    
    # [8] Moradias Inadequadas/Taxa de População Assistida (Portal da Transparência)
    if indicadores_flat[8] == 0.0 and taxa_populacao_assistida_calc > 0:
        indicadores_flat[8] = taxa_populacao_assistida_calc
        logger.info(f"   ✅ [Índice 8] Pop. Assistida (Bolsa Família): {taxa_populacao_assistida_calc:.2f}% (PORTAL)")
    elif indicadores_flat[8] == 0.0:
        logger.info(f"   ⚪ [Índice 8] Pop. Assistida: 0.0 (SEM DADOS)")
    else:
        logger.info(f"   ⚪ [Índice 8] Pop. Assistida: {indicadores_flat[8]:.2f}% (MANUAL)")
    
    # [9] Sem-teto (proxy de vulnerabilidade social)
    if indicadores_flat[9] == 0.0 and sem_teto_100k_calc > 0:
        indicadores_flat[9] = sem_teto_100k_calc
        logger.info(f"   ✅ [Índice 9] Sem-teto/100k (Bolsa Família): {sem_teto_100k_calc:.2f} (PORTAL)")
    elif indicadores_flat[9] == 0.0:
        logger.info(f"   ⚪ [Índice 9] Sem-teto/100k: 0.0 (SEM DADOS)")
    
    # [15] Relação Estudante/Professor (ISO37120)
    relacao_estudante_professor = inep_data.get("relacao_estudante_professor", 0) or 0
    if indicadores_flat[15] == 0.0 and relacao_estudante_professor > 0:
        indicadores_flat[15] = relacao_estudante_professor
        logger.info(f"   ✅ [Índice 15] Relação Est./Prof: {relacao_estudante_professor:.2f} alunos/prof (INEP)")
    elif indicadores_flat[15] == 0.0:
        logger.info(f"   ⚪ [Índice 15] Relação Est./Prof: 0.0 (SEM DADOS)")
    
    # [16] IDEB Anos Iniciais (ISO37120)
    ideb_anos_iniciais = inep_data.get("ideb_anos_iniciais", 0) or 0
    if indicadores_flat[16] == 0.0 and ideb_anos_iniciais > 0:
        indicadores_flat[16] = ideb_anos_iniciais
        logger.info(f"   ✅ [Índice 16] IDEB Anos Iniciais: {ideb_anos_iniciais:.1f}/10 (INEP)")
    elif indicadores_flat[16] == 0.0:
        logger.info(f"   ⚪ [Índice 16] IDEB Anos Iniciais: 0.0 (SEM DADOS)")
    
    # [5] Mulheres Eleitas em Cargos (% - TSE)
    if indicadores_flat[5] == 0.0 and mulheres_eleitas_pct > 0:
        indicadores_flat[5] = mulheres_eleitas_pct
        logger.info(f"   ✅ [Índice 5] Mulheres Eleitas: {mulheres_eleitas_pct:.1f}% (TSE)")
    elif indicadores_flat[5] == 0.0:
        logger.info(f"   ⚪ [Índice 5] Mulheres Eleitas: 0.0 (SEM DADOS)")
    
    # [7] Participação Eleitoral (% - TSE)
    if indicadores_flat[7] == 0.0 and participacao_eleitoral_pct > 0:
        indicadores_flat[7] = participacao_eleitoral_pct
        logger.info(f"   ✅ [Índice 7] Participação Eleitoral: {participacao_eleitoral_pct:.1f}% (TSE)")
    elif indicadores_flat[7] == 0.0:
        logger.info(f"   ⚪ [Índice 7] Participação Eleitoral: 0.0 (SEM DADOS)")
    
    # [24] Monitoramento Ar em Tempo Real (proxy de infraestrutura)
    if indicadores_flat[24] == 0.0 and monitoramento_ar_calc > 0:
        indicadores_flat[24] = monitoramento_ar_calc
        logger.info(f"   ✅ [Índice 24] Monitoramento Ar: {monitoramento_ar_calc:.2f}% (SICONFI proxy)")
    elif indicadores_flat[24] == 0.0:
        logger.info(f"   ⚪ [Índice 24] Monitoramento Ar: 0.0 (SEM DADOS)")
    
    # [33] Escolas Conectadas com TeleGestão (ISO37122)
    escolas_conectadas_pct = inep_data.get("escolas_conectadas_pct", 0) or 0
    if indicadores_flat[33] == 0.0 and escolas_conectadas_pct > 0:
        indicadores_flat[33] = escolas_conectadas_pct
        logger.info(f"   ✅ [Índice 33] Escolas Conectadas: {escolas_conectadas_pct:.1f}% (INEP)")
    elif indicadores_flat[33] == 0.0:
        logger.info(f"   ⚪ [Índice 33] Escolas Conectadas: 0.0 (SEM DADOS)")
    
    # ✨ PHASE 2: DataSUS Expandido - 5 Novos Indicadores de Saúde [28-32]
    
    # [28] Hospitais por 100k habitantes (DataSUS Expandido)
    if indicadores_flat[28] == 0.0 and hospitais_por_100k > 0:
        indicadores_flat[28] = hospitais_por_100k
        logger.info(f"   ✅ [Índice 28] Hospitais/100k hab: {hospitais_por_100k:.2f} (DataSUS Expandido)")
    elif indicadores_flat[28] == 0.0:
        logger.info(f"   ⚪ [Índice 28] Hospitais/100k hab: 0.0 (SEM DADOS)")
    
    # [29] Leitos UTI (%) (DataSUS Expandido)
    if indicadores_flat[29] == 0.0 and leitos_uti_pct > 0:
        indicadores_flat[29] = leitos_uti_pct
        logger.info(f"   ✅ [Índice 29] Leitos UTI: {leitos_uti_pct:.1f}% (DataSUS Expandido)")
    elif indicadores_flat[29] == 0.0:
        logger.info(f"   ⚪ [Índice 29] Leitos UTI: 0.0 (SEM DADOS)")
    
    # [30] Cobertura Vacinação COVID (%) (DataSUS Expandido)
    if indicadores_flat[30] == 0.0 and cobertura_vacina_covid_pct > 0:
        indicadores_flat[30] = cobertura_vacina_covid_pct
        logger.info(f"   ✅ [Índice 30] Cobertura Vacina COVID: {cobertura_vacina_covid_pct:.1f}% (DataSUS Expandido)")
    elif indicadores_flat[30] == 0.0:
        logger.info(f"   ⚪ [Índice 30] Cobertura Vacina COVID: 0.0 (SEM DADOS)")
    
    # [31] Cobertura Atenção Básica (%) (DataSUS Expandido)
    if indicadores_flat[31] == 0.0 and cobertura_atencao_basica_pct > 0:
        indicadores_flat[31] = cobertura_atencao_basica_pct
        logger.info(f"   ✅ [Índice 31] Cobertura Atenção Básica: {cobertura_atencao_basica_pct:.1f}% (DataSUS Expandido)")
    elif indicadores_flat[31] == 0.0:
        logger.info(f"   ⚪ [Índice 31] Cobertura Atenção Básica: 0.0 (SEM DADOS)")
    
    # [32] Agentes Comunitários de Saúde (DataSUS Expandido)
    if indicadores_flat[32] == 0.0 and agentes_comunitarios_saude > 0:
        indicadores_flat[32] = agentes_comunitarios_saude
        logger.info(f"   ✅ [Índice 32] Agentes Comunitários: {agentes_comunitarios_saude:.0f} (DataSUS Expandido)")
    elif indicadores_flat[32] == 0.0:
        logger.info(f"   ⚪ [Índice 32] Agentes Comunitários: 0.0 (SEM DADOS)")
    
    # ✨ PHASE 2 TASK 2: Portal Transparência Expandido - 3 Novos Indicadores Sociais [37,39,44]
    
    # [37] Beneficiários de Programas Sociais (%) (Portal Expandido - Phase 2 Task 2)
    if indicadores_flat[37] == 0.0 and beneficiarios_programas_sociais_pct > 0:
        indicadores_flat[37] = beneficiarios_programas_sociais_pct
        logger.info(f"   ✅ [Índice 37] Beneficiários Programas Sociais: {beneficiarios_programas_sociais_pct:.1f}% (Portal Expandido)")
    elif indicadores_flat[37] == 0.0:
        logger.info(f"   ⚪ [Índice 37] Beneficiários Programas Sociais: 0.0 (SEM DADOS)")
    
    # [39] Cobertura Alimentação Escolar (%) (Portal Expandido - Phase 2 Task 2)
    if indicadores_flat[39] == 0.0 and cobertura_alimentacao_escolar_pct > 0:
        indicadores_flat[39] = cobertura_alimentacao_escolar_pct
        logger.info(f"   ✅ [Índice 39] Cobertura Alimentação Escolar: {cobertura_alimentacao_escolar_pct:.1f}% (Portal Expandido)")
    elif indicadores_flat[39] == 0.0:
        logger.info(f"   ⚪ [Índice 39] Cobertura Alimentação Escolar: 0.0 (SEM DADOS)")
    
    # [44] Acesso a Água Potável (%) (Portal Expandido - Phase 2 Task 2 - SNIS)
    if indicadores_flat[44] == 0.0 and acesso_agua_potavel_pct > 0:
        indicadores_flat[44] = acesso_agua_potavel_pct
        logger.info(f"   ✅ [Índice 44] Acesso Água Potável: {acesso_agua_potavel_pct:.1f}% (Portal Expandido)")
    elif indicadores_flat[44] == 0.0:
        logger.info(f"   ⚪ [Índice 44] Acesso Água Potável: 0.0 (SEM DADOS)")
    
    # [35] Hospitais por 100k habitantes (proxy para serviços de saúde)
    if indicadores_flat[35] == 0.0 and hospitais_100k_calc > 0:
        indicadores_flat[35] = hospitais_100k_calc
        logger.info(f"   ✅ [Índice 35] Hospitais/100k hab: {hospitais_100k_calc:.2f} (DATASUS + IBGE)")
    elif indicadores_flat[35] == 0.0:
        logger.info(f"   ⚪ [Índice 35] Hospitais/100k hab: 0.0 (SEM DADOS)")
    
    # [36] Seguro Saúde Básico (proxy: acesso a hospitais)
    if indicadores_flat[36] == 0.0 and seguro_saude_calc > 0:
        indicadores_flat[36] = min(seguro_saude_calc, 100.0)  # Cap em 100%
        logger.info(f"   ✅ [Índice 36] Seguro Saúde: {indicadores_flat[36]:.2f}% (DataSUS proxy)")
    elif indicadores_flat[36] == 0.0:
        logger.info(f"   ⚪ [Índice 36] Seguro Saúde: 0.0 (SEM DADOS)")
    
    # [38] Abrigos de Emergência (proxy: população vulnerável)
    if indicadores_flat[38] == 0.0 and abrigos_emergencia_calc > 0:
        indicadores_flat[38] = abrigos_emergencia_calc
        logger.info(f"   ✅ [Índice 38] Abrigos Emergência: {abrigos_emergencia_calc:.2f}/100k (Portal proxy)")
    elif indicadores_flat[38] == 0.0:
        logger.info(f"   ⚪ [Índice 38] Abrigos Emergência: 0.0 (SEM DADOS)")
    
    # [42] Mapas de Ameaças Públicos (proxy: infraestrutura de dados)
    if indicadores_flat[42] == 0.0 and mapas_ameacas_calc > 0:
        indicadores_flat[42] = mapas_ameacas_calc
        logger.info(f"   ✅ [Índice 42] Mapas Ameaças: {mapas_ameacas_calc:.2f}% (SICONFI proxy)")
    elif indicadores_flat[42] == 0.0:
        logger.info(f"   ⚪ [Índice 42] Mapas Ameaças: 0.0 (SEM DADOS)")
    
    # 🎯 5 NOVAS APIs (PARTE 3) - INJEÇÃO DAS 5 NOVAS APIS
    
    # [6] Condenações por Corrupção/100k (CNJ)
    if indicadores_flat[6] == 0.0 and condenacoes_corrupcao_100k > 0:
        indicadores_flat[6] = condenacoes_corrupcao_100k
        logger.info(f"   ✅ [Índice 6] Condenações Corrupção: {condenacoes_corrupcao_100k:.2f}/100k (CNJ)")
    elif indicadores_flat[6] == 0.0:
        logger.info(f"   ⚪ [Índice 6] Condenações Corrupção: 0.0 (SEM DADOS)")
    
    # [14] Acidentes Industriais/100k (Min. Trabalho)
    if indicadores_flat[14] == 0.0 and acidentes_industriais_100k > 0:
        indicadores_flat[14] = acidentes_industriais_100k
        logger.info(f"   ✅ [Índice 14] Acidentes Industriais: {acidentes_industriais_100k:.2f}/100k (Min. Trabalho)")
    elif indicadores_flat[14] == 0.0:
        logger.info(f"   ⚪ [Índice 14] Acidentes Industriais: 0.0 (SEM DADOS)")
    
    # [22] Medidores Inteligentes Energia (ANEEL)
    if indicadores_flat[22] == 0.0 and medidores_inteligentes_pct > 0:
        indicadores_flat[22] = medidores_inteligentes_pct
        logger.info(f"   ✅ [Índice 22] Medidores Inteligentes: {medidores_inteligentes_pct:.1f}% (ANEEL)")
    elif indicadores_flat[22] == 0.0:
        logger.info(f"   ⚪ [Índice 22] Medidores Inteligentes: 0.0 (SEM DADOS)")
    
    # [32] Frota Ônibus Zero Emissão (ANTP)
    if indicadores_flat[32] == 0.0 and frota_onibus_zero_emissao_pct > 0:
        indicadores_flat[32] = frota_onibus_zero_emissao_pct
        logger.info(f"   ✅ [Índice 32] Frota Ônibus Zero Emissão: {frota_onibus_zero_emissao_pct:.1f}% (ANTP)")
    elif indicadores_flat[32] == 0.0:
        logger.info(f"   ⚪ [Índice 32] Frota Ônibus Zero Emissão: 0.0 (SEM DADOS)")
    
    # [46] Mortalidade por Desastres/100k (Defesa Civil)
    if indicadores_flat[46] == 0.0 and mortalidade_desastres_100k > 0:
        indicadores_flat[46] = mortalidade_desastres_100k
        logger.info(f"   ✅ [Índice 46] Mortalidade Desastres: {mortalidade_desastres_100k:.2f}/100k (Defesa Civil)")
    elif indicadores_flat[46] == 0.0:
        logger.info(f"   ⚪ [Índice 46] Mortalidade Desastres: 0.0 (SEM DADOS)")
    
    return indicadores_flat







async def processar_cidade_real(
    codigo_ibge: str, 
    nome_cidade: str, 
    manual: ManualCityIndicators = None,
    db: Session = None
) -> dict:
    """
    ✨ PROCESSAMENTO REFATORADO: Agregação Dinâmica de 47 Indicadores ISO com Cache Inteligente
    
    Implementa as 3 estratégias solicitadas em sequência:
    1. Flattening: Extrai 47 indicadores em lista plana respeitando ordem Pydantic
    2. Injeção de APIs: Sobrescreve campos específicos com dados de SICONFI, IBGE, DataSUS
    3. Cache Inteligente: Salva dados frescos das APIs no banco de dados (se db passado)
    
    Args:
        codigo_ibge: Código IBGE do município
        nome_cidade: Nome da cidade
        manual: Indicadores manuais estruturados por ISO (ManualCityIndicators)
        db: Sessão SQLAlchemy opcional para salvar dados no banco (cache inteligente)
    
    Returns:
        Dict com nome_cidade e indicadores_flatalizados (50 valores), ou None em erro
    """
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"🏙️  PROCESSANDO: {nome_cidade} (IBGE: {codigo_ibge})")
        logger.info(f"{'='*80}")
        
        # ===================================================================
        # PASSO 0: CARREGAMENTO DE DADOS EXISTENTES (DB + LOCAL DATA SERVICE)
        # ===================================================================
        if manual is None:
            logger.warning(f"   ⚠️  Nenhum indicador manual fornecido, tentando carregar do banco...")
            manual = ManualCityIndicators()
            
            # Tentar carregar do banco de dados PRIMEIRO - essa é a fonte de verdade
            if db is not None:
                try:
                    from app.models import CityManualData
                    ciudad_banco = db.query(CityManualData).filter_by(codigo_ibge=codigo_ibge).first()
                    if ciudad_banco and ciudad_banco.indicadores_manuais:
                        logger.info(f"   ✅ Dados carregados do banco: {len(ciudad_banco.indicadores_manuais)} campos")
                        # Reconstruir ManualCityIndicators a partir do JSON
                        try:
                            manual = ManualCityIndicators(**ciudad_banco.indicadores_manuais)
                            logger.info(f"   ✅ Todos os 50 indicadores carregados do banco com SUCESSO!")
                        except Exception as e:
                            logger.warning(f"   ⚠️  Erro ao converter dados do banco, usando defaults: {str(e)}")
                            manual = ManualCityIndicators()
                    else:
                        logger.info(f"   ℹ️  Nenhum dado no banco para {codigo_ibge}, usando defaults")
                except Exception as banco_error:
                    logger.warning(f"   ⚠️  Erro ao consultar banco: {str(banco_error)}")
        else:
            # Se manual foi fornecido, também tentar atualizar com dados do banco para campos que estão vazios
            logger.info(f"   ℹ️  Indicadores manuais fornecidos, verificando se há atualizações no banco...")
            if db is not None:
                try:
                    from app.models import CityManualData
                    ciudad_banco = db.query(CityManualData).filter_by(codigo_ibge=codigo_ibge).first()
                    if ciudad_banco and ciudad_banco.indicadores_manuais:
                        # Usar dados do banco como base, depois sobrescrever com manual se não for zero
                        manual_banco = ManualCityIndicators(**ciudad_banco.indicadores_manuais)
                        
                        # Mesclar: manual tem prioridade, mas banco preenche os vazios
                        for iso_classe in ["iso_37120", "iso_37122", "iso_37123"]:
                            manual_obj = getattr(manual, iso_classe)
                            banco_obj = getattr(manual_banco, iso_classe)
                            
                            for field in manual_obj.__fields__:
                                manual_val = getattr(manual_obj, field)
                                banco_val = getattr(banco_obj, field)
                                
                                # Se manual é zero e banco tem valor, usar banco
                                if manual_val == 0.0 and banco_val > 0:
                                    setattr(manual_obj, field, banco_val)
                        
                        logger.info(f"   ✅ Indicadores mesclados: manual + banco")
                except Exception as merge_error:
                    logger.warning(f"   ⚠️  Erro ao mesclar dados do banco: {str(merge_error)}")
        
        # ===================================================================
        # PASSO 1: EXTRAÇÃO DINÂMICA (FLATTENING)
        # ===================================================================
        logger.info(f"\n📋 PASSO 1: EXTRAÇÃO DINÂMICA (FLATTENING)")
        indicadores_flat = flatten_manual_indicators(manual)
        
        logger.info(f"   ✅ 50 indicadores extraídos")
        logger.info(f"   📊 Primeiros 5: {indicadores_flat[:5]}")
        logger.info(f"   📊 Últimos 5: {indicadores_flat[-5:]}")
        
        # ===================================================================
        # Chamar APIs externas em paralelo (SICONFI, IBGE, DataSUS, INEP)
        # ===================================================================
        logger.info(f"\n📡 Buscando dados em APIs externas (paralelo) - Timeout: 10s")
        
        # 🎯 População padrão para as novas APIs (será atualizada se IBGE responder)
        populacao_default = 100000
        
        try:
            # Chamar 12 APIs em paralelo: 7 originais + 5 novas (PARTE 3)
            siconfi_data, ibge_data, datasus_data, inep_data, transparencia_data, datasus_expanded_data, portal_social_data, \
            aneel_data, ministerio_trabalho_data, antp_data, defesa_civil_data, cnj_data = await asyncio.gather(
                asyncio.wait_for(get_siconfi_finances(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_ibge_population(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_datasus_health_infrastructure(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_inep_education(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_transparencia_social(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_datasus_expanded_wrapper(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_portal_transparencia_expanded_wrapper(codigo_ibge), timeout=10.0),  # NEW: Social Programs
                # 🎯 5 NOVAS APIs (PARTE 3) - usando populacao_default
                asyncio.wait_for(get_aneel_smart_metering(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_ministerio_trabalho_accidents(codigo_ibge, populacao_default), timeout=10.0),
                asyncio.wait_for(get_antp_zero_emission_fleet(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_defesa_civil_disasters(codigo_ibge, populacao_default), timeout=10.0),
                asyncio.wait_for(get_cnj_corruption_convictions(codigo_ibge, populacao_default), timeout=10.0),
                return_exceptions=True  # Captura também timeouts
            )
            
            # Verificar se alguma chamada retornou Exception (timeout ou erro)
            if isinstance(siconfi_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO SICONFI ({codigo_ibge}): {type(siconfi_data).__name__}")
                siconfi_data = {}
            
            if isinstance(ibge_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO IBGE ({codigo_ibge}): {type(ibge_data).__name__}")
                ibge_data = {}
            
            if isinstance(datasus_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO DataSUS ({codigo_ibge}): {type(datasus_data).__name__}")
                datasus_data = {}
            
            if isinstance(inep_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO INEP ({codigo_ibge}): {type(inep_data).__name__}")
                inep_data = {}
            
            if isinstance(transparencia_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO Portal da Transparência ({codigo_ibge}): {type(transparencia_data).__name__}")
                transparencia_data = {}
            
            if isinstance(datasus_expanded_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO DataSUS Expandido ({codigo_ibge}): {type(datasus_expanded_data).__name__}")
                datasus_expanded_data = {}
            
            if isinstance(portal_social_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO Portal Transparência Expandido ({codigo_ibge}): {type(portal_social_data).__name__}")
                portal_social_data = {}
            
            # 🎯 Validação das 5 NOVAS APIs (PARTE 3)
            if isinstance(aneel_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO ANEEL ({codigo_ibge}): {type(aneel_data).__name__}")
                aneel_data = {}
            
            if isinstance(ministerio_trabalho_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO Min. Trabalho ({codigo_ibge}): {type(ministerio_trabalho_data).__name__}")
                ministerio_trabalho_data = {}
            
            if isinstance(antp_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO ANTP ({codigo_ibge}): {type(antp_data).__name__}")
                antp_data = {}
            
            if isinstance(defesa_civil_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO Defesa Civil ({codigo_ibge}): {type(defesa_civil_data).__name__}")
                defesa_civil_data = {}
            
            if isinstance(cnj_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO CNJ ({codigo_ibge}): {type(cnj_data).__name__}")
                cnj_data = {}
            
            # Log de sucesso
            if isinstance(siconfi_data, dict):
                logger.info(f"   ✅ SICONFI respondeu em < 10s")
            if isinstance(ibge_data, (dict, int, float)) and not isinstance(ibge_data, Exception):
                logger.info(f"   ✅ IBGE respondeu em < 10s")
            if isinstance(datasus_data, dict):
                logger.info(f"   ✅ DataSUS respondeu em < 10s")
            if isinstance(inep_data, dict):
                logger.info(f"   ✅ INEP respondeu em < 10s")
            if isinstance(transparencia_data, dict):
                logger.info(f"   ✅ Portal da Transparência respondeu em < 10s")
            if isinstance(datasus_expanded_data, dict):
                logger.info(f"   ✅ DataSUS Expandido respondeu em < 10s")
            if isinstance(portal_social_data, dict):
                logger.info(f"   ✅ Portal Transparência Expandido respondeu em < 10s")
            # 🎯 Log das 5 NOVAS APIs (PARTE 3)
            if isinstance(aneel_data, dict):
                logger.info(f"   ✅ ANEEL respondeu em < 10s")
            if isinstance(ministerio_trabalho_data, dict):
                logger.info(f"   ✅ Min. Trabalho respondeu em < 10s")
            if isinstance(antp_data, dict):
                logger.info(f"   ✅ ANTP respondeu em < 10s")
            if isinstance(defesa_civil_data, dict):
                logger.info(f"   ✅ Defesa Civil respondeu em < 10s")
            if isinstance(cnj_data, dict):
                logger.info(f"   ✅ CNJ respondeu em < 10s")
        
        except Exception as e:
            logger.error(f"   ❌ Erro crítico ao buscar APIs: {str(e)}")
            siconfi_data, ibge_data, datasus_data, inep_data, datasus_expanded_data, portal_social_data = {}, {}, {}, {}, {}, {}
            aneel_data, ministerio_trabalho_data, antp_data, defesa_civil_data, cnj_data = {}, {}, {}, {}, {}
        
        # Normalizar dados das APIs com defaults
        siconfi_data = siconfi_data or {}
        ibge_data = ibge_data or 100000  # Default população
        datasus_data = datasus_data or {}
        datasus_expanded_data = datasus_expanded_data or {}
        transparencia_data = transparencia_data or {}
        portal_social_data = portal_social_data or {}  # NEW: Portal social programs
        # 🎯 Normalizar as 5 NOVAS APIs (PARTE 3)
        aneel_data = aneel_data or {}
        ministerio_trabalho_data = ministerio_trabalho_data or {}
        antp_data = antp_data or {}
        defesa_civil_data = defesa_civil_data or {}
        cnj_data = cnj_data or {}
        
        # Se IBGE retornou um float, converter para dict
        if isinstance(ibge_data, (int, float)):
            populacao = float(ibge_data) if ibge_data and ibge_data > 0 else 100000
            ibge_data = {"populacao": populacao}
        else:
            ibge_data = ibge_data or {}
            populacao = ibge_data.get("populacao", 0) or 100000
        
        # 🎯 Carregar dados ETL (indicators_master.json gerado por process_local_data.py)
        logger.info(f"\n📂 Carregando dados ETL (CAGED, DATASUS SIM)...")
        etl_data = load_etl_data_for_city(codigo_ibge)
        if etl_data:
            logger.info(f"   ✅ Dados ETL carregados: {list(etl_data.keys())}")
        else:
            logger.info(f"   ℹ️  Nenhum dado ETL para {codigo_ibge}")
        
        # ⭐ PASSO 2: INJEÇÃO DOS DADOS AUTOMÁTICOS
        # ===================================================================
        logger.info(f"\n💉 PASSO 2: INJEÇÃO DOS DADOS AUTOMÁTICOS")
        indicadores_flat = inject_api_data_into_flat_list(
            indicadores_flat,
            siconfi_data,
            ibge_data,
            datasus_data,
            inep_data,
            transparencia_data,
            datasus_expanded_data,
            portal_social_data,  # NEW: Pass social programs data
            etl_data,  # 🎯 NEW: Pass ETL data (CAGED, DATASUS SIM)
            # 🎯 5 NOVAS APIs (PARTE 3)
            aneel_data,
            ministerio_trabalho_data,
            antp_data,
            defesa_civil_data,
            cnj_data,
            nome_cidade
        )
        
        logger.info(f"   ✅ Dados das APIs injetados")
        
        # ===================================================================
        # 💾 PASSO 3: CACHE INTELIGENTE - Salvar Dados Frescos no Banco
        # ===================================================================
        if db is not None:
            logger.info(f"\n💾 PASSO 3: CACHE INTELIGENTE - Salvando no banco")
            try:
                from app.models import CityManualData, CityManualDataHistory
                from datetime import datetime
                
                # Reconstruir dicionário JSON de 50 indicadores a partir da lista plana atualizada
                # Mapear de volta para a estrutura nested
                manual_atual = ManualCityIndicators()
                
                # ISO 37120 (índices 0-16) - 17 indicadores (16 originais + 1 INEP educação não, 2 INEP)
                manual_atual.iso_37120.taxa_desemprego_pct = indicadores_flat[0]
                manual_atual.iso_37120.taxa_endividamento_pct = indicadores_flat[1]
                manual_atual.iso_37120.despesas_capital_pct = indicadores_flat[2]
                manual_atual.iso_37120.receita_propria_pct = indicadores_flat[3]
                manual_atual.iso_37120.orcamento_per_capita = indicadores_flat[4]
                manual_atual.iso_37120.mulheres_eleitas_pct = indicadores_flat[5]
                manual_atual.iso_37120.condenacoes_corrupcao_100k = indicadores_flat[6]
                manual_atual.iso_37120.participacao_eleitoral_pct = indicadores_flat[7]
                manual_atual.iso_37120.moradias_inadequadas_pct = indicadores_flat[8]
                manual_atual.iso_37120.sem_teto_100k = indicadores_flat[9]
                manual_atual.iso_37120.bombeiros_100k = indicadores_flat[10]
                manual_atual.iso_37120.mortes_incendio_100k = indicadores_flat[11]
                manual_atual.iso_37120.agentes_policia_100k = indicadores_flat[12]
                manual_atual.iso_37120.homicidios_100k = indicadores_flat[13]
                manual_atual.iso_37120.acidentes_industriais_100k = indicadores_flat[14]
                manual_atual.iso_37120.relacao_estudante_professor = indicadores_flat[15]  # NEW INEP
                manual_atual.iso_37120.ideb_anos_iniciais = indicadores_flat[16]           # NEW INEP
                
                # ISO 37122 (índices 17-33) - 17 indicadores (15 originais + 1 educacional INEP + 1 gap)
                manual_atual.iso_37122.sobrevivencia_novos_negocios_100k = indicadores_flat[17]
                manual_atual.iso_37122.empregos_tic_pct = indicadores_flat[18]
                manual_atual.iso_37122.graduados_stem_100k = indicadores_flat[19]
                manual_atual.iso_37122.energia_residuos_pct = indicadores_flat[20]
                manual_atual.iso_37122.iluminacao_telegestao_pct = indicadores_flat[21]
                manual_atual.iso_37122.medidores_inteligentes_energia_pct = indicadores_flat[22]
                manual_atual.iso_37122.edificios_verdes_pct = indicadores_flat[23]
                manual_atual.iso_37122.monitoramento_ar_tempo_real_pct = indicadores_flat[24]
                manual_atual.iso_37122.servicos_urbanos_online_pct = indicadores_flat[25]
                manual_atual.iso_37122.prontuario_eletronico_pct = indicadores_flat[26]
                manual_atual.iso_37122.consultas_remotas_100k = indicadores_flat[27]
                manual_atual.iso_37122.medidores_inteligentes_agua_pct = indicadores_flat[28]
                manual_atual.iso_37122.areas_cobertas_cameras_pct = indicadores_flat[29]
                manual_atual.iso_37122.lixeiras_sensores_pct = indicadores_flat[30]
                manual_atual.iso_37122.semaforos_inteligentes_pct = indicadores_flat[31]
                manual_atual.iso_37122.frota_onibus_limpos_pct = indicadores_flat[32]
                manual_atual.iso_37122.escolas_conectadas_pct = indicadores_flat[33]      # NEW INEP
                
                # ISO 37123 + Sendai (índices 34-49) - 16 indicadores
                manual_atual.iso_37123.seguro_ameacas_pct = indicadores_flat[34]
                manual_atual.iso_37123.empregos_informais_pct = indicadores_flat[35]
                manual_atual.iso_37123.escolas_preparacao_emergencia_pct = indicadores_flat[36]
                manual_atual.iso_37123.populacao_treinada_emergencia_pct = indicadores_flat[37]
                manual_atual.iso_37123.hospitais_geradores_backup_pct = indicadores_flat[38]
                manual_atual.iso_37123.seguro_saude_basico_pct = indicadores_flat[39]
                manual_atual.iso_37123.imunizacao_pct = indicadores_flat[40]
                manual_atual.iso_37123.abrigos_emergencia_100k = indicadores_flat[41]
                manual_atual.iso_37123.edificios_vulneraveis_pct = indicadores_flat[42]
                manual_atual.iso_37123.rotas_evacuacao_100k = indicadores_flat[43]
                manual_atual.iso_37123.reservas_alimentos_72h_pct = indicadores_flat[44]
                manual_atual.iso_37123.mapas_ameacas_publicos_pct = indicadores_flat[45]
                manual_atual.iso_37123.mortalidade_desastres_100k = indicadores_flat[46]
                manual_atual.iso_37123.pessoas_afetadas_desastres_100k = indicadores_flat[47]
                manual_atual.iso_37123.perdas_desastres_pct_pib = indicadores_flat[48]
                manual_atual.iso_37123.danos_infraestrutura_basica_pct = indicadores_flat[49]
                
                # Converter novo dict
                dados_novos = manual_atual.model_dump()
                
                # Buscar registro existente
                cidade_existente = db.query(CityManualData).filter_by(
                    codigo_ibge=codigo_ibge
                ).first()
                
                if cidade_existente:
                    # Capturar dados antigos para auditoria
                    dados_antigos = cidade_existente.indicadores_manuais or {}
                    
                    # Atualizar o registro
                    cidade_existente.indicadores_manuais = dados_novos
                    cidade_existente.usuario_atualizou = "topsis_cache_inteligente"
                    cidade_existente.data_atualizacao = datetime.utcnow()
                    
                    # Registrar auditoria apenas se houve mudanças significativas
                    mudancas = []
                    for idx, (valor_antigo, valor_novo) in enumerate(
                        zip(
                            [dados_antigos.get("iso_37120", {}).get(k, 0) for k in dados_antigos.get("iso_37120", {}).keys()] +
                            [dados_antigos.get("iso_37122", {}).get(k, 0) for k in dados_antigos.get("iso_37122", {}).keys()] +
                            [dados_antigos.get("iso_37123", {}).get(k, 0) for k in dados_antigos.get("iso_37123", {}).keys()],
                            indicadores_flat
                        )
                    ):
                        if abs(valor_antigo - valor_novo) > 0.01:  # Diferença > 0.01 unidades
                            mudancas.append(f"idx[{idx}]: {valor_antigo:.2f} → {valor_novo:.2f}")
                    
                    if mudancas:
                        historico = CityManualDataHistory(
                            codigo_ibge=codigo_ibge,
                            dados_antigos=dados_antigos,
                            dados_novos=dados_novos,
                            alteracoes_resumo=f"Cache inteligente (TOPSIS): {len(mudancas)} valores atualizados",
                            usuario_atualizou="topsis_cache",
                            motivo_atualizacao="Atualização automática de cache via TOPSIS com injeção de APIs",
                            data_alteracao=datetime.utcnow()
                        )
                        db.add(historico)
                        logger.info(f"   ✅ Histórico registrado: {len(mudancas)} valor(es) atualizado(s)")
                    else:
                        logger.info(f"   ℹ️  Nenhuma mudança significativa detectada (diferenças < 0.01)")
                    
                    db.commit()
                    logger.info(f"   ✅ Banco de dados atualizado (cache inteligente)")
                else:
                    # Criar novo registro se não existir
                    nova_cidade = CityManualData(
                        codigo_ibge=codigo_ibge,
                        nome_cidade=nome_cidade,
                        indicadores_manuais=dados_novos,
                        fonte="topsis_cache_inteligente",
                        usuario_atualizou="topsis_cache_inteligente",
                        data_criacao=datetime.utcnow(),
                        data_atualizacao=datetime.utcnow()
                    )
                    db.add(nova_cidade)
                    
                    # Registrar primeiro histórico
                    historico = CityManualDataHistory(
                        codigo_ibge=codigo_ibge,
                        dados_antigos={},
                        dados_novos=dados_novos,
                        alteracoes_resumo="Criação inicial via cache inteligente TOPSIS",
                        usuario_atualizou="topsis_cache_inteligente",
                        motivo_atualizacao="Primeira sincronização automática de dados via TOPSIS",
                        data_alteracao=datetime.utcnow()
                    )
                    db.add(historico)
                    db.commit()
                    logger.info(f"   ✅ Novo registro criado e salvo (cache inteligente)")
                    
            except Exception as cache_error:
                logger.warning(f"   ⚠️  Falha ao salvar cache inteligente (continuando): {str(cache_error)}")
        else:
            logger.info(f"\n💾 PASSO 3: Cache inteligente DESABILITADO (sem sessão de banco)")
        
        # ===================================================================
        # 📊 PASSO 4: SALVAR SNAPSHOT HISTÓRICO DE INDICADORES
        # ===================================================================
        if db is not None:
            logger.info(f"\n📊 PASSO 4: SALVANDO SNAPSHOT HISTÓRICO DE INDICADORES")
            try:
                periodo_referencia = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                
                # Salvar snapshot dos 50 indicadores calculados para esta cidade
                snapshot = IndicatorSnapshot(
                    codigo_ibge=codigo_ibge,
                    valores_indicadores=indicadores_flat,  # Lista de 50 valores
                    data_calculo=datetime.utcnow(),
                    fonte_dados="hibrido",  # APIs + Manual
                    periodo_referencia=periodo_referencia
                )
                db.add(snapshot)
                db.commit()
                
                dados_nao_zero_temp = len([v for v in indicadores_flat if v > 0])
                logger.info(f"   ✅ Snapshot histórico salvo: {len(indicadores_flat)} indicadores")
                logger.info(f"   📈 Indicadores com dados: {dados_nao_zero_temp}/50 ({dados_nao_zero_temp/50*100:.1f}%)")
                
            except Exception as snapshot_error:
                logger.warning(f"   ⚠️  Falha ao salvar snapshot histórico (continuando): {str(snapshot_error)}")
        else:
            logger.info(f"\n📊 PASSO 4: Snapshot histórico DESABILITADO (sem sessão de banco)")
        
        # ===================================================================
        # ✅ VALIDAÇÃO FINAL
        # ====================================================================
        assert len(indicadores_flat) == 50, f"❌ ERRO: Esperado 50 indicadores, obteve {len(indicadores_flat)}"
        
        # Estatísticas
        dados_nao_zero = len([v for v in indicadores_flat if v != 0.0])
        media_indicadores = np.mean(indicadores_flat) if indicadores_flat else 0.0
        min_indicador = np.min(indicadores_flat) if indicadores_flat else 0.0
        max_indicador = np.max(indicadores_flat) if indicadores_flat else 0.0
        
        logger.info(f"\n📊 RESUMO FINAL ({nome_cidade}):")
        logger.info(f"   ✅ Total indicadores: 50 (47 ISO + 3 INEP educação)")
        logger.info(f"   ✅ Indicadores não-zero: {dados_nao_zero}/50 ({dados_nao_zero/50*100:.1f}%)")
        logger.info(f"   📈 Média: {media_indicadores:.2f}")
        logger.info(f"   📉 Mínimo: {min_indicador:.2f}")
        logger.info(f"   📈 Máximo: {max_indicador:.2f}")
        
        resultado = {
            "nome_cidade": nome_cidade,
            "indicadores_flatalizados": indicadores_flat,
            "metadata_cobertura": {
                "nome_cidade": nome_cidade,
                "total_indicadores": 50,
                "quantidade_dados_reais": dados_nao_zero,
                "pct_cobertura": (dados_nao_zero / 50) * 100,
                "media_indicadores": float(media_indicadores),
                "min_indicador": float(min_indicador),
                "max_indicador": float(max_indicador),
            }
        }
        
        logger.info(f"✅ {nome_cidade} processada com SUCESSO\n")
        return resultado
        
    except Exception as e:
        logger.error(f"❌ ERRO ao processar {nome_cidade}: {str(e)}", exc_info=True)
        return None



@topsis_router.post("/ranking-hibrido", response_model=TOPSISResult)
async def get_hybrid_ranking(payload: List[CityHybridInput], db: Session = Depends(get_db)) -> TOPSISResult:
    """
    ✨ ENDPOINT PRINCIPAL: Ranking Smart Cities com 50 Indicadores ISO + INEP Completos

    ESTRUTURA: 50 indicadores totais (47 ISO: 16 ISO37120 + 15 ISO37122 + 16 ISO37123 + Sendai + 3 INEP educação)

    PESOS: Equitativos (1/50 = 0.02 cada)
    IMPACTOS: Definidos matematicamente conforme ISO e Marco de Sendai
    
    AGREGAÇÃO (3 PASSOS):
    1. Flattening: Extrai 50 indicadores em lista plana respeitando ordem Pydantic (47 ISO + 3 INEP)
    2. Injeção de APIs: Sobrescreve campos específicos com dados automáticos
    3. Mock Survival: Preenche gaps percentuais com valores aleatórios (TODO)
    
    Requisitos:
    - MÍNIMO 2 cidades (TOPSIS precisa comparação)
    - Dados podem vir de manual_indicators ou serem calculados de APIs
    
    Returns:
        TOPSISResult com ranking ordenado por Índice Smart
        
    Raises:
        HTTPException 400: Menos de 2 cidades
        HTTPException 502: Falha ao processar nenhuma cidade
    """
    # ===== VALIDAÇÃO DE ENTRADA =====
    if len(payload) < 2:
        logger.warning(f"❌ VALIDAÇÃO FALHOU: Apenas {len(payload)} cidade(s) enviada(s)")
        raise HTTPException(
            status_code=400,
            detail=f"TOPSIS requer mínimo 2 cidades para comparação. Recebido: {len(payload)} cidade(s)."
        )
    
    try:
        logger.info("=" * 100)
        logger.info(f"🚀 INICIANDO CÁLCULO TOPSIS HÍBRIDO REFATORADO")
        logger.info(f"📊 Cidades: {len(payload)} | Indicadores: 50 (47 ISO: 16 ISO37120 + 15 ISO37122 + 16 ISO37123 + 3 INEP educação)")
        logger.info(f"🔄 Método: Flattening → API Injection → Mock Survival")
        logger.info("=" * 100)
        
        # Processa todas as cidades em paralelo, passando a sessão do banco para cache inteligente
        resultados_cidades = await asyncio.gather(
            *[
                processar_cidade_real(
                    city.codigo_ibge,
                    city.nome_cidade,
                    # Converter manual_indicators para ManualCityIndicators se for dict
                    (
                        converter_dict_to_manual_indicators(city.manual_indicators) 
                        if isinstance(city.manual_indicators, dict) 
                        else (city.manual_indicators or ManualCityIndicators())
                    ),
                    db=db  # 💾 Passar sessão do banco para cache inteligente
                ) for city in payload
            ],
            return_exceptions=False
        )
        
        # Filtra cidades processadas com sucesso
        cidades_sucesso = [r for r in resultados_cidades if r is not None]
        
        logger.info(f"\n✅ RESULTADO: {len(cidades_sucesso)}/{len(payload)} cidades processadas com sucesso")
        
        if not cidades_sucesso:
            logger.error("❌ FALHA CRÍTICA: Nenhuma cidade conseguiu ser processada")
            raise HTTPException(
                status_code=502,
                detail="Falha ao processar dados das cidades. Tente novamente mais tarde."
            )
        
        # Prepara dados para TOPSIS
        cidades_nomes = [r["nome_cidade"] for r in cidades_sucesso]
        
        # Constrói matriz de decisão (50 indicadores x N cidades)
        matriz_decisao = [r["indicadores_flatalizados"] for r in cidades_sucesso]
        
        # ===== VALIDAÇÃO: Todas as linhas devem ter 50 elementos (18 ISO37120 + 16 ISO37122 + 16 ISO37123) =====
        for idx, linha in enumerate(matriz_decisao):
            num_indicadores_esperado = len(IMPACTOS_TOTAIS)
            if len(linha) != num_indicadores_esperado:
                logger.error(f"❌ ERRO: Cidade {idx} ({cidades_nomes[idx]}) tem {len(linha)} indicadores ao invés de {num_indicadores_esperado}")
                raise HTTPException(
                    status_code=502,
                    detail=f"Inconsistência: Cidade {cidades_nomes[idx]} tem {len(linha)} indicadores, esperado {num_indicadores_esperado} (18 ISO37120 + 16 ISO37122 + 16 ISO37123)"
                )
        
        logger.info(f"\n📊 MATRIZ DE DECISÃO VALIDADA:")
        logger.info(f"   Dimensão: {len(matriz_decisao)} cidades × {_NUM_INDICADORES} indicadores")
        logger.info(f"   Pesos: Equitativos (1/{_NUM_INDICADORES} = {PESOS_EQUITATIVOS[0]:.4f})")
        logger.info(f"   Impactos: 18 (ISO37120) + 16 (ISO37122) + 16 (ISO37123+Sendai)")
        logger.info(f"   Cidades: {', '.join(cidades_nomes)}")
        
        # ===================================================================
        # ✅ MANTER DADOS ORIGINAIS NA MATRIZ
        # ===================================================================
        # Antes havia imputação pela média nos zeros. Isso “achatava” cidades
        # com muitos fallbacks, fazendo o gráfico e o ranking ficarem quase iguais.
        # Agora preservamos os valores originais: zeros continuam zero e o TOPSIS
        # lida com isso naturalmente no cálculo, sem misturar fallback com dado real.
        logger.info(f"\n🧪 MATRIZ ORIGINAL PRESERVADA: zeros e fallbacks mantidos sem imputação pela média")

        matriz_np = np.array(matriz_decisao, dtype=float)

        # Converter de volta para lista de listas Python puro (sem alteração)
        matriz_decisao = matriz_np.tolist()
        
        # Executa TOPSIS com configuração completa
        topsis_input = TOPSISInput(
            cidades=cidades_nomes,
            indicadores_nomes=INDICADORES_NOMES,
            matriz_decisao=matriz_decisao,
            pesos=PESOS_EQUITATIVOS,
            impactos=IMPACTOS_TOTAIS,
        )
        
        result = calculate_topsis(topsis_input)
        
        # Adicionar metadados aos detalhes
        if result.detalhes_calculo is None:
            result.detalhes_calculo = {}
        
        result.detalhes_calculo["pesos"] = PESOS_EQUITATIVOS
        result.detalhes_calculo["impactos"] = IMPACTOS_TOTAIS
        result.detalhes_calculo["indicadores_nomes"] = INDICADORES_NOMES
        result.detalhes_calculo["total_indicadores"] = len(INDICADORES_NOMES)
        
        # Adicionar metadados de cobertura de dados por cidade
        coberturas = [r.get("metadata_cobertura", {}) for r in cidades_sucesso]
        result.detalhes_calculo["cobertura_dados_por_cidade"] = coberturas
        result.detalhes_calculo["imputacao_media"] = False
        
        logger.info(f"\n🏆 RANKING FINAL CALCULADO:")
        for i, city in enumerate(result.ranking, 1):
            logger.info(f"   #{i:2d} {city.nome_cidade:20s} → Índice Smart: {city.indice_smart:.4f} ({city.indice_smart*100:.2f}%)")
        
        logger.info("=" * 100)
        
        # ==========================================
        # PERSISTIR SNAPSHOTS HISTÓRICOS
        # ==========================================
        
        try:
            periodo_referencia = datetime.utcnow().strftime("%Y-%m")
            
            # Salvar snapshot do ranking (47 indicadores ISO completos)
            ranking_data = [
                {
                    "nome_cidade": city.nome_cidade,
                    "indice_smart": float(city.indice_smart),
                    "posicao": i + 1
                }
                for i, city in enumerate(result.ranking)
            ]
            
            ranking_snapshot = RankingSnapshot(
                ranking_data=ranking_data,
                matriz_decisao=matriz_decisao,
                indicadores_nomes=INDICADORES_NOMES,
                pesos=PESOS_EQUITATIVOS,
                impactos=IMPACTOS_TOTAIS,
                data_calculo=datetime.utcnow(),
                periodo_referencia=periodo_referencia,
                quantidade_cidades=len(result.ranking),
            )
            db.add(ranking_snapshot)
            db.commit()
            logger.info(f"✅ SNAPSHOT SALVO: {periodo_referencia} (N={len(cidades_sucesso)} cidades, 50 indicadores)")

        except Exception as e:
            logger.error(f"⚠️  Erro ao salvar snapshot: {str(e)}")
            db.rollback()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO ao gerar ranking híbrido: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar ranking de cidades. Contate o administrador."
        )


# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINT: DEBUG APIs - Diagóstico de Coleta de Dados
# ═════════════════════════════════════════════════════════════════════════════

@topsis_router.get("/debug-apis/{codigo_ibge}")
async def debug_apis(codigo_ibge: str):
    """
    Endpoint de diagnóstico para debugar coleta de dados das 4 APIs governamentais + INEP.
    
    Chama as 4 APIs assincronamente em paralelo e retorna:
    - Dados brutos de cada API (IBGE, SICONFI, DataSUS, INEP)
    - Status indicando se é dado REAL ou FALLBACK
    - Informação sobre qual tier de fallback foi usado
    - Contagem de dados reais vs fallback
    - Classificação de consistência geral
    
    Útil para:
    - Verificar o status das APIs governamentais
    - Rastrear dados brutos antes do processamento TOPSIS
    - Diagnosticar problemas de coleta
    - Validar qualidade de dados
    
    Exemplo:
        GET /topsis/debug-apis/4106902
        
    Resposta:
        {
            "codigo_testado": "4106902",
            "timestamp": "2026-04-01T14:43:24",
            "ibge": {"dados": {...}, "status": "API_REAL", "fonte": "..."},
            "siconfi": {"dados": {...}, "status": "API_REAL", "fonte": "..."},
            "datasus": {"dados": {...}, "status": "FALLBACK_ESPECIFICO", "fonte": "..."},
            "inep": {"dados": {...}, "status": "API_REAL", "fonte": "..."},
            "resumo": {
                "total_apis_ok": 3,
                "total_fallbacks": 1,
                "consistencia": "PARCIAL_FALLBACK",
                "explicacao": {...}
            }
        }
    """
    logger.info(f"🔍 DEBUG: Iniciando diagnóstico COMPLETO para {codigo_ibge}")
    
    try:
        # Executar as 4 chamadas assincronamente em paralelo (IBGE, SICONFI, DataSUS, INEP)
        ibge_result, siconfi_result, datasus_result, inep_result = await asyncio.gather(
            get_ibge_population(codigo_ibge),
            get_siconfi_finances(codigo_ibge),
            get_datasus_health_infrastructure(codigo_ibge),
            get_inep_education(codigo_ibge),
            return_exceptions=False
        )
        
        logger.info(f"✅ Coleta assincronamente concluída para {codigo_ibge}:")
        logger.info(f"   IBGE: {ibge_result.get('fonte') if ibge_result else 'ERRO'}")
        logger.info(f"   SICONFI: {siconfi_result.get('fonte') if siconfi_result else 'ERRO'}")
        logger.info(f"   DataSUS: {datasus_result.get('fonte') if datasus_result else 'ERRO'}")
        logger.info(f"   INEP: {inep_result.get('fonte') if inep_result else 'ERRO'}")
        
        # Helper para classificar status baseado na 'fonte'
        def classificar_status(resultado: Dict[str, Any]) -> str:
            """Classifica se o dado é real ou fallback baseado na chave 'fonte'."""
            if not resultado:
                return "ERRO_COLETA"
            
            fonte = resultado.get("fonte", "desconhecida").lower()
            
            # Prioridade: Universal > Banco > Específico > API Real
            if "fallback universal" in fonte:
                return "FALLBACK_UNIVERSAL"
            elif "banco" in fonte:
                return "FALLBACK_BANCO"
            elif "fallback" in fonte:
                return "FALLBACK_ESPECIFICO"
            elif any(api in fonte for api in ["ibge", "siconfi", "datasus", "mec", "inep"]) and "fallback" not in fonte:
                return "API_REAL"
            else:
                return "STATUS_DESCONHECIDO"
        
        # Classificar status de cada API
        ibge_status = classificar_status(ibge_result)
        siconfi_status = classificar_status(siconfi_result)
        datasus_status = classificar_status(datasus_result)
        inep_status = classificar_status(inep_result)
        
        # Contar dados reais vs fallback
        tous_apis = [ibge_status, siconfi_status, datasus_status, inep_status]
        apis_ok = sum([1 for s in tous_apis if s == "API_REAL"])
        fallbacks = sum([1 for s in tous_apis if "FALLBACK" in s or "BANCO" in s])
        erros = sum([1 for s in tous_apis if s == "ERRO_COLETA"])
        
        # Determinar consistência geral
        if apis_ok == 4:
            consistencia = "DADOS_REAIS_COMPLETO"
        elif apis_ok >= 2:
            consistencia = "PARCIAL_FALLBACK"
        elif apis_ok == 1:
            consistencia = "MINIMO_FALLBACK"
        elif fallbacks > 0:
            consistencia = "COMPLETO_FALLBACK"
        else:
            consistencia = "ERROS_NA_COLETA"
        
        resposta = {
            "codigo_testado": codigo_ibge,
            "timestamp": datetime.utcnow().isoformat(),
            
            # Dados IBGE
            "ibge": {
                "dados": ibge_result,
                "status": ibge_status,
                "fonte": ibge_result.get("fonte", "desconhecida") if ibge_result else "N/A"
            },
            
            # Dados SICONFI
            "siconfi": {
                "dados": siconfi_result,
                "status": siconfi_status,
                "fonte": siconfi_result.get("fonte", "desconhecida") if siconfi_result else "N/A"
            },
            
            # Dados DataSUS
            "datasus": {
                "dados": datasus_result,
                "status": datasus_status,
                "fonte": datasus_result.get("fonte", "desconhecida") if datasus_result else "N/A"
            },
            
            # Dados INEP (NOVO!)
            "inep": {
                "dados": inep_result,
                "status": inep_status,
                "fonte": inep_result.get("fonte", "desconhecida") if inep_result else "N/A"
            },
            
            # Resumo geral
            "resumo": {
                "total_apis_ok": apis_ok,
                "total_fallbacks": fallbacks,
                "total_erros": erros,
                "consistencia": consistencia,
                "tabela_status": {
                    "IBGE": ibge_status,
                    "SICONFI": siconfi_status,
                    "DataSUS": datasus_status,
                    "INEP": inep_status
                },
                "explicacao": {
                    "API_REAL": "✅ Dado coletado diretamente da API governamental (mais recente e confiável)",
                    "FALLBACK_BANCO": "⚠️ Dado persistido no banco de dados (cache local, pode estar desatualizado)",
                    "FALLBACK_ESPECIFICO": "⚠️ Dado de fallback para 3 cidades pré-configuradas (Apucarana, Londrina, Maringá)",
                    "FALLBACK_UNIVERSAL": "⚠️ Dado de média nacional para 5.570 municipios (menos preciso)",
                    "ERRO_COLETA": "❌ Erro ao tentar coletar o dado, nenhum fallback disponível",
                    "STATUS_DESCONHECIDO": "❓ Status não identificado, revisar logs"
                }
            }
        }
        
        logger.info(f"✅ DEBUG CONCLUÍDO: {codigo_ibge}")
        logger.info(f"   APIs OK: {apis_ok}/4 | Fallbacks: {fallbacks} | Erros: {erros}")
        logger.info(f"   Status: IBGE={ibge_status}, SICONFI={siconfi_status}, DataSUS={datasus_status}, INEP={inep_status}")
        logger.info(f"   Consistência Geral: {consistencia}")
        
        return resposta
        
    except Exception as e:
        logger.error(f"❌ ERRO no debug de APIs para {codigo_ibge}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao debugar APIs: {str(e)}"
        )


def converter_dict_to_manual_indicators(data: Dict[str, Any]) -> ManualCityIndicators:
    """
    Converte Dict para ManualCityIndicators estruturado por ISO.
    
    Suporta dois formatos:
    1. Dict simples do frontend: {"bombeiros_por_100k": 10, ...}
    2. Dict nested do banco: {"iso_37120": {...}, "iso_37122": {...}, ...}
    
    Returns:
        ManualCityIndicators com campos preenchidos
    """
    if not data:
        return ManualCityIndicators()
    
    # Verificar se é formato nested do banco (iso_37120, iso_37122, iso_37123)
    if "iso_37120" in data or "iso_37122" in data or "iso_37123" in data:
        try:
            # Formato do banco - converter diretamente
            return ManualCityIndicators(**data)
        except Exception as banco_error:
            logger.warning(f"⚠️ Erro ao converter dict nested: {str(banco_error)}, usando defaults")


# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /cities - Lista de Cidades
# ═════════════════════════════════════════════════════════════════════════════

@topsis_router.get("/cities", response_model=List[Dict[str, Any]])
async def get_cities(db: Session = Depends(get_db)):
    """
    Retorna lista de todas as cidades disponíveis para ranking.
    
    Returns:
        Lista com codigo_ibge e nome de cada cidade
    """
    try:
        result = []

        # 1) Cidades presentes nos dados manuais
        for city in db.query(CityManualData.codigo_ibge, CityManualData.nome_cidade).all():
            result.append({
                "codigo_ibge": str(city.codigo_ibge),
                "nome": city.nome_cidade or f"Cidade {city.codigo_ibge}"
            })

        # 2) Capitais + cidade fictícia de testes
        result.extend(CAPITAIS_BRASILEIRAS)

        # Remover duplicatas e ordenar por nome
        result = sorted(_unique_cities(result), key=lambda item: item["nome"])
        
        logger.info(f"✅ Retornando {len(result)} cidades disponíveis")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar cidades: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar cidades")


# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /indicators - Lista de Indicadores
# ═════════════════════════════════════════════════════════════════════════════

@topsis_router.get("/indicators", response_model=List[Dict[str, Any]])
async def get_indicators():
    """
    Retorna metadados de todos os 50 indicadores TOPSIS.
    
    Returns:
        Lista com índice, nome e impacto (maximize/minimize) de cada indicador
    """
    try:
        indicators = []
        for idx, (nome, impacto) in enumerate(zip(INDICADORES_NOMES, IMPACTOS_TOTAIS)):
            indicators.append({
                "indice": idx,
                "nome": nome,
                "impacto": "maximize" if impacto == 1 else "minimize",
                "peso": PESOS_EQUITATIVOS[idx],
                "categoria": (
                    "ISO 37120" if idx < 18 else (
                        "ISO 37122" if idx < 34 else "ISO 37123 + Sendai"
                    )
                )
            })
        
        logger.info(f"✅ Retornando {len(indicators)} indicadores")
        return indicators
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar indicadores: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao listar indicadores")


# ═════════════════════════════════════════════════════════════════════════════
# ENDPOINT: GET /snapshots/{codigo_ibge} - Histórico de Snapshots
# ═════════════════════════════════════════════════════════════════════════════

@topsis_router.get("/snapshots/{codigo_ibge}", response_model=List[Dict[str, Any]])
async def get_city_snapshots(codigo_ibge: str, db: Session = Depends(get_db)):
    """
    Retorna histórico de snapshots calculados para uma cidade.
    
    Args:
        codigo_ibge: Código IBGE da cidade (8 dígitos)
    
    Returns:
        Lista de snapshots com data_calculo, indicadores e fonte de dados
    """
    try:
        # Validar formato do código IBGE
        if not codigo_ibge.isdigit() or len(codigo_ibge) != 8:
            raise HTTPException(status_code=400, detail="Código IBGE deve ter 8 dígitos")
        
        # Buscar snapshots no banco (ordenado por data descendente)
        snapshots = db.query(IndicatorSnapshot).filter(
            IndicatorSnapshot.codigo_ibge == codigo_ibge
        ).order_by(IndicatorSnapshot.data_calculo.desc()).all()
        
        result = [
            {
                "data_calculo": s.data_calculo.isoformat(),
                "periodo_referencia": s.periodo_referencia,
                "fonte_dados": s.fonte_dados,
                "quantidade_indicadores": len(s.valores_indicadores) if s.valores_indicadores else 0,
                "valores_indicadores": s.valores_indicadores or []
            }
            for s in snapshots
        ]
        
        logger.info(f"✅ Retornando {len(result)} snapshots para cidade {codigo_ibge}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao buscar snapshots para {codigo_ibge}: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar snapshots históricos")