import asyncio
import httpx

async def buscar_codigo_londrina():
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        # Buscar Londrina no IBGE
        print("Procurando código IBGE para Londrina...")
        
        try:
            # IBGE tem endpoint para buscar por nome
            response = await client.get(
                'https://servicodados.ibge.gov.br/api/v1/localidades/municipios',
            )
            
            if response.status_code == 200:
                municipios = response.json()
                
                # Filtrar por Londrina
                londrina = [m for m in municipios if 'londrina' in m['nome'].lower()]
                
                if londrina:
                    for m in londrina:
                        print(f"\n✅ Encontrado: {m['nome']}")
                        print(f"   Código IBGE: {m['id']}")
                        print(f"   UF: {m.get('microrregiao', {}).get('mesorregiao', {}).get('uf', {}).get('nome', 'N/A')}")
                else:
                    print("❌ Londrina não encontrada")
            else:
                print(f"❌ Erro ao buscar: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erro: {str(e)[:100]}")

asyncio.run(buscar_codigo_londrina())
