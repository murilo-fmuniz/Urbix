from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

backend = Path(__file__).resolve().parent.parent
project_root = backend.parent
sys.path.insert(0, str(backend))
load_dotenv(backend / ".env")

from app.etl_config import FONTES_API, INDICADORES

PENDING_TOKENS = ("pendente", "incompleto", "nao_baixado", "implementacao")
AXES = {
    "economia": "Economia e Governança",
    "sociedade_seguranca": "Sociedade e Segurança",
    "educacao_inovacao": "Educação e Inovação",
    "sustentabilidade_smart_city": "Sustentabilidade e Smart City",
    "resiliencia_desastres": "Resiliência e Desastres",
    "conectividade": "Conectividade",
}


def is_pending(status: str) -> bool:
    return any(token in status.lower() for token in PENDING_TOKENS)


def fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    if isinstance(value, int):
        return f"{value:,}".replace(",", ".")
    return str(value)


def db_stats(conn, indicator: str, total_municipios: int) -> dict:
    historical = conn.execute(text("""
        SELECT COUNT(*) AS records,
               COUNT(*) FILTER (WHERE valor IS NOT NULL) AS valued,
               COUNT(DISTINCT codigo_ibge) FILTER (WHERE valor IS NOT NULL) AS municipalities,
               MIN(ano_referencia) FILTER (WHERE valor IS NOT NULL) AS year_min,
               MAX(ano_referencia) FILTER (WHERE valor IS NOT NULL) AS year_max
        FROM valores_indicadores WHERE id_indicador = :id
    """), {"id": indicator}).mappings().one()
    latest = conn.execute(text("""
        SELECT COUNT(*) FILTER (WHERE valor IS NOT NULL) AS valued,
               COUNT(DISTINCT codigo_ibge) FILTER (WHERE valor IS NOT NULL) AS municipalities,
               MIN(ano_referencia) FILTER (WHERE valor IS NOT NULL) AS year_min,
               MAX(ano_referencia) FILTER (WHERE valor IS NOT NULL) AS year_max
        FROM valores_indicadores_latest WHERE id_indicador = :id
    """), {"id": indicator}).mappings().one()
    coverage = (latest["municipalities"] or 0) / total_municipios * 100 if total_municipios else 0
    return {
        "records": historical["records"] or 0,
        "valued": historical["valued"] or 0,
        "municipalities": historical["municipalities"] or 0,
        "year_min": historical["year_min"], "year_max": historical["year_max"],
        "latest_valued": latest["valued"] or 0,
        "latest_municipalities": latest["municipalities"] or 0,
        "latest_year_min": latest["year_min"], "latest_year_max": latest["year_max"],
        "coverage": coverage,
    }


def source_summary(conn) -> list[dict]:
    rows = conn.execute(text("""
        SELECT COALESCE(fonte, '[sem fonte]') AS fonte, COUNT(*) AS registros,
               COUNT(DISTINCT id_indicador) AS indicadores,
               COUNT(DISTINCT codigo_ibge) AS municipios
        FROM valores_indicadores WHERE valor IS NOT NULL
        GROUP BY fonte ORDER BY registros DESC
    """)).mappings().all()
    return [dict(row) for row in rows]


