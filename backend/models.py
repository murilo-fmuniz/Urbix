from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class State(Base):
    """Tabela de estados brasileiros"""
    __tablename__ = 'states'
    
    id = Column(Integer, primary_key=True)
    ibge_code = Column(String(2), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    abbreviation = Column(String(2), nullable=False, unique=True)
    region = Column(String(50))  # Norte, Nordeste, Centro-Oeste, Sudeste, Sul
    
    # Relacionamentos
    cities = relationship('City', back_populates='state', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<State(name='{self.name}', abbreviation='{self.abbreviation}')>"


class City(Base):
    """Tabela de cidades"""
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    ibge_code = Column(String(7), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    state_id = Column(Integer, ForeignKey('states.id'), nullable=False)
    country = Column(String(100), default='Brasil')
    
    # Dados geográficos
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Dados demográficos
    population = Column(Integer)
    area_km2 = Column(Float)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    state = relationship('State', back_populates='cities')
    indicators = relationship('CityIndicator', back_populates='city', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<City(name='{self.name}', ibge_code='{self.ibge_code}')>"


class IndicatorCategory(Base):
    """Categorias de indicadores"""
    __tablename__ = 'indicator_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    color = Column(String(7))  # Hex color code
    
    # Relacionamentos
    indicators = relationship('Indicator', back_populates='category')
    
    def __repr__(self):
        return f"<IndicatorCategory(name='{self.name}')>"


class Indicator(Base):
    """Definições dos indicadores"""
    __tablename__ = 'indicators'
    
    id = Column(Integer, primary_key=True)
    iso_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Categoria
    category_id = Column(Integer, ForeignKey('indicator_categories.id'))
    
    # Unidade de medida
    unit = Column(String(50))  # %, km², pessoas, etc.
    
    # Configurações
    target_value = Column(Float)  # Valor alvo/meta
    is_higher_better = Column(Boolean, default=True)  # True se valor maior é melhor
    
    # Fonte de dados
    data_source = Column(String(200))  # IBGE, DATASUS, etc.
    data_source_url = Column(Text)
    
    # Metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    category = relationship('IndicatorCategory', back_populates='indicators')
    city_values = relationship('CityIndicator', back_populates='indicator', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Indicator(iso_code='{self.iso_code}', name='{self.name}')>"


class CityIndicator(Base):
    """Valores dos indicadores por cidade"""
    __tablename__ = 'city_indicators'
    
    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id'), nullable=False)
    indicator_id = Column(Integer, ForeignKey('indicators.id'), nullable=False)
    
    # Valor do indicador
    value = Column(Float, nullable=False)
    
    # Período de referência
    year = Column(Integer)
    reference_date = Column(DateTime)
    
    # Metadados
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    data_quality = Column(String(20))  # 'excellent', 'good', 'fair', 'poor'
    notes = Column(Text)
    
    # Relacionamentos
    city = relationship('City', back_populates='indicators')
    indicator = relationship('Indicator', back_populates='city_values')
    
    def __repr__(self):
        return f"<CityIndicator(city_id={self.city_id}, indicator_id={self.indicator_id}, value={self.value})>"


class ApiSyncLog(Base):
    """Log de sincronizações com APIs externas"""
    __tablename__ = 'api_sync_logs'
    
    id = Column(Integer, primary_key=True)
    api_name = Column(String(100), nullable=False)  # 'IBGE', 'DATASUS', etc.
    endpoint = Column(String(500))
    
    # Status da sincronização
    status = Column(String(20), nullable=False)  # 'success', 'error', 'partial'
    records_processed = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Detalhes
    error_message = Column(Text)
    execution_time_seconds = Column(Float)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ApiSyncLog(api_name='{self.api_name}', status='{self.status}')>"
