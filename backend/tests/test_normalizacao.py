"""
Testes para validar a normalização de entrada (cidade, código indicador, estado).
"""

import pytest
from app.utils import (
    normalize_indicator_code,
    normalize_city_name,
    normalize_state,
    normalize_comparison_value
)


class TestIndicatorCodeNormalization:
    """Testes para normalização de código de indicador"""
    
    def test_uppercase_with_dot(self):
        """Deve manter maiúsculas com ponto"""
        assert normalize_indicator_code("ECO.1") == "ECO.1"
    
    def test_lowercase_with_dot(self):
        """Deve converter minúsculas para maiúsculas"""
        assert normalize_indicator_code("eco.1") == "ECO.1"
    
    def test_without_dot(self):
        """Deve adicionar ponto entre letra e número"""
        assert normalize_indicator_code("ECO1") == "ECO.1"
        assert normalize_indicator_code("eco1") == "ECO.1"
    
    def test_mixed_case(self):
        """Deve normalizar caso misto"""
        assert normalize_indicator_code("EcO.1") == "ECO.1"
        assert normalize_indicator_code("eCo1") == "ECO.1"
    
    def test_with_accents(self):
        """Deve remover acentos e converter para maiúscula"""
        assert normalize_indicator_code("eço.1") == "ECO.1"
        assert normalize_indicator_code("são.1") == "SAO.1"
    
    def test_with_spaces(self):
        """Deve remover espaços extras"""
        assert normalize_indicator_code("  ECO.1  ") == "ECO.1"
        assert normalize_indicator_code("  eco1  ") == "ECO.1"


class TestCityNameNormalization:
    """Testes para normalização de nome de cidade"""
    
    def test_lowercase(self):
        """Deve converter para Title Case"""
        assert normalize_city_name("apucarana") == "Apucarana"
    
    def test_uppercase(self):
        """Deve converter para Title Case"""
        assert normalize_city_name("APUCARANA") == "Apucarana"
    
    def test_mixed_case(self):
        """Deve normalizar para Title Case"""
        assert normalize_city_name("ApucaranA") == "Apucarana"
    
    def test_compound_name_lowercase(self):
        """Deve manter entre palavras Title Case"""
        assert normalize_city_name("são paulo") == "São Paulo"
    
    def test_compound_name_uppercase(self):
        """Deve manter entre palavras Title Case"""
        assert normalize_city_name("SÃO PAULO") == "São Paulo"
    
    def test_with_accents(self):
        """Deve manter acentos"""
        assert normalize_city_name("maringá") == "Maringá"
        assert normalize_city_name("LONDRINA") == "Londrina"
    
    def test_with_spaces(self):
        """Deve remover espaços extras"""
        assert normalize_city_name("  apucarana  ") == "Apucarana"


class TestStateNormalization:
    """Testes para normalização de sigla de estado"""
    
    def test_lowercase_sigla(self):
        """Deve converter sigla para maiúscula"""
        assert normalize_state("pr") == "PR"
    
    def test_uppercase_sigla(self):
        """Deve manter sigla maiúscula"""
        assert normalize_state("PR") == "PR"
    
    def test_state_name_paraná(self):
        """Deve converter nome de estado para sigla"""
        assert normalize_state("paraná") == "PR"
    
    def test_state_name_sãopaulo(self):
        """Deve converter nome de estado para sigla"""
        assert normalize_state("são paulo") == "SP"
    
    def test_with_spaces(self):
        """Deve remover espaços extras"""
        assert normalize_state("  PR  ") == "PR"


class TestComparisonValueNormalization:
    """Testes para normalização de valores para comparação"""
    
    def test_uppercase(self):
        """Deve converter para minúsculas"""
        assert normalize_comparison_value("ISO 37122") == "iso 37122"
    
    def test_mixed_case(self):
        """Deve converter para minúsculas"""
        assert normalize_comparison_value("ISO37122") == "iso37122"
    
    def test_with_accents(self):
        """Deve manter acentos em minúsculas"""
        assert normalize_comparison_value("SAÚDE") == "saúde"
    
    def test_with_spaces(self):
        """Deve remover espaços extras"""
        assert normalize_comparison_value("  SAÚDE  ") == "saúde"


class TestIntegration:
    """Testes de integração - fluxos combinados"""
    
    def test_create_indicator_various_formats(self):
        """Múltiplos formatos de código devem resultar no mesmo código normalizado"""
        formats = ["ECO.1", "eco.1", "eco1", "ECO1", "eço.1"]
        normalized = [normalize_indicator_code(fmt) for fmt in formats]
        assert all(code == "ECO.1" for code in normalized)
    
    def test_filter_city_various_formats(self):
        """Múltiplos formatos de cidade devem resultar no mesmo valor normalizado"""
        cities = ["apucarana", "APUCARANA", "Apucarana", "ApucaranA"]
        normalized = [normalize_city_name(city) for city in cities]
        assert all(city == "Apucarana" for city in normalized)
