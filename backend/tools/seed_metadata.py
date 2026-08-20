from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.etl_config import INDICADORES
from app.models import Indicador, Municipio

BACKEND_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BACKEND_DIR / "app" / "data" / "ibge_catalog.json"


def _load_ibge_catalog() -> dict:
    if not CATALOG_PATH.exists():
        return {"states": [], "municipalities": []}
    try:
        payload = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
        return {"states": [], "municipalities": []}
    except Exception:
        return {"states": [], "municipalities": []}


def _normalize_state(value) -> str:
    state = str(value or "").strip().upper()
    return state[:2] if state else ""


def _indicator_name_from_key(indicator_key: str) -> str:
    key = indicator_key.replace("_numerador", "").replace("_denominador", "")
    return key.replace("_", " ").strip().title()


def _is_negative_impact(indicator_key: str) -> bool:
    text = indicator_key.lower()
    negative_terms = [
        "desemprego", "endividamento", "homicidios", "mortes", "inadequadas",
        "sem_teto", "acidentes", "corrupcao", "mortalidade", "afetadas",
        "perdas", "danos", "condenacoes", "inseguranca", "crime"
    ]
    return any(term in text for term in negative_terms)


def seed_municipios(db_session: Session) -> int:
    payload = _load_ibge_catalog()
    municipios = payload.get("municipalities", [])
    inserted = 0

    for item in municipios:
        if not isinstance(item, dict):
            continue

        codigo_ibge = str(item.get("codigo_ibge") or item.get("codigo") or "").strip()
        nome = str(item.get("nome") or item.get("name") or "").strip()
        estado = _normalize_state(item.get("uf_abbr") or item.get("estado") or item.get("uf") or "")

        if not codigo_ibge or not nome:
            continue

        municipio = db_session.query(Municipio).filter(Municipio.codigo_ibge == codigo_ibge).first()
        if municipio is None:
            db_session.add(Municipio(codigo_ibge=codigo_ibge, nome=nome, estado=estado))
            inserted += 1
        else:
            changed = False
            if municipio.nome != nome:
                municipio.nome = nome
                changed = True
            if municipio.estado != estado:
                municipio.estado = estado
                changed = True
            if changed:
                db_session.add(municipio)

    db_session.commit()
    return inserted


def seed_indicadores(db_session: Session) -> int:
    indicator_ids: set[str] = set()
    for _, indicators in INDICADORES.items():
        for key in indicators.keys():
            indicator_ids.add(key)

    inserted = 0
    for indicator_key in sorted(indicator_ids):
        nome = _indicator_name_from_key(indicator_key)
        existing = db_session.query(Indicador).filter(Indicador.id == indicator_key).first()
        if existing is None:
            db_session.add(
                Indicador(
                    id=indicator_key,
                    nome=nome,
                    norma_iso="ISO 37120",
                    peso=0.02,
                    impacto=-1 if _is_negative_impact(indicator_key) else 1,
                )
            )
            inserted += 1
        else:
            changed = False
            if existing.nome != nome:
                existing.nome = nome
                changed = True
            if existing.norma_iso != "ISO 37120":
                existing.norma_iso = "ISO 37120"
                changed = True
            if existing.peso != 0.02:
                existing.peso = 0.02
                changed = True
            if existing.impacto != (-1 if _is_negative_impact(indicator_key) else 1):
                existing.impacto = -1 if _is_negative_impact(indicator_key) else 1
                changed = True
            if changed:
                db_session.add(existing)

    db_session.commit()
    return inserted


def seed_metadata() -> dict:
    Base.metadata.create_all(bind=engine)
    db_session = SessionLocal()
    try:
        municipios = seed_municipios(db_session)
        indicadores = seed_indicadores(db_session)
        return {"municipios": municipios, "indicadores": indicadores}
    finally:
        db_session.close()


if __name__ == "__main__":
    print(seed_metadata())
