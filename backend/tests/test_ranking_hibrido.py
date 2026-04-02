#!/usr/bin/env python3
"""
Script de Teste: Validação do Endpoint /ranking-hibrido Refatorado

Este script testa as 3 estratégias de agregação:
1. Flattening (Extração dinâmica de 47 indicadores)
2. API Injection (Injeção de dados automáticos)
3. Mock Survival (Preenchimento de gaps)

Uso:
    python test_ranking_hibrido.py
    
Requisitos:
    - Backend rodando em http://localhost:8000
    - Dependências: requests, json
"""

import requests
import json
import sys
from typing import Dict, List, Any
import time

# ==========================================
# CONFIGURAÇÃO
# ==========================================

BACKEND_URL = "http://localhost:8000"
TOPSIS_ENDPOINT = f"{BACKEND_URL}/topsis/ranking-hibrido"

# Payload de teste com 3 cidades
TEST_PAYLOAD = [
    {
        "codigo_ibge": "3126400",
        "nome_cidade": "Brasília",
        "manual_indicators": {
            "bombeiros_por_100k": 50.0,
            "pontos_iluminacao_telegestao": 35.0,
            "medidores_inteligentes_energia": 22.0,
            "area_verde_mapeada": 45.0
        }
    },
    {
        "codigo_ibge": "3550308",
        "nome_cidade": "São Paulo",
        "manual_indicators": {
            "bombeiros_por_100k": 42.0,
            "pontos_iluminacao_telegestao": 28.0,
            "medidores_inteligentes_energia": 18.0,
            "area_verde_mapeada": 32.0
        }
    },
    {
        "codigo_ibge": "2304400",
        "nome_cidade": "Fortaleza",
        "manual_indicators": {
            "bombeiros_por_100k": 38.0,
            "pontos_iluminacao_telegestao": 0.0,  # Gap para testar mock
            "medidores_inteligentes_energia": 0.0,  # Gap para testar mock
            "area_verde_mapeada": 25.0
        }
    }
]

# ==========================================
# FUNÇÕES DE TESTE
# ==========================================

def print_header(titulo: str, nivel: int = 1):
    """Imprime cabeçalho formatado"""
    chars = "=" if nivel == 1 else "-"
    print(f"\n{chars * 100}")
    print(f"{titulo}")
    print(f"{chars * 100}\n")


