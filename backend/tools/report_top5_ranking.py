from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database import SessionLocal
from app.models import Indicador, Municipio
from app.services.topsis_core import aplicar_topsis, preparar_matriz_decisao

with SessionLocal() as db:
    cidades = [row[0] for row in db.query(Municipio.codigo_ibge).order_by(Municipio.codigo_ibge).all()]
    nomes = {row.codigo_ibge: row.nome for row in db.query(Municipio.codigo_ibge, Municipio.nome).all()}
    print(f"MUNICIPIOS={len(cidades)}")
    matriz = preparar_matriz_decisao(cidades, [], db)
    indicadores = list(matriz.columns)
    metadados = {item.id: item for item in db.query(Indicador).all()}
    pesos = {coluna: metadados[coluna].peso if coluna in metadados else 0.02 for coluna in indicadores}
    impactos = {coluna: metadados[coluna].impacto if coluna in metadados else 1 for coluna in indicadores}
    for resultado in aplicar_topsis(matriz, pesos, impactos)[:5]:
        codigo = resultado["codigo_ibge"]
        print(f"TOP|{codigo}|{nomes.get(codigo, ' desconhecido')}|{resultado['pontuacao_topsis']:.4f}|indicadores={len(resultado['valores_calculados'])}")
    print(f"INDICADORES={len(indicadores)}|{','.join(indicadores)}")
