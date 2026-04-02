from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date

# ==========================================
# SUB-MODELOS DE INDICADORES ISO - ESTRUTURA COMPLETA
# ==========================================

class ISO37120Indicators(BaseModel):
    """ISO 37120 - Indicadores de Cidades Sustentáveis e Resilientes
    
    Cobre: Economia e Finanças, Governança, Habitação, Segurança, Saúde, etc.
    Total de 16 indicadores
    """
    # Economia e Finanças (5 indicadores)
    taxa_desemprego_pct: float = Field(default=0.0, description="Taxa de desemprego (%)")
    taxa_endividamento_pct: float = Field(default=0.0, description="Taxa de endividamento (%)")
    despesas_capital_pct: float = Field(default=0.0, description="Despesas de capital (% do orçamento)")
    receita_propria_pct: float = Field(default=0.0, description="Receita própria (% da receita total)")
    orcamento_per_capita: float = Field(default=0.0, description="Orçamento per capita (R$)")
    # Governança (3 indicadores)
    mulheres_eleitas_pct: float = Field(default=0.0, description="Mulheres eleitas em cargos de gestão (%)")
    condenacoes_corrupcao_100k: float = Field(default=0.0, description="Condenações por corrupção por 100k hab")
    participacao_eleitoral_pct: float = Field(default=0.0, description="Participação eleitoral (%)")
    # Habitação e Segurança (8 indicadores)
    moradias_inadequadas_pct: float = Field(default=0.0, description="Moradias inadequadas (% da população)")
    sem_teto_100k: float = Field(default=0.0, description="Sem-teto por 100k habitantes")
    bombeiros_100k: float = Field(default=0.0, description="Bombeiros por 100k habitantes")
    mortes_incendio_100k: float = Field(default=0.0, description="Mortes por incêndio por 100k hab")
    agentes_policia_100k: float = Field(default=0.0, description="Agentes de polícia por 100k hab")
    homicidios_100k: float = Field(default=0.0, description="Homicídios por 100k habitantes")
    acidentes_industriais_100k: float = Field(default=0.0, description="Acidentes industriais por 100k hab")


class ISO37122Indicators(BaseModel):
    """ISO 37122 - Indicadores de Cidades Inteligentes (Smart Cities)
    
    Cobre: Economia smart, Educação, Energia, Ambiente, Saúde, Infraestrutura, Mobilidade
    Total de 15 indicadores
    """
    # Economia Smart e Educação (3 indicadores)
    sobrevivencia_novos_negocios_100k: float = Field(default=0.0, description="Novos negócios vigentes por 100k hab")
    empregos_tic_pct: float = Field(default=0.0, description="Empregos em TIC (% da força de trabalho)")
    graduados_stem_100k: float = Field(default=0.0, description="Graduados STEM por 100k habitantes")
    # Energia e Meio Ambiente (5 indicadores)
    energia_residuos_pct: float = Field(default=0.0, description="Energia de resíduos (% da energia total)")
    iluminacao_telegestao_pct: float = Field(default=0.0, description="Iluminação pública com telegestão (%)")
    medidores_inteligentes_energia_pct: float = Field(default=0.0, description="Medidores inteligentes de energia (%)")
    edificios_verdes_pct: float = Field(default=0.0, description="Edifícios verdes certificados (%)")
    monitoramento_ar_tempo_real_pct: float = Field(default=0.0, description="Monitoramento de ar em tempo real (%)")
    # Serviços e Saúde (3 indicadores)
    servicos_urbanos_online_pct: float = Field(default=0.0, description="Serviços urbanos online (%)")
    prontuario_eletronico_pct: float = Field(default=0.0, description="Prontuário eletrônico (% população)")
    consultas_remotas_100k: float = Field(default=0.0, description="Consultas remotas por 100k habitantes")
    # Infraestrutura e Mobilidade (4 indicadores)
    medidores_inteligentes_agua_pct: float = Field(default=0.0, description="Medidores inteligentes de água (%)")
    areas_cobertas_cameras_pct: float = Field(default=0.0, description="Áreas cobertas por câmeras (% da cidade)")
    lixeiras_sensores_pct: float = Field(default=0.0, description="Lixeiras com sensores (%)")
    semaforos_inteligentes_pct: float = Field(default=0.0, description="Semáforos inteligentes (%)")
    frota_onibus_limpos_pct: float = Field(default=0.0, description="Frota de ônibus zero emissão (%)")


