from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import func

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.etl_config import INDICADORES
from app.models import ValorIndicador
from app.services.topsis_core import _indicadores_validos_para_topsis


def build_ids_necessarios() -> set[str]:
    validos = set(_indicadores_validos_para_topsis())
    ids = set()
    for _, indicadores in INDICADORES.items():
        for ind, regras in indicadores.items():
            if ind not in validos:
                continue
            if regras.get("tipo_calculo") == "direto":
                ids.add(ind)
            else:
                ids.add(f"{ind}_numerador")
                denominador = regras.get("denominador")
                if denominador:
                    ids.add(denominador)
    return ids


def main() -> None:
    ids = sorted(build_ids_necessarios())
    db = SessionLocal()
    try:
        rows = (
            db.query(ValorIndicador.id_indicador, func.count(ValorIndicador.id))
            .filter(ValorIndicador.id_indicador.in_(ids))
            .group_by(ValorIndicador.id_indicador)
            .all()
        )
        counts = {id_ind: int(total) for id_ind, total in rows}
    finally:
        db.close()

    missing = []
    print(f"IDS_NECESSARIOS|{len(ids)}")
    for i in ids:
        c = counts.get(i, 0)
        print(f"{i}|{c}")
        if c == 0:
            missing.append(i)

    print(f"MISSING_TOTAL|{len(missing)}")
    print(f"MISSING_IDS|{missing}")


if __name__ == "__main__":
    main()
