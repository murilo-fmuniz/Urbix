from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable

import requests

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import Base, SessionLocal, engine
from app.models import Municipio, ValorIndicador, ValorIndicadorLatest
from app.services.topsis_core import _rebuild_snapshot_latest, preparar_matriz_decisao
from tools.local_etl_service import atualizar_snapshot_latest


BASE_CONFIG = {
    "populacao_total": {
        "table": "6579",
        "year": 2025,
        "var": "9324",
        "fonte": "SIDRA (6579)",
        "mult": 1.0,
    },
    "pib_absoluto": {
        "table": "5938",
        "year": 2023,
        "var": "37",
        "fonte": "SIDRA (5938)",
        "mult": 1000.0,
    },
    "forca_de_trabalho": {
        "table": "6580",
        "year": 2022,
        "var": "1641",
        "fonte": "SIDRA Censo (6580)",
        "mult": 1.0,
    },
    "total_domicilios": {
        "table": "9922",
        "year": 2022,
        "var": "381",
        "extra": "c1/6795",
        "fonte": "SIDRA Censo (9922)",
        "mult": 1.0,
    },
}


def _sidra_url(table: str, year: int, ibges: list[str] | None, var: str, extra: str | None = None) -> str:
    territorio = "all" if not ibges else ",".join(ibges)
    base = f"https://apisidra.ibge.gov.br/values/t/{table}/p/{year}/n6/{territorio}/v/{var}"
    if extra:
        base = f"{base}/{extra}"
    return f"{base}?formato=json"


def _parse_float(raw) -> float | None:
    if raw is None:
        return None
    value = str(raw).strip().replace(".", "").replace(",", ".")
    if value in {"", "-", "...", "X"}:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _normalize_ibge(raw: str) -> str | None:
    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if len(digits) >= 7:
        return digits[-7:]
    return None


def _resolve_ibge_from_n6(raw: str, cidades_alvo: list[str]) -> str | None:
    """Resolve retorno SIDRA n6 (6 dígitos) para IBGE de 7 dígitos das cidades alvo."""
    code = _normalize_ibge(raw)
    if code:
        return code

    digits = "".join(ch for ch in str(raw) if ch.isdigit())
    if len(digits) == 6:
        candidatos = [c for c in cidades_alvo if c.startswith(digits)]
        if len(candidatos) == 1:
            return candidatos[0]
    return None


def _extract_municipio_codigo(item: dict, cidades_alvo: list[str]) -> str | None:
    """Extrai código IBGE do item SIDRA com fallback para chaves comuns (D2C, D1C)."""
    for key in ("D2C", "D1C"):
        if key in item:
            resolved = _resolve_ibge_from_n6(item.get(key, ""), cidades_alvo)
            if resolved:
                return resolved
    return None


def _extract_municipio_codigo_global(item: dict) -> str | None:
    for key in ("D2C", "D1C"):
        if key in item:
            code = _normalize_ibge(item.get(key, ""))
            if code:
                return code
    return None


def _upsert_base_rows(db, id_indicador: str, ano: int, fonte: str, rows: Iterable[tuple[str, float]]) -> int:
    rows = list(rows)
    if not rows:
        return 0

    ibges = sorted({ibge for ibge, _ in rows})
    db.query(ValorIndicador).filter(
        ValorIndicador.codigo_ibge.in_(ibges),
        ValorIndicador.id_indicador == id_indicador,
        ValorIndicador.ano_referencia == ano,
    ).delete(synchronize_session=False)

    novos = [
        ValorIndicador(
            codigo_ibge=ibge,
            id_indicador=id_indicador,
            ano_referencia=ano,
            valor=valor,
            fonte=fonte,
        )
        for ibge, valor in rows
    ]
    db.bulk_save_objects(novos)
    db.commit()
    return len(novos)


