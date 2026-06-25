#!/usr/bin/env python
"""Teste rápido para verificar indicadores [28-32] após injeção"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.routers.topsis import processar_cidade_real
from app.models import CityManualData
from sqlalchemy.orm import Session
from app.database import SessionLocal

async def test_indices_28_32():
    print("\n" + "="*70)
    print("[TEST] Verificar injecao dos indicadores [28-32] (DataSUS Expandido)")
    print("="*70)
    
    db = SessionLocal()
    try:
        # Get Apucarana data
        city = db.query(CityManualData).filter(
            CityManualData.codigo_ibge == "4101408"
        ).first()
        
        if not city:
            print("[ERROR] Apucarana nao encontrada no banco")
            return
        
        print(f"\n[INFO] Processando: Apucarana (IBGE: 4101408)")
        
        # Process the city
        result = await processar_cidade_real(
            codigo_ibge="4101408",
            nome_cidade="Apucarana",
            db=db
        )
        
        print(f"\n[SUCCESS] Resultado do processamento:")
        print(f"   Total de indicadores: {len(result.get('indicadores_flatalizados', []))}")
        
        # Check indices 28-32
        indicators = result.get("indicadores_flatalizados", [])
        print(f"\n[DATA] Indicadores [28-32] (DataSUS Expandido):")
        print(f"   [28] Hospitais/100k hab: {indicators[28]:.2f}")
        print(f"   [29] Leitos UTI (%):     {indicators[29]:.2f}")
        print(f"   [30] Vacina COVID (%):   {indicators[30]:.2f}")
        print(f"   [31] Atencao Basica (%): {indicators[31]:.2f}")
        print(f"   [32] Agentes Comunitarios: {indicators[32]:.0f}")
        
        # Check if any are > 0 (success condition)
        filled_count = sum(1 for i in [28, 29, 30, 31, 32] if indicators[i] > 0)
        print(f"\n[STATUS] Indicadores preenchidos: {filled_count}/5")
        
        if filled_count >= 3:
            print("[SUCCESS] Pelo menos 3 indicadores foram injetados!")
        else:
            print("[WARNING] Menos de 3 indicadores foram injetados")
        
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_indices_28_32())
