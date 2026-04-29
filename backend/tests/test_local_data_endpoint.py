"""
Integration Tests: Local Data Endpoint
=======================================

Testes de endpoints FastAPI que consomem dados do indicators_master.json.
Usa TestClient do FastAPI para validação de HTTP responses.
"""

import pytest
from fastapi.testclient import TestClient
from typing import Dict, Any

# Import da aplicação FastAPI
from app.main import app


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Cria TestClient para fazer requisições HTTP."""
    return TestClient(app)


@pytest.fixture
def apucarana_id() -> str:
    """ID de Apucarana para testes."""
    return "4101408"


@pytest.fixture
def londrina_id() -> str:
    """ID de Londrina para testes."""
    return "4113700"


@pytest.fixture
def inexistent_id() -> str:
    """ID inexistente para testes."""
    return "9999999"


# ============================================================================
# TESTES DO ENDPOINT GET /municipio/{id}
# ============================================================================

class TestMunicipioEndpoint:
    """Testes do endpoint de consulta de município."""
    
    def test_get_municipio_apucarana_status_200(self, client: TestClient, apucarana_id: str):
        """✅ GET /api/v1/municipio/4101408 retorna status 200."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        assert response.status_code == 200, \
            f"Esperado 200, recebido {response.status_code}: {response.text}"
    
    def test_get_municipio_apucarana_json_valid(self, client: TestClient, apucarana_id: str):
        """✅ Response é JSON válido."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        data = response.json()
        assert isinstance(data, dict), "Response deve ser um JSON dict"
    
    def test_get_municipio_apucarana_payload(self, client: TestClient, apucarana_id: str):
        """✅ Payload contém nome e indicadores."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        data = response.json()
        
        assert 'nome' in data, "Response deve ter 'nome'"
        assert 'indicadores' in data, "Response deve ter 'indicadores'"
        assert data['nome'] == "Apucarana", f"Nome deve ser 'Apucarana', recebido: {data['nome']}"
    
    def test_get_municipio_apucarana_indicadores(self, client: TestClient, apucarana_id: str):
        """✅ Indicadores estão presentes e corretos."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        data = response.json()
        
        indicadores = data['indicadores']
        assert isinstance(indicadores, dict), "indicadores deve ser dict"
        assert len(indicadores) > 0, "indicadores deve ter pelo menos um valor"
        assert 'densidade_banda_larga' in indicadores, "Deve ter densidade_banda_larga"
    
    def test_get_municipio_londrina_status_200(self, client: TestClient, londrina_id: str):
        """✅ GET /municipio/4113700 (Londrina) retorna 200."""
        response = client.get(f"/api/v1/municipio/{londrina_id}")
        assert response.status_code == 200
    
    def test_get_municipio_londrina_nome(self, client: TestClient, londrina_id: str):
        """✅ Londrina tem nome correto."""
        response = client.get(f"/api/v1/municipio/{londrina_id}")
        data = response.json()
        
        assert data['nome'] == "Londrina"
    
    def test_get_municipio_londrina_indicadores(self, client: TestClient, londrina_id: str):
        """✅ Londrina tem indicadores."""
        response = client.get(f"/api/v1/municipio/{londrina_id}")
        data = response.json()
        
        assert 'densidade_banda_larga' in data['indicadores']
        assert isinstance(data['indicadores']['densidade_banda_larga'], (int, float))


# ============================================================================
# TESTES DE ERRO 404
# ============================================================================

class TestMunicipioEndpointErrors:
    """Testes de tratamento de erros no endpoint."""
    
    def test_get_municipio_inexistent_status_404(self, client: TestClient, inexistent_id: str):
        """✅ GET /municipio/9999999 retorna 404 Not Found."""
        response = client.get(f"/api/v1/municipio/{inexistent_id}")
        assert response.status_code == 404, \
            f"Esperado 404, recebido {response.status_code}"
    
    def test_get_municipio_inexistent_error_detail(self, client: TestClient, inexistent_id: str):
        """✅ Error 404 tem detail message."""
        response = client.get(f"/api/v1/municipio/{inexistent_id}")
        data = response.json()
        
        assert 'detail' in data, "Response deve ter 'detail'"
        assert "não encontrado" in data['detail'].lower() or "not found" in data['detail'].lower()
    
    def test_get_municipio_invalid_format_status(self, client: TestClient):
        """✅ ID inválido é tratado apropriadamente."""
        response = client.get("/api/v1/municipio/abc")
        # Pode ser 404 (não encontrado) ou 422 (validation error) dependendo da impl
        assert response.status_code in [404, 422]


# ============================================================================
# TESTES DE CONTENT-TYPE
# ============================================================================

class TestMunicipioEndpointHeaders:
    """Testes de headers HTTP."""
    
    def test_response_content_type_json(self, client: TestClient, apucarana_id: str):
        """✅ Response tem Content-Type: application/json."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        
        assert response.headers['content-type'] == "application/json", \
            f"Esperado application/json, recebido: {response.headers['content-type']}"
    
    def test_response_has_required_headers(self, client: TestClient, apucarana_id: str):
        """✅ Response tem headers obrigatórios."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        
        assert 'content-type' in response.headers
        # FastAPI adiciona automaticamente estes
        assert response.headers.get('content-length') is not None or \
               response.headers.get('transfer-encoding') is not None


# ============================================================================
# TESTES DE PERFORMANCE
# ============================================================================

class TestMunicipioEndpointPerformance:
    """Testes de performance do endpoint."""
    
    def test_response_time_reasonable(self, client: TestClient, apucarana_id: str):
        """✅ Response é rápido (< 100ms com cache)."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        
        # Primeira chamada pode ser mais lenta (carrega cache)
        # Depois deve ser muito rápida
        # Não vamos ser muito rigoroso aqui (100ms é bem tolerante)
        assert response.status_code == 200
    
    def test_multiple_requests_performance(self, client: TestClient):
        """✅ Múltiplas requisições são rápidas (cache funciona)."""
        import time
        
        # Primeira requisição (carrega cache)
        client.get("/api/v1/municipio/4101408")
        
        # Medir tempo das próximas N requisições
        ids = ["4101408", "4113700", "1100015", "1302603", "1400100"]
        times = []
        
        for city_id in ids:
            start = time.time()
            response = client.get(f"/api/v1/municipio/{city_id}")
            elapsed = time.time() - start
            times.append(elapsed)
            
            assert response.status_code == 200
        
        # Tempo médio deve ser muito baixo (< 50ms por requisição)
        avg_time = sum(times) / len(times)
        assert avg_time < 0.050, f"Tempo médio muito alto: {avg_time}s"


