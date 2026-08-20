#!/usr/bin/env python3
"""Diagnóstico rápido de cobertura de IDs sem SQLAlchemy."""

import sqlite3
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.etl_config import INDICADORES
from app.services.topsis_core import _indicadores_validos_para_topsis


def main():
    # Construir IDs necessários
    validos = set(_indicadores_validos_para_topsis())
    ids = set()
    for _, indicadores in INDICADORES.items():
        for ind, regras in indicadores.items():
            if ind not in validos:
                continue
            tipo = regras.get("tipo_calculo")
            if tipo == "direto":
                ids.add(ind)
            else:
                ids.add(f"{ind}_numerador")
                denominador = regras.get("denominador")
                if denominador:
                    ids.add(denominador)

    ids = sorted(list(ids))
    print(f"IDS_NECESSARIOS|{len(ids)}", flush=True)

    # Consulta direta SQLite
    db_path = backend_dir / "urbix.db"
    conn = sqlite3.connect(str(db_path), timeout=5)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    missing = []
    for id_ind in ids:
        try:
            cur.execute(
                "SELECT COUNT(*) as cnt FROM valores_indicadores WHERE id_indicador = ?",
                (id_ind,)
            )
            row = cur.fetchone()
            cnt = row["cnt"] if row else 0
            print(f"{id_ind}|{cnt}", flush=True)
            if cnt == 0:
                missing.append(id_ind)
        except Exception as e:
            print(f"{id_ind}|ERROR: {e}", flush=True)

    conn.close()

    print(f"MISSING_TOTAL|{len(missing)}", flush=True)
    if missing:
        print(f"MISSING_IDS|{missing}", flush=True)
    else:
        print("MISSING_IDS|[]", flush=True)


if __name__ == "__main__":
    main()
