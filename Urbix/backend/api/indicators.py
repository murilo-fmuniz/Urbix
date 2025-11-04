from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from database import db

router = APIRouter()

class IndicatorBase(BaseModel):
    name: str = Field(..., description="Nome do indicador")
    category: str = Field(..., description="Categoria do indicador")
    value: float = Field(..., description="Valor atual do indicador")
    target: float = Field(..., description="Meta do indicador")
    description: Optional[str] = Field(None, description="Descrição detalhada do indicador")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Qualidade da Água",
                "category": "Ambiental",
                "value": 85,
                "target": 90,
                "description": "Índice de qualidade da água potável"
            }
        }
    }

class Indicator(IndicatorBase):
    id: int = Field(..., description="ID único do indicador")

@router.get("/indicators", response_model=List[Indicator])
async def get_indicators():
    return db.get_all_indicators()

@router.get("/indicators/{indicator_id}", response_model=Indicator)
async def get_indicator(indicator_id: int):
    indicator = db.get_indicator_by_id(indicator_id)
    if not indicator:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return indicator

@router.post("/indicators", response_model=Indicator)
async def create_indicator(indicator: IndicatorBase):
    return db.add_indicator(indicator.dict())