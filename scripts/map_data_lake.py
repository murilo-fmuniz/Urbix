#!/usr/bin/env python3
"""
Mapeia o data lake local em backend/data/planilhas e gera um dicionário de dados em Markdown.
Versão Turbinada: Força bruta em Encodings e Separadores para arquivos Governamentais.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, List, Dict, Any
import warnings

import pandas as pd

# Ignora os warnings chatos do Pandas sobre extensões de Excel antigas
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

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
    """Tenta ler CSV/TXT combinando Encodings e Separadores, descendo até 40 linhas."""
    resultados = []
    encodings = ["utf-8", "latin1", "iso-8859-1", "cp1252", "utf-8-sig"]
    separators = [";", ",", "\t", "|"]
    
    is_gz = path.name.lower().endswith('.gz')
    compression = 'gzip' if is_gz else None

    for skiprows in range(40): 
        success = False
        for enc in encodings:
            if success: break
            for sep in separators:
                try:
                    df = pd.read_csv(
                        path,
                        nrows=5, 
                        sep=sep,
                        skiprows=skiprows,
                        encoding=enc,
                        compression=compression,
                        on_bad_lines="skip",
                        engine="python" if sep == "|" else "c"
                    )
                    cols = clean_columns(df.columns)
                    if is_meaningful_columns(cols):
                        resultados.append({
                            "sheet": "CSV/TXT",
                            "skiprows": skiprows,
                            "encoding": enc,
                            "separator": sep,
                            "columns": cols
                        })
                        success = True
                        break # Achou o separador certo
                except Exception:
                    continue
        if success:
            break # Achou no CSV, não precisa descer mais linhas

    return resultados


def read_excel_headers(path: Path) -> tuple[List[Dict[str, Any]], list[str], Optional[str]]:
    """Varre TODAS as abas do Excel até a linha 40."""
    resultados = []
    try:
        # Usa xlrd para .xls antigos (padrão IBGE) e openpyxl para .xlsx
        engine = "xlrd" if path.suffix.lower() == ".xls" else "openpyxl"
        xls = pd.ExcelFile(path, engine=engine)
        sheet_names = list(xls.sheet_names)
    except Exception as exc:
        return [], [], f"{type(exc).__name__}: {exc}"

    for sheet_name in sheet_names:
        for skiprows in range(40): 
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name, nrows=0, skiprows=skiprows)
                cols = clean_columns(df.columns)
                if is_meaningful_columns(cols):
                    resultados.append({
                        "sheet": sheet_name,
                        "skiprows": skiprows,
                        "columns": cols
                    })
                    break 
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
    lines.append("# 📊 Dicionário de Dados do ETL Urbix")
    lines.append("")
    lines.append(f"_Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    lines.append("")
    lines.append(f"- **Pasta raiz varrida:** `{PLANILHAS_ROOT}`")
    lines.append(f"- **Arquivos analisados:** {len(scan_results)}")
    lines.append("")

    for folder_name in sorted(grouped.keys()):
        lines.append(f"## 📁 {folder_name}")
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
                    
                    meta_info = f"(Cabeçalho na linha {skip})"
                    if aba == "CSV/TXT":
                        meta_info = f"(Linha {skip} | Sep: '{tab['separator']}' | Enc: {tab['encoding']})"
                    
                    lines.append(f"  - 📌 **Tabela Mapeada:** `{aba}` {meta_info}")
                    lines.append(f"    - Total de colunas: {len(cols)}")
                    lines.append("    - **Colunas:**")
                    for col in cols:
                        lines.append(f"      * `{col}`")
            else:
                lines.append("- ⚠️ Nenhum cabeçalho válido detectado")

            if item["error"]:
                lines.append(f"- 🛑 Status: {item['error']}")

            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    if not PLANILHAS_ROOT.exists():
        raise SystemExit(f"Pasta não encontrada: {PLANILHAS_ROOT}")

    files = collect_files(PLANILHAS_ROOT)
    scan_results: list[dict] = []

    print("=" * 80)
    print("🚀 INICIANDO MAPEAMENTO EXTREMO DO DATA LAKE")
    print("=" * 80)
    print(f"Raiz: {PLANILHAS_ROOT}")
    print(f"Arquivos candidatos: {len(files)}")
    print()

    for file_path in files:
        if file_path.name.startswith("._") or file_path.name == ".DS_Store":
            continue

        print(f"Buscando em: {file_path.name}...", end=" ")
        result = scan_file(file_path)
        scan_results.append(result)

        tabelas_encontradas = len(result["tables"])
        if tabelas_encontradas:
            print(f"✅ OK ({tabelas_encontradas} tabelas)")
        elif result["error"]:
            print(f"❌ ERRO ({result['error']})")
        else:
            print("⚠️ SEM DADOS")

    report = build_report(scan_results)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print()
    print(f"🎉 Relatório detalhado gerado em: {REPORT_FILE}")
    print("Abra o arquivo .md para ver os nomes exatos das colunas e atualizar o etl_config.py!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())