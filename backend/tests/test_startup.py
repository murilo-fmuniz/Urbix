#!/usr/bin/env python3
"""
Script de teste para validar startup do backend
"""
import sys
import asyncio
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    logger.info("=" * 80)
    logger.info("🧪 TESTE DE STARTUP DO BACKEND URBIX")
    logger.info("=" * 80)
    
    # ========== TESTE 1: Imports ==========
    logger.info("\n[TESTE 1] Verificando imports...")
    from app.main import app
    logger.info("✅ Imports do app.main carregados com sucesso")
    
    # ========== TESTE 2: Verificar routers ==========
    logger.info("\n[TESTE 2] Verificando routers...")
    routes = [route.path for route in app.routes]
    logger.info(f"✅ Total de rotas: {len(routes)}")
    for route in sorted(routes):
        logger.info(f"   - {route}")
    
    # ========== TESTE 3: Verificar schemas ==========
    logger.info("\n[TESTE 3] Verificando schemas...")
    from app.schemas import (
        CityDataInput,
        ManualCityIndicators,
        CityHybridInput,
        IndicatorValues,
        TOPSISInput,
        TOPSISResult,
    )
    logger.info("✅ Todos os schemas carregados com sucesso")
    
    # ========== TESTE 4: Verificar serviços ==========
    logger.info("\n[TESTE 4] Verificando serviços...")
    from app.services.indicators import (
        calculate_all_indicators,
        calculate_debt_service_rate,
        calculate_capital_expenditure_rate,
        calculate_financial_independence,
        calculate_gross_budget_per_capita,
    )
    from app.services.external_apis import (
        get_ibge_population,
        get_siconfi_finances,
        get_datasus_health_infrastructure,
    )
    from app.services.topsis import calculate_topsis
    logger.info("✅ Todos os serviços carregados com sucesso")
    
    # ========== TESTE 5: Testar cálculo de indicadores ==========
    logger.info("\n[TESTE 5] Testando cálculo de indicadores...")
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
    logger.info("✅ Indicadores calculados com sucesso:")
    for key, value in indicadores.items():
        logger.info(f"   - {key}: {value}")
    
    # ========== TESTE 6: Validar estrutura do schema ManualCityIndicators ==========
    logger.info("\n[TESTE 6] Validando schema ManualCityIndicators...")
    manual_data = ManualCityIndicators(
        pontos_iluminacao_telegestao=60.0,
        medidores_inteligentes_energia=45.0,
        bombeiros_por_100k=60.0,
        area_verde_mapeada=50.0,
    )
    logger.info(f"✅ ManualCityIndicators validado: {manual_data.dict()}")
    
    # ========== TESTE 7: Validar entrada híbrida ==========
    logger.info("\n[TESTE 7] Validando CityHybridInput...")
    hybrid_input = CityHybridInput(
        codigo_ibge="4101408",
        manual_indicators=manual_data,
    )
    logger.info(f"✅ CityHybridInput validado: {hybrid_input.dict()}")
    
    logger.info("\n" + "=" * 80)
    logger.info("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
    logger.info("=" * 80)
    sys.exit(0)
    
except Exception as e:
    logger.error(f"\n❌ ERRO NO TESTE: {str(e)}", exc_info=True)
    sys.exit(1)
