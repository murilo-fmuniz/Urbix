"""
Script de teste local para validar a melhoria do TOPSIS
Chama as funções diretamente sem HTTP
"""

import sys
sys.path.insert(0, 'd:\\Docs\\Faculdade\\IC\\Urbix\\backend')

import asyncio
from app.database import SessionLocal
from app.routers.topsis import processar_cidade_real
from app.schemas import ManualCityIndicators

async def test_local():
    """Testa o processamento local sem HTTP"""
    db = SessionLocal()
    
    try:
        print("=" * 70)
        print("TESTE LOCAL DO TOPSIS - VERIFICAÇÃO DE INDICADORES")
        print("=" * 70)
        
        # Testar Apucarana - SEM indicadores manuais (deve carregar do banco)
        print("\n\n[TESTE 1] Apucarana sem indicadores manuais (carrega do banco)")
        print("-" * 70)
        resultado1 = await processar_cidade_real(
            codigo_ibge="4101408",
            nome_cidade="Apucarana",
            manual=None,  # SEM dados manuais!
            db=db
        )
        
        if resultado1:
            indicadores = resultado1["indicadores_flatalizados"]
            print(f"\nResultado: {len(indicadores)} indicadores")
            
            # Contar indicadores com dados
            nao_zero = sum(1 for v in indicadores if v > 0)
            print(f"  - Indicadores com dados: {nao_zero}/{len(indicadores)}")
            print(f"  - Cobertura: {nao_zero/len(indicadores)*100:.1f}%")
            
            # Mostrar alguns valores
            print(f"\n  Valores da lista plana (primeiros 20):")
            for i, v in enumerate(indicadores[:20]):
                print(f"    [{i:2d}] {v:.4f}")
                
            print(f"\n  Valores da lista plana (últimos 10):")
            for i, v in enumerate(indicadores[-10:], start=len(indicadores)-10):
                print(f"    [{i:2d}] {v:.4f}")
        else:
            print("ERRO: Processamento falhou")
        
        # Testar São Paulo
        print("\n\n[TESTE 2] São Paulo sem indicadores manuais (carrega do banco)")
        print("-" * 70)
        resultado2 = await processar_cidade_real(
            codigo_ibge="3550308",
            nome_cidade="São Paulo",
            manual=None,  # SEM dados manuais!
            db=db
        )
        
        if resultado2:
            indicadores = resultado2["indicadores_flatalizados"]
            print(f"\nResultado: {len(indicadores)} indicadores")
            
            # Contar indicadores com dados
            nao_zero = sum(1 for v in indicadores if v > 0)
            print(f"  - Indicadores com dados: {nao_zero}/{len(indicadores)}")
            print(f"  - Cobertura: {nao_zero/len(indicadores)*100:.1f}%")
            
            # Comparar com Apucarana
            if resultado1:
                ind1 = resultado1["indicadores_flatalizados"]
                nao_zero1 = sum(1 for v in ind1 if v > 0)
                print(f"\nComparacao com Apucarana:")
                print(f"  - Apucarana: {nao_zero1} com dados")
                print(f"  - Sao Paulo: {nao_zero} com dados")
                print(f"  - Diferenca: {abs(nao_zero - nao_zero1)} indicadores")
        else:
            print("ERRO: Processamento falhou")
    
    finally:
        db.close()
        print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(test_local())
