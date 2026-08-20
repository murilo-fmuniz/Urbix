#!/usr/bin/env python3
"""Mapeia o data lake local em backend/data/planilhas e gera um dicionário de dados em Markdown.

Regras Atualizadas:
- Percorre todas as subpastas recursivamente.
- Suporta .csv, .xlsx, .xls, .txt e .csv.gz.
- Faz varredura dinâmica (Dynamic Sniffing) nas primeiras 15 linhas buscando cabeçalhos válidos.
- No Excel, varre as 3 primeiras abas caso a aba inicial seja uma capa/índice.
- Ignora arquivos .ods e .pdf.
- Gera dicionario_de_dados_etl.md na raiz do projeto.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLANILHAS_ROOT = PROJECT_ROOT / "backend" / "data" / "planilhas"
REPORT_FILE = PROJECT_ROOT / "dicionario_de_dados_etl.md"

IGNORED_EXTENSIONS = {".ods", ".pdf", ".7z", ".zip", ".rar"}
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt", ".gz"}


def normalize_rel_dir(path: Path) -> str:
    """Converte a pasta relativa em uma string amigável para o relatório."""
    try:
        rel = path.relative_to(PLANILHAS_ROOT)
    except ValueError:
        rel = path

    if str(rel) in {".", ""}:
        return "raiz"
    parts = [part for part in rel.parts if part not in {".", ""}]
    return " / ".join(parts) if parts else "raiz"


def is_meaningful_columns(columns: Iterable[str]) -> bool:
    """
    Detecta se os cabeçalhos parecem válidos matematicamente.
    Exige que pelo menos 40% das colunas não sejam lixo ('Unnamed').
    """
    cols = [str(col).strip() for col in columns if str(col).strip()]
    if len(cols) < 2:  # Tabelas úteis geralmente têm mais de 1 coluna
        return False

    meaningful = [col for col in cols if not col.lower().startswith("unnamed")]
    
    # Se menos de 40% das colunas possuem nome real, é provavelmente título sujo
    if len(meaningful) < (len(cols) * 0.4):
        return False

    return True


def clean_columns(columns: Iterable[str]) -> list[str]:
    """Limpa quebras de linha e espaços dos nomes das colunas."""
    return [" ".join(str(col).split()).strip() for col in columns if str(col).strip()]


def read_csv_headers(path: Path) -> tuple[list[str], Optional[int], Optional[str]]:
    """Lê cabeçalhos de CSV/TXT testando múltiplas linhas de salto e separadores."""
    
    # O sniffer do pandas funciona melhor se dermos algumas linhas para ele ler
    for skiprows in range(15):  # Testa da linha 0 até a 14
        try:
            df = pd.read_csv(
                path,
                nrows=5, # Lê algumas linhas para o sniffer deduzir o delimitador
                sep=None,
                engine="python",
                skiprows=skiprows,
                on_bad_lines="skip",
                encoding="utf-8-sig",
            )
            cols = clean_columns(df.columns)
            if is_meaningful_columns(cols):
                return cols, skiprows, None
        except Exception:
            continue  # Falhou nesta linha, tenta a próxima

    return [], None, "Cabeçalho válido não encontrado após varredura de 15 linhas."


def read_excel_headers(path: Path) -> tuple[list[str], Optional[int], Optional[str], list[str]]:
    """Lê cabeçalhos de XLS/XLSX buscando em múltiplas abas e linhas."""
    try:
        # Deixa o pandas decidir a engine (openpyxl para xlsx, xlrd para xls)
        xls = pd.ExcelFile(path)
        sheet_names = list(xls.sheet_names)
    except Exception as exc:
        return [], None, f"{type(exc).__name__}: {exc}", []

    # Varre as 3 primeiras abas. A aba 0 frequentemente é capa ou aviso do governo.
    sheets_to_check = sheet_names[:3]

    for sheet_name in sheets_to_check:
        for skiprows in range(15): # Testa da linha 0 até a 14
            try:
                df = pd.read_excel(
                    xls,
                    sheet_name=sheet_name,
                    nrows=0,
                    skiprows=skiprows,
                )
                cols = clean_columns(df.columns)
                if is_meaningful_columns(cols):
                    msg = f"Encontrado na aba '{sheet_name}'" if sheet_name != sheet_names[0] else None
                    return cols, skiprows, msg, sheet_names
            except Exception:
                continue

    return [], None, "Cabeçalho vazio ou sujo nas primeiras planilhas e linhas.", sheet_names


def scan_file(path: Path) -> dict:
    """Extrai metadados mínimos do arquivo sem carregar a base inteira."""
    suffix = path.suffix.lower()
    
    # Tratamento especial para arquivos compactados comuns
    if path.name.lower().endswith(".csv.gz"):
        suffix = ".csv"

    result = {
        "path": path,
        "columns": [],
        "skiprows": None,
        "error": None,
        "sheet_names": [],
        "format": suffix,
    }

    try:
        if suffix in IGNORED_EXTENSIONS:
            result["error"] = f"Formato ignorado no escopo: {suffix}"
            return result

        if suffix in {".csv", ".txt"}:
            cols, skiprows, error = read_csv_headers(path)
            result["columns"] = cols
            result["skiprows"] = skiprows
            result["error"] = error
            return result

        if suffix in {".xlsx", ".xls"}:
            cols, skiprows, error, sheet_names = read_excel_headers(path)
            result["columns"] = cols
            result["skiprows"] = skiprows
            result["error"] = error
            result["sheet_names"] = sheet_names
            return result

        result["error"] = f"Formato não suportado: {suffix}"
        return result

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result


def collect_files(root: Path) -> list[Path]:
    """Coleta os arquivos suportados e ignorados (para fins de log)."""
    files: list[Path] = []
    
    # Tratamento para identificar extensões complexas como .csv.gz
    valid_exts = SUPPORTED_EXTENSIONS.union(IGNORED_EXTENSIONS)
    
    for file_path in root.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() in valid_exts or file_path.name.lower().endswith(".csv.gz"):
                files.append(file_path)
    return sorted(files)


def build_report(scan_results: list[dict]) -> str:
    """Gera o relatório Markdown estruturado."""
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in scan_results:
        folder_name = normalize_rel_dir(item["path"].parent)
        grouped[folder_name].append(item)

    lines: list[str] = []
    lines.append("# Dicionário de Dados do ETL (Varredura Profunda)")
    lines.append("")
    lines.append(f"_Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    lines.append("")
    lines.append(f"- Pasta raiz varrida: `{PLANILHAS_ROOT}`")
    lines.append(f"- Arquivos analisados: {len(scan_results)}")
    lines.append("")

    for folder_name in sorted(grouped.keys()):
        lines.append(f"## {folder_name}")
        lines.append("")

        for item in sorted(grouped[folder_name], key=lambda x: x["path"].name.lower()):
            path = item["path"]
            lines.append(f"### {path.name}")

            if item["sheet_names"]:
                lines.append(f"- Planilhas: {', '.join(item['sheet_names'])}")

            if item["skiprows"] is not None:
                lines.append(f"- skiprows dinâmico detectado: `{item['skiprows']}`")

            if item["columns"]:
                lines.append(f"- Total de colunas: {len(item['columns'])}")
                for col in item["columns"]:
                    lines.append(f"* {col}")
            else:
                lines.append("- Nenhum cabeçalho válido detectado")

            if item["error"]:
                lines.append(f"- Observação/Status: {item['error']}")

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if not PLANILHAS_ROOT.exists():
        raise SystemExit(f"Pasta não encontrada: {PLANILHAS_ROOT}")

    files = collect_files(PLANILHAS_ROOT)
    scan_results: list[dict] = []

    print("=" * 80)
    print("MAPEAMENTO PROFUNDO DO DATA LAKE")
    print("=" * 80)
    print(f"Raiz: {PLANILHAS_ROOT}")
    print(f"Arquivos candidatos: {len(files)}")
    print()

    for file_path in files:
        # Ignora lixos visuais do Mac/Windows
        if file_path.name.startswith("._") or file_path.name == ".DS_Store":
            continue

        result = scan_file(file_path)
        scan_results.append(result)

        status = "OK" if result["columns"] else "SEM COLUNAS"
        if result["error"]:
            status = f"INFO ({result['error']})" if result["columns"] else f"ERRO ({result['error']})"

        print(f"{file_path.relative_to(PLANILHAS_ROOT)} -> {status}")

    report = build_report(scan_results)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print()
    print(f"Relatório gerado em: {REPORT_FILE}")
    print("Fim.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())