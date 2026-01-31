"""Modelo de Estados brasileiros"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


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
