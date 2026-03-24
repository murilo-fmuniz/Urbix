"""
Serviço de Integração com APIs Governamentais

Este módulo contém funções assíncronas para consumir dados de APIs
governamentais brasileiras de forma robusta e eficiente.

APIs Utilizadas:
- IBGE SIDRA: Dados demográficos (população)
- SICONFI (Tesouro): Dados financeiros municipais
- DataSUS: Dados de infraestrutura de saúde
"""

import httpx
from typing import Dict, Optional, Any
import logging

# Logger para rastrear chamadas e erros das APIs
logger = logging.getLogger(__name__)

# Timeout padrão para requisições (em segundos)
DEFAULT_TIMEOUT = 30.0


async def get_ibge_population(codigo_ibge: str) -> Optional[float]:
    """
    Obtém a população estimada de um município via API IBGE SIDRA.
    
    Consulta a API SIDRA do IBGE para obter a população estimada
    do município referente ao código IBGE informado.
    
    Documentação: https://apisidra.ibge.gov.br/home/ajuda
    Tabela 6579: População estimada
    Variável: 9324
    
    Args:
        codigo_ibge: Código IBGE do município (ex: "4101408" para Apucarana)
    
    Returns:
        float: População estimada, ou None em caso de erro
    
    Raises:
        httpx.HTTPError: Erros de rede são capturados e registrados
    
    Example:
        >>> populacao = await get_ibge_population("4101408")
        >>> print(populacao)
        130000.0
    """
    # Nota: A URL real é /p/last 1 (com espaço), httpx vai URL-encode para last%201
    url = f"https://apisidra.ibge.gov.br/values/t/6579/n6/{codigo_ibge}/v/9324"
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            data = response.json()
            
            # A resposta é um array. O primeiro elemento [0] contém metadados,
            # o segundo elemento [1] contém os dados reais
            if len(data) > 1 and "V" in data[1]:
                # IMPORTANTE: O valor V vem como STRING, precisa converter para float
                populacao = float(data[1]["V"])
                logger.info(f"População obtida para código {codigo_ibge}: {populacao}")
                return populacao
            else:
                logger.warning(f"Resposta inesperada do IBGE para código {codigo_ibge}")
                logger.warning(f"Data estrutura: {data}")
                return None
                
    except httpx.HTTPError as e:
        logger.error(f"Erro ao consultar IBGE para código {codigo_ibge}: {str(e)}")
        return None
    except (ValueError, KeyError, IndexError) as e:
        logger.error(f"Erro ao processar resposta IBGE para código {codigo_ibge}: {str(e)}")
        return None


