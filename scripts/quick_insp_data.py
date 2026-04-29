#!/usr/bin/env python3
"""Quick inspection of data files to understand structure"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "backend" / "data" / "planilhas"

print("=" * 80)
print("INSPECTING DATA FILES STRUCTURE")
print("=" * 80)

# ATU
print("\n1. ATU_MUNICIPIOS_2025.xlsx:")
try:
    df_atu = pd.read_excel(
        DATA_DIR / "ATU_2025_MUNICIPIOS" / "ATU_MUNICIPIOS_2025.xlsx",
        sheet_name=0,
        nrows=5
    )
    print(f"   Colunas: {list(df_atu.columns)[:5]}...")
    print(f"   Shape: {df_atu.shape}")
    print(f"   ⚠️ Nenhuma coluna óbvia encontrada")
except Exception as e:
    print(f"   ❌ Erro: {type(e).__name__}")

# Try with skip
print("\n   Tentando com skiprows=5:")
try:
    df_atu = pd.read_excel(
        DATA_DIR / "ATU_2025_MUNICIPIOS" / "ATU_MUNICIPIOS_2025.xlsx",
        sheet_name=0,
        skiprows=5,
        nrows=5
    )
    print(f"   Colunas: {list(df_atu.columns)[:5]}...")
    print(f"   Shape: {df_atu.shape}")
    if any("código" in str(c).lower() for c in df_atu.columns):
        print(f"   ✓ Coluna de código encontrada!")
        print(f"   Primeiras linhas: {df_atu.iloc[0].to_dict()}")
except Exception as e:
    print(f"   ❌ Erro: {type(e).__name__}")

# IDEB
print("\n2. divulgacao_anos_iniciais_municipios_2023.xlsx:")
try:
    df_ideb = pd.read_excel(
        DATA_DIR / "divulgacao_anos_iniciais_municipios_2023" / "divulgacao_anos_iniciais_municipios_2023.xlsx",
        sheet_name=0,
        nrows=5
    )
    print(f"   Colunas: {list(df_ideb.columns)[:8]}...")
    if any("código" in str(c).lower() for c in df_ideb.columns):
        print(f"   ✓ Coluna de código encontrada")
except Exception as e:
    print(f"   ❌ Erro: {type(e).__name__}")

print("\n" + "=" * 80)
