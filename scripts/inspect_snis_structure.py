#!/usr/bin/env python3
"""Inspeciona a estrutura de arquivos SNIS sem carregar os dados completos.

Uso:
    python scripts/inspect_snis_structure.py
    python scripts/inspect_snis_structure.py snis_dados.csv
    python scripts/inspect_snis_structure.py snis_dados.xlsx
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "planilhas"


def _find_files() -> list[Path]:
    if not BASE_DIR.exists():
        return []

    files: list[Path] = []
    for ext in ("*.csv", "*.xlsx", "*.xls", "*.ods"):
        files.extend(sorted(BASE_DIR.rglob(ext)))

    # Preferir formatos mais estáveis/rápidos quando houver arquivos irmãos com mesmo stem
    preferred_by_stem: dict[str, Path] = {}
    priority = {".csv": 0, ".xlsx": 1, ".xls": 2, ".ods": 3}

    for file_path in files:
        stem_key = str(file_path.with_suffix(""))
        current = preferred_by_stem.get(stem_key)
        if current is None or priority[file_path.suffix.lower()] < priority[current.suffix.lower()]:
            preferred_by_stem[stem_key] = file_path

    return sorted(preferred_by_stem.values())


def _print_columns(columns: Iterable[str]) -> None:
    cols = list(columns)
    print(f"Total de colunas: {len(cols)}")
    for idx, col in enumerate(cols, start=1):
        print(f"{idx}. {col}")


def _is_meaningful(columns: Iterable[str]) -> bool:
    cols = [str(c).strip() for c in columns if str(c).strip()]
    if not cols:
        return False

    lowered = [c.lower() for c in cols]
    keywords = ("ibge", "codigo", "código", "agua", "água", "lixo", "residuo", "resíduo", "destin", "recurso", "municip")
    return any(any(k in c for k in keywords) for c in lowered)


def inspect_csv(path: Path) -> None:
    print(f"\nArquivo: {path.name}")

    header_found = False
    for skiprows in range(0, 6):
        try:
            df = pd.read_csv(
                path,
                sep=";",
                nrows=0,
                skiprows=skiprows,
                on_bad_lines="skip",
                encoding="utf-8-sig",
                engine="python",
            )
            if _is_meaningful(df.columns):
                print(f"Cabeçalho detectado com skiprows={skiprows}")
                _print_columns(df.columns)
                header_found = True
                break
        except Exception:
            continue

    if not header_found:
        try:
            df = pd.read_csv(
                path,
                sep=";",
                nrows=0,
                on_bad_lines="skip",
                encoding="utf-8-sig",
                engine="python",
            )
            print("Cabeçalho lido sem skiprows adaptativo")
            _print_columns(df.columns)
        except Exception as e:
            print(f"Falha ao ler CSV: {type(e).__name__}: {e}")


def inspect_excel(path: Path) -> None:
    print(f"\nArquivo: {path.name}")

    try:
        xls = pd.ExcelFile(path)
        print(f"Planilhas encontradas: {', '.join(xls.sheet_names)}")
    except Exception as e:
        print(f"Falha ao abrir planilha: {type(e).__name__}: {e}")
        return

    for sheet in xls.sheet_names:
        print(f"\n[Planilha] {sheet}")
        header_found = False

        for skiprows in range(0, 6):
            try:
                df = pd.read_excel(path, sheet_name=sheet, nrows=0, skiprows=skiprows)
                if _is_meaningful(df.columns):
                    print(f"Cabeçalho detectado com skiprows={skiprows}")
                    _print_columns(df.columns)
                    header_found = True
                    break
            except Exception:
                continue

        if not header_found:
            try:
                df = pd.read_excel(path, sheet_name=sheet, nrows=0)
                print("Cabeçalho lido sem skiprows adaptativo")
                _print_columns(df.columns)
            except Exception as e:
                print(f"Falha ao ler planilha: {type(e).__name__}: {e}")


def main() -> int:
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if not target.is_absolute():
            target = BASE_DIR / target
        files = [target]
    else:
        files = _find_files()

    print("=" * 80)
    print("INSPEÇÃO DE ESTRUTURA - SNIS")
    print("=" * 80)

    if not BASE_DIR.exists():
        print(f"Pasta planilhas não encontrada: {BASE_DIR}")
        return 1

    if not files:
        print(f"Nenhum arquivo CSV/XLSX/ODS encontrado em {BASE_DIR}")
        return 1

    for file_path in files:
        if not file_path.exists():
            print(f"\nArquivo não encontrado: {file_path}")
            continue

        try:
            suffix = file_path.suffix.lower()
            if suffix == ".csv":
                inspect_csv(file_path)
            elif suffix in {".xlsx", ".xls", ".ods"}:
                inspect_excel(file_path)
            else:
                print(f"\nFormato não suportado: {file_path.name}")
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"\nFalha ao inspecionar {file_path.name}: {type(e).__name__}: {e}")

    print("\n" + "=" * 80)
    print("INSPEÇÃO CONCLUÍDA")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
