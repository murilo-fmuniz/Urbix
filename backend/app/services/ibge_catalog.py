"""Helpers para carregar o catálogo IBGE local.

Fonte:
- backend/app/data/ibge_catalog.json
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

CATALOG_PATH = Path(__file__).parent.parent / "data" / "ibge_catalog.json"


@lru_cache(maxsize=1)
def load_ibge_catalog() -> Dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {"states": [], "municipalities": []}
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def municipality_by_code() -> Dict[str, Dict[str, Any]]:
    catalog = load_ibge_catalog()
    return {item["codigo_ibge"]: item for item in catalog.get("municipalities", []) if item.get("codigo_ibge")}


@lru_cache(maxsize=1)
def municipality_by_name() -> Dict[str, Dict[str, Any]]:
    catalog = load_ibge_catalog()
    return {item["nome"].casefold(): item for item in catalog.get("municipalities", []) if item.get("nome")}


@lru_cache(maxsize=1)
def state_by_abbr() -> Dict[str, Dict[str, Any]]:
    catalog = load_ibge_catalog()
    return {item["abbr"].casefold(): item for item in catalog.get("states", []) if item.get("abbr")}


def find_municipality_by_name(name: str) -> Optional[Dict[str, Any]]:
    if not name:
        return None
    return municipality_by_name().get(str(name).strip().casefold())


def find_municipality_by_code(code: str) -> Optional[Dict[str, Any]]:
    if not code:
        return None
    return municipality_by_code().get(str(code).strip().zfill(7))


def build_municipality_options(names: List[str], include_pr_state: bool = True) -> List[Dict[str, Any]]:
    options: List[Dict[str, Any]] = []
    for name in names:
        item = find_municipality_by_name(name)
        if not item:
            continue
        label = item["nome"]
        if include_pr_state and item.get("uf_abbr"):
            label = f"{label} - {item['uf_abbr']}"
        options.append({
            "codigo_ibge": item["codigo_ibge"],
            "nome": label,
            "uf_abbr": item.get("uf_abbr", ""),
            "uf_nome": item.get("uf_nome", ""),
        })
    return options
