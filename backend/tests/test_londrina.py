import asyncio
import httpx

async def teste_londrina():
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        # Testar código IBGE de Londrina
        codigo = "4106902"
        
        # Teste 1: Verificar se IBGE reconhece o código
        print("=" * 80)
        print(f"TESTE 1: Validar código IBGE {codigo}")
        print("=" * 80)
        
        try:
            response = await client.get(f'https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo}')
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Código válido: {data['nome']}")
                print(f"   Região: {data.get('microrregiao', {}).get('mesorregiao', {}).get('uf', {}).get('nome', 'N/A')}")
            else:
                print(f"❌ Código não encontrado (status {response.status_code})")
        except Exception as e:
            print(f"❌ Erro: {str(e)[:100]}")
        
        # Teste 2: Tentar SICONFI com LONDRINA
        print("\n" + "=" * 80)
        print(f"TESTE 2: SICONFI para Londrina")
        print("=" * 80)
        
        try:
            response = await client.get(
                'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo',
                params={
                    'id_ente': codigo,
                    'an_exercicio': 2023,
                    'nr_periodo': 6,
                    'co_tipo_demonstrativo': 'RREO',
                    'no_anexo': 'RREO-Anexo 01'
                }
            )
            data = response.json()
            items = data.get('items', [])
            print(f"✅ Status: {response.status_code}")
            print(f"   Items retornados: {len(items)}")
            
            if items:
                print(f"   ✅ Dados disponíveis!")
                print(f"      Primeira: {items[0]['conta']}")
            else:
                print(f"   ⚠️ Nenhum item retornado para Londrina")
        except Exception as e:
            print(f"❌ Erro SICONFI: {str(e)[:100]}")
        
        # Teste 3: Tentar APUCARANA para comparar
        print("\n" + "=" * 80)
        print(f"TESTE 3: SICONFI para Apucarana (4101408)")
        print("=" * 80)
        
        try:
            response = await client.get(
                'https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo',
                params={
                    'id_ente': '4101408',
                    'an_exercicio': 2023,
                    'nr_periodo': 6,
                }
            )
            data = response.json()
            items = data.get('items', [])
            print(f"✅ Status: {response.status_code}")
            print(f"   Items retornados: {len(items)}")
            
            if items:
                print(f"   ✅ Dados disponíveis!")
            else:
                print(f"   ⚠️ Nenhum item retornado")
        except Exception as e:
            print(f"❌ Erro SICONFI: {str(e)[:100]}")

asyncio.run(teste_londrina())
