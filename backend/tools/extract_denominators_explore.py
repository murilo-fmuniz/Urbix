#!/usr/bin/env python3
"""
Extrai denominadores (Total Escolas, Hospitais, Pontos Iluminação, Serviços, Unidades Saúde)
a partir de MUNIC 2024 e CNES.
"""

import sys
from pathlib import Path
import pandas as pd
import sqlite3

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import ValorIndicador, Municipio


DENOMINADORES_MUNIC = {
    # Colunas que representam totais/quantidades no MUNIC
    # Consultar structure MUNIC 2024 para identificar exatos
    "Total Escolas (INEP)": None,  # Será identificado durante exploração
    "Total Pontos Iluminação (MUNIC)": None,
    "Total Serviços Ofertados (MUNIC)": None,
}

DENOMINADORES_CNES = {
    "Total Hospitais (CNES)": None,
    "Total Unidades Saúde (CNES)": None,
}


def identify_munic_columns():
    """Identifica colunas do MUNIC 2024 para os denominadores."""
    base_path = backend_dir / "data" / "planilhas" / "MUNIC_2024" / "Base_MUNIC_2024_20251107.xlsx"
    
    if not base_path.exists():
        print(f"ERRO: Arquivo MUNIC não encontrado em {base_path}")
        return {}
    
    # Lê apenas headers para análise
    try:
        df = pd.read_excel(base_path, sheet_name="Geral", header=0, nrows=0)
        print(f"Colunas disponíveis no MUNIC (Geral):")
        for i, col in enumerate(df.columns):
            print(f"  {i:3d}: {col}")
        
        df = pd.read_excel(base_path, sheet_name="Informática e comunicação", header=0, nrows=0)
        print(f"\nColunas disponíveis no MUNIC (Informática e comunicação):")
        for i, col in enumerate(df.columns):
            print(f"  {i:3d}: {col}")
            
    except Exception as e:
        print(f"Erro ao ler MUNIC: {e}")
    
    return {}


def identify_cnes_columns():
    """Identifica colunas do CNES para os denominadores."""
    cnes_dir = backend_dir / "data" / "planilhas" / "CNES"
    
    if not cnes_dir.exists():
        print(f"ERRO: Diretório CNES não encontrado em {cnes_dir}")
        return {}
    
    # Lista arquivos CNES disponíveis
    print(f"Arquivos CNES disponíveis:")
    for f in cnes_dir.glob("*"):
        if f.is_file():
            print(f"  {f.name}")


if __name__ == "__main__":
    print("=" * 80)
    print("EXPLORAÇÃO: Identificando colunas para denominadores")
    print("=" * 80)
    print()
    
    identify_munic_columns()
    print()
    identify_cnes_columns()
