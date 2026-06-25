"""
Seed de cidade fictícia para testes de CRUD e séries históricas.

Cria uma cidade exemplo no banco para facilitar validação da admin page,
alterações manuais e histórico de snapshots.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import CityManualData, IndicatorSnapshot
from app.schemas import ManualCityIndicators


DEMO_CITY_CODE = "9999999"
DEMO_CITY_NAME = "UTFPRCity"
DEMO_USER = "seed-demo"


def _build_demo_manual_indicators() -> dict:
    """Cria uma estrutura completa com 47 indicadores e alguns valores fictícios."""
    manual = ManualCityIndicators().model_dump()

    manual["iso_37120"].update(
        {
            "taxa_desemprego_pct": 7.8,
            "taxa_endividamento_pct": 31.4,
            "despesas_capital_pct": 12.6,
            "receita_propria_pct": 27.9,
            "orcamento_per_capita": 5420.0,
            "mulheres_eleitas_pct": 41.2,
            "condenacoes_corrupcao_100k": 0.8,
            "participacao_eleitoral_pct": 79.5,
            "moradias_inadequadas_pct": 9.1,
            "sem_teto_100k": 2.4,
            "bombeiros_100k": 46.0,
            "mortes_incendio_100k": 0.9,
            "agentes_policia_100k": 133.0,
            "homicidios_100k": 14.2,
            "acidentes_industriais_100k": 1.1,
            "relacao_estudante_professor": 18.7,
            "ideb_anos_iniciais": 6.4,
        }
    )

    manual["iso_37122"].update(
        {
            "sobrevivencia_novos_negocios_100k": 812.0,
            "empregos_tic_pct": 4.8,
            "graduados_stem_100k": 126.0,
            "energia_residuos_pct": 7.6,
            "iluminacao_telegestao_pct": 36.4,
            "medidores_inteligentes_energia_pct": 42.0,
            "edificios_verdes_pct": 8.5,
            "monitoramento_ar_tempo_real_pct": 44.2,
            "servicos_urbanos_online_pct": 69.5,
            "prontuario_eletronico_pct": 58.3,
            "consultas_remotas_100k": 292.0,
            "medidores_inteligentes_agua_pct": 21.0,
            "areas_cobertas_cameras_pct": 39.0,
            "lixeiras_sensores_pct": 14.0,
            "semaforos_inteligentes_pct": 28.0,
            "frota_onibus_limpos_pct": 18.0,
            "escolas_conectadas_pct": 81.0,
        }
    )

    manual["iso_37123"].update(
        {
            "seguro_ameacas_pct": 19.0,
            "empregos_informais_pct": 21.8,
            "escolas_preparacao_emergencia_pct": 67.0,
            "populacao_treinada_emergencia_pct": 36.5,
            "hospitais_geradores_backup_pct": 87.0,
            "seguro_saude_basico_pct": 73.0,
            "imunizacao_pct": 91.8,
            "abrigos_emergencia_100k": 3.2,
            "edificios_vulneraveis_pct": 11.5,
            "rotas_evacuacao_100k": 8.2,
            "reservas_alimentos_72h_pct": 41.0,
            "mapas_ameacas_publicos_pct": 59.0,
            "mortalidade_desastres_100k": 2.0,
            "pessoas_afetadas_desastres_100k": 84.0,
            "perdas_desastres_pct_pib": 0.7,
            "danos_infraestrutura_basica_pct": 5.4,
        }
    )

    return manual


def _build_snapshot_values(version: int) -> list[float]:
    """Gera uma matriz de 50 valores fictícios com pequenas variações."""
    return [round(10.0 + (idx * 0.63) + (version * 0.75), 2) for idx in range(50)]


def seed_demo_city(db: Session) -> bool:
    """Cria a cidade UTFPRCity se ela ainda não existir."""
    existing = db.query(CityManualData).filter_by(codigo_ibge=DEMO_CITY_CODE).first()
    if existing:
        return False

    demo_city = CityManualData(
        codigo_ibge=DEMO_CITY_CODE,
        nome_cidade=DEMO_CITY_NAME,
        indicadores_manuais=_build_demo_manual_indicators(),
        fonte="seed-demo",
        usuario_atualizou=DEMO_USER,
    )
    db.add(demo_city)
    db.flush()

    base_date = datetime.utcnow()
    for version, month_offset in enumerate([3, 2, 1], start=1):
        snapshot = IndicatorSnapshot(
            codigo_ibge=DEMO_CITY_CODE,
            valores_indicadores=_build_snapshot_values(version),
            fonte_dados="seed-demo",
            periodo_referencia=(base_date - timedelta(days=30 * month_offset)).strftime("%Y-%m"),
            data_calculo=base_date - timedelta(days=30 * month_offset),
        )
        db.add(snapshot)

    db.commit()
    return True