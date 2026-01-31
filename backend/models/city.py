"""Modelo de Cidades"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


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
