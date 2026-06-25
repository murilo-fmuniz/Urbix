#!/usr/bin/env python3
"""
Script de Teste: Validar Integração TOPSIS + ETL

Testa se:
1. ETL gera indicators_master.json com dados de CAGED e DATASUS SIM
2. TOPSIS carrega dados ETL corretamente
3. Indicadores são injetados (Taxa Desemprego, Homicídios)
4. Rankings refletem dados reais (não mais todos idênticos)

Uso: python scripts/test_topsis_etl_integration.py
"""

import asyncio
import sys
import logging
from pathlib import Path
import json

# Setup
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# TESTE 1: ETL Gera Dados
# ============================================================================

async def test_etl_generation():
    """Testa se ETL gera indicators_master.json"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: ETL Gera indicators_master.json")
    logger.info("="*80)
    
    from process_local_data import DataProcessor
    
    processor = DataProcessor()
    processor.process_all()
    
    # Verificar se arquivo foi gerado
    etl_file = BACKEND_DIR / "app" / "data" / "indicators_master.json"
    
    if not etl_file.exists():
        logger.error(f"❌ Arquivo ETL não gerado: {etl_file}")
        return False
    
    logger.info(f"✅ Arquivo ETL gerado: {etl_file}")
    
    # Ler e validar conteúdo
    try:
        with open(etl_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        if "municipios" not in master_data:
            logger.error("❌ Estrutura inválida: falta 'municipios'")
            return False
        
        num_cities = len(master_data["municipios"])
        logger.info(f"✅ ETL contém dados de {num_cities} municípios")
        
        # Validar dados de teste
        test_cities = ["4101408", "4113700", "4115200"]  # Apucarana, Londrina, Maringá
        
        logger.info(f"\n📊 Validando dados das cidades de teste:")
        for city_code in test_cities:
            if city_code not in master_data["municipios"]:
                logger.warning(f"   ⚠️  {city_code}: Não encontrado")
                continue
            
            city_data = master_data["municipios"][city_code]
            
            # Verificar indicadores esperados
            indicators = {
                "saldo_empregos_caged": city_data.get("saldo_empregos_caged"),
                "homicidios_100k": city_data.get("homicidios_100k"),
            }
            
            logger.info(f"   - {city_code}:")
            for key, value in indicators.items():
                if value and value > 0:
                    logger.info(f"      ✅ {key}: {value}")
                else:
                    logger.info(f"      ⚠️  {key}: {value} (vazio ou zero)")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Erro ao ler ETL: {str(e)}")
        return False


# ============================================================================
# TESTE 2: TOPSIS Carrega Dados ETL
# ============================================================================

def test_topsis_loads_etl():
    """Testa se TOPSIS carrega dados ETL corretamente"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: TOPSIS Carrega Dados ETL")
    logger.info("="*80)
    
    sys.path.insert(0, str(BACKEND_DIR / "app" / "routers"))
    
    try:
        from topsis import load_etl_data_for_city
        
        test_cities = ["4101408", "4113700", "4115200"]
        
        logger.info(f"\n📡 Testando load_etl_data_for_city():")
        all_success = True
        
        for city_code in test_cities:
            etl_data = load_etl_data_for_city(city_code)
            
            if etl_data:
                logger.info(f"   ✅ {city_code}: Dados carregados")
                for key, value in etl_data.items():
                    logger.info(f"      - {key}: {value}")
            else:
                logger.warning(f"   ⚠️  {city_code}: Nenhum dado ETL")
                all_success = False
        
        return all_success
    
    except Exception as e:
        logger.error(f"❌ Erro ao carregar ETL no TOPSIS: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


# ============================================================================
# TESTE 3: Verificar Indicadores Injetados
# ============================================================================

def test_indicators_injection():
    """Testa se indicadores ETL são injetados corretamente"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Indicadores ETL São Injetados")
    logger.info("="*80)
    
    etl_file = BACKEND_DIR / "app" / "data" / "indicators_master.json"
    
    if not etl_file.exists():
        logger.error(f"❌ Arquivo ETL não encontrado")
        return False
    
    try:
        with open(etl_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        test_cities = ["4101408", "4113700", "4115200"]
        
        logger.info(f"\n🎯 Indicadores do ETL por cidade:")
        
        for city_code in test_cities:
            if city_code not in master_data["municipios"]:
                continue
            
            city_data = master_data["municipios"][city_code]
            
            # Indicadores esperados
            saldo = city_data.get("saldo_empregos_caged", 0)
            homicidios = city_data.get("homicidios_100k", 0)
            
            logger.info(f"\n   🏙️  {city_code}:")
            logger.info(f"      [Índice 0] Taxa Desemprego (proxy): Saldo={saldo}")
            logger.info(f"      [Índice 13] Homicídios/100k: {homicidios}")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Erro ao validar indicadores: {str(e)}")
        return False


# ============================================================================
# TESTE 4: Comparar Dados com/sem ETL
# ============================================================================

def test_data_variation():
    """Testa se dados ETL geram variação entre cidades"""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Dados ETL Geram Variação Entre Cidades")
    logger.info("="*80)
    
    etl_file = BACKEND_DIR / "app" / "data" / "indicators_master.json"
    
    if not etl_file.exists():
        logger.error(f"❌ Arquivo ETL não encontrado")
        return False
    
    try:
        with open(etl_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        test_cities = ["4101408", "4113700", "4115200"]
        
        values_by_indicator = {
            "saldo_empregos_caged": [],
            "homicidios_100k": [],
        }
        
        logger.info(f"\n📊 Variação de Indicadores Entre Cidades:")
        
        for city_code in test_cities:
            if city_code not in master_data["municipios"]:
                continue
            
            city_data = master_data["municipios"][city_code]
            
            for indicator, values_list in values_by_indicator.items():
                value = city_data.get(indicator, 0)
                values_list.append(value)
        
        # Verificar se há variação
        all_variation = True
        for indicator, values in values_by_indicator.items():
            unique_values = len(set(v for v in values if v != 0))
            logger.info(f"   {indicator}:")
            logger.info(f"      - Valores: {values}")
            logger.info(f"      - Valores únicos (não-zero): {unique_values}")
            
            if unique_values <= 1:
                logger.warning(f"      ⚠️  Sem variação suficiente!")
                all_variation = False
            else:
                logger.info(f"      ✅ Variação detectada")
        
        return all_variation
    
    except Exception as e:
        logger.error(f"❌ Erro ao validar variação: {str(e)}")
        return False


# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Executar todos os testes"""
    logger.info("="*80)
    logger.info("🧪 TESTE DE INTEGRAÇÃO: TOPSIS + ETL")
    logger.info("="*80)
    
    results = {}
    
    try:
        # Teste 1
        results["ETL Generation"] = await test_etl_generation()
        
        # Teste 2
        results["TOPSIS Loads ETL"] = test_topsis_loads_etl()
        
        # Teste 3
        results["Indicators Injection"] = test_indicators_injection()
        
        # Teste 4
        results["Data Variation"] = test_data_variation()
        
        # Resumo
        logger.info("\n" + "="*80)
        logger.info("📋 RESUMO DOS TESTES")
        logger.info("="*80)
        
        for test_name, passed in results.items():
            status = "✅ PASSOU" if passed else "❌ FALHOU"
            logger.info(f"{test_name}: {status}")
        
        all_passed = all(results.values())
        
        logger.info("\n" + "="*80)
        if all_passed:
            logger.info("✨ TODOS OS TESTES PASSARAM!")
            logger.info("🎉 TOPSIS + ETL Integrados com Sucesso!")
            logger.info("\n💡 Próximos passos:")
            logger.info("   1. Executar TOPSIS endpoint POST /api/v1/topsis/ranking-hibrido")
            logger.info("   2. Verificar se rankings são diferenciados (não idênticos)")
            logger.info("   3. Validar que cidades com maior desemprego/homicídios têm scores menores")
        else:
            logger.error("❌ ALGUNS TESTES FALHARAM")
            logger.error("Por favor, verifique os logs acima")
            sys.exit(1)
        
        logger.info("="*80)
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante testes: {type(e).__name__}: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
