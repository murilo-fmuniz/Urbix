from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.indicadores import indicators_router
from app.database import get_db

app = FastAPI()

# ==========================================
# CORS MIDDLEWARE
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(indicators_router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"message": "Welcome to the Urbix API!"}

