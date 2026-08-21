import pandas as pd
import requests
import json
from pathlib import Path

def investigar_dados():
    print("="*60)
    print("🕵️‍♂️ INVESTIGANDO DADOS REAIS")
    print("="*60)

    # 1. Investigar a API do IBGE (Força de Trabalho)
    print("\n--- 1. API SIDRA (FORÇA DE TRABALHO) ---")
    url = "https://apisidra.ibge.gov.br/values/t/6580/p/2022/n6/all/v/1641?formato=json"
    try:
        res = requests.get(url, timeout=10).json()
        print("🔍 Colunas disponíveis:")
        print(json.dumps(res[0], indent=2, ensure_ascii=False))
        print("🔍 Exemplo da primeira linha real:")
        print(json.dumps(res[1], indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Erro na API: {e}")

    # 2. Investigar a Planilha MUNIC
    print("\n--- 2. PLANILHA MUNIC (HABITAÇÃO) ---")
    base_dir = Path(__file__).resolve().parent.parent
    munic_path = base_dir / "data" / "planilhas" / "MUNIC_2024" / "Base_MUNIC_2024_20251107.xlsx"
    
    if munic_path.exists():
        try:
            # Lê apenas a primeira linha (cabeçalho) para não pesar a memória
            df = pd.read_excel(munic_path, sheet_name="Habitacao", nrows=0)
            print("🔍 Colunas reais encontradas no Excel:")
            print(df.columns.tolist()[:15]) # Mostra as 15 primeiras
        except Exception as e:
            print(f"❌ Erro ao ler Excel: {e}")
    else:
        print(f"⚠️ Arquivo não encontrado: {munic_path}")

if __name__ == "__main__":
    investigar_dados()