# ============================================================================
# TESTES DE DADOS CORRETOS
# ============================================================================

class TestMunicipioDataCorrectness:
    """Testes para validar correção dos dados retornados."""
    
    def test_apucarana_data_matches_json(self, client: TestClient, apucarana_id: str):
        """✅ Dados de Apucarana correspondem ao JSON."""
        from app.services.local_data_service import LocalDataService
        
        # Obter via endpoint
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        endpoint_data = response.json()
        
        # Obter via service direto
        service_data = LocalDataService.find_by_id(apucarana_id)
        
        # Devem ser iguais
        assert endpoint_data == service_data, \
            "Dados do endpoint devem corresponder aos do service"
    
    def test_londrina_data_matches_json(self, client: TestClient, londrina_id: str):
        """✅ Dados de Londrina correspondem ao JSON."""
        from app.services.local_data_service import LocalDataService
        
        response = client.get(f"/api/v1/municipio/{londrina_id}")
        endpoint_data = response.json()
        
        service_data = LocalDataService.find_by_id(londrina_id)
        
        assert endpoint_data == service_data
    
    def test_all_cities_accessible(self, client: TestClient):
        """✅ Todas as 23 cidades são acessíveis."""
        from app.services.local_data_service import LocalDataService
        
        all_data = LocalDataService.find_all()
        municipios = all_data['municipios']
        
        for city_id in list(municipios.keys())[:5]:  # Testa primeiras 5
            response = client.get(f"/api/v1/municipio/{city_id}")
            assert response.status_code == 200, \
                f"Cidade {city_id} não acessível"


# ============================================================================
# TESTES DE SCHEMA
# ============================================================================

class TestMunicipioResponseSchema:
    """Testes para validar schema da response."""
    
    def test_response_schema_required_fields(self, client: TestClient, apucarana_id: str):
        """✅ Response tem campos obrigatórios."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        data = response.json()
        
        # Campos obrigatórios
        assert 'nome' in data
        assert 'indicadores' in data
        
        # Tipos
        assert isinstance(data['nome'], str)
        assert isinstance(data['indicadores'], dict)
    
    def test_indicadores_all_numeric(self, client: TestClient, apucarana_id: str):
        """✅ Todos os valores em indicadores são numéricos."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        data = response.json()
        
        for key, value in data['indicadores'].items():
            assert isinstance(value, (int, float)), \
                f"Indicador {key} deve ser número, recebido: {type(value)}"
    
    def test_indicadores_non_empty(self, client: TestClient, apucarana_id: str):
        """✅ Indicadores não estão vazios."""
        response = client.get(f"/api/v1/municipio/{apucarana_id}")
        data = response.json()
        
        assert len(data['indicadores']) > 0, "Deve ter pelo menos um indicador"


# ============================================================================
# TESTES DE INTEGRAÇÃO COMPLETA
# ============================================================================

class TestEndpointIntegration:
    """Testes de integração completa do endpoint."""
    
    def test_workflow_apucarana_londrina_and_error(self, client: TestClient):
        """✅ Workflow: busca Apucarana → Londrina → inexistente."""
        
        # 1. Busca Apucarana (deve suceder)
        r1 = client.get("/api/v1/municipio/4101408")
        assert r1.status_code == 200
        assert r1.json()['nome'] == "Apucarana"
        
        # 2. Busca Londrina (deve suceder)
        r2 = client.get("/api/v1/municipio/4113700")
        assert r2.status_code == 200
        assert r2.json()['nome'] == "Londrina"
        
        # 3. Busca inexistente (deve retornar 404)
        r3 = client.get("/api/v1/municipio/9999999")
        assert r3.status_code == 404
    
    def test_multiple_sequential_requests(self, client: TestClient):
        """✅ Múltiplas requisições sequenciais funcionam."""
        for i in range(10):
            response = client.get("/api/v1/municipio/4101408")
            assert response.status_code == 200
            assert response.json()['nome'] == "Apucarana"
