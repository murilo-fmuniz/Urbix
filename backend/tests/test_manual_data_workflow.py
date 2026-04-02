#!/usr/bin/env python
"""
Test Suite for Manual Data Storage and Historical Rankings
Tests the complete workflow of manual data persistence and snapshot creation
"""

import json
import requests
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
TEST_IBGE = "4101408"  # Apucarana
TEST_IBGE_2 = "4113700"  # Londrina (optional)

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_test(title):
    """Print test title"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_response(response, title="Response"):
    """Pretty print API response"""
    try:
        data = response.json()
        print(f"\n{Colors.YELLOW}{title}:{Colors.RESET}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print(f"{Colors.YELLOW}{title}:{Colors.RESET}")
        print(response.text)

def test_create_manual_data():
    """Test 1: Create/Update Manual Data"""
    print_test("TEST 1: Criar/Atualizar Dados Manuais")
    
    payload = {
        "nome_cidade": "Apucarana",
        "usuario_atualizou": "João Silva (joao@prefeitura.pr.gov.br)",
        "dados": {
            "pontos_iluminacao_telegestao": 1500,
            "medidores_inteligentes_energia": 850,
            "cameras_videomonitoramento": 320,
            "estacoes_qualidade_ar": 5,
            "pontos_wifi_publico": 420
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/manual-data/{TEST_IBGE}",
            json=payload,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print_success(f"Dados criados/atualizados para Apucarana ({TEST_IBGE})")
            print_response(response, "Resposta")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_get_manual_data():
    """Test 2: Get Manual Data"""
    print_test("TEST 2: Obter Dados Manuais Atuais")
    
    try:
        response = requests.get(
            f"{BASE_URL}/manual-data/{TEST_IBGE}",
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"Dados obtidos para {TEST_IBGE}")
            print_response(response, "Resposta")
            return True
        elif response.status_code == 404:
            print_error(f"Cidade {TEST_IBGE} não encontrada")
            return False
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_update_manual_data():
    """Test 3: Partial Update Manual Data"""
    print_test("TEST 3: Atualizar Parcialmente Dados Manuais")
    
    payload = {
        "pontos_iluminacao_telegestao": 1750,
        "usuario_atualizou": "Maria Santos (maria@prefeitura.pr.gov.br)",
    }
    
    try:
        response = requests.patch(
            f"{BASE_URL}/manual-data/{TEST_IBGE}",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print_success(f"Dados parcialmente atualizados para {TEST_IBGE}")
            print_response(response, "Resposta")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_get_history():
    """Test 4: Get Change History"""
    print_test("TEST 4: Obter Histórico de Alterações (Auditoria)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/manual-data/{TEST_IBGE}/history?limit=5",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Histórico obtido com {len(data)} registros")
            print_response(response, "Resposta")
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_create_hybrid_ranking():
    """Test 5: Create Hybrid Ranking (auto-saves snapshots)"""
    print_test("TEST 5: Gerar Ranking Híbrido (Auto-salva Snapshots)")
    
    # Prepare cities for ranking
    cities = [
        {"codigo_ibge": TEST_IBGE}  # Apucarana com dados manuais
    ]
    
    if TEST_IBGE_2:
        cities.append({"codigo_ibge": TEST_IBGE_2})
    
    print_info(f"Calculando ranking para {len(cities)} cidade(s)...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/topsis/ranking-hibrido",
            json=cities,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Ranking gerado com sucesso!")
            print_response(response, "Resposta (resumida)")
            
            # Print ranking summary
            if 'ranking' in data:
                print(f"\n{Colors.YELLOW}Resumo do Ranking:{Colors.RESET}")
                for i, cidade in enumerate(data['ranking'][:5], 1):
                    score = cidade.get('score_topsis', 'N/A')
                    score_str = f"{float(score):.3f}" if score != 'N/A' and score is not None else 'N/A'
                    print(f"  {i}. {cidade.get('nome_cidade', 'N/A')}: {score_str}")
            
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_get_indicator_history():
    """Test 6: Get Indicator Historical Series"""
    print_test("TEST 6: Obter Série Histórica de Indicadores")
    
    try:
        response = requests.get(
            f"{BASE_URL}/manual-data/{TEST_IBGE}/indicadores/historico?limit=12",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Série histórica obtida com {len(data)} períodos")
            
            if len(data) > 0:
                # Print latest snapshot
                latest = data[-1]
                print(f"\n{Colors.YELLOW}Último Snapshot:{Colors.RESET}")
                print(f"  Período: {latest.get('periodo_referencia')}")
                print(f"  Data Cálculo: {latest.get('data_calculo')}")
                
                if latest.get('indicadores'):
                    print(f"  Indicadores: {len(latest['indicadores'])} disponíveis")
            
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_get_ranking_history():
    """Test 7: Get Ranking Historical Series"""
    print_test("TEST 7: Obter Série Histórica de Rankings")
    
    try:
        response = requests.get(
            f"{BASE_URL}/manual-data/rankings/historico?limit=12",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Histórico de rankings obtido com {len(data)} registros")
            
            # Group by period
            periodos = {}
            for item in data:
                periodo = item.get('periodo_referencia')
                if periodo not in periodos:
                    periodos[periodo] = 0
                periodos[periodo] += 1
            
            print(f"\n{Colors.YELLOW}Resumo por Período:{Colors.RESET}")
            for periodo in sorted(periodos.keys(), reverse=True)[:5]:
                print(f"  {periodo}: {periodos[periodo]} cidades")
            
            return True
        else:
            print_error(f"Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def test_get_ranking_by_period():
    """Test 8: Get Ranking for Specific Period"""
    print_test("TEST 8: Obter Ranking de um Período Específico")
    
    # Use current month
    periodo = datetime.now().strftime("%Y-%m")
    
    try:
        response = requests.get(
            f"{BASE_URL}/manual-data/rankings/periodo/{periodo}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            ranking_data = data.get('ranking_data', [])
            print_success(f"Ranking do período {periodo} obtido com {len(ranking_data)} cidades")
            
            if len(ranking_data) > 0:
                print(f"\n{Colors.YELLOW}Top 3 Cidades:{Colors.RESET}")
                # ranking_data contains strings/items, sort by score if available
                sorted_data = []
                for item in ranking_data[:3]:
                    if isinstance(item, dict):
                        score = item.get('score_topsis', 0)
                        try:
                            score_val = float(score) if score is not None else 0
                        except (ValueError, TypeError):
                            score_val = 0
                        sorted_data.append((item, score_val))
                
                for i, (cidade, score) in enumerate(sorted(sorted_data, key=lambda x: x[1], reverse=True), 1):
                    cidade_nome = cidade.get('nome_cidade', 'N/A') if isinstance(cidade, dict) else str(cidade)
                    print(f"  {i}. {cidade_nome}: {score:.3f}")
            
            return True
        else:
            print_error(f"Status {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Erro ao conectar: {str(e)}")
        return False

def main():
    """Run all tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║  TESTE COMPLETO: DADOS MANUAIS E HISTÓRICOS                  ║")
    print("║  (Manual Data Storage + Historical Rankings)                 ║")
    print("╚═══════════════════════════════════════════════════════════════╝")
    print(Colors.RESET)
    
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Cidade Teste: Apucarana ({TEST_IBGE})")
    print_info(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Run tests
    results = {}
    
    print(f"{Colors.YELLOW}[FASE 1] TESTES DE DADOS MANUAIS{Colors.RESET}")
    results['create'] = test_create_manual_data()
    time.sleep(1)
    
    results['get'] = test_get_manual_data()
    time.sleep(1)
    
    results['update'] = test_update_manual_data()
    time.sleep(1)
    
    results['history'] = test_get_history()
    time.sleep(2)  # Wait before next phase
    
    print(f"\n{Colors.YELLOW}[FASE 2] TESTES DE RANKING E SNAPSHOTS{Colors.RESET}")
    results['ranking'] = test_create_hybrid_ranking()
    time.sleep(2)
    
    results['indicators'] = test_get_indicator_history()
    time.sleep(1)
    
    results['rankings_history'] = test_get_ranking_history()
    time.sleep(1)
    
    results['period_ranking'] = test_get_ranking_by_period()
    
    # Summary
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}RESUMO DOS TESTES{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = f"{Colors.GREEN}PASSOU{Colors.RESET}" if passed_test else f"{Colors.RED}FALHOU{Colors.RESET}"
        print(f"  {test_name.ljust(20)}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} testes passaram{Colors.RESET}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ TODOS OS TESTES PASSARAM!{Colors.RESET}")
        print(f"{Colors.GREEN}O sistema de dados manuais e histórico está funcionando corretamente.{Colors.RESET}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ ALGUNS TESTES FALHARAM{Colors.RESET}")
        print(f"{Colors.RED}Verifique os erros acima para mais detalhes.{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    exit(main())
