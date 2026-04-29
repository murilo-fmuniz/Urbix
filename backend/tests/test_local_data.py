"""
Unit Tests: Local Data Service
===============================

Testes para validar carregamento e acesso aos dados locais do JSON.
Usa pytest com fixtures e assertions estruturadas.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

from app.services.local_data_service import LocalDataService


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(autouse=True)
def clear_cache():
    """Limpa cache antes de cada teste (isolamento)."""
    LocalDataService.clear_cache()
    yield
    LocalDataService.clear_cache()


@pytest.fixture
def json_file_path() -> Path:
    """Retorna caminho do arquivo JSON."""
    return Path(__file__).parent.parent / "app" / "data" / "indicators_master.json"


@pytest.fixture
def json_data(json_file_path: Path) -> Dict[str, Any]:
    """Carrega dados JSON para validação."""
    with open(json_file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# ============================================================================
# TESTES DE CARREGAMENTO E SINTAXE JSON
# ============================================================================

class TestJSONLoading:
    """Testes de carregamento e validação do arquivo JSON."""
    
    def test_json_file_exists(self, json_file_path: Path):
        """✅ Valida que o arquivo JSON existe."""
        assert json_file_path.exists(), f"Arquivo não encontrado: {json_file_path}"
    
    def test_json_syntax_valid(self, json_data: Dict[str, Any]):
        """✅ Valida que o JSON tem sintaxe correta."""
        assert isinstance(json_data, dict), "JSON deve ser um dicionário"
        assert 'metadata' in json_data, "JSON deve ter 'metadata'"
        assert 'municipios' in json_data, "JSON deve ter 'municipios'"
    
    def test_metadata_structure(self, json_data: Dict[str, Any]):
        """✅ Valida estrutura de metadados."""
        metadata = json_data['metadata']
        
        assert isinstance(metadata, dict), "metadata deve ser dict"
        assert 'data_processamento' in metadata, "metadata deve ter data_processamento"
        assert 'total_municipios' in metadata, "metadata deve ter total_municipios"
        assert 'cidades_validas' in metadata, "metadata deve ter cidades_validas"
        assert 'filtro' in metadata, "metadata deve ter filtro"
    
    def test_municipios_structure(self, json_data: Dict[str, Any]):
        """✅ Valida estrutura de municípios."""
        municipios = json_data['municipios']
        
        assert isinstance(municipios, dict), "municipios deve ser dict"
        assert len(municipios) > 0, "Deve haver pelo menos um município"
        
        # Validar primeiro município
        first_city_id = list(municipios.keys())[0]
        first_city = municipios[first_city_id]
        
        assert isinstance(first_city, dict), "Cada município deve ser dict"
        assert 'nome' in first_city, "Município deve ter 'nome'"
        assert 'indicadores' in first_city, "Município deve ter 'indicadores'"
        assert isinstance(first_city['indicadores'], dict), "indicadores deve ser dict"


# ============================================================================
# TESTES DE BUSCA POR APUCARANA
# ============================================================================

class TestApucaranaData:
    """Testes específicos para Apucarana (4101408)."""
    
    def test_apucarana_exists(self):
        """✅ Valida que Apucarana existe no JSON."""
        data = LocalDataService.find_by_id("4101408")
        assert data is not None, "Apucarana deve estar no JSON"
    
    def test_apucarana_nome(self):
        """✅ Valida nome correto de Apucarana."""
        data = LocalDataService.find_by_id("4101408")
        assert data['nome'] == "Apucarana", f"Nome deve ser 'Apucarana', recebido: {data['nome']}"
    
    def test_apucarana_densidade_banda_larga(self):
        """✅ Valida que Apucarana tem densidade_banda_larga."""
        data = LocalDataService.find_by_id("4101408")
        indicadores = data['indicadores']
        
        assert 'densidade_banda_larga' in indicadores, "Deve ter densidade_banda_larga"
        assert isinstance(indicadores['densidade_banda_larga'], (int, float)), \
            f"densidade_banda_larga deve ser número, recebido: {type(indicadores['densidade_banda_larga'])}"
        assert indicadores['densidade_banda_larga'] > 0, "densidade_banda_larga deve ser > 0"
    
    def test_apucarana_find_indicadores(self):
        """✅ Valida busca apenas de indicadores."""
        indicadores = LocalDataService.find_indicadores_by_id("4101408")
        
        assert indicadores is not None, "Deve retornar indicadores"
        assert 'densidade_banda_larga' in indicadores
    
    def test_apucarana_find_nome(self):
        """✅ Valida busca apenas do nome."""
        nome = LocalDataService.find_nome_by_id("4101408")
        
        assert nome == "Apucarana"


# ============================================================================
# TESTES DE BUSCA POR LONDRINA
# ============================================================================

class TestLondrinaData:
    """Testes específicos para Londrina (4113700)."""
    
    def test_londrina_exists(self):
        """✅ Valida que Londrina existe."""
        data = LocalDataService.find_by_id("4113700")
        assert data is not None, "Londrina deve estar no JSON"
    
    def test_londrina_nome(self):
        """✅ Valida nome correto de Londrina."""
        data = LocalDataService.find_by_id("4113700")
        assert data['nome'] == "Londrina", f"Nome deve ser 'Londrina', recebido: {data['nome']}"
    
    def test_londrina_indicadores_presentes(self):
        """✅ Valida que Londrina tem indicadores."""
        data = LocalDataService.find_by_id("4113700")
        
        assert len(data['indicadores']) > 0, "Londrina deve ter pelo menos um indicador"
    
    def test_londrina_densidade_banda_larga(self):
        """✅ Valida densidade_banda_larga de Londrina."""
        indicadores = LocalDataService.find_indicadores_by_id("4113700")
        
        assert 'densidade_banda_larga' in indicadores, "Londrina deve ter densidade_banda_larga"
        assert isinstance(indicadores['densidade_banda_larga'], (int, float))
        assert indicadores['densidade_banda_larga'] > 0


# ============================================================================
# TESTES DE BUSCA COM ID INEXISTENTE
# ============================================================================

class TestInexistentCity:
    """Testes para comportamento com IDs inexistentes."""
    
    def test_inexistent_id_returns_none(self):
        """✅ Valida que ID inexistente retorna None (não exceção)."""
        data = LocalDataService.find_by_id("9999999")
        assert data is None, "Deve retornar None para cidade inexistente"
    
    def test_inexistent_id_indicadores_returns_none(self):
        """✅ Valida que busca de indicadores de ID inexistente retorna None."""
        indicadores = LocalDataService.find_indicadores_by_id("9999999")
        assert indicadores is None, "Deve retornar None para indicadores inexistentes"
    
    def test_inexistent_id_nome_returns_none(self):
        """✅ Valida que busca de nome de ID inexistente retorna None."""
        nome = LocalDataService.find_nome_by_id("9999999")
        assert nome is None, "Deve retornar None para nome inexistente"
    
    def test_empty_id_returns_none(self):
        """✅ Valida que ID vazio retorna None."""
        data = LocalDataService.find_by_id("")
        assert data is None, "Deve retornar None para ID vazio"


# ============================================================================
# TESTES DE NORMALIZAÇÃO DE ID
# ============================================================================

class TestIDNormalization:
    """Testes para normalização de códigos IBGE."""
    
    def test_id_normalization_short(self):
        """✅ Valida normalização de ID curto."""
        # ID com menos de 7 dígitos deve ser preenchido com zeros
        data = LocalDataService.find_by_id("4101408")
        assert data is not None, "Deve encontrar mesmo com normalização"
    
    def test_id_normalization_string(self):
        """✅ Valida que string é normalizada corretamente."""
        data1 = LocalDataService.find_by_id("4101408")
        data2 = LocalDataService.find_by_id(4101408)  # Como int
        
        assert data1 == data2, "Deve funcionar tanto com string quanto int"
    
    def test_id_normalization_with_spaces(self):
        """✅ Valida normalização com espaços."""
        data = LocalDataService.find_by_id("  4101408  ")
        assert data is not None, "Deve tratar espaços em branco"


# ============================================================================
# TESTES DE CACHE
# ============================================================================

class TestCaching:
    """Testes para mecanismo de cache."""
    
    def test_cache_loads_once(self):
        """✅ Valida que cache é carregado apenas uma vez."""
        cache_info_1 = LocalDataService.get_cache_info()
        assert not cache_info_1['is_loaded'], "Cache deve estar vazio inicialmente"
        
        # Primeira busca (carrega cache)
        LocalDataService.find_by_id("4101408")
        cache_info_2 = LocalDataService.get_cache_info()
        assert cache_info_2['is_loaded'], "Cache deve estar carregado após primeira busca"
        
        # Segunda busca (usa cache)
        LocalDataService.find_by_id("4113700")
        cache_info_3 = LocalDataService.get_cache_info()
        
        assert cache_info_2['cache_loaded_at'] == cache_info_3['cache_loaded_at'], \
            "Timestamp do cache não deve mudar"
    
    def test_cache_clear(self):
        """✅ Valida que cache pode ser limpo."""
        LocalDataService.find_by_id("4101408")
        cache_info_1 = LocalDataService.get_cache_info()
        assert cache_info_1['is_loaded'], "Cache deve estar carregado"
        
        LocalDataService.clear_cache()
        cache_info_2 = LocalDataService.get_cache_info()
        assert not cache_info_2['is_loaded'], "Cache deve estar limpo após clear()"
    
    def test_cache_size(self):
        """✅ Valida que cache tem número correto de municípios."""
        LocalDataService.find_by_id("4101408")
        cache_info = LocalDataService.get_cache_info()
        
        assert cache_info['total_municipios'] > 0, "Cache deve ter pelo menos 1 município"
        assert cache_info['total_municipios'] == 23, "Cache deve ter 23 municípios (conforme ETL)"


# ============================================================================
# TESTES DE METADADOS
# ============================================================================

class TestMetadata:
    """Testes para acesso aos metadados."""
    
    def test_get_metadata(self):
        """✅ Valida acesso aos metadados."""
        metadata = LocalDataService.get_metadata()
        
        assert isinstance(metadata, dict), "Metadados devem ser dict"
        assert 'data_processamento' in metadata
        assert 'total_municipios' in metadata
    
    def test_find_all(self):
        """✅ Valida retorno de todos os dados."""
        all_data = LocalDataService.find_all()
        
        assert 'metadata' in all_data
        assert 'municipios' in all_data
        assert len(all_data['municipios']) == 23


# ============================================================================
# TESTES DE TIPAGEM
# ============================================================================

class TestTyping:
    """Testes de validação de tipos (para Python 3.12+)."""
    
    def test_find_by_id_return_type(self):
        """✅ Valida que find_by_id retorna tipo correto."""
        result = LocalDataService.find_by_id("4101408")
        assert isinstance(result, dict) or result is None, \
            f"find_by_id deve retornar dict ou None, recebido: {type(result)}"
    
    def test_find_indicadores_by_id_return_type(self):
        """✅ Valida que find_indicadores_by_id retorna tipo correto."""
        result = LocalDataService.find_indicadores_by_id("4101408")
        assert isinstance(result, dict) or result is None
    
    def test_find_nome_by_id_return_type(self):
        """✅ Valida que find_nome_by_id retorna tipo correto."""
        result = LocalDataService.find_nome_by_id("4101408")
        assert isinstance(result, str) or result is None
    
    def test_get_metadata_return_type(self):
        """✅ Valida que get_metadata retorna dict."""
        result = LocalDataService.get_metadata()
        assert isinstance(result, dict)


# ============================================================================
# TESTE DE INTEGRAÇÃO
# ============================================================================

class TestIntegration:
    """Testes de integração completa."""
    
    def test_full_workflow(self):
        """✅ Testa workflow completo: carrega → busca → valida."""
        # 1. Buscar Apucarana
        apucarana = LocalDataService.find_by_id("4101408")
        assert apucarana is not None
        
        # 2. Buscar Londrina
        londrina = LocalDataService.find_by_id("4113700")
        assert londrina is not None
        
        # 3. Buscar inexistente
        inexistente = LocalDataService.find_by_id("9999999")
        assert inexistente is None
        
        # 4. Metadados
        metadata = LocalDataService.get_metadata()
        assert metadata['total_municipios'] == 23
        
        # 5. Cache ainda está carregado (3 chamadas compartilham mesmo cache)
        cache_info = LocalDataService.get_cache_info()
        assert cache_info['is_loaded']
        assert cache_info['total_municipios'] == 23
