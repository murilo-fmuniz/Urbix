from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import topsis, indicadores # <-- 1. ADICIONEI O INDICADORES AQUI
from app.database import Base, engine, ensure_sqlite_optimizations

app = FastAPI(
    title="Urbix API - Offline Engine",
    description="Motor matemático TOPSIS para análise de Smart Cities",
    version="2.0.0"
)

# Configuração de CORS (Permite que o React na porta 5173 converse com o FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrando apenas a rota do Cérebro Matemático
app.include_router(topsis.router)
app.include_router(indicadores.router) # <-- 2. TIREI O COMENTÁRIO DESTA LINHA


@app.on_event("startup")
def startup_database_tuning():
    """Garante tabelas e otimizações de banco antes de atender requisições."""
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_optimizations(create_indexes=True)

@app.get("/")
def read_root():
    return {
        "status": "online", 
        "message": "Urbix Engine está operando em modo offline e blindado."
    }