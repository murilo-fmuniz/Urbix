from pathlib import Path
import sys

from sqlalchemy import text

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal, Base, engine
from tools.local_etl_service import deduplicar_historico_mesmo_ano, atualizar_snapshot_latest


def run():
    print("=" * 70)
    print("🚀 OTIMIZAÇÃO DE RUNTIME DO BANCO (TOPSIS)")
    print("=" * 70)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print("\n--- CRIANDO ÍNDICES DE APOIO ---")
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_vi_cidade_indicador_ano_id ON valores_indicadores (codigo_ibge, id_indicador, ano_referencia DESC, id DESC)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_vi_cidade_indicador ON valores_indicadores (codigo_ibge, id_indicador)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_municipios_nome ON municipios (nome)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS ix_municipios_estado ON municipios (estado)"))
        db.commit()
        print("✅ Índices criados/confirmados")

        deduplicar_historico_mesmo_ano(db)
        atualizar_snapshot_latest(db)

        total = db.execute(text("SELECT COUNT(*) FROM valores_indicadores")).scalar() or 0
        latest = db.execute(text("SELECT COUNT(*) FROM valores_indicadores_latest")).scalar() or 0
        print(f"\n📊 Total valores_indicadores: {total}")
        print(f"📊 Total valores_indicadores_latest: {latest}")

        print("\n🎉 Otimização concluída.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
