"""
Diagnóstico completo: testar diferentes endpoints e formatos de requisição
"""

import asyncio
import httpx
import json
from typing import Dict, Any

DEFAULT_TIMEOUT = 30.0

async def test_all_siconfi_endpoints():
    """Testar diferentes endpoints da API SICONFI"""
    
    print("=" * 100)
    print("🔍 TESTE COMPLETO: Diferentes endpoints SICONFI")
    print("=" * 100)
    
    endpoints = [
        # Endpoint 1: RREO (Relatório Resumido de Execução Orçamentária)
        {
            "nome": "RREO - Relatório Resumido",
            "url": "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo",
            "params": {
                "id_ente": "4101408",
                "an_exercicio": 2023,
                "nr_periodo": 12,
            }
        },
        # Endpoint 2: RGF (Relatório de Gestão Fiscal - Lei de Responsabilidade Fiscal)
        {
            "nome": "RGF - Gestão Fiscal",
            "url": "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf",
            "params": {
                "id_ente": "4101408",
                "an_exercicio": 2023,
                "nr_periodo": 6,
            }
        },
        # Endpoint 3: Serviços (tentar encontrar endpoint de dados agregados)
        {
            "nome": "Dados básicos município",
            "url": "https://apidatalake.tesouro.gov.br/ords/transferencias_municipios",
            "params": {
                "municipio_cd_ibge": "4101408",
                "ano": 2023,
            }
        },
    ]
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
        for endpoint in endpoints:
            print(f"\n{'='*100}")
            print(f"🔗 {endpoint['nome']}")
            print(f"   URL: {endpoint['url']}")
            print(f"   Params: {endpoint['params']}")
            print('='*100)
            
            try:
                response = await client.get(endpoint['url'], params=endpoint['params'])
                
                print(f"\n✅ Status: {response.status_code}")
                print(f"📝 Content-Type: {response.headers.get('content-type', 'N/A')}")
                print(f"📊 Content-Length: {len(response.content)} bytes")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        
                        if isinstance(data, dict):
                            print(f"\n📦 Resposta (DICT):")
                            print(f"   Chaves: {list(data.keys())}")
                            
                            if "items" in data:
                                items = data.get("items", [])
                                print(f"\n   📋 Items: {len(items)} registros")
                                
                                if items:
                                    print(f"\n   🔍 PRIMEIRA AMOSTRA:")
                                    primeiro = items[0]
                                    for chave, valor in list(primeiro.items())[:10]:
                                        if isinstance(valor, (int, float)):
                                            print(f"      {chave}: {valor:,.2f}")
                                        else:
                                            print(f"      {chave}: {valor}")
                                    if len(primeiro) > 10:
                                        print(f"      ... +{len(primeiro) - 10} campos")
                            
                            for chave in ["count", "hasMore", "limit", "offset"]:
                                if chave in data:
                                    print(f"   {chave}: {data[chave]}")
                        
                        elif isinstance(data, list):
                            print(f"\n📦 Resposta (LISTA):")
                            print(f"   Total: {len(data)} items")
                            if data:
                                print(f"\n   🔍 PRIMEIRA AMOSTRA:")
                                primeiro = data[0]
                                if isinstance(primeiro, dict):
                                    for chave, valor in list(primeiro.items())[:10]:
                                        if isinstance(valor, (int, float)):
                                            print(f"      {chave}: {valor:,.2f}")
                                        else:
                                            print(f"      {chave}: {valor}")
                        else:
                            print(f"\n📦 Tipo: {type(data)}")
                            print(f"   Conteúdo: {str(data)[:300]}")
                    
                    except json.JSONDecodeError:
                        print(f"\n❌ Resposta não é JSON válido")
                        print(f"   Primeiros 200 chars: {response.text[:200]}")
                else:
                    print(f"\n❌ Erro HTTP: {response.status_code}")
                    print(f"   Resposta: {response.text[:300]}")
                    
            except httpx.TimeoutException:
                print(f"\n⏱️  TIMEOUT (30 segundos)")
            except httpx.ConnectError as e:
                print(f"\n🔌 ERRO DE CONEXÃO: {str(e)[:150]}")
            except Exception as e:
                print(f"\n⚠️  ERRO: {type(e).__name__}: {str(e)[:150]}")
            
            await asyncio.sleep(1)


