"""
Serviço de Cálculo de Indicadores ISO 37120/37122/37123

Este módulo contém funções para calcular indicadores de Smart Cities
de acordo com as normas ISO 37120, 37122 e 37123.

As fórmulas utilizadas seguem padrões:
- Simples divisão com multiplicação por 100 (porcentagem)
- Ou divisão com multiplicação por 100.000 (taxa por habitantes)
"""

from app.schemas import CityDataInput, IndicatorValues
def calculate_financial_independence(receita_propria: float, receita_total: float) -> float:
    """
    Calcula a Independência Financeira (% receita própria sobre total).
    """
    if receita_total <= 0:
        return 0.0
    return round((receita_propria / receita_total) * 100, 2)

def calculate_gross_budget_per_capita(despesas_totais: float, populacao: float) -> float:
    """
    Calcula o Orçamento Bruto per capita.
    """
    if populacao <= 0:
        return 0.0
    return round(despesas_totais / populacao, 2)


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


def calculate_all_indicators(city_data: CityDataInput) -> dict:
    """
    Calcula todos os indicadores (automáticos e híbridos) para uma cidade.
    Retorna um dicionário com todos os valores.
    """
    try:
        taxa_endividamento = calculate_debt_service_rate(city_data)
        despesas_capital_percentual = calculate_capital_expenditure_rate(city_data)
        mulheres_eleitas_percentual = calculate_women_elected_rate(city_data)
        hospitais_por_100mil = calculate_hospitals_per_capita(city_data)
        independencia_financeira = calculate_financial_independence(city_data.receita_propria, city_data.receita_total)
        orcamento_per_capita = calculate_gross_budget_per_capita(city_data.despesas_totais, city_data.populacao_total)

        # Indicadores manuais (se presentes)
        pontos_iluminacao_telegestao = getattr(city_data, 'pontos_iluminacao_telegestao', 0.0)
        medidores_inteligentes_energia = getattr(city_data, 'medidores_inteligentes_energia', 0.0)
        bombeiros_por_100k = getattr(city_data, 'bombeiros_por_100k', 0.0)
        area_verde_mapeada = getattr(city_data, 'area_verde_mapeada', 0.0)

        return {
            'taxa_endividamento': taxa_endividamento,
            'despesas_capital_percentual': despesas_capital_percentual,
            'mulheres_eleitas_percentual': mulheres_eleitas_percentual,
            'hospitais_por_100mil': hospitais_por_100mil,
            'independencia_financeira': independencia_financeira,
            'orcamento_per_capita': orcamento_per_capita,
            'pontos_iluminacao_telegestao': pontos_iluminacao_telegestao,
            'medidores_inteligentes_energia': medidores_inteligentes_energia,
            'bombeiros_por_100k': bombeiros_por_100k,
            'area_verde_mapeada': area_verde_mapeada,
        }
    except ValueError as e:
        raise ValueError(f"Erro ao calcular indicadores: {str(e)}")
