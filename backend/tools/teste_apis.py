import requests
import json
import os
from pathlib import Path

# Garante que os arquivos serão salvos na pasta atual do script
BASE_DIR = Path(__file__).parent

CIDADES_TESTE = {
    "4208302": "Itapema/SC",
    "4101408": "Apucarana/PR"
}

def explorar_siconfi(ibge, nome):
    print(f"\n🌐 Explorando SICONFI para {nome} ({ibge})...")
    
    # 1. RREO - Anexo 01 (Busca por Receitas Próprias/Impostos e Despesas de Capital)
    url_rreo = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    params_rreo = {
        "an_exercicio": 2023,
        "nr_periodo": 6, # Último bimestre (acumulado do ano)
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 01",
        "id_ente": ibge
    }
    
    # 2. RGF - Anexo 02 (Busca por Dívida Consolidada)
    url_rgf = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rgf"
    params_rgf = {
        "an_exercicio": 2023,
        "in_periodicidade": "S", # Semestral
        "nr_periodo": 2,         # Último semestre
        "co_tipo_demonstrativo": "RGF",
        "no_anexo": "RGF-Anexo 02",
        "id_ente": ibge
    }

    try:
        print("  -> Baixando Balanço Orçamentário (RREO Anexo 01)...")
        res_rreo = requests.get(url_rreo, params=params_rreo, timeout=15)
        rreo_data = res_rreo.json()
        
        caminho_rreo = BASE_DIR / f"teste_siconfi_rreo_{ibge}.json"
        with open(caminho_rreo, "w", encoding="utf-8") as f:
            json.dump(rreo_data, f, indent=2, ensure_ascii=False)
        
        print("  -> Baixando Gestão Fiscal / Dívida (RGF Anexo 02)...")
        res_rgf = requests.get(url_rgf, params=params_rgf, timeout=15)
        rgf_data = res_rgf.json()
        
        caminho_rgf = BASE_DIR / f"teste_siconfi_rgf_{ibge}.json"
        with open(caminho_rgf, "w", encoding="utf-8") as f:
            json.dump(rgf_data, f, indent=2, ensure_ascii=False)

        # Analisando as contas devolvidas no RREO para ajudar a achar os códigos
        contas_rreo = [item.get("conta") for item in rreo_data.get("items", [])[:15]]
        print(f"  ✅ Concluído! Primeiras 15 contas achadas no RREO:")
        for c in contas_rreo:
            print(f"     - {c}")
            
        print(f"  📁 Arquivos JSON salvos em {BASE_DIR} para inspeção!")

    except Exception as e:
        print(f"  ❌ Falha na comunicação com a API: {e}")

def run():
    print("="*60)
    print("🚀 SONDAGEM DE APIS GOVERNAMENTAIS (TESTE DE INTEGRAÇÃO)")
    print("="*60)
    
    for ibge, nome in CIDADES_TESTE.items():
        explorar_siconfi(ibge, nome)

if __name__ == "__main__":
    run()