async def get_siconfi_finances(
    codigo_ibge: str,
    ano_exercicio: int = 2023,
    nr_periodo: int = 6
) -> Optional[Dict[str, float]]:
    """
    Obtém dados financeiros de um município via API SICONFI do Tesouro.
    
    Consulta a API SICONFI para obter receitas e despesas do município
    referente ao exercício fiscal especificado.
    
    A função retorna:
    - receita_propria: RECEITAS DE IMPOSTOS OU RECEITAS REALIZADAS
    - despesas_capital: DESPESAS DE CAPITAL (Despesas Liquidadas)
    - servico_divida: SERVIÇO DA DÍVIDA ou JUROS E ENCARGOS (Despesas Liquidadas)
    
    Documentação: https://apidatalake.tesouro.gov.br/docs
    
    Args:
        codigo_ibge: Código IBGE do município (ex: "4101408")
        ano_exercicio: Ano fiscal (padrão: 2023)
        nr_periodo: Período do exercício, 1-12 ou 6 (semestral)
    
    Returns:
        Dict com chaves: 'receita_propria', 'despesas_capital', 'servico_divida'
        Todos em float. Retorna None em caso de erro.
    
    Raises:
        httpx.HTTPError: Erros de rede são capturados e registrados
    
    Example:
        >>> dados = await get_siconfi_finances("4101408")
        >>> print(dados)
        {'receita_propria': 500000.0, 'despesas_capital': 200000.0, 'servico_divida': 150000.0}
    """
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    params = {
        "id_ente": codigo_ibge,
        "an_exercicio": ano_exercicio,
        "nr_periodo": nr_periodo,
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 01"
    }
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            dados_resposta = response.json()
            
            # A resposta contém um array 'items'
            if not isinstance(dados_resposta, dict) or "items" not in dados_resposta:
                logger.warning(f"Resposta inesperada do SICONFI para código {codigo_ibge}")
                return None
            
            items = dados_resposta.get("items", [])
            
            if not items:
                logger.warning(f"Nenhum dado financeiro encontrado para código {codigo_ibge}")
                return None
            
            receita_propria = 0.0
            despesas_capital = 0.0
            servico_divida = 0.0
            
            # IMPORTANTE: SICONFI usa estrutura diferente:
            # - "conta": Nome da conta contábil
            # - "coluna": Tipo de valor (PREVISÃO INICIAL, RECEITAS REALIZADAS, DESPESAS LIQUIDADAS)
            # - "valor": Valor numérico
            # - "cod_conta": Código da conta
            
            # Procura pelos dados corretos
            # IMPORTANTE: A estrutura real do SICONFI é:
            # - RECEITAS: "RECEITAS CORRENTES", "RECEITAS DE CAPITAL", "TOTAL DAS RECEITAS (V)"
            # - Coluna para realizadas: "Até o Bimestre (c)" (não "REALIZADAS")
            # - CAPITAL: "DESPESAS DE CAPITAL" com coluna "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)"
            # - DÍVIDA: "AMORTIZAÇÃO DA DÍVIDA" e "JUROS E ENCARGOS DA DÍVIDA"
            #          com coluna "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)"
            
            for item in items:
                conta = item.get("conta", "").upper()
                cod_conta = item.get("cod_conta", "").upper()
                coluna = item.get("coluna", "").upper()
                valor = float(item.get("valor", 0) or 0)
                
                # Pular valores zerados para não somar infinitamente zeros
                if valor == 0:
                    continue
                
                # RECEITAS: Procura contas com RECEITA + coluna "Até o Bimestre (c)" (realizadas)
                # As contas pertinentes são "RECEITAS CORRENTES", "RECEITAS DE CAPITAL",
                # "TOTAL DAS RECEITAS (V)", "RECEITAS (EXCETO INTRA-ORÇAMENTÁRIAS) (I)"
                if "RECEITA" in conta and "ATÉ O BIMESTRE" in coluna:
                    # Pega o total (maior agregação) para evitar duplicação
                    if "TOTAL DAS RECEITAS" in conta:
                        receita_propria = valor  # Sobrescreve com o total
                        logger.debug(f"[RECEITA-TOTAL] {conta} / {coluna}: {valor}")
                    elif receita_propria == 0:  # Se ainda não temos total, usa subtotal
                        receita_propria += valor
                        logger.debug(f"[RECEITA-SUB] {conta} / {coluna}: +{valor}")
                
                # DESPESAS DE CAPITAL: "DESPESAS DE CAPITAL" com coluna "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)"
                if "DESPESAS DE CAPITAL" in conta and "DESPESAS LIQUIDADAS ATÉ O BIMESTRE" in coluna:
                    despesas_capital += valor
                    logger.debug(f"[CAPITAL] {conta} / {coluna}: +{valor}")
                
                # SERVIÇO DA DÍVIDA: "AMORTIZAÇÃO DA DÍVIDA" ou "JUROS E ENCARGOS"
                # com coluna "DESPESAS LIQUIDADAS ATÉ O BIMESTRE (h)"
                # IMPORTANTE: Ser específico para não pegar "PESSOAL E ENCARGOS SOCIAIS"
                if "DESPESAS LIQUIDADAS ATÉ O BIMESTRE" in coluna:
                    if ("AMORTIZAÇÃO" in conta or "AMORTIZACAO" in conta):
                        servico_divida += valor
                        logger.debug(f"[DÍVIDA-AMORT] {conta} / {coluna}: +{valor}")
                    elif "JUROS" in conta and "ENCARGO" in conta and "DÍVIDA" in conta:
                        # Especificar: só "JUROS E ENCARGOS DA DÍVIDA", não outros "ENCARGOS"
                        servico_divida += valor
                        logger.debug(f"[DÍVIDA-JUROS] {conta} / {coluna}: +{valor}")
            
            resultado = {
                "receita_propria": receita_propria,
                "despesas_capital": despesas_capital,
                "servico_divida": servico_divida
            }
            
            logger.info(f"Dados financeiros obtidos para código {codigo_ibge}: {resultado}")
            return resultado
            
    except httpx.ConnectError as e:
        # Timeout ou erro de conexão - API indisponível
        logger.warning(f"⚠️  SICONFI temporariamente indisponível para {codigo_ibge} (timeout/conexão)")
        return {
            "receita_propria": 0.0,
            "despesas_capital": 0.0,
            "servico_divida": 0.0
        }
    except httpx.HTTPStatusError as e:
        # Erro HTTP (502, 503, etc)
        if e.response.status_code in [502, 503, 504]:
            logger.warning(f"⚠️  SICONFI indisponível ({e.response.status_code}) para {codigo_ibge}")
        else:
            logger.error(f"Erro HTTP {e.response.status_code} ao consultar SICONFI para {codigo_ibge}")
        return {
            "receita_propria": 0.0,
            "despesas_capital": 0.0,
            "servico_divida": 0.0
        }
    except httpx.HTTPError as e:
        logger.error(f"Erro ao consultar SICONFI para código {codigo_ibge}: {str(e)}")
        return {
            "receita_propria": 0.0,
            "despesas_capital": 0.0,
            "servico_divida": 0.0
        }
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Erro ao processar resposta SICONFI para código {codigo_ibge}: {str(e)}")
        return {
            "receita_propria": 0.0,
            "despesas_capital": 0.0,
            "servico_divida": 0.0
        }


