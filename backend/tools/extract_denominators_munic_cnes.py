#!/usr/bin/env python3
"""
Extrai denominadores faltantes de MUNIC 2024 e CNES:
- Total Escolas (INEP)
- Total Hospitais (CNES)
- Total Pontos Iluminação (MUNIC)
- Total Serviços Ofertados (MUNIC)
- Total Unidades Saúde (CNES)
"""

import sys
from pathlib import Path
from datetime import datetime

import pandas as pd

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.database import SessionLocal
from app.models import ValorIndicador


DENOMINATORS_CONFIG = {
    # Denominadores de MUNIC - usaremos contagem de valores válidos como proxy
    "Total Escolas (INEP)": {
        "source": "MUNIC",
        "sheet": "Recursos humanos",  
        "description": "Será estimado via dados de educação MUNIC + INEP",
    },
    "Total Pontos Iluminação (MUNIC)": {
        "source": "MUNIC",
        "sheet": "Informática e comunicação",
        "description": "Total de pontos de iluminação com potencial de telegestão",
    },
    "Total Serviços Ofertados (MUNIC)": {
        "source": "MUNIC",
        "sheet": "Informática e comunicação",
        "description": "Total de serviços municipais ofertados online",
    },
    "Total Hospitais (CNES)": {
        "source": "CNES",
        "description": "Contagem de estabelecimentos hospitalares por município",
    },
    "Total Unidades Saúde (CNES)": {
        "source": "CNES",
        "description": "Contagem total de unidades de saúde por município",
    },
}


def get_munic_denominators():
    """Extrai denominadores do MUNIC 2024."""
    munic_path = backend_dir / "data" / "planilhas" / "MUNIC_2024" / "Base_MUNIC_2024_20251107.xlsx"
    
    if not munic_path.exists():
        print(f"[ERRO] MUNIC 2024 não encontrado: {munic_path}")
        return {}
    
    print(f"[MUNIC] Lendo {munic_path.name}...")
    
    try:
        # Lê sheet de Recursos humanos para educação/escolas
        df_rh = pd.read_excel(munic_path, sheet_name="Recursos humanos", header=0)
        print(f"  Recursos humanos: {len(df_rh)} linhas")
        
        # Lê sheet de Informática para pontos iluminação e serviços
        df_info = pd.read_excel(munic_path, sheet_name="Informática e comunicação", header=0)
        print(f"  Informática: {len(df_info)} linhas")
        
        # Tenta identificar colunas relevantes
        print(f"  Colunas Recursos humanos: {list(df_rh.columns)[:10]}")
        print(f"  Colunas Informática: {list(df_info.columns)[:10]}")
        
    except Exception as e:
        print(f"[ERRO] Ao ler MUNIC: {e}")
        return {}
    
    return {}


def get_cnes_denominators():
    """Extrai denominadores do CNES."""
    cnes_dir = backend_dir / "data" / "planilhas" / "CNES"
    
    if not cnes_dir.exists():
        print(f"[ERRO] CNES não encontrado: {cnes_dir}")
        return {}
    
    print(f"[CNES] Procurando arquivos em {cnes_dir.name}...")
    
    csv_files = list(cnes_dir.glob("*.csv"))
    csv_gz_files = list(cnes_dir.glob("*.csv.gz"))
    
    print(f"  Encontrados {len(csv_files)} CSVs e {len(csv_gz_files)} CSV.GZs")
    
    if csv_files:
        for f in csv_files[:3]:
            print(f"    - {f.name}")
    if csv_gz_files:
        for f in csv_gz_files[:3]:
            print(f"    - {f.name}")
    
    return {}


def insert_denominators(db: SessionLocal, dados: dict):
    """Insere denominadores no banco."""
    for id_indicador, valores_por_municipio in dados.items():
        print(f"[INSERT] {id_indicador}...")
        for codigo_ibge, valor in valores_por_municipio.items():
            existing = (
                db.query(ValorIndicador)
                .filter_by(
                    codigo_ibge=codigo_ibge,
                    id_indicador=id_indicador,
                    ano_referencia=datetime.now().year,
                )
                .first()
            )
            if existing:
                continue
            
            registro = ValorIndicador(
                codigo_ibge=codigo_ibge,
                id_indicador=id_indicador,
                ano_referencia=datetime.now().year,
                valor=float(valor),
                fonte="MUNIC_2024|CNES",
            )
            db.add(registro)
        
        db.commit()
        print(f"  {id_indicador}: {len(valores_por_municipio)} registros")


def main():
    print("=" * 80)
    print("EXTRAÇÃO DE DENOMINADORES: MUNIC 2024 + CNES")
    print("=" * 80)
    print()
    
    # Exploração de estrutura
    munic_data = get_munic_denominators()
    print()
    cnes_data = get_cnes_denominators()
    print()
    
    print("=" * 80)
    print("RESUMO DA EXPLORAÇÃO")
    print("=" * 80)
    print()
    
    for denom_id, config in DENOMINATORS_CONFIG.items():
        source = config["source"]
        desc = config["description"]
        print(f"[{source:5s}] {denom_id}")
        print(f"         {desc}")
        print()


if __name__ == "__main__":
    main()
