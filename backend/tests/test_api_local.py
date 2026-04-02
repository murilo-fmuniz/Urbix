#!/usr/bin/env python3
"""
Teste usando FastAPI TestClient (não precisa do servidor rodando)
"""

import json
import sys
import os

# Add the backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Payload que o frontend enviará com indicadores simplificados (valores 0-100, já em %)
payload_frontend_simples = [
    {
        "codigo_ibge": "4101408",
        "nome_cidade": "Apucarana",
        "manual_indicators": {
            "pontos_iluminacao_telegestao": 60.0,      # 60%
            "medidores_inteligentes_energia": 50.0,    # 50%
            "bombeiros_por_100k": 40.0,                # 40 bombeiros/100k hab
            "area_verde_mapeada": 35.0                 # 35%
        }
    },
    {
        "codigo_ibge": "4113700",
        "nome_cidade": "Londrina",
        "manual_indicators": {
            "pontos_iluminacao_telegestao": 75.0,      # 75%
            "medidores_inteligentes_energia": 65.0,    # 65%
            "bombeiros_por_100k": 50.0,                # 50 bombeiros/100k hab
            "area_verde_mapeada": 45.0                 # 45%
        }
    }
]

print("\n" + "="*80)
print("TESTE DE INTEGRAÇÃO: Payload Frontend → Endpoint /ranking-hibrido")
print("="*80)

print(f"\n📤 Enviando payload com indicadores simples (0-100%):")
print(json.dumps(payload_frontend_simples, indent=2, ensure_ascii=False)[:600] + "...")

try:
    print(f"\n🔄 POST para /api/v1/topsis/ranking-hibrido...")
    response = client.post(
        "/api/v1/topsis/ranking-hibrido",
        json=payload_frontend_simples
    )
    
    print(f"\n📥 Status: {response.status_code}")
    
    if response.status_code == 200:
        resultado = response.json()
        print(f"✅ SUCESSO!")
        
        print(f"\n📊 Estrutura da resposta:")
        print(f"   Keys: {list(resultado.keys())}")
        
        ranking = resultado.get("ranking", [])
        print(f"\n📊 Ranking ({len(ranking)} cidades):")
        for i, city in enumerate(ranking, 1):
            print(f"   {i}. {city.get('nome_cidade', 'N/A')}: {city.get('indice_smart', 0):.2%}")
        
        print(f"\n📈 Top 1:")
        if ranking:
            top_city = ranking[0]
            print(f"   Cidade: {top_city.get('nome_cidade', 'N/A')}")
            print(f"   Índice Smart: {top_city.get('indice_smart', 0):.2%}")
            
        print(f"\n✅ Teste PASSOU! Backend aceita corretamente o formato do frontend.")
            
    else:
        print(f"❌ ERRO HTTP {response.status_code}!")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n❌ ERRO: {str(e)}")
    import traceback
    traceback.print_exc()
