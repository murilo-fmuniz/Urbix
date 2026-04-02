"""
TESTE: Endpoint /debug-apis
=============================
Valida o novo endpoint de diagnóstico para APIs governamentais.
"""

import requests
import json
from typing import Dict, Any

# URL da API
BASE_URL = "http://localhost:8000"
ENDPOINT = "/api/v1/topsis/debug-apis"

# Cidades para testar
CIDADES_TESTE = [
    "4106902",  # Apucarana (fallback especifico)
    "3109402",  # São Paulo (com dados SICONFI real)
    "1234567",  # Cidade ficticia (fallback universal)
]


def teste_debug_api(codigo_ibge: str) -> Dict[str, Any]:
    """Testa o endpoint debug-apis para um código IBGE."""
    
    url = f"{BASE_URL}{ENDPOINT}/{codigo_ibge}"
    
    print(f"\n{'='*70}")
    print(f"🔍 Testando: {codigo_ibge}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Exibir resumo
        print(f"\n✅ Status Code: {response.status_code}\n")
        
        print(f"📊 RESUMO:")
        print(f"   APIs OK: {data['resumo']['total_apis_ok']}/3")
        print(f"   Fallbacks: {data['resumo']['total_fallbacks']}/3")
        print(f"   Consistência: {data['resumo']['consistencia']}")
        
        # Detalhes por API
        print(f"\n📍 IBGE:")
        print(f"   Status: {data['ibge']['status']}")
        print(f"   Fonte: {data['ibge']['fonte']}")
        if 'populacao' in data['ibge']['dados']:
            print(f"   População: {data['ibge']['dados']['populacao']:,} hab")
        
        print(f"\n💰 SICONFI:")
        print(f"   Status: {data['siconfi']['status']}")
        print(f"   Fonte: {data['siconfi']['fonte']}")
        if 'receita_total' in data['siconfi']['dados']:
            print(f"   Receita Total: R$ {data['siconfi']['dados']['receita_total']:,.0f}")
        
        print(f"\n🏥 DataSUS:")
        print(f"   Status: {data['datasus']['status']}")
        print(f"   Fonte: {data['datasus']['fonte']}")
        if 'num_hospitais' in data['datasus']['dados']:
            print(f"   Hospitais: {data['datasus']['dados']['num_hospitais']}")
        
        print(f"\n📋 JSON COMPLETO:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        return data
        
    except requests.exceptions.ConnectionError:
        print(f"❌ ERRO: Não consegui conectar em {BASE_URL}")
        print(f"   Verifique se o servidor está rodando com: uvicorn main:app --reload")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"❌ ERRO HTTP: {e.response.status_code}")
        print(f"   {e.response.text}")
        return None
    except requests.exceptions.Timeout:
        print(f"❌ ERRO: Timeout na requisição (10s)")
        return None
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        return None


def main():
    """Executa testes para todas as cidades."""
    
    print("\n" + "="*70)
    print("🧪 TESTE: ENDPOINT /debug-apis/{codigo_ibge}")
    print("="*70)
    print(f"\nEndpoint diagnóstico para debugar APIs governamentais")
    print(f"Testando {len(CIDADES_TESTE)} cidades...\n")
    
    resultados = {}
    
    for codigo in CIDADES_TESTE:
        resultado = teste_debug_api(codigo)
        resultados[codigo] = resultado
    
    # Resumo final
    print("\n" + "="*70)
    print("📈 RESUMO DOS TESTES")
    print("="*70)
    
    for codigo, resultado in resultados.items():
        if resultado:
            consistencia = resultado['resumo']['consistencia']
            apis_ok = resultado['resumo']['total_apis_ok']
            print(f"  {codigo}: {consistencia:20s} ({apis_ok}/3 APIs OK)")
        else:
            print(f"  {codigo}: ❌ FALHA NA REQUISIÇÃO")
    
    print("\n✅ TESTES CONCLUÍDOS\n")


if __name__ == "__main__":
    main()
