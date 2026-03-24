from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date

# ==========================================
# SCHEMAS DE AUDITORIA
# ==========================================
class AuditoriaBase(BaseModel):
    fonte_nome: str
    fonte_url: Optional[str] = None
    data_extracao: Optional[date] = None
    observacoes: Optional[str] = None

class AuditoriaCreate(AuditoriaBase):
    pass

class AuditoriaResponse(AuditoriaBase):
    id: int
    dados_coleta_id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS DE DADOS DE COLETA
# ==========================================
class DadosColetaBase(BaseModel):
    cidade: str
    estado: str
    ano_referencia: int
    valor_numerador: Optional[float] = None
    valor_denominador: Optional[float] = None
    valor_final: Optional[float] = None
    dado_disponivel: bool = False

class DadosColetaCreate(DadosColetaBase):
    auditoria: Optional[AuditoriaCreate] = None

class DadosColetaResponse(DadosColetaBase):
    id: int
    indicador_id: int
    auditoria: Optional[AuditoriaResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS DE METODOLOGIA
# ==========================================
class MetodologiaBase(BaseModel):
    desc_numerador: str
    desc_denominador: str
    multiplicador: float
    unidade_medida: str

class MetodologiaCreate(MetodologiaBase):
    pass

class MetodologiaResponse(MetodologiaBase):
    id: int
    indicador_id: int

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS DE INDICADOR (MESTRE)
# ==========================================
class IndicadorBase(BaseModel):
    codigo_indicador: str
    nome: str
    norma: str
    grande_area: str
    eixo: str
    tipo: str
    descricao: str

class IndicadorCreate(IndicadorBase):
    metodologia: Optional[MetodologiaCreate] = None
    dados_coleta: List[DadosColetaCreate] = []

class IndicadorResponse(IndicadorBase):
    id: int
    metodologia: Optional[MetodologiaResponse] = None
    dados_coleta: List[DadosColetaResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SCHEMAS PARA CÁLCULO DE INDICADORES
# ==========================================
class CityDataInput(BaseModel):
    """
    Modelo para receber dados brutos de uma cidade.
    Será utilizado para calcular os indicadores ISO 37120/37122/37123.
    """
    nome_cidade: str
    populacao_total: float
    receita_propria: float
    custo_servico_divida: float  # custo total do serviço da dívida de longo prazo
    despesas_capital: float  # total das despesas em ativos fixos
    despesas_operacionais: float  # total das despesas operacionais
    despesas_totais: float  # total das despesas (operacionais + capital)
    num_mulheres_eleitas: int
    total_cargos_gestao: int
    quantidade_hospitais: int = 0  # número de hospitais (opcional)


class IndicatorValues(BaseModel):
    """Valores calculados para os indicadores de uma cidade."""
    taxa_endividamento: float  # %
    despesas_capital_percentual: float  # %
    mulheres_eleitas_percentual: float  # %
    hospitais_por_100mil: float  # hospitais por 100 mil habitantes


class CityIndicatorResult(BaseModel):
    """Resultado dos indicadores calculados para uma cidade."""
    nome_cidade: str
    indicadores: IndicatorValues


class TOPSISInput(BaseModel):
    """
    Entrada para cálculo TOPSIS.
    Contém a matriz de decisão (cidades x indicadores),
    pesos e impactos de cada critério.
    """
    cidades: List[str]
    indicadores_nomes: List[str]
    matriz_decisao: List[List[float]]  # cidades x indicadores
    pesos: List[float]  # pesos para cada indicador
    impactos: List[int]  # 1 para benefício, -1 para custo


class CitySmartIndex(BaseModel):
    """Índice Smart (TOPSIS) de uma cidade."""
    nome_cidade: str
    indice_smart: float  # valor de C_i


class TOPSISResult(BaseModel):
    """Resultado completo do cálculo TOPSIS."""
    ranking: List[CitySmartIndex]  # ordenado por indice_smart descendente
    detalhes_calculo: dict  # informações adicionais para auditoria