class ISO37123AndSendaiIndicators(BaseModel):
    """ISO 37123 + Marco de Sendai - Indicadores de Resiliência e Gestão de Riscos
    
    Cobre: Resiliência econômica e social, Preparação para emergências, Proteção infraestrutura,
    Redução de riscos de desastres conforme Marco de Sendai 2015-2030
    Total de 16 indicadores
    """
    # Resiliência Econômica e Social (4 indicadores)
    seguro_ameacas_pct: float = Field(default=0.0, description="População coberta por seguro contra ameaças (%)")
    empregos_informais_pct: float = Field(default=0.0, description="Empregos informais (% da força de trabalho)")
    escolas_preparacao_emergencia_pct: float = Field(default=0.0, description="Escolas com plano de emergência (%)")
    populacao_treinada_emergencia_pct: float = Field(default=0.0, description="População treinada para emergência (%)")
    # Saúde e Preparação (3 indicadores)
    hospitais_geradores_backup_pct: float = Field(default=0.0, description="Hospitais com gerador backup (%)")
    seguro_saude_basico_pct: float = Field(default=0.0, description="População com seguro saúde básico (%)")
    imunizacao_pct: float = Field(default=0.0, description="Taxa de imunização (% população)")
    # Infraestrutura e Prevenção (5 indicadores)
    abrigos_emergencia_100k: float = Field(default=0.0, description="Abrigos de emergência por 100k habitantes")
    edificios_vulneraveis_pct: float = Field(default=0.0, description="Edifícios vulneráveis a desastres (%)")
    rotas_evacuacao_100k: float = Field(default=0.0, description="Rotas de evacuação identificadas por 100k")
    reservas_alimentos_72h_pct: float = Field(default=0.0, description="Cidades com reservas 72h de alimentos (%)")
    mapas_ameacas_publicos_pct: float = Field(default=0.0, description="Mapas de ameaças públicos e atualizados (%)")
    # Marco de Sendai - Redução de Riscos de Desastres (RRD) (4 indicadores)
    mortalidade_desastres_100k: float = Field(default=0.0, description="Mortalidade por desastres por 100k hab")
    pessoas_afetadas_desastres_100k: float = Field(default=0.0, description="Pessoas afetadas por desastres por 100k")
    perdas_desastres_pct_pib: float = Field(default=0.0, description="Perdas econômicas por desastres (% PIB)")
    danos_infraestrutura_basica_pct: float = Field(default=0.0, description="Danos à infraestrutura básica (%)")


# ==========================================
# SCHEMA DE INDICADORES MANUAIS (HÍBRIDO) - COMPLETO
# ==========================================
class ManualCityIndicators(BaseModel):
    """Indicadores manuais completos de uma cidade organizado por norma ISO
    
    Estrutura hierárquica para entrada de dados via AdminPage e TOPSIS.
    Total: 16 (ISO37120) + 15 (ISO37122) + 16 (ISO37123+Sendai) = 47 indicadores
    
    Todos os campos possuem default 0.0 para suportar dados parciais.
    """
    iso_37120: ISO37120Indicators = Field(
        default_factory=ISO37120Indicators, 
        description="Indicadores ISO 37120 - Cidades Sustentáveis e Resilientes"
    )
    iso_37122: ISO37122Indicators = Field(
        default_factory=ISO37122Indicators, 
        description="Indicadores ISO 37122 - Cidades Inteligentes"
    )
    iso_37123: ISO37123AndSendaiIndicators = Field(
        default_factory=ISO37123AndSendaiIndicators, 
        description="Indicadores ISO 37123 e Marco de Sendai - Resiliência"
    )

