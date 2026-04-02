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
)
from app.database import SessionLocal, get_db
from app.models import IndicatorSnapshot, RankingSnapshot, DadosColeta, Indicador

# Logger para rastreamento
logger = logging.getLogger(__name__)

topsis_router = APIRouter(prefix="/topsis", tags=["TOPSIS"])

# ==========================================
# CONFIGURAÇÃO TOPSIS: IMPACTOS E PESOS
# ==========================================

# Definição dos 47 indicadores em ordem (16 + 15 + 16)
INDICADORES_NOMES = [
    # ISO 37120 (16 indicadores)
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
    
    # ISO 37122 (15 indicadores)
    "Sobrevivência Novos Negócios (100k hab)",          # 15
    "Empregos em TIC (% força trabalho)",               # 16
    "Graduados STEM (100k hab)",                        # 17
    "Energia de Resíduos (% energia total)",            # 18
    "Iluminação Pública com Telegestão (%)",            # 19
    "Medidores Inteligentes Energia (%)",               # 20
    "Edifícios Verdes Certificados (%)",                # 21
    "Monitoramento Ar em Tempo Real (%)",               # 22
    "Serviços Urbanos Online (%)",                      # 23
    "Prontuário Eletrônico (% população)",              # 24
    "Consultas Remotas (100k hab)",                     # 25
    "Medidores Inteligentes Água (%)",                  # 26
    "Áreas Cobertas por Câmeras (% cidade)",            # 27
    "Lixeiras com Sensores (%)",                        # 28
    "Semáforos Inteligentes (%)",                       # 29
    "Frota Ônibus Zero Emissão (%)",                    # 30
    
    # ISO 37123 + Marco de Sendai (16 indicadores)
    "Seguros contra Ameaças (% população)",             # 31
    "Empregos Informais (% força trabalho)",            # 32
    "Escolas com Plano Emergência (%)",                 # 33
    "População Treinada em Emergência (%)",             # 34
    "Hospitais com Gerador Backup (%)",                 # 35
    "Seguro Saúde Básico (% população)",                # 36
    "Taxa de Imunização (%)",                           # 37
    "Abrigos de Emergência (100k hab)",                 # 38
    "Edifícios Vulneráveis a Desastres (%)",            # 39
    "Rotas de Evacuação Identificadas (100k)",          # 40
    "Reservas de Alimentos 72h (%)",                    # 41
    "Mapas de Ameaças Públicos (%)",                    # 42
    "Mortalidade por Desastres (100k hab)",             # 43
    "Pessoas Afetadas por Desastres (100k hab)",        # 44
    "Perdas por Desastres (% PIB)",                     # 45
    "Danos à Infraestrutura Básica (%)",                # 46
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
_NUM_INDICADORES = len(IMPACTOS_TOTAIS)  # Deve ser 47
PESOS_EQUITATIVOS = [1.0 / _NUM_INDICADORES] * _NUM_INDICADORES

logger.info(f"✅ TOPSIS Configurado: {_NUM_INDICADORES} indicadores, peso equitativo: {PESOS_EQUITATIVOS[0]:.4f}")

# ==========================================
# FUNÇÕES AUXILIARES: INTERPOLAÇÃO INTELIGENTE
# ==========================================

# ==========================================
# FUNÇÕES AUXILIARES: EXTRAÇÃO, INJEÇÃO E MOCK
# ==========================================

def flatten_manual_indicators(manual: ManualCityIndicators) -> List[float]:
    """
    ⭐ PASSO 1: EXTRAÇÃO DINÂMICA (FLATTENING)
    
    Extrai todos os 47 indicadores do objeto ManualCityIndicators em ordem plana [float].
    Respeita RIGOROSAMENTE a ordem declarada no Pydantic.
    
    Estrutura esperada:
    - ISO 37120: 16 indicadores
    - ISO 37122: 15 indicadores
    - ISO 37123 + Sendai: 16 indicadores
    
    Args:
        manual: Objeto ManualCityIndicators estruturado por ISO
    
    Returns:
        Lista plana com 47 floats em ordem
    """
    indicadores_flat = [
        # ===== ISO 37120 (16 indicadores) =====
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
        
        # ===== ISO 37122 (15 indicadores) =====
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
    
    assert len(indicadores_flat) == 47, f"❌ ERRO: Esperado 47 indicadores, obteve {len(indicadores_flat)}"
    logger.debug(f"✅ Flattening completo: 47 indicadores extraídos em ordem")
    
    return indicadores_flat


def inject_api_data_into_flat_list(
    indicadores_flat: List[float],
    siconfi_data: Dict[str, Any],
    ibge_data: Dict[str, Any],
    datasus_data: Dict[str, Any],
    nome_cidade: str
) -> List[float]:
    """
    ⭐ PASSO 2: INJEÇÃO DOS DADOS AUTOMÁTICOS (5 INDICADORES REAIS)
    
    Sobrescreve valores específicos na lista plana com dados das APIs:
    - SICONFI: taxa_endividamento_pct, receita_propria_pct, despesas_capital_pct, orcamento_per_capita, divida_consolidada
    - IBGE: população (para cálculos per capita)
    - DataSUS: hospitais_por_100k
    
    A lógica de sobrescrita respeita APENAS os valores que não são 0.0 no manual.
    Se o manual tem valor > 0, mantém o manual (dados do usuário têm prioridade).
    Se o manual é 0.0, sobrescreve com API (dados automáticos como fallback).
    
    Args:
        indicadores_flat: Lista plana com 47 valores (após flattening)
        siconfi_data: Dict com receita_propria, despesas_capital, receita_total, divida_consolidada, etc
        ibge_data: Dict com populacao
        datasus_data: Dict com num_hospitais, etc
        nome_cidade: Para logging
    
    Returns:
        Lista atualizada com dados das APIs injetados onde apropriado
    """
    indicadores_flat = list(indicadores_flat)  # Copiar para não modificar original
    
    # ==========================================================
    # 🛡️ BLINDAGEM CONTRA TIPOS ERRADOS DA API/FALLBACK (ERRO 503)
    # ==========================================================
    siconfi_data = siconfi_data if isinstance(siconfi_data, dict) else {}
    datasus_data = datasus_data if isinstance(datasus_data, dict) else {}
    
    if isinstance(ibge_data, (int, float)):
        ibge_data = {"populacao": float(ibge_data)}
    elif not isinstance(ibge_data, dict):
        ibge_data = {}
    # ==========================================================
    
    # Extrair dados das APIs com validação segura
    populacao = ibge_data.get("populacao", 0) or 1  # Evitar divisão por zero
    
    receita_propria_valor = siconfi_data.get("receita_propria", 0) or 0
    despesas_capital_valor = siconfi_data.get("despesas_capital", 0) or 0
    receita_total_valor = siconfi_data.get("receita_total", 0) or 1  # Evitar divisão por zero
    divida_consolidada_valor = siconfi_data.get("divida_consolidada", 0) or 0
    
    num_hospitais = datasus_data.get("num_hospitais", 0) or 0
    
    logger.info(f"\n💾 INJEÇÃO DE DADOS DAS APIS ({nome_cidade}) - 5 INDICADORES REAIS:")
    logger.info(f"   📊 SICONFI: receita_propria={receita_propria_valor}, despesas_capital={despesas_capital_valor}, receita_total={receita_total_valor}, divida_consolidada={divida_consolidada_valor}")
    logger.info(f"   📊 IBGE: população={populacao}")
    logger.info(f"   📊 DataSUS: hospitais={num_hospitais}")
    
    # ===== CÁLCULOS DOS 5 INDICADORES REAIS =====
    
    # Índice [1] = Taxa de Endividamento (%)
    taxa_endividamento_calc = (divida_consolidada_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # Índice [2] = Despesas de Capital (% orçamento)
    despesas_capital_pct_calc = (despesas_capital_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # Índice [3] = Receita Própria (% receita total)
    receita_propria_pct_calc = (receita_propria_valor / receita_total_valor * 100) if receita_total_valor > 0 else 0.0
    
    # Índice [4] = Orçamento per capita (R$)
    orcamento_per_capita_calc = (receita_total_valor / populacao) if populacao > 0 else 0.0
    
    # Índice [35] = Hospitais com Gerador Backup (usando como proxy hospitais_por_100k)
    hospitais_100k_calc = (num_hospitais / populacao * 100000) if populacao > 0 else 0.0
    
    # ===== INJEÇÕES NA MATRIZ =====
    
    # [1] Taxa de Endividamento
    if indicadores_flat[1] == 0.0 and taxa_endividamento_calc > 0:
        indicadores_flat[1] = taxa_endividamento_calc
        logger.info(f"   ✅ [Índice 1] Taxa Endividamento: {taxa_endividamento_calc:.2f}% (DO SICONFI - RGF)")
    else:
        logger.info(f"   ⚪ [Índice 1] Taxa Endividamento: {indicadores_flat[1]:.2f}% (MANUAL)")
    
    # [2] Despesas de Capital
    if indicadores_flat[2] == 0.0 and despesas_capital_pct_calc > 0:
        indicadores_flat[2] = despesas_capital_pct_calc
        logger.info(f"   ✅ [Índice 2] Despesas Capital: {despesas_capital_pct_calc:.2f}% (DO SICONFI - RREO)")
    else:
        logger.info(f"   ⚪ [Índice 2] Despesas Capital: {indicadores_flat[2]:.2f}% (MANUAL)")
    
    # [3] Receita Própria
    if indicadores_flat[3] == 0.0 and receita_propria_pct_calc > 0:
        indicadores_flat[3] = receita_propria_pct_calc
        logger.info(f"   ✅ [Índice 3] Receita Própria: {receita_propria_pct_calc:.2f}% (DO SICONFI - RREO)")
    else:
        logger.info(f"   ⚪ [Índice 3] Receita Própria: {indicadores_flat[3]:.2f}% (MANUAL)")
    
    # [4] Orçamento per capita
    if indicadores_flat[4] == 0.0 and orcamento_per_capita_calc > 0:
        indicadores_flat[4] = orcamento_per_capita_calc
        logger.info(f"   ✅ [Índice 4] Orçamento/per capita: R$ {orcamento_per_capita_calc:.2f} (DO SICONFI - RREO)")
    else:
        logger.info(f"   ⚪ [Índice 4] Orçamento/per capita: R$ {indicadores_flat[4]:.2f} (MANUAL)")
    
    # [35] Hospitais por 100k habitantes (proxy para hospitais_geradores_backup)
    if indicadores_flat[35] == 0.0 and hospitais_100k_calc > 0:
        indicadores_flat[35] = hospitais_100k_calc
        logger.info(f"   ✅ [Índice 35] Hospitais/100k hab: {hospitais_100k_calc:.2f} (DO DATASUS + IBGE)")
    else:
        logger.info(f"   ⚪ [Índice 35] Hospitais/100k hab: {indicadores_flat[35]:.2f} (MANUAL)")
    
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
    1. ⭐ Flattening: Extrai 47 indicadores em lista plana respeitando ordem Pydantic
    2. ⭐ Injeção de APIs: Sobrescreve campos específicos com dados de SICONFI, IBGE, DataSUS
    3. 💾 Cache Inteligente: Salva dados frescos das APIs no banco de dados (se db passado)
    
    Args:
        codigo_ibge: Código IBGE do município
        nome_cidade: Nome da cidade
        manual: Indicadores manuais estruturados por ISO (ManualCityIndicators)
        db: Sessão SQLAlchemy opcional para salvar dados no banco (cache inteligente)
    
    Returns:
        Dict com nome_cidade e indicadores_flatalizados (47 valores), ou None em erro
    """
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"🏙️  PROCESSANDO: {nome_cidade} (IBGE: {codigo_ibge})")
        logger.info(f"{'='*80}")
        
        # Se não houver indicadores manuais, criar com defaults
        if manual is None:
            logger.warning(f"   ⚠️  Nenhum indicador manual fornecido, usando defaults")
            manual = ManualCityIndicators()
        
        # ===================================================================
        # ⭐ PASSO 1: EXTRAÇÃO DINÂMICA (FLATTENING)
        # ===================================================================
        logger.info(f"\n📋 PASSO 1: EXTRAÇÃO DINÂMICA (FLATTENING)")
        indicadores_flat = flatten_manual_indicators(manual)
        
        logger.info(f"   ✅ 47 indicadores extraídos")
        logger.info(f"   📊 Primeiros 5: {indicadores_flat[:5]}")
        logger.info(f"   📊 Últimos 5: {indicadores_flat[-5:]}")
        
        # ===================================================================
        # 📡 Chamar APIs externas em paralelo (SICONFI, IBGE, DataSUS)
        # ===================================================================
        logger.info(f"\n📡 Buscando dados em APIs externas (paralelo) - Timeout: 10s")
        
        try:
            # Chamar APIs com timeout de 10 segundos cada
            siconfi_data, ibge_data, datasus_data = await asyncio.gather(
                asyncio.wait_for(get_siconfi_finances(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_ibge_population(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_datasus_health_infrastructure(codigo_ibge), timeout=10.0),
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
            
            # Log de sucesso
            if isinstance(siconfi_data, dict):
                logger.info(f"   ✅ SICONFI respondeu em < 10s")
            if isinstance(ibge_data, (dict, int, float)) and not isinstance(ibge_data, Exception):
                logger.info(f"   ✅ IBGE respondeu em < 10s")
            if isinstance(datasus_data, dict):
                logger.info(f"   ✅ DataSUS respondeu em < 10s")
        
        except Exception as e:
            logger.error(f"   ❌ Erro crítico ao buscar APIs: {str(e)}")
            siconfi_data, ibge_data, datasus_data = {}, {}, {}
        
        # Normalizar dados das APIs com defaults
        siconfi_data = siconfi_data or {}
        ibge_data = ibge_data or 100000  # Default população
        datasus_data = datasus_data or {}
        
        # Se IBGE retornou um float, converter para dict
        if isinstance(ibge_data, (int, float)):
            populacao = float(ibge_data) if ibge_data and ibge_data > 0 else 100000
            ibge_data = {"populacao": populacao}
        else:
            ibge_data = ibge_data or {}
            populacao = ibge_data.get("populacao", 0) or 100000
        
        # ===================================================================
        # ⭐ PASSO 2: INJEÇÃO DOS DADOS AUTOMÁTICOS
        # ===================================================================
        logger.info(f"\n💉 PASSO 2: INJEÇÃO DOS DADOS AUTOMÁTICOS")
        indicadores_flat = inject_api_data_into_flat_list(
            indicadores_flat,
            siconfi_data,
            ibge_data,
            datasus_data,
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
                
                # Reconstruir dicionário JSON de 47 indicadores a partir da lista plana atualizada
                # Mapear de volta para a estrutura nested
                manual_atual = ManualCityIndicators()
                
                # ISO 37120 (índices 0-14)
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
                
                # ISO 37122 (índices 15-29)
                manual_atual.iso_37122.sobrevivencia_novos_negocios_100k = indicadores_flat[15]
                manual_atual.iso_37122.empregos_tic_pct = indicadores_flat[16]
                manual_atual.iso_37122.graduados_stem_100k = indicadores_flat[17]
                manual_atual.iso_37122.energia_residuos_pct = indicadores_flat[18]
                manual_atual.iso_37122.iluminacao_telegestao_pct = indicadores_flat[19]
                manual_atual.iso_37122.medidores_inteligentes_energia_pct = indicadores_flat[20]
                manual_atual.iso_37122.edificios_verdes_pct = indicadores_flat[21]
                manual_atual.iso_37122.monitoramento_ar_tempo_real_pct = indicadores_flat[22]
                manual_atual.iso_37122.servicos_urbanos_online_pct = indicadores_flat[23]
                manual_atual.iso_37122.prontuario_eletronico_pct = indicadores_flat[24]
                manual_atual.iso_37122.consultas_remotas_100k = indicadores_flat[25]
                manual_atual.iso_37122.medidores_inteligentes_agua_pct = indicadores_flat[26]
                manual_atual.iso_37122.areas_cobertas_cameras_pct = indicadores_flat[27]
                manual_atual.iso_37122.lixeiras_sensores_pct = indicadores_flat[28]
                manual_atual.iso_37122.semaforos_inteligentes_pct = indicadores_flat[29]
                manual_atual.iso_37122.frota_onibus_limpos_pct = indicadores_flat[30]
                
                # ISO 37123 + Sendai (índices 31-46)
                manual_atual.iso_37123.seguro_ameacas_pct = indicadores_flat[31]
                manual_atual.iso_37123.empregos_informais_pct = indicadores_flat[32]
                manual_atual.iso_37123.escolas_preparacao_emergencia_pct = indicadores_flat[33]
                manual_atual.iso_37123.populacao_treinada_emergencia_pct = indicadores_flat[34]
                manual_atual.iso_37123.hospitais_geradores_backup_pct = indicadores_flat[35]
                manual_atual.iso_37123.seguro_saude_basico_pct = indicadores_flat[36]
                manual_atual.iso_37123.imunizacao_pct = indicadores_flat[37]
                manual_atual.iso_37123.abrigos_emergencia_100k = indicadores_flat[38]
                manual_atual.iso_37123.edificios_vulneraveis_pct = indicadores_flat[39]
                manual_atual.iso_37123.rotas_evacuacao_100k = indicadores_flat[40]
                manual_atual.iso_37123.reservas_alimentos_72h_pct = indicadores_flat[41]
                manual_atual.iso_37123.mapas_ameacas_publicos_pct = indicadores_flat[42]
                manual_atual.iso_37123.mortalidade_desastres_100k = indicadores_flat[43]
                manual_atual.iso_37123.pessoas_afetadas_desastres_100k = indicadores_flat[44]
                manual_atual.iso_37123.perdas_desastres_pct_pib = indicadores_flat[45]
                manual_atual.iso_37123.danos_infraestrutura_basica_pct = indicadores_flat[46]
                
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
        # ✅ VALIDAÇÃO FINAL
        # ====================================================================
        assert len(indicadores_flat) == 47, f"❌ ERRO: Esperado 47 indicadores, obteve {len(indicadores_flat)}"
        
        # Estatísticas
        dados_nao_zero = len([v for v in indicadores_flat if v != 0.0])
        media_indicadores = np.mean(indicadores_flat) if indicadores_flat else 0.0
        min_indicador = np.min(indicadores_flat) if indicadores_flat else 0.0
        max_indicador = np.max(indicadores_flat) if indicadores_flat else 0.0
        
        logger.info(f"\n📊 RESUMO FINAL ({nome_cidade}):")
        logger.info(f"   ✅ Total indicadores: 47")
        logger.info(f"   ✅ Indicadores não-zero: {dados_nao_zero}/47 ({dados_nao_zero/47*100:.1f}%)")
        logger.info(f"   📈 Média: {media_indicadores:.2f}")
        logger.info(f"   📉 Mínimo: {min_indicador:.2f}")
        logger.info(f"   📈 Máximo: {max_indicador:.2f}")
        
        resultado = {
            "nome_cidade": nome_cidade,
            "indicadores_flatalizados": indicadores_flat,
            "metadata_cobertura": {
                "nome_cidade": nome_cidade,
                "total_indicadores": 47,
                "quantidade_dados_reais": dados_nao_zero,
                "pct_cobertura": (dados_nao_zero / 47) * 100,
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
    ✨ ENDPOINT PRINCIPAL: Ranking Smart Cities com 47 Indicadores ISO Completos
    
    ESTRUTURA: 47 indicadores totais (16 ISO37120 + 15 ISO37122 + 16 ISO37123 + Sendai)
    
    PESOS: Equitativos (1/47 ≈ 0.0213 cada)
    
    IMPACTOS: Definidos matematicamente conforme ISO e Marco de Sendai
    
    AGREGAÇÃO (3 PASSOS):
    1. Flattening: Extrai 47 indicadores em lista plana respeitando ordem Pydantic
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
        logger.info(f"📊 Cidades: {len(payload)} | Indicadores: 47 (16 ISO37120 + 15 ISO37122 + 16 ISO37123)")
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
        
        # Constrói matriz de decisão (47 indicadores x N cidades)
        matriz_decisao = [r["indicadores_flatalizados"] for r in cidades_sucesso]
        
        # ===== VALIDAÇÃO: Todas as linhas devem ter 47 elementos =====
        for idx, linha in enumerate(matriz_decisao):
            if len(linha) != 47:
                logger.error(f"❌ ERRO: Cidade {idx} ({cidades_nomes[idx]}) tem {len(linha)} indicadores ao invés de 47")
                raise HTTPException(
                    status_code=502,
                    detail=f"Inconsistência: Cidade {cidades_nomes[idx]} tem {len(linha)} indicadores, esperado 47"
                )
        
        logger.info(f"\n📊 MATRIZ DE DECISÃO VALIDADA:")
        logger.info(f"   Dimensão: {len(matriz_decisao)} cidades × 47 indicadores")
        logger.info(f"   Pesos: Equitativos (1/47 = {PESOS_EQUITATIVOS[0]:.4f})")
        logger.info(f"   Impactos: 16 (ISO37120) + 15 (ISO37122) + 16 (ISO37123+Sendai)")
        logger.info(f"   Cidades: {', '.join(cidades_nomes)}")
        
        # ===================================================================
        # ✅ IMPUTAÇÃO PELA MÉDIA (Mean Imputation)
        # ===================================================================
        logger.info(f"\n💉 IMPUTAÇÃO PELA MÉDIA: Preenchendo valores faltantes (0.0) com média dos dados reais")
        
        # Converter para NumPy para facilitar operações
        matriz_np = np.array(matriz_decisao, dtype=float)
        total_imputados = 0
        
        # Iterar sobre cada coluna (47 indicadores)
        for col_idx in range(47):
            coluna = matriz_np[:, col_idx]
            valores_reais = coluna[coluna > 0.0]  # Apenas valores > 0.0
            
            if len(valores_reais) > 0:
                media_coluna = float(np.mean(valores_reais))
                
                # Contar zeros para imputar
                zeros_na_coluna = np.sum(coluna == 0.0)
                
                if zeros_na_coluna > 0:
                    # Substituir zeros pela média
                    matriz_np[coluna == 0.0, col_idx] = media_coluna
                    total_imputados += zeros_na_coluna
                    
                    logger.debug(f"   [Índice {col_idx:2d}] {INDICADORES_NOMES[col_idx]:50s} → Média: {media_coluna:8.2f} (Imputados: {zeros_na_coluna})")
        
        logger.info(f"   ✅ Total valores imputados: {total_imputados} ({total_imputados/(47*len(matriz_decisao))*100:.1f}% da matriz)")
        
        # Converter de volta para lista de listas Python puro
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
            logger.info(f"✅ SNAPSHOT SALVO: {periodo_referencia} (N={len(cidades_sucesso)} cidades, 47 indicadores)")

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
    Endpoint de diagnóstico para debugar coleta de dados das APIs governamentais.
    
    Chama as 3 APIs assincronamente e retorna:
    - Dados brutos de cada API
    - Status indicando se é dado REAL ou FALLBACK
    - Informação sobre qual tier de fallback foi usado
    
    Útil para:
    - Verificar o status das APIs governamentais
    - Rastrear dados brutos antes do processamento TOPSIS
    - Diagnosticar problemas de coleta
    
    Exemplo:
        GET /topsis/debug-apis/4106902
        
    Resposta:
        {
            "codigo_testado": "4106902",
            "timestamp": "2026-04-01T14:43:24",
            "ibge": {
                "dados": {...},
                "status": "API_REAL | FALLBACK_ESPECIFICO | FALLBACK_UNIVERSAL",
                "fonte": "string informativa"
            },
            "siconfi": {...},
            "datasus": {...},
            "resumo": {
                "total_apis_ok": 1,
                "total_fallbacks": 2,
                "consistencia": "DADOS_REAIS | PARCIAL_FALLBACK | COMPLETO_FALLBACK"
            }
        }
    """
    logger.info(f"🔍 DEBUG: Iniciando diagnóstico para {codigo_ibge}")
    
    try:
        # Executar as 3 chamadas assincronamente em paralelo
        ibge_result, siconfi_result, datasus_result = await asyncio.gather(
            get_ibge_population(codigo_ibge),
            get_siconfi_finances(codigo_ibge),
            get_datasus_health_infrastructure(codigo_ibge),
            return_exceptions=False
        )
        
        # Helper para classificar status
        def classificar_status(resultado: Dict[str, Any]) -> str:
            """Classifica se o dado é real ou fallback baseado na chave 'fonte'."""
            if not resultado:
                return "ERRO_COLETA"
            
            fonte = resultado.get("fonte", "desconhecida")
            
            if "fallback universal" in fonte.lower():
                return "FALLBACK_UNIVERSAL"
            elif "fallback" in fonte.lower() and "banco" not in fonte.lower():
                return "FALLBACK_ESPECIFICO"
            elif "banco" in fonte.lower():
                return "FALLBACK_BANCO"
            elif "ibge" in fonte.lower() or "siconfi" in fonte.lower() or "datasus" in fonte.lower():
                return "API_REAL"
            else:
                return "STATUS_DESCONHECIDO"
        
        # Estruturar resposta
        ibge_status = classificar_status(ibge_result)
        siconfi_status = classificar_status(siconfi_result)
        datasus_status = classificar_status(datasus_result)
        
        # Contar quantos são dados reais vs fallback
        apis_ok = sum([
            1 for s in [ibge_status, siconfi_status, datasus_status] 
            if s == "API_REAL"
        ])
        fallbacks = sum([
            1 for s in [ibge_status, siconfi_status, datasus_status] 
            if "FALLBACK" in s or "BANCO" in s
        ])
        
        # Determinar consistência geral
        if apis_ok == 3:
            consistencia = "DADOS_REAIS_COMPLETO"
        elif apis_ok >= 1:
            consistencia = "PARCIAL_FALLBACK"
        else:
            consistencia = "COMPLETO_FALLBACK"
        
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
            
            # Resumo geral
            "resumo": {
                "total_apis_ok": apis_ok,
                "total_fallbacks": fallbacks,
                "consistencia": consistencia,
                "explicacao": {
                    "API_REAL": "Dado coletado diretamente da API governamental",
                    "FALLBACK_BANCO": "Dado persistido no banco de dados (cache local)",
                    "FALLBACK_ESPECIFICO": "Dado de fallback para 3 cidades pré-configuradas",
                    "FALLBACK_UNIVERSAL": "Dado de média nacional para 5.570 cidades",
                    "ERRO_COLETA": "Erro ao tentar coletar o dado"
                }
            }
        }
        
        logger.info(f"✅ DEBUG CONCLUÍDO: {codigo_ibge} | "
                   f"IBGE={ibge_status}, SICONFI={siconfi_status}, DataSUS={datasus_status} | "
                   f"Consistência: {consistencia}")
        
        return resposta
        
    except Exception as e:
        logger.error(f"❌ ERRO no debug de APIs para {codigo_ibge}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao debugar APIs: {str(e)}"
        )


def converter_dict_to_manual_indicators(data: Dict[str, Any]) -> ManualCityIndicators:
    """
    Converte Dict simples do frontend para ManualCityIndicators estruturado por ISO.
    
    Mapeia campos simples (se existirem) para a estrutura ISO hierárquica.
    """
    if not data:
        return ManualCityIndicators()
    
    resultado = ManualCityIndicators()
    
    # Mapeamentos do frontend para ISO
    if "bombeiros_por_100k" in data:
        resultado.iso_37120.bombeiros_100k = float(data["bombeiros_por_100k"]) if data["bombeiros_por_100k"] else 0.0
    
    if "pontos_iluminacao_telegestao" in data:
        resultado.iso_37122.iluminacao_telegestao_pct = float(data["pontos_iluminacao_telegestao"]) if data["pontos_iluminacao_telegestao"] else 0.0
    
    if "medidores_inteligentes_energia" in data:
        resultado.iso_37122.medidores_inteligentes_energia_pct = float(data["medidores_inteligentes_energia"]) if data["medidores_inteligentes_energia"] else 0.0
    
    if "area_verde_mapeada" in data:
        resultado.iso_37122.edificios_verdes_pct = float(data["area_verde_mapeada"]) if data["area_verde_mapeada"] else 0.0
    
    logger.debug(f"✅ Conversor: bombeiros={resultado.iso_37120.bombeiros_100k}, iluminacao={resultado.iso_37122.iluminacao_telegestao_pct}")
    
    return resultado


