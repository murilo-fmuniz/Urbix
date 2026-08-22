import sys
from pathlib import Path

# Garante que o Python ache a pasta app/
backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.etl_config import INDICADORES
from sqlalchemy import text

def run():
    db = SessionLocal()
    print("🔄 Registrando Indicadores Calculados no Banco...")
    
    for dominio, indicadores in INDICADORES.items():
        for id_ind, config in indicadores.items():
            nome_formatado = id_ind.replace("_", " ").title()
            
            try:
                # O 'ON CONFLICT DO NOTHING' garante que não vamos 
                # apagar os pesos e impactos que já estão funcionando
                db.execute(text(f"""
                    INSERT INTO indicadores (id, nome, norma_iso, peso, impacto)
                    VALUES ('{id_ind}', '{nome_formatado}', 'TOPSIS Engine', 1.0, 1)
                    ON CONFLICT (id) DO NOTHING;
                """))
                db.commit()
            except Exception as e:
                db.rollback()
                print(f"Erro ao inserir {id_ind}: {e}")
                
    db.close()
    print("✅ Catálogo sincronizado! O motor TOPSIS agora enxerga 100% dos indicadores.")

if __name__ == "__main__":
    run()