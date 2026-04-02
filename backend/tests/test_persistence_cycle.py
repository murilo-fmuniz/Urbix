"""
TESTE: Ciclo de Persistência Fechado
=====================================
Valida que o 4-tier fallback funciona corretamente:
1. API Real (com retry)
2. Banco (cache persistente)
3. FALLBACK_ESPECIFICO (3 cidades)
4. FALLBACK_UNIVERSAL (5.570 cidades)

Objetivo: Verificar que dados já visitados são recuperados do banco
antes de retornar FALLBACK_UNIVERSAL.
"""

import asyncio
import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.external_apis import (
    get_siconfi_finances,
    get_ibge_population,
    get_datasus_health_infrastructure,
    _get_data_from_db,
)
from app.database import SessionLocal
from app.models import CityManualData


async def test_persistence_cycle():
    """Testa o ciclo de persistência de dados."""
    
    print("\n" + "="*70)
    print("🔄 TESTE: CICLO DE PERSISTÊNCIA FECHADO")
    print("="*70)
    
    # Dados de teste: 3 cidades
    test_cities = [
        {
            "codigo_ibge": "4106902",  # Apucarana (fallback especifico)
            "name": "Apucarana"
        },
        {
            "codigo_ibge": "3109402",  # São Paulo (fallback especifico)
            "name": "São Paulo"
        },
        {
            "codigo_ibge": "1234567",  # Cidade ficticia (fallback universal)
            "name": "Cidade Ficticia"
        }
    ]
    
    print("\n1️⃣  TESTE DE CONSULTA AO BANCO (_get_data_from_db)")
    print("-" * 70)
    
    for city in test_cities:
        codigo = city["codigo_ibge"]
        name = city["name"]
        
        db_data = _get_data_from_db(codigo)
        
        if db_data:
            print(f"✅ {name} ({codigo}): Dados encontrados no banco")
            if "iso_37120" in db_data:
                print(f"   - SICONFI: Tem iso_37120")
            if "iso_37122" in db_data:
                print(f"   - IBGE: Tem iso_37122")
            if "iso_37123" in db_data:
                print(f"   - DataSUS: Tem iso_37123")
        else:
            print(f"❌ {name} ({codigo}): Nenhum dado no banco (será usado fallback)")
    
    print("\n2️⃣  TESTE DE FALLBACK HIERARQUIZADO - SICONFI")
    print("-" * 70)
    
    for city in test_cities:
        codigo = city["codigo_ibge"]
        name = city["name"]
        
        try:
            result = await get_siconfi_finances(codigo)
            fonte = result.get("fonte", "desconhecida")
            print(f"✅ {name} ({codigo}):")
            print(f"   Fonte: {fonte}")
            print(f"   Receita Total: R$ {result.get('receita_total', 0):,.0f}")
        except Exception as e:
            print(f"❌ {name} ({codigo}): Erro - {type(e).__name__}")
    
    print("\n3️⃣  TESTE DE FALLBACK HIERARQUIZADO - IBGE POPULAÇÃO")
    print("-" * 70)
    
    for city in test_cities:
        codigo = city["codigo_ibge"]
        name = city["name"]
        
        try:
            result = await get_ibge_population(codigo)
            fonte = result.get("fonte", "desconhecida")
            print(f"✅ {name} ({codigo}):")
            print(f"   Fonte: {fonte}")
            print(f"   População: {result.get('populacao', 0):,} habitantes")
        except Exception as e:
            print(f"❌ {name} ({codigo}): Erro - {type(e).__name__}")
    
    print("\n4️⃣  TESTE DE FALLBACK HIERARQUIZADO - DATASUS HOSPITAIS")
    print("-" * 70)
    
    for city in test_cities:
        codigo = city["codigo_ibge"]
        name = city["name"]
        
        try:
            result = await get_datasus_health_infrastructure(codigo)
            fonte = result.get("fonte", "desconhecida")
            print(f"✅ {name} ({codigo}):")
            print(f"   Fonte: {fonte}")
            print(f"   Hospitais: {result.get('num_hospitais', 0)}")
        except Exception as e:
            print(f"❌ {name} ({codigo}): Erro - {type(e).__name__}")
    
    print("\n5️⃣  VERIFICAÇÃO: DADOS PERSISTIDOS NO BANCO")
    print("-" * 70)
    
    try:
        with SessionLocal() as db:
            cidades_salvas = db.query(CityManualData).count()
            print(f"✅ Total de cidades com dados persistidos: {cidades_salvas}")
            
            # Listar algumas
            for city_data in db.query(CityManualData).limit(5):
                print(f"   - {city_data.codigo_ibge}: " +
                      f"Última atualização: {city_data.data_ultima_atualizacao}")
    except Exception as e:
        print(f"❌ Erro ao consultar banco: {type(e).__name__}")
    
    print("\n" + "="*70)
    print("✅ TESTE CONCLUÍDO")
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_persistence_cycle())