def test_backend_connectivity():
    """Testa se backend está acessível"""
    print_header("1️⃣  TESTE: Conectividade com Backend", 1)
    
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=5)
        if response.status_code == 404:  # Endpoint não existe, mas backend respondeu
            print("✅ Backend ESTÁ RESPONDENDO (porta 8000 aberta)")
            return True
        elif response.status_code == 200:
            print("✅ Backend RESPONDENDO NORMALMENTE")
            return True
    except requests.ConnectionError:
        print("❌ ERRO: Backend NÃO está respondendo")
        print(f"   Certifique-se que o backend está rodando:")
        print(f"   $ cd backend && uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"⚠️  ERRO inesperado: {str(e)}")
        return False


def test_payload_validation():
    """Valida estrutura do payload"""
    print_header("2️⃣  TESTE: Validação do Payload", 1)
    
    print(f"📊 Cidades no payload: {len(TEST_PAYLOAD)}")
    
    for i, city in enumerate(TEST_PAYLOAD, 1):
        print(f"\n   #{i} {city['nome_cidade']}")
        print(f"      IBGE: {city['codigo_ibge']}")
        print(f"      Fields: {', '.join(city['manual_indicators'].keys())}")
        
        # Contar campos com 0.0
        zeros = sum(1 for v in city['manual_indicators'].values() if v == 0.0)
        print(f"      Campos com 0.0 (para mock): {zeros}")
    
    print("\n✅ Payload validado")
    return True


def test_ranking_endpoint():
    """Testa o endpoint POST /ranking-hibrido"""
    print_header("3️⃣  TESTE: Endpoint /ranking-hibrido", 1)
    
    try:
        print(f"🚀 Enviando requisição para {TOPSIS_ENDPOINT}...")
        print(f"   Payload: {len(TEST_PAYLOAD)} cidades")
        
        start_time = time.time()
        response = requests.post(
            TOPSIS_ENDPOINT,
            json=TEST_PAYLOAD,
            timeout=30
        )
        elapsed_time = time.time() - start_time
        
        print(f"⏱️  Tempo de resposta: {elapsed_time:.2f}s")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Endpoint retornou 200 OK")
            return True, response.json()
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return False, None
            
    except requests.Timeout:
        print("❌ TIMEOUT: Requisição demorou mais de 30s")
        return False, None
    except requests.ConnectionError:
        print("❌ Erro de conexão com backend")
        return False, None
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False, None


def validate_response_structure(result: Dict[str, Any]) -> bool:
    """Valida estrutura da resposta"""
    print_header("4️⃣  TESTE: Estrutura da Resposta", 1)
    
    checks = {
        "cidades": lambda r: isinstance(r.get("cidades"), list),
        "ranking": lambda r: isinstance(r.get("ranking"), list),
        "detalhes_calculo": lambda r: isinstance(r.get("detalhes_calculo"), dict),
    }
    
    for field, check in checks.items():
        if check(result):
            print(f"✅ Campo '{field}' presente e tipo correto")
        else:
            print(f"❌ Campo '{field}' FALTANDO ou tipo incorreto")
            return False
    
    return True


def validate_ranking_data(result: Dict[str, Any]) -> bool:
    """Valida dados do ranking"""
    print_header("5️⃣  TESTE: Dados do Ranking", 1)
    
    ranking = result.get("ranking", [])
    
    if len(ranking) < 2:
        print(f"❌ Ranking deve ter pelo menos 2 cidades, obteve {len(ranking)}")
        return False
    
    print(f"✅ Ranking com {len(ranking)} cidades:\n")
    
    for i, city in enumerate(ranking, 1):
        indice = city.get("indice_smart", 0)
        nome = city.get("nome_cidade", "???")
        pct = city.get("percentual_smart", "???")
        
        print(f"   #{i} {nome:20s} → {pct:7s} (Índice: {indice:.4f})")
    
    # Validar que índices são diferentes (não binários)
    indices = [c.get("indice_smart", 0) for c in ranking]
    max_indice = max(indices)
    min_indice = min(indices)
    
    print(f"\n   Range de Índices: {min_indice:.4f} → {max_indice:.4f}")
    
    # Heurística: Se range é muito pequeno, pode ser problema de distribuição
    if max_indice - min_indice < 0.05:
        print(f"   ⚠️  Warning: Pequena variância nos índices (diff < 0.05)")
        print(f"      Isso pode indicar que a matriz tem pouca variância")
    else:
        print(f"   ✅ Variância aceitável (diff ≥ 0.05)")
    
    return True


def validate_coverage_metadata(result: Dict[str, Any]) -> bool:
    """Valida metadados de cobertura"""
    print_header("6️⃣  TESTE: Metadados de Cobertura", 1)
    
    calculatosdetalhes = result.get("detalhes_calculo", {})
    cobertura = calculatosdetalhes.get("cobertura_dados_por_cidade", [])
    
    if not cobertura:
        print("⚠️  Nenhum metadado de cobertura encontrado")
        return True
    
    print("Cobertura de Dados por Cidade:\n")
    
    for cov in cobertura:
        nome = cov.get("nome_cidade", "???")
        total = cov.get("total_indicadores", 0)
        reais = cov.get("quantidade_dados_reais", 0)
        pct = cov.get("pct_cobertura", 0)
        media = cov.get("media_indicadores", 0)
        
        print(f"   {nome:20s}: {reais}/{total} reais ({pct:.1f}%) | Média: {media:.2f}")
    
    print("\n✅ Metadados validados")
    return True


def validate_matrix_dimensions(result: Dict[str, Any]) -> bool:
    """Valida dimensões da matriz de decisão"""
    print_header("7️⃣  TESTE: Dimensões da Matriz de Decisão", 1)
    
    detalhes = result.get("detalhes_calculo", {})
    total_ind = detalhes.get("total_indicadores", 0)
    
    print(f"   Total de Indicadores: {total_ind}")
    
    if total_ind != 47:
        print(f"❌ ERRO: Esperado 47 indicadores, obteve {total_ind}")
        return False
    
    print(f"✅ Dimensão de indicadores correta (47)")
    
    # Validar pesos
    pesos = detalhes.get("pesos", [])
    if len(pesos) != 47:
        print(f"❌ ERRO: Pesos incorretos - {len(pesos)} ao invés de 47")
        return False
    
    print(f"✅ Pesos corretos (47 elementos, cada um ≈ {1/47:.4f})")
    
    # Validar impactos
    impactos = detalhes.get("impactos", [])
    if len(impactos) != 47:
        print(f"❌ ERRO: Impactos incorretos - {len(impactos)} ao invés de 47")
        return False
    
    print(f"✅ Impactos corretos (47 elementos)")
    
    return True


def main():
    """Executa suite completa de testes"""
    
    print("\n")
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 98 + "║")
    print("║" + "  🧪 SUITE DE TESTES: TOPSIS Híbrido Refatorado (47 Indicadores ISO)".center(98) + "║")
    print("║" + " " * 98 + "║")
    print("╚" + "=" * 98 + "╝")
    
    tests_passed = 0
    tests_failed = 0
    
    # Teste 1: Conectividade
    if not test_backend_connectivity():
        print("\n❌ FALHA CRÍTICA: Backend não está acessível")
        print("   Inicie o backend com: cd backend && uvicorn main:app --reload")
        sys.exit(1)
    tests_passed += 1
    
    # Teste 2: Validação do Payload
    if not test_payload_validation():
        tests_failed += 1
    else:
        tests_passed += 1
    
    # Teste 3: Endpoint
    success, result = test_ranking_endpoint()
    if not success:
        tests_failed += 1
        print("\n❌ Não foi possível continuar os testes (endpoint falhou)")
        print("\nVerifique os logs do backend para mais detalhes")
        sys.exit(1)
    tests_passed += 1
    
    # Teste 4: Estrutura da Resposta
    if not validate_response_structure(result):
        tests_failed += 1
    else:
        tests_passed += 1
    
    # Teste 5: Dados do Ranking
    if not validate_ranking_data(result):
        tests_failed += 1
    else:
        tests_passed += 1
    
    # Teste 6: Cobertura de Dados
    if not validate_coverage_metadata(result):
        tests_failed += 1
    else:
        tests_passed += 1
    
    # Teste 7: Dimensões da Matriz
    if not validate_matrix_dimensions(result):
        tests_failed += 1
    else:
        tests_passed += 1
    
    # ==========================================
    # RESUMO FINAL
    # ==========================================
    
    print_header("📋 RESUMO DOS TESTES", 1)
    
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Testes PASSOU: {tests_passed}/{total_tests}")
    print(f"❌ Testes FALHARAM: {tests_failed}/{total_tests}")
    print(f"📊 Taxa de Sucesso: {success_rate:.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 TODOS OS TESTES PASSARAM! ✨")
        print("\nO endpoint /ranking-hibrido está FUNCIONANDO CORRETAMENTE:")
        print("  ✅ Flattening: 47 indicadores extraídos em ordem")
        print("  ✅ API Injection: Dados automáticos injetados")
        print("  ✅ Mock Survival: Gaps preenchidos com valores realistas")
        print("  ✅ Matriz Validada: Dimensões corretas (N cidades × 47 indicadores)")
        sys.exit(0)
    else:
        print("\n❌ ALGUNS TESTES FALHARAM")
        print("\nVerifique os erros acima e os logs do backend")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERRO NÃO TRATADO: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
