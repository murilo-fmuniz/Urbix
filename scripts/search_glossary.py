#!/usr/bin/env python3
"""Busca palavras-chave no glossário SINISA e imprime Código + Descrição das linhas que baterem.

Uso:
    python scripts/search_glossary.py
    python scripts/search_glossary.py --file "caminho/para/Glossario.xlsx"

O script tenta localizar automaticamente um arquivo de glossário dentro de:
backend/data/planilhas/SINISA_RESIDUOS_Planilhas_2023/SINISA_RESIDUOS_Planilhas_2023

Se o arquivo for PDF, o script avisa e encerra. Se for XLSX, ele percorre as abas e
faz busca case-insensitive nas descrições.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SINISA_DIR = (
    PROJECT_ROOT
    / "backend"
    / "data"
    / "planilhas"
    / "SINISA_RESIDUOS_Planilhas_2023"
    / "SINISA_RESIDUOS_Planilhas_2023"
)

KEYWORDS_INDICADOR_20 = [
    "energia",
    "biogás",
    "biogas",
    "recuperação energética",
    "recuperacao energetica",
    "valorização",
    "valorizacao",
]

KEYWORDS_INDICADOR_30 = [
    "sensor",
    "inteligente",
    "monitoramento",
    "telegestão",
    "telegestao",
    "conteinerização",
    "conteinerizacao",
]

ALL_KEYWORDS = KEYWORDS_INDICADOR_20 + KEYWORDS_INDICADOR_30


def find_default_glossary_file() -> Optional[Path]:
    """Tenta localizar automaticamente um arquivo de glossário SINISA."""
    if not SINISA_DIR.exists():
        return None

    preferred_patterns = [
        "*gloss*.*",
        "*Gloss*.*",
        "*informacoes*.*",
        "*informação*.*",
        "*informacao*.*",
    ]

    candidates: list[Path] = []
    for pattern in preferred_patterns:
        candidates.extend([p for p in SINISA_DIR.rglob(pattern) if p.is_file()])

    # Remove duplicatas preservando ordem
    unique_candidates: list[Path] = []
    seen = set()
    for path in candidates:
        key = str(path).lower()
        if key not in seen:
            unique_candidates.append(path)
            seen.add(key)

    # Prioriza nomes com glossário/informações
    def sort_key(path: Path) -> tuple[int, str]:
        name = path.name.lower()
        priority = 0
        if "gloss" in name:
            priority = 0
        elif "inform" in name:
            priority = 1
        else:
            priority = 2
        return (priority, name)

    unique_candidates.sort(key=sort_key)
    return unique_candidates[0] if unique_candidates else None


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def row_matches(row_text: str, keywords: Iterable[str]) -> bool:
    text = row_text.lower()
    return any(keyword.lower() in text for keyword in keywords)


def find_code_and_description(df: pd.DataFrame) -> tuple[Optional[str], Optional[str]]:
    """Tenta identificar colunas de código e descrição por nome."""
    code_col = None
    desc_col = None

    for col in df.columns:
        col_text = normalize_text(col).lower()
        if code_col is None and any(token in col_text for token in ["código", "codigo", "cod", "ifr", "irs", "id"]):
            code_col = col
        if desc_col is None and any(token in col_text for token in ["descr", "defini", "texto", "nome", "indicador", "campo"]):
            desc_col = col

    # fallback: primeira coluna e segunda coluna
    if code_col is None and len(df.columns) >= 1:
        code_col = df.columns[0]
    if desc_col is None and len(df.columns) >= 2:
        desc_col = df.columns[1]

    return code_col, desc_col


def inspect_sheet(sheet_name: str, file_path: Path, keywords: list[str]) -> list[tuple[str, str, str]]:
    """Retorna lista de matches como (codigo, descricao, keyword_hit)."""
    matches: list[tuple[str, str, str]] = []

    # O glossário costuma ser pequeno; lemos algumas linhas de preview para achar o cabeçalho.
    for skiprows in range(0, 11):
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                skiprows=skiprows,
                dtype=str,
                engine="openpyxl",
            )
        except Exception:
            continue

        if df.empty:
            continue

        code_col, desc_col = find_code_and_description(df)
        if code_col is None or desc_col is None:
            continue

        for _, row in df.iterrows():
            code = normalize_text(row.get(code_col))
            description = normalize_text(row.get(desc_col))
            row_blob = " | ".join(normalize_text(v) for v in row.values)
            if not row_blob.strip():
                continue

            if row_matches(row_blob, keywords):
                hit = next((kw for kw in keywords if kw.lower() in row_blob.lower()), "")
                matches.append((code, description, hit))

        if matches:
            return matches

    return matches


def main() -> int:
    parser = argparse.ArgumentParser(description="Busca palavras-chave no glossário SINISA.")
    parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Caminho para o arquivo do glossário (XLSX ou PDF). Se omitido, o script tenta localizar automaticamente.",
    )
    args = parser.parse_args()

    file_path = Path(args.file).expanduser().resolve() if args.file else find_default_glossary_file()

    if file_path is None:
        raise SystemExit(
            "Nenhum arquivo de glossário encontrado. Passe --file com o caminho do XLSX/PDF do glossário."
        )

    if not file_path.exists():
        raise SystemExit(f"Arquivo não encontrado: {file_path}")

    print("=" * 100)
    print("BUSCA NO GLOSSÁRIO SINISA")
    print("=" * 100)
    print(f"Arquivo: {file_path}")
    print()

    if file_path.suffix.lower() == ".pdf":
        raise SystemExit(
            "O arquivo localizado é PDF. Este script foi feito para XLSX. Se você quiser, eu posso criar uma versão para PDF também."
        )

    xls = pd.ExcelFile(file_path, engine="openpyxl")

    keywords_groups = [
        ("[20] Energia de Resíduos", KEYWORDS_INDICADOR_20),
        ("[30] Lixeiras com Sensores", KEYWORDS_INDICADOR_30),
    ]

    total_matches = 0

    for sheet_name in xls.sheet_names:
        print(f"## Aba: {sheet_name}")
        sheet_has_matches = False

        for label, keywords in keywords_groups:
            matches = inspect_sheet(sheet_name, file_path, keywords)
            if not matches:
                continue

            sheet_has_matches = True
            print(f"\n{label}")
            for code, description, hit in matches:
                total_matches += 1
                print(f"- Código: {code or '(não identificado)'}")
                print(f"  Descrição: {description or '(não identificada)'}")
                if hit:
                    print(f"  Match: {hit}")

        if not sheet_has_matches:
            print("- Nenhum match encontrado nesta aba.")

        print()

    print("=" * 100)
    print(f"Total de matches encontrados: {total_matches}")
    print("Fim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
