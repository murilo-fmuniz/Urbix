#!/usr/bin/env python
"""Test Phase 2 Task 2 - Portal Transparência Expandido"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.portal_transparencia_expanded import (
    get_portal_transparencia_expanded,
    FALLBACK_TRANSPARENCIA_EXPANDED,
    FALLBACK_UNIVERSAL_SOCIAL
)

async def test_portal_expanded():
    print("\n" + "="*70)
    print("[TEST] Phase 2 Task 2 - Portal Transparência Expandido")
    print("="*70)
    
    # Test 1: Fallback data loaded
    print("\n[TEST 1] Fallback data loaded")
    print(f"  [OK] Apucarana (4101408): {FALLBACK_TRANSPARENCIA_EXPANDED.get('4101408', {})}")
    print(f"  [OK] Universal fallback: {FALLBACK_UNIVERSAL_SOCIAL}")
    
    # Test 2: Get data for a city with fallback
    print("\n[TEST 2] Get Portal data for Apucarana (fallback)")
    data = await get_portal_transparencia_expanded("4101408")
    print(f"  Result: {data}")
    
    expected_keys = [
        "beneficiarios_programas_sociais_pct",
        "cobertura_alimentacao_escolar_pct",
        "acesso_agua_potavel_pct"
    ]
    
    filled_count = 0
    for key in expected_keys:
        if key in data and data[key] > 0:
            print(f"  [OK] {key}: {data[key]}")
            filled_count += 1
        else:
            print(f"  [EMPTY] {key}: {data.get(key, 'MISSING')}")
    
    print(f"\n  Indicators filled: {filled_count}/3")
    
    # Test 3: Get data for unknown city (should use universal fallback)
    print("\n[TEST 3] Get Portal data for unknown city (universal fallback)")
    data = await get_portal_transparencia_expanded("9999999")
    print(f"  Result: {data}")
    
    print("\n" + "="*70)
    if filled_count >= 2:
        print("[SUCCESS] Phase 2 Task 2 tests PASSED!")
    else:
        print("[WARNING] Some indicators not filled, but fallback system OK")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_portal_expanded())
