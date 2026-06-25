from app.routers.topsis import flatten_manual_indicators
from app.schemas import ManualCityIndicators

manual = ManualCityIndicators()
manual.iso_37122.escolas_conectadas_pct = 92.11

flat = flatten_manual_indicators(manual)
print(f"Índice 33: {flat[33]}")
print(f"Total de indicadores: {len(flat)}")
print(f"Posição de escolas_conectadas_pct: 33" if flat[33] == 92.11 else f"Posição ERRADA! Valor em 33 é {flat[33]}")