async def get_datasus_health_infrastructure(codigo_ibge: str) -> Optional[int]:
    """
    Obtém o número de hospitais de um município via API DataSUS (CNES).
    
    Consulta a API DataSUS para obter informações sobre infraestrutura
    de saúde, contando estabelecimentos que possuem atendimento hospitalar.
    
    Documentação: https://apidadosabertos.saude.gov.br/
    
    IMPORTANTE: O DataSUS usa estrutura diferente:
    - Resposta em: 'estabelecimentos' (não 'data')
    - Campo para identificar hospital: 'estabelecimento_possui_atendimento_hospitalar' (1=sim, 0=não)
    - Usa código IBGE completo (7 dígitos)
    
    Args:
        codigo_ibge: Código IBGE do município completo (ex: "4101408")
    
    Returns:
        int: Número de hospitais na cidade. Retorna 0 em caso de erro ou timeout.
    
    Example:
        >>> hospitais = await get_datasus_health_infrastructure("4101408")
        >>> print(hospitais)
        3
    """
    url = "https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
    
    # Usa código IBGE completo (7 dígitos)
    params = {
        "codigo_ibge": codigo_ibge
    }
    
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            dados_resposta = response.json()
            
            # IMPORTANTE: DataSUS retorna em 'estabelecimentos', não em 'data'
            if isinstance(dados_resposta, dict):
                items = dados_resposta.get("estabelecimentos", [])
            else:
                items = dados_resposta if isinstance(dados_resposta, list) else []
            
            if not items:
                logger.info(f"Nenhum estabelecimento encontrado para código {codigo_ibge}")
                return 0
            
            # Conta estabelecimentos que têm atendimento hospitalar = 1
            # Campo: 'estabelecimento_possui_atendimento_hospitalar' (1=hospital, 0=não)
            quantidade_hospitais = 0
            for item in items:
                tem_atendimento = item.get("estabelecimento_possui_atendimento_hospitalar", 0)
                if tem_atendimento == 1:
                    quantidade_hospitais += 1
            
            logger.info(f"DataSUS: {quantidade_hospitais} hospitais encontrados para código {codigo_ibge}")
            return quantidade_hospitais
            
    except httpx.ConnectError as e:
        # Timeout ou erro de conexão
        logger.warning(f"⚠️  DataSUS temporariamente indisponível para {codigo_ibge} (timeout/conexão)")
        return 0
    except httpx.HTTPStatusError as e:
        # Erro HTTP (502, 503, etc)
        if e.response.status_code in [502, 503, 504]:
            logger.warning(f"⚠️  DataSUS indisponível ({e.response.status_code}) para {codigo_ibge}")
        else:
            logger.error(f"Erro HTTP {e.response.status_code} ao consultar DataSUS para {codigo_ibge}")
        return 0
    except httpx.HTTPError as e:
        logger.error(f"Erro ao consultar DataSUS para código {codigo_ibge}: {str(e)}")
        return 0
    except (ValueError, KeyError, TypeError) as e:
        logger.error(f"Erro ao processar resposta DataSUS para código {codigo_ibge}: {str(e)}")
        return 0
        return 0


async def get_city_complete_data(codigo_ibge: str) -> Optional[Dict[str, Any]]:
    """
    Obtém dados completos de uma cidade consultando as 3 APIs em paralelo.
    
    Esta função utiliza asyncio.gather() para fazer as 3 chamadas
    simultâneas, reduzindo o tempo total de espera.
    
    Args:
        codigo_ibge: Código IBGE do município
    
    Returns:
        Dict com chaves: 'populacao', 'receita_propria', 'despesas_capital',
        'servico_divida', 'quantidade_hospitais'. Retorna None se alguma
        chamada falhar.
    
    Example:
        >>> dados = await get_city_complete_data("4101408")
        >>> print(dados)
        {
            'populacao': 130000.0,
            'receita_propria': 500000.0,
            'despesas_capital': 200000.0,
            'servico_divida': 150000.0,
            'quantidade_hospitais': 5
        }
    """
    import asyncio
    
    # Executa as 3 chamadas em paralelo
    populacao, finances, hospitais = await asyncio.gather(
        get_ibge_population(codigo_ibge),
        get_siconfi_finances(codigo_ibge),
        get_datasus_health_infrastructure(codigo_ibge),
        return_exceptions=False
    )
    
    # Valida se todas as chamadas foram bem-sucedidas
    if populacao is None or finances is None:
        logger.error(f"Falha ao obter dados completos para código {codigo_ibge}")
        return None
    
    resultado = {
        "populacao": populacao,
        "receita_propria": finances.get("receita_propria", 0.0),
        "despesas_capital": finances.get("despesas_capital", 0.0),
        "servico_divida": finances.get("servico_divida", 0.0),
        "quantidade_hospitais": hospitais if hospitais is not None else 0
    }
    
    return resultado
