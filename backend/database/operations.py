"""
Database operations using SQLAlchemy ORM
Provides high-level functions for common database operations
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from models import (
    City, State, Indicator, IndicatorCategory, 
    CityIndicator, ApiSyncLog
)


# ==================== CITY OPERATIONS ====================

def get_all_cities(db: Session, skip: int = 0, limit: int = 100) -> List[City]:
    """Retorna todas as cidades com paginação"""
    return db.query(City).offset(skip).limit(limit).all()


def get_city_by_id(db: Session, city_id: int) -> Optional[City]:
    """Retorna uma cidade por ID"""
    return db.query(City).filter(City.id == city_id).first()


def get_city_by_ibge_code(db: Session, ibge_code: str) -> Optional[City]:
    """Retorna uma cidade pelo código IBGE"""
    return db.query(City).filter(City.ibge_code == ibge_code).first()


def search_cities(db: Session, query: str, limit: int = 20) -> List[City]:
    """Busca cidades por nome"""
    search_pattern = f"%{query}%"
    return db.query(City).filter(
        City.name.ilike(search_pattern)
    ).limit(limit).all()


# ==================== INDICATOR OPERATIONS ====================

def get_all_indicators(db: Session) -> List[Indicator]:
    """Retorna todos os indicadores"""
    return db.query(Indicator).options(
        joinedload(Indicator.category)
    ).all()


def get_indicator_by_id(db: Session, indicator_id: int) -> Optional[Indicator]:
    """Retorna um indicador por ID"""
    return db.query(Indicator).options(
        joinedload(Indicator.category)
    ).filter(Indicator.id == indicator_id).first()


def get_indicator_by_iso_code(db: Session, iso_code: str) -> Optional[Indicator]:
    """Retorna um indicador pelo código ISO"""
    return db.query(Indicator).filter(
        Indicator.iso_code == iso_code
    ).first()


def get_indicators_by_category(db: Session, category_name: str) -> List[Indicator]:
    """Retorna indicadores de uma categoria específica"""
    return db.query(Indicator).join(IndicatorCategory).filter(
        IndicatorCategory.name == category_name
    ).all()


# ==================== CITY INDICATOR OPERATIONS ====================

def get_city_indicators(db: Session, city_id: int) -> List[CityIndicator]:
    """Retorna todos os indicadores de uma cidade"""
    return db.query(CityIndicator).options(
        joinedload(CityIndicator.indicator).joinedload(Indicator.category)
    ).filter(CityIndicator.city_id == city_id).all()


def get_indicator_for_city(
    db: Session, 
    city_id: int, 
    indicator_id: int
) -> Optional[CityIndicator]:
    """Retorna um indicador específico de uma cidade"""
    return db.query(CityIndicator).filter(
        and_(
            CityIndicator.city_id == city_id,
            CityIndicator.indicator_id == indicator_id
        )
    ).first()


def upsert_city_indicator(
    db: Session,
    city_id: int,
    indicator_id: int,
    value: float,
    **kwargs
) -> CityIndicator:
    """Insere ou atualiza um indicador de cidade"""
    existing = get_indicator_for_city(db, city_id, indicator_id)
    
    if existing:
        # Atualizar
        existing.value = value
        for key, val in kwargs.items():
            if hasattr(existing, key):
                setattr(existing, key, val)
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # Inserir
        new_indicator = CityIndicator(
            city_id=city_id,
            indicator_id=indicator_id,
            value=value,
            **kwargs
        )
        db.add(new_indicator)
        db.commit()
        db.refresh(new_indicator)
        return new_indicator


# ==================== CATEGORY OPERATIONS ====================

def get_all_categories(db: Session) -> List[IndicatorCategory]:
    """Retorna todas as categorias de indicadores"""
    return db.query(IndicatorCategory).all()


def get_category_by_name(db: Session, name: str) -> Optional[IndicatorCategory]:
    """Retorna uma categoria pelo nome"""
    return db.query(IndicatorCategory).filter(
        IndicatorCategory.name == name
    ).first()


# ==================== STATISTICS ====================

def get_city_statistics(db: Session, city_id: int) -> Dict[str, Any]:
    """Retorna estatísticas dos indicadores de uma cidade"""
    indicators = get_city_indicators(db, city_id)
    
    if not indicators:
        return {
            'total_indicators': 0,
            'average_value': 0,
            'categories': {}
        }
    
    # Calcular estatísticas por categoria
    categories = {}
    for ci in indicators:
        cat_name = ci.indicator.category.name if ci.indicator.category else 'Sem categoria'
        if cat_name not in categories:
            categories[cat_name] = {
                'count': 0,
                'total': 0,
                'average': 0
            }
        categories[cat_name]['count'] += 1
        categories[cat_name]['total'] += ci.value
    
    # Calcular médias
    for cat in categories.values():
        cat['average'] = cat['total'] / cat['count']
    
    return {
        'total_indicators': len(indicators),
        'average_value': sum(ci.value for ci in indicators) / len(indicators),
        'categories': categories
    }
