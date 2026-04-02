#!/usr/bin/env python
"""
Script de diagnóstico para API SICONFI.
Testa conectividade, timeouts e estrutura de resposta.
"""

import asyncio
import httpx
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Teste 1: Conectividade básica
async def testar_conectividade_basica():
    """Testa se a API responde a requisições básicas"""
    print("\n" + "="*60)
    print("TESTE 1: Conectividade Básica")
    print("="*60)
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    params = {
        "id_ente": "4101408",  # Apucarana
        "an_exercicio": 2023,
        "nr_periodo": 6,
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 01"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            print(f"🔗 Conectando a: {url}")
            print(f"📊 Parâmetros: {params}")
            
            response = await client.get(url, params=params)
            print(f"✅ Status Code: {response.status_code}")
            
            if response.status_code == 200:
                dados = response.json()
                print(f"✅ Resposta em JSON recebida")
                print(f"   Keys: {list(dados.keys()) if isinstance(dados, dict) else 'N/A'}")
                
                if isinstance(dados, dict) and "items" in dados:
                    items = dados["items"]
                    print(f"   Items encontrados: {len(items)}")
                    if items:
                        print(f"   Primeiro item: {json.dumps(items[0], indent=2)}")
                        return True
                else:
                    print(f"❌ Estrutura inesperada: {json.dumps(dados, indent=2)[:500]}")
                    return False
            else:
                print(f"❌ Status Code: {response.status_code}")
                print(f"   Resposta: {response.text[:500]}")
                return False
                
    except httpx.ConnectError as e:
        print(f"❌ Erro de conexão (timeout?): {str(e)}")
        return False
    except httpx.TimeoutException as e:
        print(f"❌ Timeout: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        return False


# Teste 2: Tentar diferentes IBGE codes
async def testar_diferentes_codigos():
    """Testa com diferentes códigos IBGE para diagnosticar se é problema de formato"""
    print("\n" + "="*60)
    print("TESTE 2: Diferentes Códigos IBGE")
    print("="*60)
    
    codigos = [
        ("4101408", "Apucarana - formato 7 dígitos"),
        ("4101408", "Apucarana - com padding?"),
    ]
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    for codigo, descricao in codigos:
        params = {
            "id_ente": codigo,
            "an_exercicio": 2023,
            "nr_periodo": 6,
            "co_tipo_demonstrativo": "RREO",
            "no_anexo": "RREO-Anexo 01"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    dados = response.json()
                    items_count = len(dados.get("items", []))
                    print(f"✅ {descricao}: {items_count} items")
                    if items_count > 0:
                        print(f"   ✓ Obteve dados!")
                else:
                    print(f"❌ {descricao}: Status {response.status_code}")
                    
        except Exception as e:
            print(f"❌ {descricao}: {str(e)}")


# Teste 3: Aumentar timeout progressivamente
async def testar_timeout_progressivo():
    """Testa com timeouts cada vez maiores"""
    print("\n" + "="*60)
    print("TESTE 3: Timeouts Progressivos")
    print("="*60)
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    params = {
        "id_ente": "4101408",
        "an_exercicio": 2023,
        "nr_periodo": 6,
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 01"
    }
    
    timeouts = [5.0, 10.0, 30.0, 60.0, 120.0]
    
    for timeout in timeouts:
        try:
            async with httpx.AsyncClient(timeout=timeout, verify=False) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    dados = response.json()
                    items_count = len(dados.get("items", []))
                    print(f"✅ Timeout {timeout}s: Sucesso! {items_count} items")
                    return True
                else:
                    print(f"⚠️  Timeout {timeout}s: Status {response.status_code}")
                    
        except httpx.TimeoutException:
            print(f"❌ Timeout {timeout}s: Expirou (API muito lenta)")
        except Exception as e:
            print(f"❌ Timeout {timeout}s: {type(e).__name__}")
    
    return False


# Teste 4: Test de DNS/Certificado
async def testar_certificado():
    """Testa problemas de SSL/certificado"""
    print("\n" + "="*60)
    print("TESTE 4: Certificado SSL")
    print("="*60)
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    try:
        # Com verify=False (atual)
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.get(url, params={"id_ente": "4101408", "an_exercicio": 2023, "nr_periodo": 6})
            print(f"✅ Com verify=False: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Com verify=False: {type(e).__name__} - {str(e)}")
    
    try:
        # Com verify=True (strict)
        async with httpx.AsyncClient(timeout=30.0, verify=True) as client:
            response = await client.get(url, params={"id_ente": "4101408", "an_exercicio": 2023, "nr_periodo": 6})
            print(f"✅ Com verify=True: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Com verify=True: {type(e).__name__} - {str(e)}")


async def main():
    print("\n🔍 DIAGNÓSTICO API SICONFI")
    print("="*60)
    
    # Teste 1: Conectividade básica
    sucesso_basico = await testar_conectividade_basica()
    
    if sucesso_basico:
        print("\n✅ API SICONFI está funcionando! Passando para testes avançados...")
        await testar_diferentes_codigos()
    else:
        print("\n❌ API SICONFI não respondeu. Executando diagnósticos...")
        await testar_timeout_progressivo()
        await testar_certificado()
    
    print("\n" + "="*60)
    print("🔍 DIAGNÓSTICO COMPLETO")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
