#!/usr/bin/env python
"""Testa a listagem de cidades do TOPSIS com capitais do Brasil e UTFPRCity."""

import unittest
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

EXPECTED_CODES = {
    "1100205",  # Porto Velho
    "1200401",  # Rio Branco
    "1302603",  # Manaus
    "1400100",  # Boa Vista
    "1501402",  # Belém
    "1600303",  # Macapá
    "1721000",  # Palmas
    "2105302",  # São Luís
    "2207702",  # Teresina
    "2304400",  # Fortaleza
    "2408102",  # Natal
    "2507507",  # João Pessoa
    "2607901",  # Recife
    "2704302",  # Maceió
    "2800308",  # Aracaju
    "2905701",  # Salvador
    "3106200",  # Belo Horizonte
    "3205309",  # Vitória
    "3304557",  # Rio de Janeiro
    "3550308",  # São Paulo
    "4106902",  # Curitiba
    "4205407",  # Florianópolis
    "4305108",  # Porto Alegre
    "5002704",  # Campo Grande
    "5103403",  # Cuiabá
    "5208707",  # Goiânia
    "5300108",  # Brasília
    "9999999",  # UTFPRCity
}

class TestTopsisCitiesList(unittest.TestCase):
    def test_topsis_cities_contains_capitals_and_utfprcity(self):
        response = client.get("/api/v1/topsis/cities")
        self.assertEqual(response.status_code, 200)

        cities = response.json()
        codes = {city["codigo_ibge"] for city in cities}

        missing = EXPECTED_CODES - codes
        self.assertFalse(missing, f"Cidades ausentes na lista TOPSIS: {sorted(missing)}")

        # A lista deve ter pelo menos as capitais + UTFPRCity
        self.assertGreaterEqual(len(cities), len(EXPECTED_CODES))


if __name__ == "__main__":
    unittest.main()
