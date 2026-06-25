"""
Script para verificar dados no banco de dados e testar o TOPSIS
"""

import sys
sys.path.insert(0, 'd:\\Docs\\Faculdade\\IC\\Urbix\\backend')

from app.database import SessionLocal
from app.models import CityManualData

def check_database():
    """Verifica dados no banco para Apucarana e São Paulo"""
    db = SessionLocal()
    
    try:
        # Verificar Apucarana
        apucarana = db.query(CityManualData).filter_by(codigo_ibge="4101408").first()
        print(f"\n[APUCARANA] (4101408):")
        if apucarana:
            print(f"   OK - Encontrado no banco")
            print(f"   Data: {apucarana.data_atualizacao}")
            if apucarana.indicadores_manuais:
                print(f"   Indicadores: {len(apucarana.indicadores_manuais)} campos")
                # Mostrar estrutura
                if isinstance(apucarana.indicadores_manuais, dict):
                    for iso_classe, dados in apucarana.indicadores_manuais.items():
                        if isinstance(dados, dict):
                            print(f"      {iso_classe}: {len(dados)} campos")
        else:
            print(f"   ERRO - NAO encontrado no banco")
        
        # Verificar São Paulo
        sp = db.query(CityManualData).filter_by(codigo_ibge="3550308").first()
        print(f"\n[SAO PAULO] (3550308):")
        if sp:
            print(f"   OK - Encontrado no banco")
            print(f"   Data: {sp.data_atualizacao}")
            if sp.indicadores_manuais:
                print(f"   Indicadores: {len(sp.indicadores_manuais)} campos")
                if isinstance(sp.indicadores_manuais, dict):
                    for iso_classe, dados in sp.indicadores_manuais.items():
                        if isinstance(dados, dict):
                            print(f"      {iso_classe}: {len(dados)} campos")
        else:
            print(f"   ERRO - NAO encontrado no banco")
        
        # Contar total de cidades
        total = db.query(CityManualData).count()
        print(f"\nTotal de cidades no banco: {total}")
        
        # Listar todas as cidades
        if total > 0:
            cidades = db.query(CityManualData).all()
            print(f"   Cidades com dados:")
            for cidade in cidades:
                print(f"      - {cidade.codigo_ibge} - {cidade.nome_cidade}")
    
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("VERIFICAÇÃO DE DADOS NO BANCO DE DADOS")
    print("=" * 60)
    check_database()
