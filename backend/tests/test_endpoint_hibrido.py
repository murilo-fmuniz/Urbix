#!/usr/bin/env python3
"""
Script de teste para validar o endpoint /ranking-hibrido
"""
import asyncio
import json
import logging
from typing import List

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_ranking_hibrido():
    """Teste do endpoint /ranking-hibrido com dados simulados"""
    try:
        logger.info("=" * 80)
        logger.info("🧪 TESTE DO ENDPOINT /ranking-hibrido")
        logger.info("=" * 80)
        
        # Importar FastAPI app
        from app.main import app
        from fastapi.testclient import TestClient
        
        # Criar cliente de testes
        client = TestClient(app)
        
        # ========== TESTE 1: Requisição válida com indicadores manuais ==========
        logger.info("\n[TESTE 1] Enviando requisição POST com dados híbridos...")
        
        payload = [
            {
                "codigo_ibge": "4101408",
                "manual_indicators": {
                    "pontos_iluminacao_telegestao": 60.0,
                    "medidores_inteligentes_energia": 45.0,
                    "bombeiros_por_100k": 60.0,
                    "area_verde_mapeada": 50.0,
                }
            },
            {
                "codigo_ibge": "4113700",
                "manual_indicators": {
                    "pontos_iluminacao_telegestao": 55.0,
                    "medidores_inteligentes_energia": 40.0,
                    "bombeiros_por_100k": 55.0,
                    "area_verde_mapeada": 45.0,
                }
            }
        ]
        
        logger.info(f"Payload: {json.dumps(payload, indent=2)}")
        
        # Fazer requisição
        response = client.post("/api/v1/topsis/ranking-hibrido", json=payload)
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"✅ Requisição bem-sucedida!")
            logger.info(f"\nResultado:")
            logger.info(json.dumps(result, indent=2, default=str))
            
            # Validar estrutura da resposta
            assert "ranking" in result, "Campo 'ranking' não encontrado"
            assert "detalhes_calculo" in result, "Campo 'detalhes_calculo' não encontrado"
            logger.info("\n✅ Estrutura da resposta validada")
            
            # Validar items do ranking
            for i, city in enumerate(result["ranking"], 1):
                assert "nome_cidade" in city, f"Campo 'nome_cidade' não encontrado em ranking[{i}]"
                assert "indice_smart" in city, f"Campo 'indice_smart' não encontrado em ranking[{i}]"
                logger.info(f"   #{i} {city['nome_cidade']}: Índice Smart = {city['indice_smart']:.4f}")
            
            logger.info("\n✅ TESTE 1 PASSOU")
        else:
            logger.error(f"❌ Erro na requisição: Status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
        
        # ========== TESTE 2: Requisição com indicadores manuais nulos ==========
        logger.info("\n[TESTE 2] Enviando requisição com indicadores manuais nulos...")
        
        payload_null = [
            {
                "codigo_ibge": "4101408",
                "manual_indicators": None
            }
        ]
        
        response = client.post("/api/v1/topsis/ranking-hibrido", json=payload_null)
        
        if response.status_code == 200:
            logger.info("✅ Requisição com indicadores nulos bem-sucedida")
            logger.info("✅ TESTE 2 PASSOU")
        else:
            logger.error(f"❌ Erro na requisição: Status {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
        
        # ========== TESTE 3: Validar que health endpoint funciona ==========
        logger.info("\n[TESTE 3] Validando endpoint /health...")
        
        response = client.get("/api/v1/health")
        if response.status_code == 200:
            logger.info(f"✅ Health endpoint respondendo: {response.json()}")
            logger.info("✅ TESTE 3 PASSOU")
        else:
            logger.error(f"❌ Health endpoint falhou: {response.status_code}")
            return False
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ TODOS OS TESTES DE ENDPOINT PASSARAM!")
        logger.info("=" * 80)
        return True
        
    except Exception as e:
        logger.error(f"❌ ERRO NO TESTE: {str(e)}", exc_info=True)
        return False


if __name__ == "__main__":
    result = asyncio.run(test_ranking_hibrido())
    exit(0 if result else 1)
