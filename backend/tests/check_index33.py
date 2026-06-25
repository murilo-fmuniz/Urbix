#!/usr/bin/env python
import sys
sys.path.insert(0, '/d:/Docs/Faculdade/IC/Urbix/backend')

from app.database import SessionLocal
from app.models import CityManualData
from app.routers.topsis import flatten_manual_indicators

db = SessionLocal()

# Load Apucarana from database
city = db.query(CityManualData).filter_by(codigo_ibge="4101408").first()
if city:
    from app.schemas import ManualCityIndicators
    
    # Convert dict to Pydantic model
    manual = ManualCityIndicators.model_validate(city.indicadores_manuais)
    
    # Flatten
    flat = flatten_manual_indicators(manual)
    
    # Find non-zero indices
    non_zero = [(i, v) for i, v in enumerate(flat) if v != 0]
    
    print("Índices com dados (não-zero):")
    for idx, val in non_zero:
        print(f"  [{idx:2d}] {val:.4f}")
    
    print(f"\nTotal: {len(non_zero)}/50 = {len(non_zero)/50*100:.1f}%")
    
    # Check index 33 specifically
    print(f"\nÍndice 33 (escolas_conectadas_pct): {flat[33]:.4f}")
else:
    print("Cidade não encontrada")

db.close()