def latest_run_log() -> dict | None:
    logs = sorted((backend / "data" / "etl_runs").glob("etl_*.json"), key=lambda path: path.stat().st_mtime)
    if not logs:
        return None
    try:
        return json.loads(logs[-1].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def build_report(output: Path) -> None:
    engine = create_engine(os.environ["DATABASE_URL"], pool_pre_ping=True)
    with engine.connect() as conn:
        total_municipios = conn.execute(text("SELECT COUNT(*) FROM municipios")).scalar() or 0
        total_records = conn.execute(text("SELECT COUNT(*) FROM valores_indicadores WHERE valor IS NOT NULL")).scalar() or 0
        total_latest = conn.execute(text("SELECT COUNT(*) FROM valores_indicadores_latest WHERE valor IS NOT NULL")).scalar() or 0
        entries = []
        for domain, indicators in INDICADORES.items():
            for indicator, rule in indicators.items():
                config = rule.get("variavel_direta") if rule.get("tipo_calculo") == "direto" else rule.get("numerador") or {}
                db_id = indicator if rule.get("tipo_calculo") == "direto" else f"{indicator}_numerador"
                status = str(rule.get("status", "sem_status"))
                entries.append({
                    "axis": AXES.get(domain, domain), "indicator": indicator, "db_id": db_id,
                    "status": status, "pending": is_pending(status),
                    "type": rule.get("tipo_calculo", "—"),
                    "source": config.get("fonte") or config.get("arquivo", "—"),
                    "file": config.get("arquivo", "—"),
                    "denominator": rule.get("denominador", "—"),
                    "stats": db_stats(conn, db_id, total_municipios),
                })
        for indicator, config in FONTES_API.get("sidra", {}).items():
            entries.append({
                "axis": "Bases de normalização", "indicator": indicator, "db_id": indicator,
                "status": "API SIDRA", "pending": False, "type": "base",
                "source": config["fonte"], "file": config["url"], "denominator": "—",
                "stats": db_stats(conn, indicator, total_municipios),
            })

        run_log = latest_run_log()
        lines = [
            "# Auditoria do ETL Urbix — Relatório para a IC", "",
            f"> Gerado em {datetime.now():%d/%m/%Y %H:%M:%S} a partir do PostgreSQL do backend.", "",
            "## Resumo executivo", "",
            f"- Municípios cadastrados: **{fmt(total_municipios)}**",
            f"- Registros históricos com valor: **{fmt(total_records)}**",
            f"- Registros no snapshot atual: **{fmt(total_latest)}**",
            f"- Indicadores configurados: **{fmt(len(entries))}**",
            f"- APIs SIDRA configuradas: **{fmt(len(FONTES_API.get('sidra', {})))}**",
            f"- SICONFI habilitado: **{'sim' if FONTES_API.get('siconfi', {}).get('habilitado') else 'não'}**", "",
            "A cobertura abaixo usa `valores_indicadores_latest`, o valor mais recente usado pelo TOPSIS.", "",
        ]
        if run_log:
            duration_minutes = (run_log.get("duration_seconds") or 0) / 60
            siconfi = next((item for item in run_log.get("apis", []) if item.get("api") == "SICONFI"), None)
            lines += [
                "## Última execução do ETL",
                "",
                f"- ID: `{run_log.get('run_id', '—')}`",
                f"- Status: **{run_log.get('status', '—')}**",
                f"- Início: `{run_log.get('started_at', '—')}`",
                f"- Fim: `{run_log.get('finished_at', '—')}`",
                f"- Duração: **{fmt(duration_minutes)} minutos**",
                f"- Escopo: **{run_log.get('scope', '—')}**",
            ]
            if siconfi:
                lines += [
                    f"- SICONFI: **{fmt(siconfi.get('consultadas', 0))}** municípios consultados, **{fmt(siconfi.get('sucesso', 0))}** respostas válidas, **{fmt(siconfi.get('falhas', 0))}** falhas, **{fmt(siconfi.get('inseridos', 0))}** registros inseridos.",
                ]
            lines += [
                f"- Eventos de APIs registrados: **{fmt(len(run_log.get('apis', [])))}**",
                f"- Eventos de indicadores registrados: **{fmt(len(run_log.get('indicators', [])))}**",
                "",
            ]
        lines += [
            "## Cobertura por eixo", "",
            "| Eixo | Com dados | Configurados | Cobertura média | Melhor | Menor |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for axis in list(AXES.values()) + ["Bases de normalização"]:
            axis_entries = [entry for entry in entries if entry["axis"] == axis]
            if not axis_entries:
                continue
            coverages = [entry["stats"]["coverage"] for entry in axis_entries]
            active = [entry for entry in axis_entries if entry["stats"]["latest_municipalities"] > 0]
            lines.append(f"| {axis} | {len(active)} | {len(axis_entries)} | {fmt(sum(coverages) / len(coverages))}% | {fmt(max(coverages))}% | {fmt(min(coverages))}% |")

        lines += ["", "## Indicadores ativos e cobertura municipal", "", "| Eixo | Indicador | Municípios | Cobertura | Ano mais recente | Fonte |", "|---|---|---:|---:|---:|---|"]
        for entry in sorted(entries, key=lambda item: (-item["stats"]["coverage"], item["indicator"])):
            stats = entry["stats"]
            if stats["latest_municipalities"]:
                lines.append(f"| {entry['axis']} | `{entry['indicator']}` | {fmt(stats['latest_municipalities'])} | {fmt(stats['coverage'])}% | {stats['latest_year_max'] or '—'} | {entry['source']} |")

        lines += ["", "## Indicadores pendentes ou sem dados atuais", "", "| Eixo | Indicador | Status | Arquivo/fonte | Motivo |", "|---|---|---|---|---|"]
        for entry in sorted(entries, key=lambda item: (item["axis"], item["indicator"])):
            stats = entry["stats"]
            if entry["pending"] or not stats["latest_municipalities"]:
                reason = "status pendente" if entry["pending"] else "sem registro no snapshot"
                lines.append(f"| {entry['axis']} | `{entry['indicator']}` | {entry['status']} | {entry['file']} | {reason} |")

        lines += ["", "## Volume por fonte", "", "| Fonte | Registros | Indicadores | Municípios |", "|---|---:|---:|---:|"]
        for row in source_summary(conn):
            lines.append(f"| {row['fonte']} | {fmt(row['registros'])} | {fmt(row['indicadores'])} | {fmt(row['municipios'])} |")

        lines += ["", "## APIs e persistência", "", "| API | Situação |", "|---|---|", "| SIDRA/IBGE | Executada no `run()` e gravada em `valores_indicadores` |", f"| SICONFI/Tesouro | {'Habilitada' if FONTES_API.get('siconfi', {}).get('habilitado') else 'Desabilitada'}; retries e substituição por ano |", ""]
        lines += ["## Notas metodológicas", "", "- Cobertura = municípios com valor no snapshot / total de municípios.", "- Ausência não foi convertida em zero nesta auditoria.", "- MUNIC binário aparece como 0/1 e representa presença/ausência.", "- SNIS usa o último ano disponível por município.", "- CAGED representa saldo de movimentações formais, não desemprego populacional.", "- Eventos climáticos possuem cobertura regional.", ""]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"RELATORIO={output}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=project_root / "docs" / "RELATORIO_AUDITORIA_ETL_IC.md")
    args = parser.parse_args()
    build_report(args.output)


if __name__ == "__main__":
    main()
