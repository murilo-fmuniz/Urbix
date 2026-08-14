import json
import re
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PLANILHAS_ROOT = PROJECT_ROOT / "backend" / "data" / "planilhas"
OUTPUT_FILE = PROJECT_ROOT / "backend" / "app" / "data" / "indicators_master.json"
CATALOG_FILE = PROJECT_ROOT / "backend" / "app" / "data" / "ibge_catalog.json"

def _resolve_first_existing(paths: list[Path]) -> Optional[Path]:
    for path in paths:
        if path.exists():
            return path
    return None

def normalize_code(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = re.sub(r"\D", "", text)
    if len(text) >= 7:
        return text[-7:]
    return text.zfill(7)

def clean_numeric(value: Any) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    text = str(value).strip().replace("%", "").replace(" ", "")
    if "." in text and "," in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except Exception:
        return None

def _load_ibge_names() -> Dict[str, str]:
    if not CATALOG_FILE.exists():
        return {}
    try:
        with CATALOG_FILE.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict):
            if isinstance(payload.get("municipalities"), list):
                result: Dict[str, str] = {}
                for item in payload["municipalities"]:
                    if not isinstance(item, dict):
                        continue
                    code = item.get("codigo_ibge") or item.get("codigo") or item.get("id")
                    name = item.get("nome") or item.get("municipio")
                    if code and name:
                        result[str(code).zfill(7)] = str(name).split(" - ")[0]
                return result
            return {str(k).zfill(7): str(v).split(" - ")[0] for k, v in payload.items()}
        if isinstance(payload, list):
            result: Dict[str, str] = {}
            for item in payload:
                if isinstance(item, dict):
                    code = item.get("codigo_ibge") or item.get("codigo") or item.get("id")
                    name = item.get("nome") or item.get("municipio")
                    if code and name:
                        result[str(code).zfill(7)] = str(name).split(" - ")[0]
            return result
    except Exception:
        pass
    return {}

def _find_code_column(columns) -> Optional[str]:
    for col in columns:
        normalized = str(col).strip().lower()
        if any(token in normalized for token in ["codigo", "codmun", "ibge", "municipio", "município"]):
            return str(col)
    return None

def _find_value_column(df: pd.DataFrame, hints) -> Optional[str]:
    for col in df.columns:
        normalized = str(col).strip().lower()
        if any(token in normalized for token in hints):
            return str(col)
    for col in df.columns:
        if str(col).strip().lower() in {"codigo", "cod", "ibge", "municipio", "município"}:
            continue
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                return str(col)
        except Exception:
            pass
    return None

def _read_excel(path: Path) -> Optional[pd.DataFrame]:
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception:
        try:
            return pd.read_excel(path, engine="odf")
        except Exception:
            return None

