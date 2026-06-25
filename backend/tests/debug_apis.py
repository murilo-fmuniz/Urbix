"""
Debug script para verificar o que as APIs estão retornando
"""

import sys
sys.path.insert(0, 'd:\\Docs\\Faculdade\\IC\\Urbix\\backend')

import asyncio
from app.services.external_apis import (
    get_siconfi_finances,
    get_ibge_population,
    get_datasus_health_infrastructure,
    get_inep_education,
    get_transparencia_social
)

async def test_apis():
    """Testa as 5 APIs para Apucarana"""
    
    codigo_ibge = "4101408"
    nome = "Apucarana"
    
    print("=" * 70)
    print(f"VERIFICACAO DE APIS PARA {nome} ({codigo_ibge})")
    print("=" * 70)
    
    # SICONFI
    print("\n[1] SICONFI (Finanças):")
    try:
        siconfi = await get_siconfi_finances(codigo_ibge)
        print(f"    Retorno: {siconfi}")
        if isinstance(siconfi, dict):
            for key, val in siconfi.items():
                print(f"      - {key}: {val}")
    except Exception as e:
        print(f"    ERRO: {e}")
    
    # IBGE
    print("\n[2] IBGE (População):")
    try:
        ibge = await get_ibge_population(codigo_ibge)
        print(f"    Retorno: {ibge} (tipo: {type(ibge).__name__})")
    except Exception as e:
        print(f"    ERRO: {e}")
    
    # DataSUS
    print("\n[3] DataSUS (Saúde):")
    try:
        datasus = await get_datasus_health_infrastructure(codigo_ibge)
        print(f"    Retorno: {datasus}")
        if isinstance(datasus, dict):
            for key, val in datasus.items():
                print(f"      - {key}: {val}")
    except Exception as e:
        print(f"    ERRO: {e}")
    
    # INEP
    print("\n[4] INEP (Educação):")
    try:
        inep = await get_inep_education(codigo_ibge)
        print(f"    Retorno: {inep}")
        if isinstance(inep, dict):
            for key, val in inep.items():
                print(f"      - {key}: {val}")
    except Exception as e:
        print(f"    ERRO: {e}")
    
    # Portal da Transparência
    print("\n[5] Portal da Transparência (Bolsa Família):")
    try:
        transparencia = await get_transparencia_social(codigo_ibge)
        print(f"    Retorno: {transparencia}")
        if isinstance(transparencia, dict):
            for key, val in transparencia.items():
                print(f"      - {key}: {val}")
    except Exception as e:
        print(f"    ERRO: {e}")

if __name__ == "__main__":
    asyncio.run(test_apis())
