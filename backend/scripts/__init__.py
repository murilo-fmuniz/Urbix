"""Scripts utilitários do Urbix Backend"""
from .init_database import main as init_database
from .migrate_data import DataMigrator, run_migration

__all__ = [
    'init_database',
    'DataMigrator',
    'run_migration'
]
