from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os


load_dotenv()  # Carrega variáveis de ambiente do arquivo .env
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./urbix.db")

is_sqlite = SQLALCHEMY_DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args=connect_args
)
# Cria a fábrica de sessões do banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A classe Base que o models.py estava sentindo falta!
Base = declarative_base()


def _is_sqlite() -> bool:
    return SQLALCHEMY_DATABASE_URL.startswith("sqlite")


def ensure_sqlite_optimizations(create_indexes: bool = False) -> None:
    """Aplica PRAGMAs e, opcionalmente, índices de apoio para reduzir latência no SQLite."""
    if not _is_sqlite():
        return

    try:
        with engine.begin() as conn:
            # Melhor concorrência/leitura para API (especialmente com ETL pesado).
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA temp_store=MEMORY"))

            if not create_indexes:
                return

            # Índice composto para seleção do registro mais recente por cidade+indicador.
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS ix_vi_cidade_indicador_ano_id
                ON valores_indicadores (codigo_ibge, id_indicador, ano_referencia DESC, id DESC)
                """
            ))

            # Índices auxiliares para busca de cidades e junções de ranking.
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS ix_vi_cidade_indicador
                ON valores_indicadores (codigo_ibge, id_indicador)
                """
            ))
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS ix_municipios_nome
                ON municipios (nome)
                """
            ))
            conn.execute(text(
                """
                CREATE INDEX IF NOT EXISTS ix_municipios_estado
                ON municipios (estado)
                """
            ))
    except OperationalError:
        # Em contexto sem tabelas (ex.: bootstrap inicial), segue normalmente.
        return

# Dependência para injetar o banco de dados nas rotas do FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()