import asyncio
import httpx

async def teste():
    async with httpx.AsyncClient(timeout=30, verify=False) as client:
        try:
            response = await client.get('https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo', params={'id_ente': '4101408', 'an_exercicio': 2023, 'nr_periodo': 6, 'co_tipo_demonstrativo': 'RREO', 'no_anexo': 'RREO-Anexo 01'})
            data = response.json()
            items = data.get('items', [])
            print(f'Status: {response.status_code}')
            print(f'Items retornados: {len(items)}')
            if items:
                print(f'Primeira item (conta): {items[0].get("conta")}')
                print(f'Primeira item (coluna): {items[0].get("coluna")}')
                print(f'Primeira item (valor): {items[0].get("valor")}')
                print('SUCCESS!')
        except Exception as e:
            print(f'Erro: {type(e).__name__}: {str(e)[:100]}')

asyncio.run(teste())
