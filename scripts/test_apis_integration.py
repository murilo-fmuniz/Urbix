#!/usr/bin/env python3
"""
Script de Teste: Validar DATASUS SIM e CAGED APIs

Testa a busca de dados reais de:
- CAGED: Empregos/Desemprego do Portal da Transparência
- DATASUS SIM: Homicídios e Mortalidade

Uso: python scripts/test_apis_integration.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Setup
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

from process_local_data import DataProcessor


async def test_caged_api():
    """Testa CAGED API para 3 cidades"""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: CAGED API (Portal da Transparência)")
    logger.info("="*80)
    
    processor = DataProcessor()
    
    test_cities = ["4101408", "4113700", "4115200"]  # Apucarana, Londrina, Maringá
    
    logger.info(f"\nTestando {len(test_cities)} cidades...")
    await processor.process_caged_api(test_cities)
    
    logger.info(f"\n✅ Resultados CAGED:")
    for city_code in test_cities:
        if city_code in processor.data:
            data = processor.data[city_code]
            saldo = data.get('saldo_empregos_caged', 'N/A')
            logger.info(f"   - {city_code}: Saldo={saldo}")
        else:
            logger.warning(f"   - {city_code}: Sem dados")


async def test_datasus_sim_api():
    """Testa DATASUS SIM API para 3 cidades"""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: DATASUS SIM API (Homicídios)")
    logger.info("="*80)
    
    processor = DataProcessor()
    
    test_cities = ["4101408", "4113700", "4115200"]  # Apucarana, Londrina, Maringá
    
    logger.info(f"\nTestando {len(test_cities)} cidades...")
    await processor.process_datasus_sim_api(test_cities)
    
    logger.info(f"\n✅ Resultados DATASUS SIM:")
    for city_code in test_cities:
        if city_code in processor.data:
            data = processor.data[city_code]
            homicidios = data.get('homicidios_100k', 'N/A')
            logger.info(f"   - {city_code}: Homicídios/100k={homicidios}")
        else:
            logger.warning(f"   - {city_code}: Sem dados")


async def test_full_etl():
    """Testa ETL completo"""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: ETL Completo (Planilhas + APIs)")
    logger.info("="*80)
    
    processor = DataProcessor()
    processor.process_all()
    
    logger.info(f"\n✅ ETL Completo - Resumo:")
    logger.info(f"   - Total de municípios: {len(processor.data)}")
    
    # Mostrar um exemplo
    if processor.data:
        first_city_code = list(processor.data.keys())[0]
        first_city_data = processor.data[first_city_code]
        
        logger.info(f"\n📍 Exemplo de dados (municipio {first_city_code}):")
        for key, value in sorted(first_city_data.items()):
            logger.info(f"   - {key}: {value}")


async def main():
    """Executar todos os testes"""
    logger.info("="*80)
    logger.info("🧪 TESTES DE INTEGRAÇÃO - APIs Governamentais")
    logger.info("="*80)
    
    try:
        # Test 1: CAGED
        await test_caged_api()
        
        # Test 2: DATASUS SIM
        await test_datasus_sim_api()
        
        # Test 3: Full ETL
        # await test_full_etl()  # Descomente para teste completo
        
        logger.info("\n" + "="*80)
        logger.info("✨ Testes concluídos com sucesso!")
        logger.info("="*80)
        
        logger.info("\n💡 Próximos passos:")
        logger.info("   1. Verificar se os dados estão sendo buscados corretamente")
        logger.info("   2. Verificar cache em: backend/data/cache_api/")
        logger.info("   3. Integrar com TOPSIS para obter rankings reais")
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante testes: {type(e).__name__}: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