async def test_siconfi_with_logging():
    """Testar SICONFI com logging detalhado"""
    
    print("\n" + "=" * 100)
    print("🔬 TESTE DETALHADO: SICONFI com LOGGING")
    print("=" * 100)
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    # Testar 2023 com diferentes períodos
    periodos = [6, 12]
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        for periodo in periodos:
            print(f"\n\n📅 Testando Período: {periodo}")
            print("-" * 100)
            
            params = {
                "id_ente": "4101408",
                "an_exercicio": 2023,
                "nr_periodo": periodo,
            }
            
            try:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get("items", [])
                    
                    print(f"✅ Status: 200 OK")
                    print(f"📊 Total items: {len(items)}")
                    
                    if items:
                        # Contar por tipo de coluna
                        colunas_count = {}
                        for item in items:
                            col = item.get("coluna", "DESCONHECIDA")
                            colunas_count[col] = colunas_count.get(col, 0) + 1
                        
                        print(f"\n📋 Distribuição por COLUNA:")
                        for coluna, count in sorted(colunas_count.items(), key=lambda x: x[1], reverse=True):
                            print(f"   {coluna[:60]:60s} = {count:3d} items")
                        
                        # Procurar RECEITAS
                        receitas_items = [item for item in items if "RECEITA" in item.get("conta", "").upper()]
                        print(f"\n💰 Items com 'RECEITA': {len(receitas_items)}")
                        
                        if receitas_items:
                            print(f"\n   Amostra de RECEITAS:")
                            for item in receitas_items[:3]:
                                print(f"      {item['conta'][:60]:60s} | Col: {item['coluna'][:30]:30s} | R$ {item['valor']:15,.2f}")
                        
                        # Procurar DESPESAS DE CAPITAL
                        cap_items = [item for item in items if "DESPESAS DE CAPITAL" in item.get("conta", "").upper()]
                        print(f"\n🏗️  Items com 'DESPESAS DE CAPITAL': {len(cap_items)}")
                        
                        if cap_items:
                            print(f"\n   Amostra de CAPITAL:")
                            for item in cap_items[:3]:
                                print(f"      {item['conta'][:60]:60s} | Col: {item['coluna'][:30]:30s} | R$ {item['valor']:15,.2f}")
                else:
                    print(f"❌ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  Erro: {str(e)[:100]}")
            
            await asyncio.sleep(0.5)


async def test_alternative_apis():
    """Testar APIs alternativas para dados financeiros municipais"""
    
    print("\n\n" + "=" * 100)
    print("🔍 TESTE: APIs ALTERNATIVAS para dados financeiros")
    print("=" * 100)
    
    alternatives = [
        {
            "nome": "1. SICONFI - Lista de municípios",
            "url": "https://apidatalake.tesouro.gov.br/ords/siconfi/carregador",
            "params": {}
        },
        {
            "nome": "2. SICONFI - Dados agregados por UF",
            "url": "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo",
            "params": {
                "id_ente": "11",  # Brasília
                "an_exercicio": 2023,
            }
        },
        {
            "nome": "3. IBGE - Dados municipais",
            "url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/4101408",
            "params": {}
        },
        {
            "nome": "4. SICONFI Dados Abertos (alternativo)",
            "url": "https://tesouro.gov.br/webservice/siconfi/v1/rreo",
            "params": {
                "cod_ibge": "4101408",
                "ano": 2023,
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT, follow_redirects=True) as client:
        for alt in alternatives:
            print(f"\n{'='*100}")
            print(f"🔗 {alt['nome']}")
            print(f"   URL: {alt['url']}")
            print('='*100)
            
            try:
                response = await client.get(alt['url'], params=alt['params'])
                print(f"✅ Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        if isinstance(data, dict):
                            print(f"   Chaves: {list(data.keys())[:10]}")
                        elif isinstance(data, list):
                            print(f"   Lista com {len(data)} items")
                        else:
                            print(f"   Tipo: {type(data)}")
                    except:
                        print(f"   Resposta (texto): {response.text[:150]}")
                else:
                    print(f"   Resposta: {response.status_code}")
                    
            except Exception as e:
                print(f"⚠️  {type(e).__name__}: {str(e)[:80]}")
            
            await asyncio.sleep(0.5)


async def main():
    await test_all_siconfi_endpoints()
    await test_siconfi_with_logging()
    await test_alternative_apis()


if __name__ == "__main__":
    asyncio.run(main())
