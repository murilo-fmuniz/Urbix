from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

# Cria a rota raiz para os indicadores
router = APIRouter(prefix="/indicadores", tags=["Indicadores"])

@router.get("/", response_model=List[schemas.Indicador])
def listar_indicadores(db: Session = Depends(get_db)):
    """
    Retorna a lista de todos os indicadores cadastrados no banco,
    incluindo seus Pesos e Impactos, ordenados por nome.
    Ideal para preencher os quadros descritivos no React.
    """
    # Consulta todos os indicadores e ordena alfabeticamente
    indicadores = db.query(models.Indicador).order_by(models.Indicador.nome.asc()).all()
    return indicadores