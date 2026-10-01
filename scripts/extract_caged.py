import os
import py7zr
from pathlib import Path

# Resolve os caminhos dinamicamente a partir da pasta scripts/
SCRIPTS_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPTS_DIR.parent
RAW_DATA_DIR = BASE_DIR / "backend" / "data" / "planilhas"
STAGE_DIR = BASE_DIR / "backend" / "data" / "stage" / "caged"

def extract_7z_files():
    print("================================================================================")
    print("📦 INICIANDO EXTRAÇÃO DOS DADOS DO CAGED (.7z)")
    print("================================================================================")
    
    # Cria o diretório de stage se ele não existir
    STAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"Buscando em: {RAW_DATA_DIR}")
    
    # Busca recursiva por arquivos .7z na pasta de planilhas
    arquivos_7z = list(RAW_DATA_DIR.rglob("*.7z"))
    
    if not arquivos_7z:
        print("Nenhum arquivo .7z encontrado no diretório.")
        return

    print(f"Encontrados {len(arquivos_7z)} arquivos compactados. Iniciando extração...\n")

    for arquivo in arquivos_7z:
        pasta_destino = STAGE_DIR / arquivo.stem
        
        # Pula a extração se a pasta de destino já existir e não estiver vazia
        if pasta_destino.exists() and any(pasta_destino.iterdir()):
            print(f"⏭️  Ignorando: {arquivo.name} (Já extraído em stage/caged/{arquivo.stem})")
            continue
            
        pasta_destino.mkdir(exist_ok=True)
        print(f"Extraindo: {arquivo.name}... ", end="", flush=True)
        
        try:
            with py7zr.SevenZipFile(arquivo, mode='r') as z:
                z.extractall(path=pasta_destino)
            print("✅ OK")
        except py7zr.exceptions.BadArchiveError:
            print("❌ ERRO (Arquivo corrompido ou formato inválido)")
        except Exception as e:
            print(f"❌ ERRO Inesperado: {e}")

    print("\n🎉 Extração finalizada! Os dados do CAGED estão no stage prontos para ingestão.")

if __name__ == "__main__":
    extract_7z_files()