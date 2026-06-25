"""
Simple API Data Inspector - Shows what APIs actually return
"""

import asyncio
import json
import logging
from app.services.external_apis import (
    get_siconfi_finances,
    get_ibge_population,
    get_datasus_health_infrastructure,
    get_inep_education,
)

# Suppress debug logging
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def main():
    codigo_ibge = "4101408"
    nome_cidade = "Apucarana"
    
    print(f"\n{'='*80}")
    print(f"API DATA INSPECTION: {nome_cidade} ({codigo_ibge})")
    print(f"{'='*80}\n")
    
    # Test SICONFI
    print("1. SICONFI (Financas)")
    print("-" * 80)
    try:
        siconfi = await get_siconfi_finances(codigo_ibge)
        print(json.dumps(siconfi, indent=2, default=str))
        print(f"\nStatus: DC={siconfi.get('divida_consolidada')}, Receita Total={siconfi.get('receita_total')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test IBGE
    print("\n\n2. IBGE (Populacao)")
    print("-" * 80)
    try:
        ibge = await get_ibge_population(codigo_ibge)
        print(f"Resultado: {ibge}")
        print(f"Tipo: {type(ibge)}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test DataSUS
    print("\n\n3. DataSUS (CNES)")
    print("-" * 80)
    try:
        datasus = await get_datasus_health_infrastructure(codigo_ibge)
        print(json.dumps(datasus, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")
    
    # Test INEP
    print("\n\n4. INEP (Educacao)")
    print("-" * 80)
    try:
        inep = await get_inep_education(codigo_ibge)
        print(json.dumps(inep, indent=2, default=str))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
