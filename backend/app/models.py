from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Text, Date, DateTime, JSON, event
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
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
# DADOS MANUAIS - ARMAZENAMENTO PERSISTENTE
# ==========================================

class CityManualData(Base):
    """Dados manuais mais recentes de cada cidade (47 indicadores ISO em JSON)"""
    __tablename__ = "city_manual_data"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(String, unique=True, index=True, nullable=False)
    nome_cidade = Column(String, nullable=True)
    
    # Indicadores manuais - Estrutura JSON para suportar 47 indicadores dinamicamente
    # Formato: {"iso_37120": {...}, "iso_37122": {...}, "iso_37123": {...}}
    # Facilita migração futura SQLite → PostgreSQL com melhor suporte a JSONB
    indicadores_manuais = Column(JSON, default=dict)
    
    # Metadados
    fonte = Column(String, default="prefeitura")
    usuario_atualizou = Column(String, nullable=True)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    historico = relationship("CityManualDataHistory", back_populates="dados_atuais", cascade="all, delete-orphan")
    snapshots_indicadores = relationship("IndicatorSnapshot", back_populates="cidade_manual", cascade="all, delete-orphan")


class CityManualDataHistory(Base):
    """Histórico completo de alterações nos dados manuais (auditoria)"""
    __tablename__ = "city_manual_data_history"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(String, ForeignKey("city_manual_data.codigo_ibge"), index=True)
    
    # Dados antes e depois (JSONB para flexibilidade)
    dados_antigos = Column(JSON, nullable=True)
    dados_novos = Column(JSON, nullable=True)
    
    # Resumo legível das mudanças
    alteracoes_resumo = Column(Text)
    
    # Auditoria
    usuario_atualizou = Column(String, nullable=True)
    motivo_atualizacao = Column(String, nullable=True)
    data_alteracao = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamento
    dados_atuais = relationship("CityManualData", back_populates="historico")


# ==========================================
# SÉRIE HISTÓRICA - INDICADORES
# ==========================================

class IndicatorSnapshot(Base):
    """Captura de indicadores calculados em um ponto no tempo (47 indicadores ISO em JSON)"""
    __tablename__ = "indicator_snapshot"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(String, ForeignKey("city_manual_data.codigo_ibge"), index=True)
    
    # Valores dos indicadores - JSON para suportar 47 indicadores dinamicamente
    # Formato: Lista de 47 floats ordenados conforme ISO 37120/37122/37123
    # Exemplo: [taxa_desemprego, taxa_endividamento, ..., danos_infraestrutura_basica]
    valores_indicadores = Column(JSON, nullable=False)
    
    # Metadados
    data_calculo = Column(DateTime, default=datetime.utcnow, index=True)
    fonte_dados = Column(String)  # "apis", "manual", "hibrido"
    periodo_referencia = Column(String)
    
    # Relacionamento
    cidade_manual = relationship("CityManualData", back_populates="snapshots_indicadores")


# ==========================================
# SÉRIE HISTÓRICA - RANKINGS
# ==========================================

class RankingSnapshot(Base):
    """Captura de ranking TOPSIS em um ponto no tempo"""
    __tablename__ = "ranking_snapshot"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Lista de cidades no ranking (JSONB)
    ranking_data = Column(JSON)
    
    # Matriz de decisão usada
    matriz_decisao = Column(JSON)
    indicadores_nomes = Column(JSON)
    pesos = Column(JSON)
    impactos = Column(JSON)
    
    # Metadados
    data_calculo = Column(DateTime, default=datetime.utcnow, index=True)
    periodo_referencia = Column(String, index=True)
    quantidade_cidades = Column(Integer)


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