"""
Router TOPSIS - Endpoints para análise de maturidade Smart Cities

Este módulo contém endpoints para:
- Cálculo de indicadores ISO 37120/37122/37123
- Análise TOPSIS de maturidade de cidades
- Geração de rankings inteligentes com dados reais de APIs governamentais
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException

from app.schemas import (
    CityDataInput,
    TOPSISInput,
    TOPSISResult,
)
from app.services.indicators import calculate_all_indicators
from app.services.topsis import calculate_topsis
from app.services.external_apis import (
    get_ibge_population,
    get_siconfi_finances,
    get_datasus_health_infrastructure,
)

# Logger para rastreamento
logger = logging.getLogger(__name__)

topsis_router = APIRouter(prefix="/topsis", tags=["TOPSIS"])


async def processar_cidade_real(codigo_ibge: str, nome_cidade: str) -> Optional[Dict[str, Any]]:
    """
    Processa uma cidade consultando APIs governamentais em paralelo.
    
    Esta função utiliza asyncio.gather() para chamar simultaneamente:
    - IBGE: População
    - SICONFI: Receitas, despesas de capital, serviço da dívida
    - DataSUS: Quantidade de hospitais
    
    Args:
        codigo_ibge: Código IBGE do município (ex: "4101408")
        nome_cidade: Nome da cidade para identificação
    
    Returns:
        Dict com resultado contendo nome_cidade e indicadores, ou None em caso de erro
    """
    try:
        logger.info(f"========== PROCESSANDO CIDADE: {nome_cidade} (IBGE: {codigo_ibge}) ==========")
        
        # Obtém dados de todas as 3 APIs em paralelo
        populacao, finances, hospitais = await asyncio.gather(
            get_ibge_population(codigo_ibge),
            get_siconfi_finances(codigo_ibge),
            get_datasus_health_infrastructure(codigo_ibge),
            return_exceptions=False
        )
        
        # =========== DEBUG LOGS: Valores exatos das APIs ===========
        logger.info(f"[DEBUG] {nome_cidade} - População IBGE: {populacao}")
        logger.info(f"[DEBUG] {nome_cidade} - Dados SICONFI: {finances}")
        logger.info(f"[DEBUG] {nome_cidade} - Hospitais DataSUS: {hospitais}")
        
        # Valida se os dados críticos foram obtidos
        if populacao is None or finances is None:
            logger.error(f"❌ {nome_cidade}: Falha ao obter dados críticos (pop={populacao}, fin={finances})")
            return None
        
        # Extrai dados financeiros com proteção contra None
        receita_propria = finances.get("receita_propria", 0.0) or 0.0
        despesas_capital = finances.get("despesas_capital", 0.0) or 0.0
        servico_divida = finances.get("servico_divida", 0.0) or 0.0
        
        logger.info(f"[DEBUG] {nome_cidade} - Receita Própria: R$ {receita_propria:,.2f}")
        logger.info(f"[DEBUG] {nome_cidade} - Despesas Capital: R$ {despesas_capital:,.2f}")
        logger.info(f"[DEBUG] {nome_cidade} - Serviço da Dívida: R$ {servico_divida:,.2f}")
        
        # Calcula despesas totais (capital + operacionais)
        # Como não temos dados separados, usamos uma estimativa
        despesas_totais = despesas_capital * 1.5  # Assume 50% mais em despesas operacionais
        despesas_operacionais = despesas_totais - despesas_capital
        
        logger.info(f"[DEBUG] {nome_cidade} - Despesas Totais (estimadas): R$ {despesas_totais:,.2f}")
        
        # Cria objeto CityDataInput com dados reais das APIs
        city_data = CityDataInput(
            nome_cidade=nome_cidade,
            populacao_total=populacao,
            receita_propria=receita_propria,
            custo_servico_divida=servico_divida,
            despesas_capital=despesas_capital,
            despesas_operacionais=despesas_operacionais,
            despesas_totais=despesas_totais,
            num_mulheres_eleitas=0,  # Não disponível nas APIs, será 0
            total_cargos_gestao=1,   # Evita divisão por zero
            quantidade_hospitais=hospitais if hospitais else 0
        )
        
        # Calcula indicadores
        indicadores = calculate_all_indicators(city_data)
        
        # =========== DEBUG LOGS: Indicadores Calculados ===========
        logger.info(f"[DEBUG] {nome_cidade} - Taxa Endividamento: {indicadores.taxa_endividamento}%")
        logger.info(f"[DEBUG] {nome_cidade} - Despesas Capital %: {indicadores.despesas_capital_percentual}%")
        logger.info(f"[DEBUG] {nome_cidade} - Mulheres Eleitas %: {indicadores.mulheres_eleitas_percentual}%")
        logger.info(f"[DEBUG] {nome_cidade} - Hospitais por 100k: {indicadores.hospitais_por_100mil}")
        
        resultado = {
            "nome_cidade": nome_cidade,
            "indicadores": indicadores,
        }
        
        logger.info(f"✅ {nome_cidade} processada com sucesso")
        return resultado
        
    except Exception as e:
        logger.error(f"Erro ao processar cidade {nome_cidade}: {str(e)}")
        return None


@topsis_router.get("/ranking-real", response_model=TOPSISResult)
async def get_real_data_ranking() -> TOPSISResult:
    """
    Endpoint principal: Constrói ranking Smart Cities com dados REAIS das APIs governamentais.
    
    Este endpoint substitui o endpoint /teste anterior, consultando:
    - IBGE SIDRA: População estimada
    - SICONFI: Dados financeiros municipais
    - DataSUS: Infraestrutura de saúde (hospitais)
    
    As cidades testadas são:
    - Apucarana (código IBGE: 4101408)
    - Londrina (código IBGE: 4113700)
    - Maringá (código IBGE: 4115200)
    
    Retorna:
        TOPSISResult com ranking ordenado por Índice Smart
    
    Raises:
        HTTPException 502: Se não conseguir obter dados de nenhuma cidade
    """
    try:
        # Define cidades a serem analisadas com seus códigos IBGE
        cidades_config = [
            {"codigo_ibge": "4101408", "nome": "Apucarana"},
            {"codigo_ibge": "4113700", "nome": "Londrina"},
            {"codigo_ibge": "4115200", "nome": "Maringá"},
        ]
        
        logger.info("=" * 80)
        logger.info("🚀 INICIANDO COLETA DE DADOS REAIS DE APIs GOVERNAMENTAIS")
        logger.info("=" * 80)
        
        # Processa todas as cidades em paralelo
        resultados_cidades = await asyncio.gather(
            *[
                processar_cidade_real(config["codigo_ibge"], config["nome"])
                for config in cidades_config
            ],
            return_exceptions=False
        )
        
        # Filtra cidades que foram processadas com sucesso
        cidades_sucesso = [r for r in resultados_cidades if r is not None]
        
        logger.info(f"\n✅ Cidades processadas com sucesso: {len(cidades_sucesso)}/{len(cidades_config)}")
        
        if not cidades_sucesso:
            logger.error("❌ FALHA CRÍTICA: Nenhuma cidade conseguiu ser processada")
            raise HTTPException(
                status_code=502,
                detail="Falha ao obter dados das APIs governamentais. Tente novamente mais tarde."
            )
        
        # Prepara dados para TOPSIS
        cidades_nomes = [r.nome_cidade for r in cidades_sucesso]
        indicadores_nomes = [
            "Taxa Endividamento (%)",
            "Despesas Capital (%)",
            "Hospitais por 100k hab"
        ]
        
        # Constrói matriz de decisão com os 3 indicadores
        matriz_decisao = []
        for resultado in cidades_sucesso:
            linha = [
                resultado.indicadores.taxa_endividamento,
                resultado.indicadores.despesas_capital_percentual,
                resultado.indicadores.hospitais_por_100mil,
            ]
            matriz_decisao.append(linha)
        
        logger.info(f"\n📊 MATRIZ DE DECISÃO CONSTRUÍDA:")
        logger.info(f"   Cidades: {cidades_nomes}")
        logger.info(f"   Indicadores: {indicadores_nomes}")
        logger.info(f"   Dados: {matriz_decisao}")
        
        # Pesos: 40% endividamento, 40% despesas capital, 20% hospitais
        pesos = [0.4, 0.4, 0.2]
        
        # Impactos:
        # Taxa Endividamento = CUSTO (quanto menor, melhor) = -1
        # Despesas Capital = BENEFÍCIO (quanto maior, melhor) = 1
        # Hospitais = BENEFÍCIO (quanto maior, melhor) = 1
        impactos = [-1, 1, 1]
        
        logger.info(f"\n⚙️  CONFIGURAÇÃO TOPSIS:")
        logger.info(f"   Pesos: {pesos}")
        logger.info(f"   Impactos: {impactos}")
        logger.info(f"\nExecutando TOPSIS com {len(cidades_sucesso)} cidades...")
        
        # Executa TOPSIS
        topsis_input = TOPSISInput(
            cidades=cidades_nomes,
            indicadores_nomes=indicadores_nomes,
            matriz_decisao=matriz_decisao,
            pesos=pesos,
            impactos=impactos,
        )
        
        result = calculate_topsis(topsis_input)
        
        logger.info(f"\n🏆 RANKING FINAL CALCULADO:")
        for i, city in enumerate(result.ranking, 1):
            logger.info(f"   #{i} {city.nome_cidade}: Índice Smart = {city.indice_smart:.4f}")
        
        logger.info("=" * 80)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado ao gerar ranking real: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao processar ranking de cidades. Contate o administrador."
        )


@topsis_router.get("/teste", response_model=TOPSISResult)
async def test_topsis_with_mock_data() -> TOPSISResult:
    """
    Endpoint de teste com dados mockados de 3 cidades reais.
    
    DESCONTINUADO: Use /ranking-real para dados reais das APIs.
    Este endpoint mantém dados mockados apenas para testes offline.
    
    Returns:
        TOPSISResult: Ranking com dados estáticos para testes
    """
    # ==========================================
    # DADOS MOCKADOS - Apenas para testes
    # ==========================================
    
    # Dados Apucarana
    apucarana_data = CityDataInput(
        nome_cidade="Apucarana",
        populacao_total=130000,
        receita_propria=500000,
        custo_servico_divida=150000,
        despesas_capital=200000,
        despesas_operacionais=300000,
        despesas_totais=500000,
        num_mulheres_eleitas=3,
        total_cargos_gestao=13,
        quantidade_hospitais=5,
    )
    
    # Dados Londrina
    londrina_data = CityDataInput(
        nome_cidade="Londrina",
        populacao_total=575000,
        receita_propria=1200000,
        custo_servico_divida=200000,
        despesas_capital=450000,
        despesas_operacionais=600000,
        despesas_totais=1050000,
        num_mulheres_eleitas=5,
        total_cargos_gestao=13,
        quantidade_hospitais=15,
    )
    
    # Dados Maringá
    mariga_data = CityDataInput(
        nome_cidade="Maringá",
        populacao_total=432000,
        receita_propria=850000,
        custo_servico_divida=120000,
        despesas_capital=300000,
        despesas_operacionais=400000,
        despesas_totais=700000,
        num_mulheres_eleitas=6,
        total_cargos_gestao=13,
        quantidade_hospitais=12,
    )
    
    # ==========================================
    # CALCULA INDICADORES PARA CADA CIDADE
    # ==========================================
    
    apucarana_indicators = calculate_all_indicators(apucarana_data)
    londrina_indicators = calculate_all_indicators(londrina_data)
    mariga_indicators = calculate_all_indicators(mariga_data)
    
    # ==========================================
    # PREPARA MATRIZ DE DECISÃO PARA TOPSIS
    # ==========================================
    
    cidades = ["Apucarana", "Londrina", "Maringá"]
    indicadores_nomes = [
        "Taxa Endividamento (%)",
        "Despesas Capital (%)",
        "Hospitais por 100k hab",
    ]
    
    # Matriz de decisão (cidades x indicadores)
    matriz_decisao = [
        [
            apucarana_indicators.taxa_endividamento,
            apucarana_indicators.despesas_capital_percentual,
            apucarana_indicators.hospitais_por_100mil,
        ],
        [
            londrina_indicators.taxa_endividamento,
            londrina_indicators.despesas_capital_percentual,
            londrina_indicators.hospitais_por_100mil,
        ],
        [
            mariga_indicators.taxa_endividamento,
            mariga_indicators.despesas_capital_percentual,
            mariga_indicators.hospitais_por_100mil,
        ],
    ]
    
    # ==========================================
    # DEFINE PESOS E IMPACTOS
    # ==========================================
    
    # Pesos: distribuição 40-40-20
    pesos = [0.4, 0.4, 0.2]
    
    # Impactos:
    # Taxa Endividamento = CUSTO (quanto menor, melhor) = -1
    # Despesas Capital = BENEFÍCIO (quanto maior, melhor) = 1
    # Hospitais = BENEFÍCIO (quanto maior, melhor) = 1
    impactos = [-1, 1, 1]
    
    # ==========================================
    # EXECUTA TOPSIS
    # ==========================================
    
    topsis_input = TOPSISInput(
        cidades=cidades,
        indicadores_nomes=indicadores_nomes,
        matriz_decisao=matriz_decisao,
        pesos=pesos,
        impactos=impactos,
    )
    
    result = calculate_topsis(topsis_input)
    
    return result
