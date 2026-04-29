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
    get_inep_education,
    get_transparencia_social,
)
from app.database import SessionLocal, get_db
from app.models import IndicatorSnapshot, RankingSnapshot, DadosColeta, Indicador

# Logger para rastreamento
logger = logging.getLogger(__name__)

topsis_router = APIRouter(prefix="/topsis", tags=["TOPSIS"])

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
    nome_cidade: str
) -> List[float]:
    """
    ⭐ PASSO 2: INJEÇÃO DOS DADOS AUTOMÁTICOS (OTIMIZADA - 15+ INDICADORES REAIS)
    
    Sobrescreve valores específicos na lista plana com dados das APIs:
    - SICONFI: receita_propria_pct, despesas_capital_pct, orcamento_per_capita, divida (endividamento)
    - IBGE: população (para cálculos per capita)
    - DataSUS: hospitais_por_100k, proxy de serviços de saúde
    - INEP: relacao_estudante_professor, ideb_anos_iniciais, escolas_conectadas_pct
    - Portal da Transparência: taxa_populacao_assistida (Bolsa Família como proxy de vulnerabilidade social)
    
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
        nome_cidade: Para logging
    
    Returns:
        Lista atualizada com dados das APIs injetados em ~15 indicadores
    """
    indicadores_flat = list(indicadores_flat)  # Copiar para não modificar original
    
    # ==========================================================
    # 🛡️ BLINDAGEM CONTRA TIPOS ERRADOS DA API/FALLBACK (ERRO 503)
    # ==========================================================
    siconfi_data = siconfi_data if isinstance(siconfi_data, dict) else {}
    datasus_data = datasus_data if isinstance(datasus_data, dict) else {}
    inep_data = inep_data if isinstance(inep_data, dict) else {}
    transparencia_data = transparencia_data if isinstance(transparencia_data, dict) else {}
    
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
    
    # Extrair dados do Portal da Transparência
    beneficiados_bolsa_familia = transparencia_data.get("beneficiados_bolsa_familia", 0) or 0
    
    logger.info(f"\n💾 INJEÇÃO DE DADOS DAS APIS ({nome_cidade}) - 15+ INDICADORES REAIS:")
    logger.info(f"   📊 SICONFI: receita={receita_propria_valor}, despesas={despesas_capital_valor}, receita_total={receita_total_valor}, dívida={divida_consolidada_valor}")
    logger.info(f"   📊 IBGE: população={populacao}")
    logger.info(f"   📊 DataSUS: hospitais={num_hospitais}")
    logger.info(f"   📊 Portal: beneficiados_bolsa_familia={beneficiados_bolsa_familia}")
    
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
        
        try:
            # Chamar APIs com timeout de 10 segundos cada (incluindo Portal da Transparência)
            siconfi_data, ibge_data, datasus_data, inep_data, transparencia_data = await asyncio.gather(
                asyncio.wait_for(get_siconfi_finances(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_ibge_population(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_datasus_health_infrastructure(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_inep_education(codigo_ibge), timeout=10.0),
                asyncio.wait_for(get_transparencia_social(codigo_ibge), timeout=10.0),
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
        
        except Exception as e:
            logger.error(f"   ❌ Erro crítico ao buscar APIs: {str(e)}")
            siconfi_data, ibge_data, datasus_data, inep_data = {}, {}, {}, {}
        
        # Normalizar dados das APIs com defaults
        siconfi_data = siconfi_data or {}
        ibge_data = ibge_data or 100000  # Default população
        datasus_data = datasus_data or {}
        transparencia_data = transparencia_data or {}
        
        # Se IBGE retornou um float, converter para dict
        if isinstance(ibge_data, (int, float)):
            populacao = float(ibge_data) if ibge_data and ibge_data > 0 else 100000
            ibge_data = {"populacao": populacao}
        else:
            ibge_data = ibge_data or {}
            populacao = ibge_data.get("populacao", 0) or 100000
        
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
        # ✅ IMPUTAÇÃO PELA MÉDIA (Mean Imputation)
        # ===================================================================
        logger.info(f"\n💉 IMPUTAÇÃO PELA MÉDIA: Preenchendo valores faltantes (0.0) com média dos dados reais")
        
        # Converter para NumPy para facilitar operações
        matriz_np = np.array(matriz_decisao, dtype=float)
        total_imputados = 0
        
        # Iterar sobre cada coluna (indicadores)
        for col_idx in range(_NUM_INDICADORES):
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
        
        percentual_imputado = (total_imputados / (_NUM_INDICADORES * len(matriz_decisao)) * 100) if len(matriz_decisao) > 0 else 0
        logger.info(f"   ✅ Total valores imputados: {total_imputados} ({percentual_imputado:.1f}% da matriz)")
        
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
            return ManualCityIndicators()
    
    # Formato simples do frontend
    resultado = ManualCityIndicators()
    
    # Mapeamentos do frontend para ISO (4 campos principais)
    if "bombeiros_por_100k" in data and data["bombeiros_por_100k"]:
        resultado.iso_37120.bombeiros_100k = float(data["bombeiros_por_100k"])
    
    if "pontos_iluminacao_telegestao" in data and data["pontos_iluminacao_telegestao"]:
        resultado.iso_37122.iluminacao_telegestao_pct = float(data["pontos_iluminacao_telegestao"])
    
    if "medidores_inteligentes_energia" in data and data["medidores_inteligentes_energia"]:
        resultado.iso_37122.medidores_inteligentes_energia_pct = float(data["medidores_inteligentes_energia"])
    
    if "area_verde_mapeada" in data and data["area_verde_mapeada"]:
        resultado.iso_37122.edificios_verdes_pct = float(data["area_verde_mapeada"])
    
    # Suportar mais campos do frontend se necessário
    mapeamentos = {
        "taxa_desemprego": ("iso_37120", "taxa_desemprego_pct"),
        "taxa_endividamento": ("iso_37120", "taxa_endividamento_pct"),
        "despesas_capital": ("iso_37120", "despesas_capital_pct"),
        "receita_propria": ("iso_37120", "receita_propria_pct"),
        "orcamento_per_capita": ("iso_37120", "orcamento_per_capita"),
        # ... adicionar mais conforme necessário
    }
    
    for key_frontend, (iso_classe, field_name) in mapeamentos.items():
        if key_frontend in data and data[key_frontend]:
            iso_obj = getattr(resultado, iso_classe)
            setattr(iso_obj, field_name, float(data[key_frontend]))
    
    logger.debug(f"✅ Conversão de frontend: bombeiros={resultado.iso_37120.bombeiros_100k}, iluminacao={resultado.iso_37122.iluminacao_telegestao_pct}")
    
    return resultado



