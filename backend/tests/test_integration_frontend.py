#!/usr/bin/env python3
"""
Teste de integração completo: Simula payload do frontend e testa o endpoint
"""

import json
import requests
from typing import List

BASE_URL = "http://localhost:8000/api/v1"

# Payload que o frontend enviará com indicadores simplificados
payload_frontend_simples = [
    {
        "codigo_ibge": "4101408",
        "nome_cidade": "Apucarana",
        "manual_indicators": {
            "pontos_iluminacao_telegestao": 60.0,
            "medidores_inteligentes_energia": 50.0,
            "bombeiros_por_100k": 40.0,
            "area_verde_mapeada": 35.0
        }
    },
    {
        "codigo_ibge": "4113700",
        "nome_cidade": "Londrina",
        "manual_indicators": {
            "pontos_iluminacao_telegestao": 75.0,
            "medidores_inteligentes_energia": 65.0,
            "bombeiros_por_100k": 50.0,
            "area_verde_mapeada": 45.0
        }
    }
]

print("\n" + "="*80)
print("TESTE DE INTEGRAÇÃO: Frontend → Backend (/ranking-hibrido)")
print("="*80)

print(f"\n📤 Enviando payload com indicadores simples:")
print(json.dumps(payload_frontend_simples, indent=2, ensure_ascii=False))

try:
    print(f"\n🔄 POST para {BASE_URL}/topsis/ranking-hibrido...")
    response = requests.post(
        f"{BASE_URL}/topsis/ranking-hibrido",
        json=payload_frontend_simples,
        timeout=30
    )
    
    print(f"\n📥 Status: {response.status_code}")
    
    if response.status_code == 200:
        resultado = response.json()
        print(f"✅ SUCESSO!")
        print(f"\n📊 Ranking:")
        for rank in resultado.get("ranking", []):
            print(f"   {rank['rank']}. {rank['cidade']}: {rank['indice_smart']:.2%}")
        
        print(f"\n📈 Indicadores do primeiro lugar:")
        if resultado.get("ranking"):
            top_city = resultado["ranking"][0]
            print(f"   Cidade: {top_city['cidade']}")
            print(f"   Índice: {top_city['indice_smart']:.2%}")
            print(f"   Status: {top_city['status']}")
            
    else:
        print(f"❌ ERRO!")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print(f"\n❌ ERRO: Não consegui conectar ao backend em {BASE_URL}")
    print("   Verifique se o servidor está rodando em http://localhost:8000")
except Exception as e:
    print(f"\n❌ ERRO: {str(e)}")
