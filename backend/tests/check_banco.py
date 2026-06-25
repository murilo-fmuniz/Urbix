from app.database import SessionLocal
from app.models import CityManualData

db = SessionLocal()
city = db.query(CityManualData).filter_by(codigo_ibge='4101408').first()

if city and city.indicadores_manuais:
    iso37120 = city.indicadores_manuais.get('iso_37120', {})
    iso37122 = city.indicadores_manuais.get('iso_37122', {})
    iso37123 = city.indicadores_manuais.get('iso_37123', {})
    
    print(f"relacao_estudante_professor: {iso37120.get('relacao_estudante_professor')}")
    print(f"ideb_anos_iniciais: {iso37120.get('ideb_anos_iniciais')}")
    print(f"escolas_conectadas_pct: {iso37122.get('escolas_conectadas_pct')}")
else:
    print("Nenhum dado encontrado no banco")
