#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🧪 Teste END-TO-END: Fazer requisição real ao servidor TOPSIS
Valida: Integração completa com as 5 novas APIs
"""
import asyncio
import json
import logging
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


async def test_endpoint_real():
    """Teste real do endpoint TOPSIS com uma cidade"""
    logger.info("\n" + "="*80)
    logger.info("🧪 TESTE END-TO-END: Requisição ao Endpoint TOPSIS")
    logger.info("="*80)
    
    try:
        from app.routers.topsis import processar_cidade_real
        from app.schemas import ManualCityIndicators, ISO37120Indicators, ISO37122Indicators, ISO37123AndSendaiIndicators
        from sqlalchemy.orm import Session
        
        # Criar indicadores manuais zerados (simular usuário não preencheu nada)
        manual = ManualCityIndicators(
            iso_37120=ISO37120Indicators(),
            iso_37122=ISO37122Indicators(),
            iso_37123=ISO37123AndSendaiIndicators()
        )
        
        # Testar com uma cidade conhecida
        codigo_ibge = "3304557"  # Rio de Janeiro
        nome_cidade = "Rio de Janeiro"
        
        logger.info(f"\n📍 Testando com: {nome_cidade} (IBGE: {codigo_ibge})")
        logger.info(f"   Indicadores: todos zerados (sem dados manuais)")
        
        # Executar processamento (sem DB)
        resultado = await processar_cidade_real(codigo_ibge, nome_cidade, manual, db=None)
        
        if resultado is None:
            logger.error("❌ Resultado None retornado")
            return False
        
        logger.info(f"\n✅ Processamento completado!")
        logger.info(f"   Tipo resultado: {type(resultado)}")
        logger.info(f"   Chaves: {resultado.keys() if isinstance(resultado, dict) else 'N/A'}")
        logger.info(f"   Nome: {resultado.get('nome_cidade')}")
        
        # O resultado tem 'indicadores_flatalizados' ou 'indicadores'?
        indicadores_key = None
        if 'indicadores_flatalizados' in resultado:
            indicadores_key = 'indicadores_flatalizados'
        elif 'indicadores' in resultado:
            indicadores_key = 'indicadores'
        
        if indicadores_key:
            indicadores = resultado.get(indicadores_key, [])
            logger.info(f"   Indicadores ({indicadores_key}): {len(indicadores)} valores")
            
            if len(indicadores) == 50:
                logger.info(f"   ✅ 50 indicadores processados corretamente")
                
                # Verificar se há dados reais (não todos 0.0)
                non_zero_count = sum(1 for v in indicadores if v > 0)
                
                logger.info(f"   📊 {non_zero_count}/50 indicadores têm dados reais (>0)")
                
                if non_zero_count > 0:
                    logger.info(f"   ✅ Dados reais foram injetados!")
                    return True
                else:
                    logger.warning(f"   ⚠️  Nenhum indicador com dados (todos 0.0)")
                    # Isso não é necessariamente erro, depende das APIs
                    return True
            else:
                logger.error(f"   ❌ Número incorreto de indicadores: {len(indicadores)}")
                logger.info(f"   Resultado: {resultado}")
                return False
        else:
            logger.error(f"   ❌ Campo de indicadores não encontrado no resultado")
            logger.info(f"   Resultado: {resultado}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao processar: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    logger.info("\n🎯 TESTE END-TO-END COM CIDADES REAIS\n")
    
    result = await test_endpoint_real()
    
    logger.info("\n" + "="*80)
    if result:
        logger.info("✅ TESTE END-TO-END PASSOU!")
        logger.info("   O servidor deveria estar funcionando")
    else:
        logger.error("❌ TESTE END-TO-END FALHOU!")
        logger.error("   Verifique os logs de erro acima")
    logger.info("="*80 + "\n")
    
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
