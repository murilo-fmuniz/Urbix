"""
Debug SICONFI RGF API Response - See what data is actually returned
"""

import asyncio
import httpx
import json

async def inspect_siconfi_rgf():
    """Query SICONFI RGF directly to see response structure"""
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"
    
    params = {
        "id_ente": "4101408",  # Apucarana
        "an_exercicio": 2023,
        "in_periodicidade": "Q",
        "nr_periodo": 3,
        "co_tipo_demonstrativo": "RGF",
        "no_anexo": "RGF-Anexo 02",
    }
    
    print("Querying SICONFI RGF endpoint...")
    print(f"URL: {url}")
    print(f"Params: {params}\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            print("Response received!")
            print(f"Status: {response.status_code}")
            print(f"Response keys: {list(data.keys())}")
            print(f"Number of items: {len(data.get('items', []))}")
            
            if data.get('items'):
                print("\n--- First 20 items from RGF ---\n")
                for i, item in enumerate(data.get('items', [])[:20]):
                    print(f"Item {i}:")
                    print(f"  conta: {item.get('conta')}")
                    print(f"  coluna: {item.get('coluna')}")
                    print(f"  valor: {item.get('valor')}")
                    print()
                
                # Search for debt-related items
                print("\n--- Searching for 'DIVIDA' in items ---\n")
                for item in data.get('items', []):
                    conta = (item.get('conta') or '').upper()
                    if 'DIVIDA' in conta or 'DC' in conta or 'CONSOLID' in conta:
                        print(f"Found: {item.get('conta')} = {item.get('valor')} ({item.get('coluna')})")
            
            # Show full response for inspection
            print("\n--- Full JSON Response ---\n")
            print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
            
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

async def inspect_siconfi_rreo():
    """Query SICONFI RREO directly to see response structure"""
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    params = {
        "id_ente": "4101408",  # Apucarana
        "an_exercicio": 2023,
        "nr_periodo": 6,
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 01",
    }
    
    print("\n\n" + "="*80)
    print("Querying SICONFI RREO endpoint...")
    print(f"URL: {url}")
    print(f"Params: {params}\n")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            print("Response received!")
            print(f"Status: {response.status_code}")
            print(f"Response keys: {list(data.keys())}")
            print(f"Number of items: {len(data.get('items', []))}")
            
            if data.get('items'):
                print("\n--- First 20 items from RREO ---\n")
                for i, item in enumerate(data.get('items', [])[:20]):
                    print(f"Item {i}:")
                    print(f"  conta: {item.get('conta')}")
                    print(f"  coluna: {item.get('coluna')}")
                    print(f"  valor: {item.get('valor')}")
                    print()
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(inspect_siconfi_rgf())
    asyncio.run(inspect_siconfi_rreo())
