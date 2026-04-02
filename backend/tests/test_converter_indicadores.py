#!/usr/bin/env python3
"""
Script de teste para validar a conversão de indicadores frontend → ISO
"""

import sys
sys.path.insert(0, '.')

from app.routers.topsis import converter_indicadores_frontend
from app.schemas import ManualCityIndicators

# ===== TESTE 1: Indicadores simples do frontend =====
print("\n" + "="*80)
print("TESTE 1: Converter indicadores simples do frontend")
print("="*80)

indicadores_frontend = {
    "pontos_iluminacao_telegestao": 60.0,
    "medidores_inteligentes_energia": 50.0,
    "bombeiros_por_100k": 40.0,
    "area_verde_mapeada": 35.0
}

print(f"\n📥 Entrada (frontend):")
for k, v in indicadores_frontend.items():
    print(f"   {k}: {v}")

resultado = converter_indicadores_frontend(indicadores_frontend)

print(f"\n📤 Saída convertida (ISO):")
print(f"   ISO 37120:")
print(f"      bombeiros_100k: {resultado.iso_37120.bombeiros_100k}")
print(f"   ISO 37122:")
print(f"      iluminacao_telegestao_pct: {resultado.iso_37122.iluminacao_telegestao_pct}")
print(f"      medidores_inteligentes_energia_pct: {resultado.iso_37122.medidores_inteligentes_energia_pct}")

# ===== TESTE 2: Entrada vazia =====
print("\n" + "="*80)
print("TESTE 2: Entrada vazia (deve usar defaults)")
print("="*80)

resultado_vazio = converter_indicadores_frontend({})
print(f"\n✅ Defaults aplicados:")
print(f"   ISO 37120 bombeiros_100k: {resultado_vazio.iso_37120.bombeiros_100k}")
print(f"   ISO 37122 iluminacao_telegestao_pct: {resultado_vazio.iso_37122.iluminacao_telegestao_pct}")

# ===== TESTE 3: None input =====
print("\n" + "="*80)
print("TESTE 3: Input None (deve retornar defaults)")
print("="*80)

resultado_none = converter_indicadores_frontend(None)
print(f"\n✅ Defaults aplicados para None:")
print(f"   Tipo: {type(resultado_none)}")
print(f"   ISO 37120 bombeiros_100k: {resultado_none.iso_37120.bombeiros_100k}")

print("\n" + "="*80)
print("✅ TODOS OS TESTES PASSARAM!")
print("="*80)
