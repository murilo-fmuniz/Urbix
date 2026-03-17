"""
Configuração de banco de dados com suporte a SQLite e PostgreSQL.

Variáveis de ambiente:
- DATABASE_URL: URL completa do banco de dados
  - SQLite (padrão): sqlite:///./urbix.db
  - PostgreSQL: postgresql://user:password@localhost:5432/urbix

Exemplo:
  export DATABASE_URL="postgresql://postgres:password@localhost:5432/urbix"
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Obtém URL do banco do .env ou usa SQLite por padrão
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./urbix.db")

# Configurações específicas por tipo de banco
engine_kwargs = {
    "connect_args": {"check_same_thread": False}  # Necessário apenas para SQLite
}

# Se for PostgreSQL, remove connect_args pois não é necessário
if DATABASE_URL.startswith("postgresql"):
    engine_kwargs = {}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency injection para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

