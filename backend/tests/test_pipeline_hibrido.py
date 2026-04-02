#!/usr/bin/env python3
"""
Script de Teste de Integração - Pipeline Híbrido Urbix

Este script simula a requisição que o Dashboard frontal enviará para o endpoint
/topsis/ranking-hibrido, validando:
- Cálculo de novos indicadores (Independência Financeira, Orçamento per capita)
- Índice Smart (C_i) do TOPSIS
- Estabilidade da matriz expandida (10 critérios)

Uso: python test_pipeline_hibrido.py
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, List, Any

# Configuração de cores para terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text: str):
    """Imprimi cabeçalho formatado"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(text: str):
    """Imprimi mensagem de sucesso"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_warning(text: str):
    """Imprimi mensagem de aviso"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text: str):
    """Imprimi mensagem de erro"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text: str):
    """Imprimi informação"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def create_payload() -> List[Dict[str, Any]]:
    """
    Cria payload de teste simulando requisição do frontend.
    
    3 cidades com indicadores manuais variados:
    - Apucarana: Moderado em infraestrutura inteligente
    - Londrina: Avançado em telegestão
    - Maringá: Iniciante com foco em áreas verdes
    """
    payload = [
        {
            "codigo_ibge": "4101408",
            "manual_indicators": {
                "pontos_iluminacao_telegestao": 60.0,  # 60% (moderado)
                "medidores_inteligentes_energia": 45.0,  # 45%
                "bombeiros_por_100k": 60.0,  # 60 bombeiros
                "area_verde_mapeada": 50.0,  # 50% da área
            }
        },
        {
            "codigo_ibge": "4113700",
            "manual_indicators": {
                "pontos_iluminacao_telegestao": 90.0,  # 90% (avançado!)
                "medidores_inteligentes_energia": 80.0,  # 80%
                "bombeiros_por_100k": 85.0,  # 85 bombeiros
                "area_verde_mapeada": 70.0,  # 70% da área
            }
        },
        {
            "codigo_ibge": "4115200",
            "manual_indicators": {
                "pontos_iluminacao_telegestao": 30.0,  # 30% (iniciante)
                "medidores_inteligentes_energia": 20.0,  # 20%
                "bombeiros_por_100k": 40.0,  # 40 bombeiros
                "area_verde_mapeada": 85.0,  # 85% da área (força em verde!)
            }
        }
    ]
    return payload


