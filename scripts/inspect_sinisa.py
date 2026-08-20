#!/usr/bin/env python3
"""Inspeciona as colunas da planilha SINISA_RESIDUOS_Indicadores_2023.xlsx.

Objetivo:
- ler a planilha com pandas
- usar skiprows=5
- descobrir os nomes exatos das colunas para finalizar o ETL de saneamento e resíduos
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SINISA_FILE = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "planilhas"
    / "SINISA_RESIDUOS_Planilhas_2023"
    / "SINISA_RESIDUOS_Planilhas_2023"
    / "SINISA_RESIDUOS_Indicadores_2023.xlsx"
)


def _clean_columns(columns) -> list[str]:
    return [str(col).strip() for col in columns if str(col).strip()]


def _looks_like_real_header(columns: list[str]) -> bool:
    if not columns:
        return False
    upper = [col.upper() for col in columns]
    return any(col.startswith("IFR") or col.startswith("IRS") for col in upper) and "CÓDIGO DO IBGE" in upper


def inspect_sheet(sheet_name: str) -> tuple[int, list[str]]:
    for skiprows in range(5, 11):
        df = pd.read_excel(
            SINISA_FILE,
            sheet_name=sheet_name,
            skiprows=skiprows,
            nrows=0,
            engine="openpyxl",
        )
        columns = _clean_columns(df.columns)
        if _looks_like_real_header(columns):
            return skiprows, columns

    # Fallback: devolve o último teste, mesmo que ainda seja meta-cabeçalho
    df = pd.read_excel(
        SINISA_FILE,
        sheet_name=sheet_name,
        skiprows=5,
        nrows=0,
        engine="openpyxl",
    )
    return 5, _clean_columns(df.columns)


def main() -> int:
    if not SINISA_FILE.exists():
        raise SystemExit(f"Arquivo não encontrado: {SINISA_FILE}")

    xls = pd.ExcelFile(SINISA_FILE, engine="openpyxl")
    print("=" * 90)
    print("INSPEÇÃO SINISA - RESÍDUOS")
    print("=" * 90)
    print(f"Arquivo: {SINISA_FILE}")
    print(f"Total de planilhas: {len(xls.sheet_names)}")
    print()

    for sheet_name in xls.sheet_names:
        try:
            skiprows, columns = inspect_sheet(sheet_name)
            print(f"[{sheet_name}]")
            print(f"skiprows usado: {skiprows}")
            print(f"Colunas ({len(columns)}):")
            for idx, col in enumerate(columns, start=1):
                print(f"  {idx:02d}. {col}")
            print()
        except Exception as exc:
            print(f"[{sheet_name}]")
            print(f"ERRO: {type(exc).__name__}: {exc}")
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
