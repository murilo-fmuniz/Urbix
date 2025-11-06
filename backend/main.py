from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import indicators

app = FastAPI(title="Urbix API",
             description="API para análise de indicadores de Cidades Sustentáveis")

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
    return {"message": "Bem-vindo à API do Urbix!"}