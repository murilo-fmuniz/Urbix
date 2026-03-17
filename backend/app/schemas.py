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