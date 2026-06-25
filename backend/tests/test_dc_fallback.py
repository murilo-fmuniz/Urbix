#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify DC fallback is working
"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.services.external_apis import get_siconfi_finances

async def main():
    print("\n" + "="*80)
    print("TESTING DC FALLBACK (RGF Empty -> Use FALLBACK_SICONFI)")
    print("="*80)
    
    result = await get_siconfi_finances('4101408')
    
    print("\nSICONFI Result for Apucarana (4101408):")
    print(f"  DC (divida_consolidada): R$ {result.get('divida_consolidada'):,.2f}")
    print(f"  Receita Total: R$ {result.get('receita_total'):,.2f}")
    print(f"  Receita Propria: R$ {result.get('receita_propria'):,.2f}")
    print(f"  Fonte: {result.get('fonte')}")
    print(f"  Fonte DC: {result.get('fonte_dc', 'N/A')}")
    
    if result.get('divida_consolidada', 0) > 0:
        print("\n[SUCCESS] DC fallback is working!")
    else:
        print("\n[FAILED] DC is still 0.0")

if __name__ == "__main__":
    asyncio.run(main())