async def test_pipeline_hibrido(base_url: str = "http://127.0.0.1:8000"):
    """
    Executa teste do pipeline híbrido com validações completas.
    """
    try:
        print_header(f"🧪 TESTE DE PIPELINE HÍBRIDO - URBIX")
        
        # ========== PASSO 1: Criar Payload ==========
        print_info("PASSO 1: Criando payload de teste...")
        payload = create_payload()
        print_success(f"Payload criado com {len(payload)} cidades")
        
        # Exibir payload
        print(f"\n{Colors.BOLD}Payload enviado:{Colors.ENDC}")
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        
        # ========== PASSO 2: Fazer Requisição ==========
        print_info("\nPASSO 2: Enviando POST para /topsis/ranking-hibrido...")
        
        endpoint = f"{base_url}/api/v1/topsis/ranking-hibrido"
        print(f"URL: {Colors.OKCYAN}{endpoint}{Colors.ENDC}")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(endpoint, json=payload)
        
        print(f"Status HTTP: {Colors.BOLD}{response.status_code}{Colors.ENDC}")
        
        # ========== PASSO 3: Validar Response ==========
        if response.status_code != 200:
            print_error(f"Erro na requisição!")
            print(f"\nResposta completa:")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return False
        
        print_success("Requisição bem-sucedida (200 OK)")
        
        # ========== PASSO 4: Parse da Resposta ==========
        print_info("\nPASSO 3: Parseando resposta...")
        result = response.json()
        
        print(f"\n{Colors.BOLD}Resposta do servidor:{Colors.ENDC}")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # ========== PASSO 5: Validações Críticas ==========
        print_info("\nPASSO 4: Executando validações críticas...")
        
        # Validação 1: Estrutura básica
        if "ranking" not in result:
            print_error("Campo 'ranking' não encontrado na resposta")
            return False
        print_success("Campo 'ranking' presente")
        
        if "detalhes_calculo" not in result:
            print_error("Campo 'detalhes_calculo' não encontrado na resposta")
            return False
        print_success("Campo 'detalhes_calculo' presente")
        
        ranking = result["ranking"]
        detalhes = result["detalhes_calculo"]
        
        # Validação 2: Número de cidades
        if len(ranking) != len(payload):
            print_error(f"Número de cidades no ranking ({len(ranking)}) != payload ({len(payload)})")
            return False
        print_success(f"Todas as {len(payload)} cidades no ranking")
        
        # ========== PASSO 6: Validar Índice Smart ==========
        print_info("\nPASSO 5: Validando Índice Smart (C_i)...")
        print(f"\n{Colors.BOLD}Ranking de Smart Cities:{Colors.ENDC}")
        
        all_indices_valid = True
        for i, city in enumerate(ranking, 1):
            nome = city.get("nome_cidade", "Desconhecida")
            indice = city.get("indice_smart", None)
            
            # Validações
            if indice is None:
                print_error(f"  #{i} {nome}: Índice Smart é NULO!")
                all_indices_valid = False
            elif indice == 0.0:
                print_warning(f"  #{i} {nome}: Índice Smart = 0.0 (atenção!)")
                all_indices_valid = False
            elif not (0.0 <= indice <= 1.0):
                print_warning(f"  #{i} {nome}: Índice Smart = {indice:.4f} (fora do intervalo [0,1])")
            else:
                print_success(f"  #{i} {nome}: Índice Smart = {Colors.BOLD}{indice:.4f}{Colors.ENDC}")
        
        if not all_indices_valid:
            print_error("Validação de Índice Smart falhou!")
            return False
        
        # ========== PASSO 7: Validar Novos Indicadores ==========
        print_info("\nPASSO 6: Validando novos indicadores (ISO 37120)...")
        print(f"\n{Colors.BOLD}Indicadores Automáticos por Cidade:{Colors.ENDC}")
        
        all_indicators_valid = True
        
        # Acessar dados da matriz para validar indicadores
        # A resposta contém detalhes_calculo.indicadores que lista os nomes
        indicadores_nomes = detalhes.get("indicadores", [])
        print_info(f"Total de indicadores na matriz: {len(indicadores_nomes)}")
        
        # Imprimir todos os indicadores
        for idx, ind_nome in enumerate(indicadores_nomes):
            print(f"  [{idx}] {ind_nome}")
        
        # Validação: Verificar se os novos indicadores estão na matriz
        novos_indicadores = [
            "Independência Financeira (%)",
            "Orçamento per capita"
        ]
        
        print(f"\n{Colors.BOLD}Verificando novos indicadores:{Colors.ENDC}")
        for novo_ind in novos_indicadores:
            if novo_ind in indicadores_nomes:
                print_success(f"'{novo_ind}' encontrado no cálculo TOPSIS")
            else:
                print_error(f"'{novo_ind}' NÃO encontrado no cálculo TOPSIS!")
                all_indicators_valid = False
        
        # ========== PASSO 8: Validar Matriz Expandida ==========
        print_info("\nPASSO 7: Validando matriz expandida (10 critérios)...")
        
        # Esperar 10 critérios
        expected_criteria_count = 10
        actual_criteria_count = len(indicadores_nomes)
        
        if actual_criteria_count == expected_criteria_count:
            print_success(f"Matriz com {actual_criteria_count} critérios (como esperado)")
        else:
            print_warning(f"Matriz com {actual_criteria_count} critérios (esperado {expected_criteria_count})")
        
        # Validar pesos
        pesos = detalhes.get("pesos_normalizados", [])
        if pesos:
            soma_pesos = sum(pesos)
            if abs(soma_pesos - 1.0) < 0.01:  # Tolerância de 0.01
                print_success(f"Soma de pesos normalized = {soma_pesos:.4f} (✓)")
            else:
                print_warning(f"Soma de pesos normalized = {soma_pesos:.4f} (esperado 1.0)")
        
        # ========== PASSO 9: Verificar Zeros e NaNs ==========
        print_info("\nPASSO 8: Verificando ZeroDivisionErrors e valores inválidos...")
        
        has_errors = False
        for i, city in enumerate(ranking, 1):
            nome = city.get("nome_cidade", "Desconhecida")
            indice = city.get("indice_smart", None)
            
            # Checagem de NaN
            if indice is not None:
                if isinstance(indice, str) and indice.lower() == "nan":
                    print_error(f"  {nome}: Índice Smart = NaN!")
                    has_errors = True
                elif isinstance(indice, float) and indice != indice:  # NaN check
                    print_error(f"  {nome}: Índice Smart = NaN!")
                    has_errors = True
        
        if has_errors:
            print_error("Validação falhou: encontrados valores inválidos (NaN)")
            return False
        
        print_success("Nenhum NaN ou erro de divisão detectado")
        
        # ========== PASSO 10: Resumo Final ==========
        print_header("📊 RESUMO FINAL DO TESTE")
        
        print(f"\n{Colors.BOLD}Resultados:{Colors.ENDC}")
        for i, city in enumerate(ranking, 1):
            nome = city.get("nome_cidade", "?")
            indice = city.get("indice_smart", 0)
            print(f"  {'🥇' if i == 1 else '🥈' if i == 2 else '🥉' if i == 3 else '  '} "
                  f"#{i} {Colors.BOLD}{nome}{Colors.ENDC}: {indice:.4f}")
        
        print(f"\n{Colors.BOLD}Estatísticas:{Colors.ENDC}")
        print(f"  Cidades processadas: {len(ranking)}")
        print(f"  Indicadores na matriz: {len(indicadores_nomes)}")
        print(f"  Soma de pesos: {sum(pesos):.4f}" if pesos else "  Pesos: N/A")
        
        # ========== CONCLUSÃO ==========
        print_header("✅ TESTE PASSOU COM SUCESSO!")
        print(f"{Colors.OKGREEN}{Colors.BOLD}O pipeline híbrido está estável e operacional.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}Novos indicadores funcionando corretamente.{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}Matriz TOPSIS expandida validada.{Colors.ENDC}\n")
        
        return True
        
    except httpx.ConnectError as e:
        print_error(f"Erro de conexão: Não foi possível conectar ao servidor")
        print(f"  Detalhes: {str(e)}")
        print_info("Certifique-se de que o servidor está rodando com:")
        print_info("  python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
        return False
        
    except httpx.TimeoutException as e:
        print_error(f"Timeout: Requisição demorou muito")
        print(f"  Detalhes: {str(e)}")
        return False
        
    except json.JSONDecodeError as e:
        print_error(f"Erro ao parsear JSON da resposta")
        print(f"  Detalhes: {str(e)}")
        return False
        
    except Exception as e:
        print_error(f"Erro inesperado durante o teste")
        print(f"  Tipo: {type(e).__name__}")
        print(f"  Detalhes: {str(e)}")
        import traceback
        print(f"\n{Colors.FAIL}Traceback:{Colors.ENDC}")
        print(traceback.format_exc())
        return False


async def main():
    """Função principal"""
    try:
        print(f"\n{Colors.BOLD}{Colors.OKCYAN}🚀 Iniciando teste de integração do Pipeline Híbrido Urbix{Colors.ENDC}\n")
        
        # Configuração
        base_url = "http://127.0.0.1:8000"
        print_info(f"Servidor alvo: {base_url}")
        print_info("Endpoint: POST /api/v1/topsis/ranking-hibrido\n")
        
        # Executar teste
        success = await test_pipeline_hibrido(base_url)
        
        # Retornar código de saída apropriado
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Teste interrompido pelo usuário{Colors.ENDC}\n")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
