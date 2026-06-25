from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from app.routers.indicadores import indicators_router
from app.routers.topsis import topsis_router
from app.routers.manual_data import manual_data_router
from app.routers.local_data import municipios_router
from app.database import get_db, engine
from app.models import Base
from app.services.demo_city_seed import seed_demo_city
from app.database import SessionLocal

app = FastAPI(
    title="Urbix API",
    description="API para cálculo de indicadores Smart Cities e análise TOPSIS",
    version="2.0.0",
)

# ==========================================
# CORS MIDDLEWARE
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Development
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        # Production (Vercel)
        "https://urbix.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# ROUTERS
# ==========================================
app.include_router(indicators_router, prefix="/api/v1")
app.include_router(topsis_router, prefix="/api/v1")
app.include_router(manual_data_router, prefix="/api/v1")
app.include_router(municipios_router, prefix="/api/v1/municipio")


@app.on_event("startup")
def startup_db_and_seed():
    """Garante tabelas e cria a cidade fictícia UTFPRCity para testes."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_city(db)
    finally:
        db.close()


@app.get("/api/v1/health")
async def health():
    """
    Health check endpoint - returns API status and timestamp.
    
    Returns:
        {
            "status": "healthy",
            "timestamp": "2024-01-15T10:30:00.000000",
            "version": "2.0.0",
            "service": "Urbix API"
        }
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "Urbix API",
        "endpoints": {
            "ranking": "/api/v1/topsis/ranking-hibrido",
            "cities": "/api/v1/topsis/cities",
            "indicators": "/api/v1/topsis/indicators",
            "snapshots": "/api/v1/topsis/snapshots/{codigo_ibge}"
        }
    }


@app.get("/")
async def root():
    return {"message": "Welcome to the Urbix API!"}

