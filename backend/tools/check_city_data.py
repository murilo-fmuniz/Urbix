import sys
from pathlib import Path

# Garante que o Python ache a pasta app/
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal
from sqlalchemy import text

def run():
    db = SessionLocal()
    cidades = {'4208302': 'Itapema', '3554102': 'Taubaté'}
    
    print("=" * 50)
    print("🕵️‍♂️ RAIO-X DOS DADOS NO BANCO NEON")
    print("=" * 50)

    for ibge, nome in cidades.items():
        print(f"\n🏙️  DADOS SALVOS PARA: {nome} ({ibge})")
        res = db.execute(text(f"""
            SELECT id_indicador, valor 
            FROM valores_indicadores_latest 
            WHERE codigo_ibge = '{ibge}' 
            ORDER BY id_indicador
        """)).fetchall()
        
        if not res:
            print("Nenhum dado encontrado!")
        else:
            for row in res:
                print(f" - {row[0]}: {row[1]}")
                
    db.close()

if __name__ == "__main__":
    run()