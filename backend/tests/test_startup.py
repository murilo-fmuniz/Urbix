#!/usr/bin/env python3
"""Smoke tests para validar o startup do backend Urbix."""

import logging

import pytest

from app.main import app
from app.schemas import (
    CityDataInput,
    CityHybridInput,
    ISO37120Indicators,
    ISO37122Indicators,
    ISO37123AndSendaiIndicators,
    ManualCityIndicators,
)
from app.services.indicators import calculate_all_indicators

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_backend_app_loads_and_has_routes():
    """✅ O app FastAPI deve importar e expor rotas básicas."""
    assert app is not None
    routes = [route.path for route in app.routes]
    assert any(route.endswith("/health") for route in routes)
    assert len(routes) > 0


def test_indicator_calculation_and_hybrid_schema_work():
    """✅ O cálculo de indicadores e os schemas híbridos devem aceitar dados válidos."""
    test_city = CityDataInput(
        nome_cidade="Teste",
        populacao_total=100000.0,
        receita_propria=10000000.0,
        receita_total=12000000.0,
        custo_servico_divida=1000000.0,
        despesas_capital=5000000.0,
        despesas_operacionais=8000000.0,
        despesas_totais=13000000.0,
        num_mulheres_eleitas=5,
        total_cargos_gestao=20,
        quantidade_hospitais=10,
        pontos_iluminacao_telegestao=50.0,
        medidores_inteligentes_energia=30.0,
        bombeiros_por_100k=50.0,
        area_verde_mapeada=40.0,
    )

    indicadores = calculate_all_indicators(test_city)
    assert isinstance(indicadores, dict)
    assert indicadores

    manual_data = ManualCityIndicators(
        iso_37120=ISO37120Indicators(
            taxa_desemprego_pct=4.2,
            taxa_endividamento_pct=5.0,
            despesas_capital_pct=10.5,
            receita_propria_pct=60.0,
            orcamento_per_capita=800.0,
            mulheres_eleitas_pct=30.0,
            condenacoes_corrupcao_100k=2.0,
            participacao_eleitoral_pct=78.0,
            moradias_inadequadas_pct=8.0,
            sem_teto_100k=12.0,
            bombeiros_100k=20.0,
            mortes_incendio_100k=1.2,
            agentes_policia_100k=15.0,
            homicidios_100k=6.0,
            acidentes_industriais_100k=3.5,
            relacao_estudante_professor=20.0,
            ideb_anos_iniciais=6.3,
        ),
        iso_37122=ISO37122Indicators(
            sobrevivencia_novos_negocios_100k=15.0,
            empregos_tic_pct=8.0,
            graduados_stem_100k=10.0,
            energia_residuos_pct=12.0,
            iluminacao_telegestao_pct=45.0,
            medidores_inteligentes_energia_pct=30.0,
            edificios_verdes_pct=22.0,
            monitoramento_ar_tempo_real_pct=18.0,
            servicos_urbanos_online_pct=60.0,
            prontuario_eletronico_pct=40.0,
            consultas_remotas_100k=5.0,
            medidores_inteligentes_agua_pct=20.0,
            areas_cobertas_cameras_pct=35.0,
            lixeiras_sensores_pct=10.0,
            semaforos_inteligentes_pct=25.0,
            frota_onibus_limpos_pct=15.0,
            escolas_conectadas_pct=70.0,
        ),
        iso_37123=ISO37123AndSendaiIndicators(
            seguro_ameacas_pct=50.0,
            empregos_informais_pct=10.0,
            escolas_preparacao_emergencia_pct=35.0,
            populacao_treinada_emergencia_pct=20.0,
            hospitais_geradores_backup_pct=40.0,
            seguro_saude_basico_pct=55.0,
            imunizacao_pct=85.0,
            abrigos_emergencia_100k=3.0,
            edificios_vulneraveis_pct=12.0,
            rotas_evacuacao_100k=8.0,
            reservas_alimentos_72h_pct=30.0,
            mapas_ameacas_publicos_pct=25.0,
            mortalidade_desastres_100k=2.0,
            pessoas_afetadas_desastres_100k=4.0,
            perdas_desastres_pct_pib=1.0,
            danos_infraestrutura_basica_pct=1.5,
        ),
    )

    hybrid_input = CityHybridInput(
        codigo_ibge="4101408",
        nome_cidade="Apucarana",
        manual_indicators=manual_data,
    )

    assert hybrid_input.codigo_ibge == "4101408"
    assert hybrid_input.manual_indicators is not None
