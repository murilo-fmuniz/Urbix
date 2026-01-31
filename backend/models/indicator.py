"""Modelos de Indicadores"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


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
