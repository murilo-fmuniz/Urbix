#!/usr/bin/env python3
"""Mapeia o data lake local em backend/data/planilhas e gera um dicionário de dados em Markdown.

Regras Atualizadas (Agressivas):
- Percorre TODAS as abas do Excel (não para na primeira que achar).
- Desce até a linha 40 buscando cabeçalhos (Dynamic Sniffing profundo).
- Retorna múltiplas tabelas válidas dentro do mesmo arquivo.
- Gera dicionario_de_dados_etl.md na raiz do projeto listando tudo.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, List, Dict, Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PLANILHAS_ROOT = PROJECT_ROOT / "backend" / "data" / "planilhas"
REPORT_FILE = PROJECT_ROOT / "dicionario_de_dados_etl.md"

IGNORED_EXTENSIONS = {".ods", ".pdf", ".7z", ".zip", ".rar"}
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".txt", ".gz"}


def normalize_rel_dir(path: Path) -> str:
    try:
        rel = path.relative_to(PLANILHAS_ROOT)
    except ValueError:
        rel = path

    if str(rel) in {".", ""}:
        return "raiz"
    parts = [part for part in rel.parts if part not in {".", ""}]
    return " / ".join(parts) if parts else "raiz"


def is_meaningful_columns(columns: Iterable[str]) -> bool:
    """Exige que pelo menos 40% das colunas não sejam lixo ('Unnamed')."""
    cols = [str(col).strip() for col in columns if str(col).strip()]
    if len(cols) < 2: 
        return False

    meaningful = [col for col in cols if not col.lower().startswith("unnamed")]
    if len(meaningful) < (len(cols) * 0.4):
        return False

    return True


def clean_columns(columns: Iterable[str]) -> list[str]:
    return [" ".join(str(col).split()).strip() for col in columns if str(col).strip()]


def read_csv_headers(path: Path) -> List[Dict[str, Any]]:
    """Lê cabeçalhos de CSV/TXT descendo até 40 linhas."""
    resultados = []
    
    for skiprows in range(40): 
        try:
            df = pd.read_csv(
                path,
                nrows=5, 
                sep=None,
                engine="python",
                skiprows=skiprows,
                on_bad_lines="skip",
                encoding="utf-8-sig",
            )
            cols = clean_columns(df.columns)
            if is_meaningful_columns(cols):
                resultados.append({
                    "sheet": "CSV_Unico",
                    "skiprows": skiprows,
                    "columns": cols
                })
                break # Se achou no CSV, não precisa descer mais linhas
        except Exception:
            continue

    return resultados


def read_excel_headers(path: Path) -> tuple[List[Dict[str, Any]], list[str], Optional[str]]:
    """Varre TODAS as abas do Excel até a linha 40."""
    resultados = []
    try:
        xls = pd.ExcelFile(path)
        sheet_names = list(xls.sheet_names)
    except Exception as exc:
        return [], [], f"{type(exc).__name__}: {exc}"

    # Varre TODAS as abas do arquivo
    for sheet_name in sheet_names:
        for skiprows in range(40): 
            try:
                df = pd.read_excel(
                    xls,
                    sheet_name=sheet_name,
                    nrows=0,
                    skiprows=skiprows,
                )
                cols = clean_columns(df.columns)
                if is_meaningful_columns(cols):
                    resultados.append({
                        "sheet": sheet_name,
                        "skiprows": skiprows,
                        "columns": cols
                    })
                    break # Achou o cabeçalho desta aba, vai para a próxima aba
            except Exception:
                continue

    error_msg = None if resultados else "Cabeçalho vazio ou sujo em todas as abas e linhas."
    return resultados, sheet_names, error_msg


def scan_file(path: Path) -> dict:
    suffix = path.suffix.lower()
    if path.name.lower().endswith(".csv.gz"):
        suffix = ".csv"

    result = {
        "path": path,
        "tables": [],
        "error": None,
        "sheet_names": [],
        "format": suffix,
    }

    try:
        if suffix in IGNORED_EXTENSIONS:
            result["error"] = f"Formato ignorado no escopo: {suffix}"
            return result

        if suffix in {".csv", ".txt"}:
            tabelas = read_csv_headers(path)
            result["tables"] = tabelas
            if not tabelas:
                result["error"] = "Cabeçalho válido não encontrado após 40 linhas."
            return result

        if suffix in {".xlsx", ".xls"}:
            tabelas, sheet_names, error = read_excel_headers(path)
            result["tables"] = tabelas
            result["sheet_names"] = sheet_names
            result["error"] = error
            return result

        result["error"] = f"Formato não suportado: {suffix}"
        return result

    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return result


def collect_files(root: Path) -> list[Path]:
    files: list[Path] = []
    valid_exts = SUPPORTED_EXTENSIONS.union(IGNORED_EXTENSIONS)
    
    for file_path in root.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() in valid_exts or file_path.name.lower().endswith(".csv.gz"):
                files.append(file_path)
    return sorted(files)


def build_report(scan_results: list[dict]) -> str:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for item in scan_results:
        folder_name = normalize_rel_dir(item["path"].parent)
        grouped[folder_name].append(item)

    lines: list[str] = []
    lines.append("# Dicionário de Dados do ETL (Varredura Extrema)")
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
            lines.append(f"### 📄 {path.name}")

            if item["sheet_names"]:
                lines.append(f"- **Total de Abas:** {len(item['sheet_names'])} ({', '.join(item['sheet_names'])})")

            if item["tables"]:
                for tab in item["tables"]:
                    aba = tab["sheet"]
                    skip = tab["skiprows"]
                    cols = tab["columns"]
                    lines.append(f"  - 📁 **Aba/Tabela:** `{aba}` (Cabeçalho detectado na linha {skip})")
                    lines.append(f"    - Total de colunas: {len(cols)}")
                    for col in cols:
                        lines.append(f"      * {col}")
            else:
                lines.append("- ⚠️ Nenhum cabeçalho válido detectado")

            if item["error"]:
                lines.append(f"- 🛑 Status: {item['error']}")

            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if not PLANILHAS_ROOT.exists():
        raise SystemExit(f"Pasta não encontrada: {PLANILHAS_ROOT}")

    files = collect_files(PLANILHAS_ROOT)
    scan_results: list[dict] = []

    print("=" * 80)
    print("MAPEAMENTO EXTREMO DO DATA LAKE")
    print("=" * 80)
    print(f"Raiz: {PLANILHAS_ROOT}")
    print(f"Arquivos candidatos: {len(files)}")
    print()

    for file_path in files:
        if file_path.name.startswith("._") or file_path.name == ".DS_Store":
            continue

        result = scan_file(file_path)
        scan_results.append(result)

        tabelas_encontradas = len(result["tables"])
        status = f"OK ({tabelas_encontradas} tabelas)" if tabelas_encontradas else "SEM DADOS"
        if result["error"]:
            status = f"ERRO ({result['error']})"

        print(f"{file_path.relative_to(PLANILHAS_ROOT)} -> {status}")

    report = build_report(scan_results)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print()
    print(f"Relatório detalhado gerado em: {REPORT_FILE}")
    print("Use o markdown gerado para reconfigurar os ponteiros do etl_config.py!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())