def backfill_sidra(db, cidades: list[str] | None = None) -> dict[str, int]:
    inseridos: dict[str, int] = {}
    filtro_cidades = set(cidades) if cidades else None

    for indicador, conf in BASE_CONFIG.items():
        url = _sidra_url(conf["table"], conf["year"], cidades, conf["var"], conf.get("extra"))
        print(f"🌐 SIDRA {indicador}: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        payload = response.json()

        rows: list[tuple[str, float]] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            if cidades:
                ibge = _extract_municipio_codigo(item, cidades)
            else:
                ibge = _extract_municipio_codigo_global(item)

            if not ibge:
                continue
            if filtro_cidades and ibge not in filtro_cidades:
                continue
            valor = _parse_float(item.get("V"))
            if valor is None:
                continue
            valor *= conf["mult"]
            rows.append((ibge, valor))

        inseridos[indicador] = _upsert_base_rows(
            db,
            indicador,
            conf["year"],
            conf["fonte"],
            rows,
        )
        print(f"✅ {indicador}: {inseridos[indicador]} linha(s) inserida(s)")

    return inseridos


def backfill_siconfi_receita(db, cidades: list[str]) -> int:
    base_url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    rows: list[tuple[str, float]] = []

    total = len(cidades)
    if total == 0:
        print("⚠️ Nenhuma cidade para consulta SICONFI")
        return 0

    for idx, ibge in enumerate(cidades, start=1):
        if idx % 250 == 0 or idx == total:
            print(f"⏳ SICONFI progresso: {idx}/{total}")
        params = {
            "an_exercicio": 2023,
            "nr_periodo": 6,
            "co_tipo_demonstrativo": "RREO",
            "no_anexo": "RREO-Anexo 03",
            "id_ente": ibge,
        }
        res = requests.get(base_url, params=params, timeout=30)
        if res.status_code != 200:
            continue
        payload = res.json()
        items = payload.get("items", []) if isinstance(payload, dict) else []
        for item in items:
            if item.get("cod_conta") == "RREO3ReceitaCorrenteLiquida":
                valor = _parse_float(item.get("valor"))
                if valor is not None:
                    rows.append((ibge, valor))
                break
        time.sleep(0.05)

    inseridos = _upsert_base_rows(db, "receita_total_municipio", 2023, "API SICONFI / RREO", rows)
    print(f"✅ receita_total_municipio: {inseridos} linha(s) inserida(s)")
    return inseridos


def diagnostico(db, cidades: list[str]) -> None:
    base_ids = [
        "populacao_total",
        "forca_de_trabalho",
        "total_domicilios",
        "pib_absoluto",
        "receita_total_municipio",
    ]

    print("\n📊 Cobertura de denominadores por cidade")
    for bid in base_ids:
        total = db.query(ValorIndicador).filter(
            ValorIndicador.codigo_ibge.in_(cidades),
            ValorIndicador.id_indicador == bid,
        ).count()
        print(f"- {bid}: {total}")

    df = preparar_matriz_decisao(cidades[: min(len(cidades), 10)], [], db)
    print(f"\n📈 Colunas finais na matriz TOPSIS: {len(df.columns)}")
    print(list(df.columns))


def refresh_snapshot_subset(db, cidades: list[str]) -> None:
    """Atualiza snapshot só para o subconjunto solicitado (mais rápido e com menos lock)."""
    if not cidades:
        return
    print("\n--- ATUALIZANDO SNAPSHOT APENAS DO SUBCONJUNTO ---")
    db.query(ValorIndicadorLatest).filter(ValorIndicadorLatest.codigo_ibge.in_(cidades)).delete(synchronize_session=False)
    db.commit()
    _rebuild_snapshot_latest(db, cidades, None)
    print("✅ Snapshot do subconjunto atualizado")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill direcionado de denominadores base para TOPSIS.")
    parser.add_argument(
        "--all",
        action="store_true",
        help="Executa para todos os municípios existentes na tabela municipios.",
    )
    parser.add_argument(
        "--cities",
        nargs="+",
        default=None,
        help="Lista de códigos IBGE (7 dígitos).",
    )
    parser.add_argument(
        "--skip-siconfi",
        action="store_true",
        help="Pula o backfill de receita_total_municipio via SICONFI.",
    )
    parser.add_argument(
        "--skip-snapshot",
        action="store_true",
        help="Pula atualização de snapshot ao final.",
    )
    args = parser.parse_args()

    print("=" * 72)
    print("🚀 BACKFILL DE DENOMINADORES BASE (SIDRA + SICONFI)")
    print("=" * 72)

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if args.all:
            cidades = [c[0] for c in db.query(Municipio.codigo_ibge).order_by(Municipio.codigo_ibge.asc()).all()]
            if not cidades:
                raise SystemExit("Nenhum município encontrado para --all")
            print(f"Modo nacional: {len(cidades)} cidades alvo")
            diagnostico_amostra = cidades[:3]
        else:
            cidades_raw = args.cities or []
            cidades = [str(c).strip() for c in cidades_raw if str(c).strip()]
            cidades = sorted(set(cidades))
            if not cidades:
                raise SystemExit("Informe --all ou uma lista em --cities")
            print(f"Cidades alvo: {cidades}")
            diagnostico_amostra = cidades

        diagnostico(db, diagnostico_amostra)
        backfill_sidra(db, None if args.all else cidades)

        if not args.skip_siconfi:
            backfill_siconfi_receita(db, cidades)
        else:
            print("⏭️ SICONFI pulado (--skip-siconfi)")

        if not args.skip_snapshot:
            if len(cidades) <= 20:
                refresh_snapshot_subset(db, cidades)
            else:
                atualizar_snapshot_latest(db)
        else:
            print("⏭️ Snapshot pulado (--skip-snapshot)")

        diagnostico(db, diagnostico_amostra)
    finally:
        db.close()


if __name__ == "__main__":
    main()
