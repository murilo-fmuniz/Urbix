"""
Urbix Backend API
API para análise de indicadores de Cidades Sustentáveis
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import indicators

app = FastAPI(
    title="Urbix API",
    description="API para análise de indicadores de Cidades Sustentáveis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(indicators.router, prefix="/api", tags=["indicators"])


@app.get("/")
async def root():
    """Root endpoint - retorna informações da API"""
    return {
        "message": "Bem-vindo à API do Urbix!",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}