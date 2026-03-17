from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, Date, event
from sqlalchemy.orm import relationship, declarative_base
from app.utils import normalize_indicator_code, normalize_city_name, normalize_state, normalize_comparison_value

Base = declarative_base()

class Indicador(Base):
    __tablename__ = 'indicadores'

    id = Column(Integer, primary_key=True, index=True)
    codigo_indicador = Column(String, unique=True, index=True)
    nome = Column(String)
    norma = Column(String)
    grande_area = Column(String)
    eixo = Column(String)
    tipo = Column(String)
    descricao = Column(Text)

    # Relacionamentos
    metodologia = relationship("Metodologia", back_populates="indicador", uselist=False, cascade="all, delete-orphan")
    dados_coleta = relationship("DadosColeta", back_populates="indicador", cascade="all, delete-orphan")


class Metodologia(Base):
    __tablename__ = 'metodologias'

    id = Column(Integer, primary_key=True, index=True)
    indicador_id = Column(Integer, ForeignKey('indicadores.id'))
    desc_numerador = Column(Text)
    desc_denominador = Column(Text)
    multiplicador = Column(Float)
    unidade_medida = Column(String)

    indicador = relationship("Indicador", back_populates="metodologia")


class DadosColeta(Base):
    __tablename__ = 'dados_coleta'

    id = Column(Integer, primary_key=True, index=True)
    indicador_id = Column(Integer, ForeignKey('indicadores.id'))
    cidade = Column(String, index=True)
    estado = Column(String)
    ano_referencia = Column(Integer)
    valor_numerador = Column(Float, nullable=True)
    valor_denominador = Column(Float, nullable=True)
    valor_final = Column(Float, nullable=True)
    dado_disponivel = Column(Boolean, default=False)

    indicador = relationship("Indicador", back_populates="dados_coleta")
    auditoria = relationship("Auditoria", back_populates="dados_coleta", uselist=False, cascade="all, delete-orphan")


class Auditoria(Base):
    __tablename__ = 'auditorias'

    id = Column(Integer, primary_key=True, index=True)
    dados_coleta_id = Column(Integer, ForeignKey('dados_coleta.id'))
    fonte_nome = Column(String)
    fonte_url = Column(String, nullable=True)
    data_extracao = Column(Date, nullable=True)
    observacoes = Column(Text, nullable=True)

    dados_coleta = relationship("DadosColeta", back_populates="auditoria")


# ==========================================
# EVENT LISTENERS - Normalização automática
# ==========================================

@event.listens_for(Indicador, 'before_insert')
@event.listens_for(Indicador, 'before_update')
def normalize_indicador(mapper, connection, target):
    """Normaliza campos do Indicador antes de inserir/atualizar"""
    if target.codigo_indicador:
        target.codigo_indicador = normalize_indicator_code(target.codigo_indicador)


@event.listens_for(DadosColeta, 'before_insert')
@event.listens_for(DadosColeta, 'before_update')
def normalize_dados_coleta(mapper, connection, target):
    """Normaliza campos de DadosColeta antes de inserir/atualizar"""
    if target.cidade:
        target.cidade = normalize_city_name(target.cidade)
    if target.estado:
        target.estado = normalize_state(target.estado)