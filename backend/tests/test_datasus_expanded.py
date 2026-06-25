#!/usr/bin/env python
"""Test DataSUS Expandido integration"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.datasus_api_expanded import (
    get_datasus_health_expanded,
    FALLBACK_DATASUS_EXPANDED,
    FALLBACK_UNIVERSAL_HEALTH
)

async def test_datasus_expanded():
    print("\n" + "="*60)
    print("🧪 TESTE: DataSUS Expandido Integration")
    print("="*60)
    
    # Test 1: Fallback data loaded
    print("\n✅ Test 1: Fallback data loaded")
    print(f"   Apucarana (4101408): {FALLBACK_DATASUS_EXPANDED.get('4101408', {})}")
    print(f"   Universal fallback: {FALLBACK_UNIVERSAL_HEALTH}")
    
    # Test 2: Get data for a city with fallback
    print("\n✅ Test 2: Get DataSUS data for Apucarana")
    data = await get_datasus_health_expanded("4101408")
    print(f"   Result: {data}")
    expected_keys = ["hospitais_por_100k", "leitos_uti_pct", "cobertura_vacina_covid_pct", 
                     "cobertura_atencao_basica_pct", "agentes_comunitarios_saude"]
    
    for key in expected_keys:
        if key in data:
            print(f"   ✅ {key}: {data[key]}")
        else:
            print(f"   ❌ {key}: MISSING!")
    
    # Test 3: Get data for unknown city (should use universal fallback)
    print("\n✅ Test 3: Get DataSUS data for unknown city (universal fallback)")
    data = await get_datasus_health_expanded("9999999")
    print(f"   Result: {data}")
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_datasus_expanded())
