"""
Teste que copia EXATAMENTE a função get_siconfi_finances
"""

import asyncio
import httpx
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 30.0

async def get_siconfi_finances_debug(
    codigo_ibge: str,
    ano_exercicio: int = 2023,
    nr_periodo: int = 6
):
    """Cópia exata da função para debug"""
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    params = {
        "id_ente": codigo_ibge,
        "an_exercicio": ano_exercicio,
        "nr_periodo": nr_periodo,
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 01"
    }
    
    logger.info(f"🔍 Requisição SICONFI para {codigo_ibge}")
    logger.info(f"   Parâmetros: {params}")
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=params)
            logger.info(f"   Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"❌ Erro HTTP: {response.status_code}")
                return None
                
            dados_resposta = response.json()
            
            logger.info(f"   Resposta keys: {list(dados_resposta.keys())}")
            
            # A resposta contém um array 'items'
            if not isinstance(dados_resposta, dict) or "items" not in dados_resposta:
                logger.warning(f"Resposta inesperada do SICONFI para código {codigo_ibge}")
                logger.warning(f"   Estrutura: {dados_resposta}")
                return None
            
            items = dados_resposta.get("items", [])
            logger.info(f"   Total items: {len(items)}")
            
            if not items:
                logger.warning(f"Nenhum dado financeiro encontrado para código {codigo_ibge}")
                return None

            receita_propria = 0.0
            receita_total = 0.0
            despesas_capital = 0.0
            servico_divida = 0.0
            
            items_processados = 0
            items_ignorados = 0

            for item in items:
                conta = item.get("conta", "").upper()
                coluna = item.get("coluna", "").upper()
                valor = float(item.get("valor", 0) or 0)
                
                if valor == 0:
                    items_ignorados += 1
                    continue
                
                # 🎯 RECEITA TOTAL
                if "RECEITAS (EXCETO INTRA-ORÇAMENTÁRIAS)" in conta and "PREVISÃO INICIAL" in coluna:
                    receita_total = valor
                    logger.debug(f"[RECEITA-TOTAL] {conta} ({coluna}): R$ {valor:,.2f}")
                    items_processados += 1
                
                # 🎯 RECEITA PRÓPRIA
                if ("RECEITAS DE IMPOSTOS" in conta or "RECEITA DE IMPOSTOS" in conta) and "PREVISÃO INICIAL" in coluna:
                    if receita_propria == 0:
                        receita_propria += valor
                        logger.debug(f"[RECEITA-PRÓPRIA] {conta} ({coluna}): R$ {valor:,.2f}")
                        items_processados += 1
                
                # 🎯 DESPESAS DE CAPITAL
                if "DESPESAS DE CAPITAL" in conta and "PREVISÃO INICIAL" in coluna:
                    despesas_capital += valor
                    logger.debug(f"[CAPITAL] {conta} ({coluna}): +R$ {valor:,.2f}")
                    items_processados += 1
                
                # 🎯 SERVIÇO DA DÍVIDA
                if "DESPESAS" in conta and ("JUROS" in conta or "ENCARGOS" in conta) and "PREVISÃO INICIAL" in coluna:
                    servico_divida += valor
                    logger.debug(f"[DÍVIDA] {conta} ({coluna}): +R$ {valor:,.2f}")
                    items_processados += 1

            logger.info(f"\n📊 RESULTADO FINAL:")
            logger.info(f"   Items processados: {items_processados}")
            logger.info(f"   Items ignorados: {items_ignorados}")
            logger.info(f"   Receita Total: R$ {receita_total:,.2f}")
            logger.info(f"   Receita Própria: R$ {receita_propria:,.2f}")
            logger.info(f"   Despesas Capital: R$ {despesas_capital:,.2f}")
            logger.info(f"   Serviço Dívida: R$ {servico_divida:,.2f}")

            resultado = {
                "receita_propria": receita_propria,
                "receita_total": receita_total,
                "despesas_capital": despesas_capital,
                "servico_divida": servico_divida
            }
            
            logger.info(f"\n✅ Resultado: {resultado}")
            return resultado
            
    except Exception as e:
        logger.error(f"❌ Erro: {type(e).__name__}: {str(e)}", exc_info=True)
        return None


async def main():
    print("=" * 100)
    print("🧪 TESTE DEBUG: get_siconfi_finances")
    print("=" * 100)
    
    # Testar com Apucarana
    print("\n\n📍 TESTANDO: Apucarana (4101408)")
    print("-" * 100)
    resultado = await get_siconfi_finances_debug("4101408", 2023, 6)
    
    print("\n\n📍 TESTANDO: Londrina (4113700)")
    print("-" * 100)
    resultado = await get_siconfi_finances_debug("4113700", 2023, 6)


if __name__ == "__main__":
    asyncio.run(main())
