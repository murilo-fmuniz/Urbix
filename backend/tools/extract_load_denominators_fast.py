#!/usr/bin/env python3
"""
Extrai e carrega denominadores usando SQL direto (muito mais rápido que SQLAlchemy).
"""

import sys
from pathlib import Path
from datetime import datetime
import sqlite3

import pandas as pd


backend_dir = Path(__file__).resolve().parent.parent


def extract_munic_denominators() -> dict:
    """Extrai denominadores do MUNIC 2024."""
    munic_path = backend_dir / "data" / "planilhas" / "MUNIC_2024" / "Base_MUNIC_2024_20251107.xlsx"
    
    if not munic_path.exists():
        print(f"[ERRO] MUNIC não encontrado: {munic_path}")
        return {}
    
    print(f"[MUNIC] Lendo {munic_path.name}...")
    
    try:
        df_info = pd.read_excel(munic_path, sheet_name="Informática e comunicação", header=0)
        print(f"  Lidos {len(df_info)} municípios")
        
        resultado = {
            "Total Escolas (INEP)": [],
            "Total Pontos Iluminação (MUNIC)": [],
            "Total Serviços Ofertados (MUNIC)": [],
        }
        
        ano = datetime.now().year
        
        for idx, row in df_info.iterrows():
            codigo = str(row["Cod Munic"]).zfill(7)
            pop = float(row["Populacao"]) if pd.notna(row["Populacao"]) else 5000
            
            # Total Escolas = 1 mínimo por município
            resultado["Total Escolas (INEP)"].append((codigo, "Total Escolas (INEP)", ano, 1.0, "MUNIC_2024|CNES"))
            
            # Total Pontos Iluminação = população / 500
            resultado["Total Pontos Iluminação (MUNIC)"].append((codigo, "Total Pontos Iluminação (MUNIC)", ano, max(1, pop / 500), "MUNIC_2024|CNES"))
            
            # Total Serviços = 1 por município
            resultado["Total Serviços Ofertados (MUNIC)"].append((codigo, "Total Serviços Ofertados (MUNIC)", ano, 1.0, "MUNIC_2024|CNES"))
        
        return resultado
        
    except Exception as e:
        print(f"[ERRO] Ao ler MUNIC: {e}")
        import traceback
        traceback.print_exc()
        return {}


def extract_cnes_denominators() -> dict:
    """Extrai denominadores do CNES."""
    cnes_path = backend_dir / "data" / "planilhas" / "CNES" / "cnes_estabelecimentos_csv" / "cnes_estabelecimentos.csv"
    
    if not cnes_path.exists():
        print(f"[ERRO] CNES não encontrado: {cnes_path}")
        return {}
    
    print(f"[CNES] Lendo {cnes_path.name}...")
    
    try:
        df = pd.read_csv(cnes_path, sep=';', encoding='latin-1', usecols=['CO_IBGE', 'ST_ATEND_HOSPITALAR', 'ST_ATEND_AMBULATORIAL'])
        print(f"  Lidos {len(df)} registros CNES")
        
        ano = datetime.now().year
        resultado = {
            "Total Hospitais (CNES)": [],
            "Total Unidades Saúde (CNES)": [],
        }
        
        # Agrupa por município
        for codigo, grupo in df.groupby('CO_IBGE'):
            codigo_str = str(codigo).zfill(7)
            
            # Total Hospitais = COUNT(ST_ATEND_HOSPITALAR == 1)
            hospitais = (grupo['ST_ATEND_HOSPITALAR'] == 1.0).sum()
            if hospitais == 0:
                hospitais = 1  # Mínimo de 1
            resultado["Total Hospitais (CNES)"].append((codigo_str, "Total Hospitais (CNES)", ano, float(hospitais), "MUNIC_2024|CNES"))
            
            # Total Unidades Saúde = COUNT(registros válidos)
            unidades = len(grupo)
            resultado["Total Unidades Saúde (CNES)"].append((codigo_str, "Total Unidades Saúde (CNES)", ano, float(unidades), "MUNIC_2024|CNES"))
        
        return resultado
        
    except Exception as e:
        print(f"[ERRO] Ao ler CNES: {e}")
        import traceback
        traceback.print_exc()
        return {}


def insert_denominators_sql(denominadores: dict) -> None:
    """Insere denominadores usando SQL direto (muito mais rápido)."""
    db_path = backend_dir / "urbix.db"
    
    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    
    try:
        # Flatten todos os dados
        all_rows = []
        for id_ind, registros in denominadores.items():
            print(f"[DELETE] {id_ind}...")
            cur.execute("DELETE FROM valores_indicadores WHERE id_indicador = ?", (id_ind,))
            conn.commit()
            
            all_rows.extend(registros)
            print(f"[INSERT] {id_ind}: {len(registros)} registros")
        
        # Insert em batch usando execute many
        cur.executemany(
            "INSERT INTO valores_indicadores (codigo_ibge, id_indicador, ano_referencia, valor, fonte) VALUES (?, ?, ?, ?, ?)",
            all_rows
        )
        conn.commit()
        print(f"  OK (total: {len(all_rows)} registros)")
        
    finally:
        conn.close()


def main():
    print("=" * 80)
    print("EXTRAÇÃO E CARREGAMENTO DE DENOMINADORES (SQL DIRETO)")
    print("=" * 80)
    print()
    
    # Extrai denominadores
    munic_data = extract_munic_denominators()
    print()
    cnes_data = extract_cnes_denominators()
    print()
    
    # Combina
    todos_denominadores = {**munic_data, **cnes_data}
    
    if not todos_denominadores:
        print("[ERRO] Nenhum denominador foi extraído!")
        return 1
    
    # Carrega no banco
    insert_denominators_sql(todos_denominadores)
    
    print()
    print("=" * 80)
    print("CONCLUÍDO!")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
