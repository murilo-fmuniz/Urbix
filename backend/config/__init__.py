"""Módulo de configuração do Urbix Backend"""
from .database import (
    engine,
    SessionLocal,
    init_db,
    drop_all_tables,
    get_db,
    get_db_session,
    get_db_dependency,
    DATABASE_URL
)

__all__ = [
    'engine',
    'SessionLocal',
    'init_db',
    'drop_all_tables',
    'get_db',
    'get_db_session',
    'get_db_dependency',
    'DATABASE_URL'
]
