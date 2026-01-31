"""
Configuração do banco de dados com suporte para SQLite e PostgreSQL
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from typing import Generator

from models.base import Base

# Configuração do banco de dados
DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'sqlite:///./data/urbix.db'  # SQLite por padrão
)

# Para PostgreSQL em produção, use:
# DATABASE_URL = 'postgresql://user:password@localhost:5432/urbix'

# Criar engine
engine = create_engine(
    DATABASE_URL,
    # Configurações específicas para SQLite
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # True para debug SQL
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Inicializa o banco de dados, criando todas as tabelas"""
    Base.metadata.create_all(bind=engine)
    print("✓ Banco de dados inicializado com sucesso!")


def drop_all_tables():
    """Remove todas as tabelas - CUIDADO: usa apenas para desenvolvimento"""
    Base.metadata.drop_all(bind=engine)
    print("✓ Todas as tabelas foram removidas!")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager para obter uma sessão do banco de dados
    
    Usage:
        with get_db() as db:
            users = db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Retorna uma nova sessão do banco de dados
    Use em FastAPI com Depends
    
    Usage:
        def get_users(db: Session = Depends(get_db_session)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # A sessão será fechada pelo FastAPI


# Para uso com FastAPI Dependency Injection
def get_db_dependency():
    """Dependency para FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