def process_broadband(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    try:
        for chunk in pd.read_csv(path, sep=";", chunksize=10000, encoding="utf-8-sig", on_bad_lines="skip", dtype=str):
            code_col = _find_code_column(chunk.columns)
            value_col = _find_value_column(chunk, ["densidade", "banda", "acesso"])
            if not code_col or not value_col:
                continue
            for _, row in chunk.iterrows():
                code = normalize_code(row.get(code_col))
                if not code:
                    continue
                value = clean_numeric(row.get(value_col))
                if value is None:
                    continue
                entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
                entry["indicadores"]["densidade_banda_larga"] = round(value, 4)
    except Exception:
        pass

def process_atu(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    df = _read_excel(path)
    if df is None:
        return
    df.columns = [str(col).strip() for col in df.columns]
    code_col = _find_code_column(df.columns)
    value_col = _find_value_column(df, ["atu", "atendimento", "taxa", "alunos", "turma"])
    if not code_col or not value_col:
        return
    for _, row in df.iterrows():
        code = normalize_code(row.get(code_col))
        if not code:
            continue
        value = clean_numeric(row.get(value_col))
        if value is None:
            continue
        entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
        entry["indicadores"]["atu_2025"] = round(value, 4)

def process_tdi(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    df = _read_excel(path)
    if df is None:
        return
    df.columns = [str(col).strip() for col in df.columns]
    code_col = _find_code_column(df.columns)
    value_col = _find_value_column(df, ["tdi", "distorc", "serie", "indice"])
    if not code_col or not value_col:
        return
    for _, row in df.iterrows():
        code = normalize_code(row.get(code_col))
        if not code:
            continue
        value = clean_numeric(row.get(value_col))
        if value is None:
            continue
        entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
        entry["indicadores"]["tdi_2025"] = round(value, 4)

def process_population(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    df = _read_excel(path)
    if df is None:
        return
    df.columns = [str(col).strip() for col in df.columns]
    code_col = _find_code_column(df.columns)
    value_col = _find_value_column(df, ["pop", "habit", "estim", "pessoa"])
    if not code_col or not value_col:
        return
    for _, row in df.iterrows():
        code = normalize_code(row.get(code_col))
        if not code:
            continue
        value = clean_numeric(row.get(value_col))
        if value is None:
            continue
        entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
        entry["indicadores"]["populacao_estimada_2025"] = int(value)

def process_cnes(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    try:
        for chunk in pd.read_csv(path, encoding="utf-8-sig", on_bad_lines="skip", sep=None, engine="python", chunksize=50000, dtype=str):
            code_col = None
            for col in chunk.columns:
                normalized = str(col).strip().lower()
                if "ibge" in normalized:
                    code_col = str(col)
                    break
            if not code_col:
                continue
            counts: Dict[str, int] = {}
            for _, row in chunk.iterrows():
                code = normalize_code(row.get(code_col))
                if not code:
                    continue
                counts[code] = counts.get(code, 0) + 1
            for code, count in counts.items():
                entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
                entry["indicadores"]["num_hospitais"] = int(count)
                if "populacao_estimada_2025" in entry["indicadores"]:
                    pop = entry["indicadores"]["populacao_estimada_2025"]
                    entry["indicadores"]["hospitais_por_100k"] = round((count / pop) * 100_000, 4) if pop else 0.0
    except Exception:
        pass

def process_fbsp(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    try:
        for chunk in pd.read_csv(path, sep=",", chunksize=10000, encoding="utf-8-sig", on_bad_lines="skip", dtype=str):
            code_col = _find_code_column(chunk.columns)
            val_homicidio = _find_value_column(chunk, ["homicidio_doloso"])
            
            if not code_col or not val_homicidio:
                continue
                
            for _, row in chunk.iterrows():
                code = normalize_code(row.get(code_col))
                if not code:
                    continue
                v_hom = clean_numeric(row.get(val_homicidio))
                if v_hom is not None:
                    entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
                    pop = entry["indicadores"].get("populacao_estimada_2025")
                    if pop and pop > 0:
                        entry["indicadores"]["homicidios_100k"] = round((v_hom / pop) * 100_000, 4)
    except Exception:
        pass

def process_pib(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    df = _read_excel(path)
    if df is None:
        return
    df.columns = [str(col).strip() for col in df.columns]
    
    code_col = _find_code_column(df.columns)
    val_pib = _find_value_column(df, ["produto interno bruto per capita"])
    
    if not code_col or not val_pib:
        return
        
    for _, row in df.iterrows():
        code = normalize_code(row.get(code_col))
        if not code:
            continue
        v_pib = clean_numeric(row.get(val_pib))
        if v_pib is not None:
            entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
            entry["indicadores"]["pib_per_capita"] = v_pib

def process_sinisa(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    """Extrai Lixeiras Inteligentes e Energia de Resíduos buscando o cabeçalho dinamicamente."""
    try:
        # Lê o arquivo sem assumir onde está o cabeçalho
        df = pd.read_excel(path, header=None, engine="openpyxl")
        header_idx = 0
        
        # Varre linha por linha até achar a palavra "ibge", "código" ou "município"
        for idx, row in df.iterrows():
            row_str = " ".join([str(x).lower() for x in row.values])
            if "código" in row_str or "ibge" in row_str or "município" in row_str:
                header_idx = idx
                break
                
        # Define a linha encontrada como o cabeçalho real e corta o "lixo" de cima
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx+1:]
        
        code_col = _find_code_column(df.columns)
        if not code_col: 
            return
            
        for _, row in df.iterrows():
            code = normalize_code(row.get(code_col))
            if not code: 
                continue
            entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
            v_lixo = clean_numeric(row.get("IRS0004"))
            v_energia = clean_numeric(row.get("IRS3005"))
            
            if v_lixo is not None: 
                entry["indicadores"]["lixeiras_com_sensores"] = v_lixo
            if v_energia is not None: 
                entry["indicadores"]["energia_de_residuos"] = v_energia
    except Exception:
        pass


def process_cetic(path: Path, municipios: Dict[str, Dict[str, Any]]) -> None:
    try:
        df = pd.read_excel(path, skiprows=5, engine="openpyxl", dtype=str)
        code_col = _find_code_column(df.columns)
        if not code_col:
            return
        for _, row in df.iterrows():
            code = normalize_code(row.get(code_col))
            if not code:
                continue
            entry = municipios.setdefault(code, {"nome": "", "indicadores": {}})
            v_prontuario = clean_numeric(row.get("B0"))
            v_tele = clean_numeric(row.get("C2"))
            if v_prontuario is not None: 
                entry["indicadores"]["prontuario_eletronico_pct"] = v_prontuario
            if v_tele is not None: 
                entry["indicadores"]["consultas_remotas_100k"] = v_tele
    except Exception:
        pass


def run_local_etl() -> Dict[str, Any]:
    municipios: Dict[str, Dict[str, Any]] = {}

    broadband_path = _resolve_first_existing([
        PLANILHAS_ROOT / "acessos_banda_larga_fixa" / "Densidade_Banda_Larga_Fixa.csv",
        PLANILHAS_ROOT / "Acesso_Banda_Larga" / "Densidade_Banda_Larga_Fixa.csv",
    ])
    if broadband_path is not None:
        process_broadband(broadband_path, municipios)

    atu_path = _resolve_first_existing([
        PLANILHAS_ROOT / "ATU_2025_MUNICIPIOS" / "ATU_MUNICIPIOS_2025.xlsx",
        PLANILHAS_ROOT / "ATU_2025_MUNICIPIOS" / "ATU_MUNICIPIOS_2025.ods",
    ])
    if atu_path is not None:
        process_atu(atu_path, municipios)

    tdi_path = _resolve_first_existing([
        PLANILHAS_ROOT / "TDI_2025_MUNICIPIOS" / "TDI_MUNICIPIOS_2025.xlsx",
        PLANILHAS_ROOT / "TDI_2025_MUNICIPIOS" / "TDI_MUNICIPIOS_2025.ods",
    ])
    if tdi_path is not None:
        process_tdi(tdi_path, municipios)

    population_path = _resolve_first_existing([
        PLANILHAS_ROOT / "Estimativas de Pupulacao" / "POP2025_20260113.xls",
    ])
    if population_path is not None:
        process_population(population_path, municipios)

    cnes_path = _resolve_first_existing([
        PLANILHAS_ROOT / "CNES" / "cnes_estabelecimentos_csv" / "cnes_estabelecimentos.csv",
    ])
    if cnes_path is not None:
        process_cnes(cnes_path, municipios)

    fbsp_path = _resolve_first_existing([
        PLANILHAS_ROOT / "FBSP" / "br_fbsp_absp_municipio.csv" / "br_fbsp_absp_municipio.csv",
        PLANILHAS_ROOT / "FBSP" / "br_fbsp_absp_municipio.csv",
    ])
    if fbsp_path is not None:
        process_fbsp(fbsp_path, municipios)

    pib_path = _resolve_first_existing([
        PLANILHAS_ROOT / "PIB_Municipios" / "base_de_dados_2010_2023_xlsx" / "PIB dos Municípios - base de dados 2010-2023.xlsx",
    ])
    if pib_path is not None:
        process_pib(pib_path, municipios)

    sinisa_path = _resolve_first_existing([
        PLANILHAS_ROOT / "SINISA_RESIDUOS_Planilhas_2023" / "SINISA_RESIDUOS_Planilhas_2023" / "SINISA_RESIDUOS_Indicadores_2023.xlsx",
    ])
    if sinisa_path is not None:
        process_sinisa(sinisa_path, municipios)

    cetic_path = _resolve_first_existing([
        PLANILHAS_ROOT / "Cetic" / "tic_saude_estabelecimentos.xlsx",
        PLANILHAS_ROOT / "Cetic" / "tic_saude_2025.xlsx"
    ])
    if cetic_path is not None:
        process_cetic(cetic_path, municipios)

    names = _load_ibge_names()
    if names:
        for code in sorted(names):
            municipios.setdefault(code, {"nome": "", "indicadores": {}})
        for code, entry in municipios.items():
            entry["nome"] = names.get(code, entry.get("nome") or "Desconhecido")
    else:
        for code, entry in municipios.items():
            entry["nome"] = entry.get("nome") or "Desconhecido"

    cidades_validas = sum(1 for entry in municipios.values() if isinstance(entry, dict) and entry.get("indicadores"))
    
    metadata = {
        "data_processamento": pd.Timestamp.now().isoformat(),
        "fonte": "ETL local a partir do data lake Urbix",
        "total_municipios": len(municipios),
        "cidades_validas": cidades_validas,
        "catalogo_ibge_municipios": len(names),
        "indicadores_processados": [
            "densidade_banda_larga",
            "atu_2025",
            "tdi_2025",
            "populacao_estimada_2025",
            "num_hospitais",
            "hospitais_por_100k",
            "homicidios_100k",
            "pib_per_capita",
            "lixeiras_com_sensores",
            "energia_de_residuos",
            "prontuario_eletronico_pct",
            "consultas_remotas_100k"
        ],
    }

    payload = {
        "metadata": metadata,
        "municipios": municipios,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    return payload