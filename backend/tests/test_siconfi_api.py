"""
Script de teste para debugar a API SICONFI.
Investigar: rate limits, parâmetros corretos, resposta completa.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Códigos IBGE para teste
CODIGOS_TESTE = {
    "4101408": "Apucarana",
    "4113700": "Londrina",
}

DEFAULT_TIMEOUT = 30.0

async def test_siconfi_raw():
    """Teste RAW da API SICONFI com diferentes parâmetros"""
    
    print("=" * 80)
    print("🧪 TESTE API SICONFI - DEBUG")
    print("=" * 80)
    
    url_base = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    # Tentar diferentes configurações
    configs = [
        {
            "nome": "Config PADRÃO (2023, período 6)",
            "params": {
                "id_ente": "4101408",
                "an_exercicio": 2023,
                "nr_periodo": 6,
                "co_tipo_demonstrativo": "RREO",
                "no_anexo": "RREO-Anexo 01"
            }
        },
        {
            "nome": "Config 2024 (período 12)",
            "params": {
                "id_ente": "4101408",
                "an_exercicio": 2024,
                "nr_periodo": 12,
                "co_tipo_demonstrativo": "RREO",
                "no_anexo": "RREO-Anexo 01"
            }
        },
        {
            "nome": "Config MÍNIMA (apenas código e ano)",
            "params": {
                "id_ente": "4101408",
                "an_exercicio": 2024,
            }
        },
        {
            "nome": "Config SEM PERÍODO (2024, última)",
            "params": {
                "id_ente": "4101408",
                "an_exercicio": 2024,
                "nr_periodo": 12,
                "co_tipo_demonstrativo": "RREO"
            }
        }
    ]
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        for config in configs:
            print(f"\n📋 Testando: {config['nome']}")
            print(f"   Parâmetros: {config['params']}")
            
            try:
                response = await client.get(url_base, params=config["params"])
                print(f"   ✅ Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verificar estrutura
                    if isinstance(data, dict):
                        print(f"   📊 Tipo resposta: Dict")
                        print(f"   🔑 Chaves principais: {list(data.keys())}")
                        
                        # Se tem 'items', mostrar quantidade e primeira amostra
                        if "items" in data:
                            items = data["items"]
                            print(f"   📦 Total de items: {len(items)}")
                            
                            if items:
                                print(f"   🔍 Primeira item (amostra):")
                                primeira = items[0]
                                for chave, valor in primeira.items():
                                    print(f"      - {chave}: {valor}")
                        
                        # Se tem 'count', 'hasMore', etc
                        for chave in ["count", "hasMore", "limit", "offset"]:
                            if chave in data:
                                print(f"   📈 {chave}: {data[chave]}")
                    else:
                        print(f"   📊 Tipo resposta: {type(data)}")
                        print(f"   📋 Conteúdo: {str(data)[:200]}")
                else:
                    print(f"   ❌ Erro: {response.status_code}")
                    print(f"   📝 Resposta: {response.text[:300]}")
                    
            except httpx.TimeoutException:
                print(f"   ⏱️  TIMEOUT (30s)")
            except httpx.ConnectError as e:
                print(f"   🔌 ERRO DE CONEXÃO: {str(e)[:100]}")
            except Exception as e:
                print(f"   ⚠️  ERRO: {str(e)[:200]}")
            
            # Pequeno delay entre requisições (respeitar rate limit)
            await asyncio.sleep(1)


async def test_years_available():
    """Testar quais anos estão disponíveis"""
    
    print("\n" + "=" * 80)
    print("📅 TESTE DE ANOS DISPONÍVEIS")
    print("=" * 80)
    
    url_base = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    anos_teste = [2020, 2021, 2022, 2023, 2024, 2025]
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        for ano in anos_teste:
            print(f"\n📅 Testando ano: {ano}")
            
            try:
                response = await client.get(url_base, params={
                    "id_ente": "4101408",
                    "an_exercicio": ano,
                    "nr_periodo": 12,
                })
                
                if response.status_code == 200:
                    data = response.json()
                    if "items" in data and data["items"]:
                        print(f"   ✅ Ano {ano}: {len(data['items'])} registros encontrados")
                    else:
                        print(f"   ⚠️  Ano {ano}: Sem dados")
                else:
                    print(f"   ❌ Ano {ano}: Status {response.status_code}")
                    
            except Exception as e:
                print(f"   ⚠️  Ano {ano}: Erro - {str(e)[:80]}")
            
            await asyncio.sleep(0.5)


async def test_rate_limit():
    """Testar rate limit fazendo múltiplas requisições"""
    
    print("\n" + "=" * 80)
    print("🚦 TESTE DE RATE LIMIT")
    print("=" * 80)
    
    url_base = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        inicio = datetime.now()
        
        for i in range(5):
            try:
                response = await client.get(url_base, params={
                    "id_ente": "4101408",
                    "an_exercicio": 2024,
                })
                
                tempo_decorrido = (datetime.now() - inicio).total_seconds()
                
                print(f"   📤 Requisição {i+1}: Status {response.status_code} ({tempo_decorrido:.2f}s)")
                
                # Verificar headers rate limit
                for header in ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset", "RateLimit-Limit", "RateLimit-Remaining"]:
                    if header in response.headers:
                        print(f"      🔹 {header}: {response.headers[header]}")
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ❌ Requisição {i+1}: {str(e)[:80]}")


async def main():
    print(f"\n🕐 Início: {datetime.now().strftime('%H:%M:%S')}\n")
    
    await test_siconfi_raw()
    await test_years_available()
    await test_rate_limit()
    
    print(f"\n🕐 Fim: {datetime.now().strftime('%H:%M:%S')}\n")


if __name__ == "__main__":
    asyncio.run(main())