# Modelo de entrada híbrido: aceita código IBGE, nome da cidade e indicadores manuais
class CityHybridInput(BaseModel):
    """Schema para entrada de dados de cidades no endpoint TOPSIS híbrido.
    
    manual_indicators: Dict com 4 campos simples do frontend
    - pontos_iluminacao_telegestao (%)
    - medidores_inteligentes_energia (%)
    - bombeiros_por_100k (unidade)
    - area_verde_mapeada (%)
    
    Estes serão mapeados para a estrutura ISO 47-indicadores dentro do endpoint.
    """
    codigo_ibge: str  # Obrigatório
    nome_cidade: str  # Obrigatório
    manual_indicators: Optional[Dict[str, Any]] = None  # Dict simples do frontend

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
    receita_total: Optional[float] = 0.0  # NOVO: para independência financeira
    custo_servico_divida: float  # custo total do serviço da dívida de longo prazo
    despesas_capital: float  # total das despesas em ativos fixos
    despesas_operacionais: float  # total das despesas operacionais
    despesas_totais: float  # total das despesas (operacionais + capital)
    num_mulheres_eleitas: int
    total_cargos_gestao: int
    quantidade_hospitais: int = 0  # número de hospitais (opcional)
    # Campos manuais opcionais (para merge híbrido)
    pontos_iluminacao_telegestao: Optional[float] = 0.0
    medidores_inteligentes_energia: Optional[float] = 0.0
    bombeiros_por_100k: Optional[float] = 0.0
    area_verde_mapeada: Optional[float] = 0.0


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
    """Índice Smart (TOPSIS) de uma cidade.
    
    Retornado no ranking com:
    - nome_cidade: Nome da cidade conforme enviado no request
    - indice_smart: Valor de C_i calculado pelo TOPSIS (0.0 a 1.0)
    """
    nome_cidade: str  # Nome da cidade do request
    indice_smart: float  # valor de C_i (0.0 a 1.0)


class TOPSISResult(BaseModel):
    """Resultado completo do cálculo TOPSIS."""
    ranking: List[CitySmartIndex]  # ordenado por indice_smart descendente
    detalhes_calculo: dict  # informações adicionais para auditoria


# ==========================================
# DADOS MANUAIS - ARMAZENAMENTO
# ==========================================

class CityManualDataCreate(BaseModel):
    """Schema para criar/atualizar dados manuais de uma cidade
    
    Nota: codigo_ibge é passado como parâmetro da URL, não no corpo da requisição
    """
    nome_cidade: Optional[str] = None
    usuario_atualizou: Optional[str] = None
    dados: Optional[dict] = {}  # Aceita estrutura aninhada {pontos_iluminacao_telegestao, medidores_inteligentes_energia, ...}


class CityManualDataUpdate(BaseModel):
    """Schema para atualizar dados manuais de uma cidade (PATCH)
    
    Agora suporta 47 indicadores via ManualCityIndicators estruturado em JSON.
    Permite atualizações parciais de forma dinấmica.
    """
    dados: Optional[ManualCityIndicators] = None
    usuario_atualizou: Optional[str] = None
    motivo_atualizacao: Optional[str] = None


class CityManualDataResponse(BaseModel):
    """Response com dados manuais atuais de uma cidade (47 indicadores ISO em JSON)"""
    id: int
    codigo_ibge: str
    nome_cidade: Optional[str]
    indicadores_manuais: dict  # 47 indicadores estruturados em JSON
    fonte: str
    usuario_atualizou: Optional[str]
    data_criacao: datetime
    data_atualizacao: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# HISTÓRICO DE ALTERAÇÕES - AUDITORIA
# ==========================================

class ManualDataHistoryResponse(BaseModel):
    """Response com histórico de alterações dos dados manuais"""
    id: int
    codigo_ibge: str
    dados_antigos: Optional[Dict[str, Any]]
    dados_novos: Optional[Dict[str, Any]]
    alteracoes_resumo: str
    usuario_atualizou: Optional[str]
    motivo_atualizacao: Optional[str]
    data_alteracao: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SÉRIE HISTÓRICA - INDICADORES
# ==========================================

class IndicatorSnapshotResponse(BaseModel):
    """Response com snapshot de indicadores de um ponto no tempo (47 indicadores ISO em JSON)"""
    id: int
    codigo_ibge: str
    valores_indicadores: dict  # 47 indicadores como lista de floats em JSON
    data_calculo: datetime
    fonte_dados: str  # "apis", "manual", "hibrido"
    periodo_referencia: str
    
    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SÉRIE HISTÓRICA - RANKINGS
# ==========================================

class RankingSnapshotResponse(BaseModel):
    """Response com snapshot de ranking de um ponto no tempo"""
    id: int
    ranking_data: List[Dict[str, Any]]
    data_calculo: datetime
    periodo_referencia: str
    quantidade_cidades: int
    
    model_config = ConfigDict(from_attributes=True)