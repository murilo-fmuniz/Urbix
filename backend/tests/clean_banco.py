from app.database import SessionLocal
from app.models import CityManualData

db = SessionLocal()

# Limpar dados de Apucarana e São Paulo
apucarana = db.query(CityManualData).filter_by(codigo_ibge='4101408').first()
if apucarana:
    apucarana.indicadores_manuais = None
    db.commit()
    print("✅ Apucarana limpo")

saopaulo = db.query(CityManualData).filter_by(codigo_ibge='3550308').first()
if saopaulo:
    saopaulo.indicadores_manuais = None
    db.commit()
    print("✅ São Paulo limpo")

print("✅ Banco limpo com sucesso!")
