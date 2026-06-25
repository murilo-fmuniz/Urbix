#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste PARTE 3: Orquestração das 5 Novas APIs
Valida: asyncio.gather(), exception handling, inject_api_data_into_flat_list()
"""
import asyncio
import sys
from pathlib import Path
import logging

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# TESTE 1: Verificar se as 5 novas APIs foram importadas corretamente
# ============================================================================
def test_imports():
    logger.info("\n" + "="*80)
    logger.info("🔍 TESTE 1: Verificar imports das 5 novas APIs")
    logger.info("="*80)
    
    try:
        from app.services.external_apis import (
            get_siconfi_finances,
            get_ibge_population,
            get_datasus_health_infrastructure,
            get_inep_education,
            get_transparencia_social,
            get_datasus_expanded_wrapper,
            get_portal_transparencia_expanded_wrapper,
            # 🎯 5 NOVAS APIS
            get_aneel_smart_metering,
            get_ministerio_trabalho_accidents,
            get_antp_zero_emission_fleet,
            get_defesa_civil_disasters,
            get_cnj_corruption_convictions,
        )
        logger.info("✅ Todos os 12 imports funcionando!")
        return True
    except ImportError as e:
        logger.error(f"❌ Erro ao importar: {e}")
        return False


# ============================================================================
# TESTE 2: Verificar se a função inject_api_data_into_flat_list() aceita os 5 novos parâmetros
# ============================================================================
def test_inject_function_signature():
    logger.info("\n" + "="*80)
    logger.info("🔍 TESTE 2: Verificar assinatura da função inject_api_data_into_flat_list()")
    logger.info("="*80)
    
    try:
        from app.routers.topsis import inject_api_data_into_flat_list
        import inspect
        
        sig = inspect.signature(inject_api_data_into_flat_list)
        params = list(sig.parameters.keys())
        
        logger.info(f"   Parâmetros: {params}")
        
        expected_params = [
            'indicadores_flat', 'siconfi_data', 'ibge_data', 'datasus_data',
            'inep_data', 'transparencia_data', 'datasus_expanded_data',
            'portal_social_data', 'etl_data',
            # 🎯 5 NOVAS
            'aneel_data', 'ministerio_trabalho_data', 'antp_data',
            'defesa_civil_data', 'cnj_data',
            'nome_cidade'
        ]
        
        if params == expected_params:
            logger.info("✅ Assinatura da função correta com os 5 novos parâmetros!")
            return True
        else:
            logger.error(f"❌ Parâmetros não correspondentes!")
            logger.error(f"   Esperado: {expected_params}")
            logger.error(f"   Obtido: {params}")
            return False
    except Exception as e:
        logger.error(f"❌ Erro ao verificar assinatura: {e}")
        return False


# ============================================================================
# TESTE 3: Simular injeção de dados com as 5 novas APIs
# ============================================================================
def test_inject_simulation():
    logger.info("\n" + "="*80)
    logger.info("🔍 TESTE 3: Simular injeção com dados fake das 5 novas APIs")
    logger.info("="*80)
    
    try:
        from app.routers.topsis import inject_api_data_into_flat_list
        
        # Dados fake com valores para as 5 novas APIs
        indicadores_flat = [0.0] * 50
        
        fake_data = {
            'indicadores_flat': indicadores_flat,
            'siconfi_data': {'receita_propria': 0, 'despesas_capital': 0, 'receita_total': 1},
            'ibge_data': {'populacao': 100000},
            'datasus_data': {'num_hospitais': 0},
            'inep_data': {'relacao_estudante_professor': 0, 'ideb_anos_iniciais': 0, 'escolas_conectadas_pct': 0},
            'transparencia_data': {'beneficiados_bolsa_familia': 0, 'participacao_eleitoral_pct': 0, 'mulheres_eleitas_pct': 0},
            'datasus_expanded_data': {'hospitais_por_100k': 0, 'leitos_uti_pct': 0, 'cobertura_vacina_covid_pct': 0, 'cobertura_atencao_basica_pct': 0, 'agentes_comunitarios_saude': 0},
            'portal_social_data': {'beneficiarios_programas_sociais_pct': 0, 'cobertura_alimentacao_escolar_pct': 0, 'acesso_agua_potavel_pct': 0},
            'etl_data': {'saldo_empregos_caged': 0, 'homicidios_100k': 0},
            # 🎯 5 NOVAS APIS com dados fake
            'aneel_data': {'medidores_inteligentes_pct': 45.5},  # Índice [22]
            'ministerio_trabalho_data': {'acidentes_industriais_100k': 12.3},  # Índice [14]
            'antp_data': {'frota_onibus_zero_emissao_pct': 8.9},  # Índice [32]
            'defesa_civil_data': {'mortalidade_desastres_100k': 2.1, 'perdas_desastres_pct_pib': 0.5},  # Índice [46] + extra
            'cnj_data': {'condenacoes_corrupcao_100k': 3.4},  # Índice [6]
            'nome_cidade': 'Teste City'
        }
        
        resultado = inject_api_data_into_flat_list(**fake_data)
        
        # Validar se os dados foram injetados nos índices corretos
        checks = [
            (6, 3.4, "CNJ - Condenações Corrupção"),
            (14, 12.3, "Min. Trabalho - Acidentes Industriais"),
            (22, 45.5, "ANEEL - Medidores Inteligentes"),
            (32, 8.9, "ANTP - Frota Zero Emissão"),
            (46, 2.1, "Defesa Civil - Mortalidade Desastres"),
        ]
        
        all_ok = True
        for idx, expected_val, desc in checks:
            if resultado[idx] == expected_val:
                logger.info(f"   ✅ [{idx}] {desc}: {resultado[idx]}")
            else:
                logger.error(f"   ❌ [{idx}] {desc}: esperado {expected_val}, obtido {resultado[idx]}")
                all_ok = False
        
        if all_ok:
            logger.info("\n✅ Todos os 5 indicadores foram injetados corretamente!")
            return True
        else:
            logger.error("\n❌ Alguns indicadores não foram injetados")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao simular injeção: {e}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TESTE 4: Verificar estrutura do asyncio.gather() em processar_cidade_real()
# ============================================================================
def test_asyncio_gather_structure():
    logger.info("\n" + "="*80)
    logger.info("🔍 TESTE 4: Verificar estrutura do asyncio.gather()")
    logger.info("="*80)
    
    try:
        import inspect
        from app.routers.topsis import processar_cidade_real
        
        source = inspect.getsource(processar_cidade_real)
        
        # Verificar se as 5 novas APIs estão no asyncio.gather()
        checks = [
            'get_aneel_smart_metering',
            'get_ministerio_trabalho_accidents',
            'get_antp_zero_emission_fleet',
            'get_defesa_civil_disasters',
            'get_cnj_corruption_convictions',
        ]
        
        all_ok = True
        for api in checks:
            if api in source:
                logger.info(f"   ✅ {api} encontrada no asyncio.gather()")
            else:
                logger.error(f"   ❌ {api} NÃO encontrada")
                all_ok = False
        
        if all_ok:
            logger.info("\n✅ Todas as 5 APIs estão no asyncio.gather()!")
            return True
        else:
            logger.error("\n❌ Algumas APIs estão faltando")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao verificar asyncio.gather(): {e}")
        return False


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    logger.info("\n" + "🎯 TESTE PARTE 3: ORQUESTRAÇÃO DAS 5 NOVAS APIS" + "\n")
    
    results = {
        "Test 1 - Imports": test_imports(),
        "Test 2 - Function Signature": test_inject_function_signature(),
        "Test 3 - Injection Simulation": test_inject_simulation(),
        "Test 4 - asyncio.gather() Structure": test_asyncio_gather_structure(),
    }
    
    logger.info("\n" + "="*80)
    logger.info("📊 RESUMO DOS TESTES")
    logger.info("="*80)
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        logger.info(f"{test_name}: {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    logger.info(f"\n📈 {passed}/{total} testes passaram")
    
    if passed == total:
        logger.info("\n🎉 TODOS OS TESTES PASSARAM! PARTE 3 ESTÁ COMPLETA!")
        sys.exit(0)
    else:
        logger.error(f"\n⚠️  {total - passed} testes falharam")
        sys.exit(1)
