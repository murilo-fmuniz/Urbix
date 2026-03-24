"""
Serviço de Cálculo de Indicadores ISO 37120/37122/37123

Este módulo contém funções para calcular indicadores de Smart Cities
de acordo com as normas ISO 37120, 37122 e 37123.

As fórmulas utilizadas seguem padrões:
- Simples divisão com multiplicação por 100 (porcentagem)
- Ou divisão com multiplicação por 100.000 (taxa por habitantes)
"""

from app.schemas import CityDataInput, IndicatorValues


def calculate_debt_service_rate(city_data: CityDataInput) -> float:
    """
    Calcula a Taxa de Endividamento.
    
    Fórmula:
    Taxa Endividamento = (Custo Total Serviço Dívida / Receita Própria) * 100
    
    Args:
        city_data: Dados da cidade (CityDataInput)
    
    Returns:
        float: Taxa de endividamento em percentual. Retorna 0.0 se receita for zero.
    """
    # EARLY RETURN: Proteção contra divisão por zero
    if city_data.receita_propria <= 0:
        return 0.0
    
    taxa_endividamento = (
        city_data.custo_servico_divida / city_data.receita_propria
    ) * 100
    
    return round(taxa_endividamento, 2)


def calculate_capital_expenditure_rate(city_data: CityDataInput) -> float:
    """
    Calcula o Percentual de Despesas de Capital.
    
    Fórmula:
    Despesas Capital % = (Total Despesas Ativos Fixos / 
                          Total Despesas Operacionais e Capital) * 100
    
    Args:
        city_data: Dados da cidade (CityDataInput)
    
    Returns:
        float: Percentual de despesas de capital. Retorna 0.0 se despesas forem zero.
    """
    # EARLY RETURN: Proteção contra divisão por zero
    if city_data.despesas_totais <= 0:
        return 0.0
    
    despesas_capital_pct = (
        city_data.despesas_capital / city_data.despesas_totais
    ) * 100
    
    return round(despesas_capital_pct, 2)


def calculate_women_elected_rate(city_data: CityDataInput) -> float:
    """
    Calcula o Percentual de Mulheres Eleitas em Cargos de Gestão.
    
    Fórmula:
    Mulheres Eleitas % = (Número Mulheres / Total Cargos Gestão) * 100
    
    Args:
        city_data: Dados da cidade (CityDataInput)
    
    Returns:
        float: Percentual de mulheres em cargos de gestão. Retorna 0.0 se cargos forem zero.
    """
    # EARLY RETURN: Proteção contra divisão por zero
    if city_data.total_cargos_gestao <= 0:
        return 0.0
    
    mulheres_pct = (
        city_data.num_mulheres_eleitas / city_data.total_cargos_gestao
    ) * 100
    
    return round(mulheres_pct, 2)


def calculate_hospitals_per_capita(city_data: CityDataInput) -> float:
    """
    Calcula a Taxa de Hospitais por 100 mil habitantes.
    
    Fórmula:
    Hospitais por 100k = (Número de Hospitais / População) * 100.000
    
    Args:
        city_data: Dados da cidade (CityDataInput)
    
    Returns:
        float: Número de hospitais por 100 mil habitantes. Retorna 0.0 se população for zero.
    """
    # EARLY RETURN: Proteção contra divisão por zero (dados da API zerados)
    if city_data.populacao_total <= 0:
        return 0.0
    
    hospitais_per_capita = (
        city_data.quantidade_hospitais / city_data.populacao_total
    ) * 100000
    
    return round(hospitais_per_capita, 2)


def calculate_all_indicators(city_data: CityDataInput) -> IndicatorValues:
    """
    Calcula todos os indicadores para uma cidade.
    
    Função principal que executa todos os cálculos de indicadores
    e retorna um objeto IndicatorValues estruturado.
    
    Args:
        city_data: Dados brutos da cidade
    
    Returns:
        IndicatorValues: Objeto com os 4 indicadores calculados
    
    Raises:
        ValueError: Se algum dado de entrada for inválido
    """
    try:
        taxa_endividamento = calculate_debt_service_rate(city_data)
        despesas_capital_percentual = calculate_capital_expenditure_rate(city_data)
        mulheres_eleitas_percentual = calculate_women_elected_rate(city_data)
        hospitais_por_100mil = calculate_hospitals_per_capita(city_data)
        
        return IndicatorValues(
            taxa_endividamento=taxa_endividamento,
            despesas_capital_percentual=despesas_capital_percentual,
            mulheres_eleitas_percentual=mulheres_eleitas_percentual,
            hospitais_por_100mil=hospitais_por_100mil,
        )
    except ValueError as e:
        raise ValueError(f"Erro ao calcular indicadores: {str(e)}")
