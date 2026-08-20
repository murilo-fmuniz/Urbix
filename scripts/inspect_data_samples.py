import pandas as pd
from pathlib import Path
import warnings

# Ignorar warnings de estilos do Excel
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def inspect_tables():
    # Caminho do seu data lake
    base_dir = Path("backend/data/planilhas")
    output_file = Path("amostra_tabelas_etl.md")
    
    print(f"🔍 Iniciando varredura profunda em: {base_dir}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 📊 Amostra de Dados do Data Lake\n\n")
        f.write("Este relatório contém os cabeçalhos e as 3 primeiras linhas reais de cada tabela.\n\n")
        
        # Coletar CSVs, XLSXs e ODSs
        arquivos = list(base_dir.rglob("*.csv")) + list(base_dir.rglob("*.xlsx")) + list(base_dir.rglob("*.ods"))
        
        for file_path in sorted(arquivos):
            relative_path = file_path.relative_to(base_dir)
            print(f"Lendo: {relative_path}")
            
            f.write(f"## 📁 `{relative_path}`\n")
            
            try:
                # Lógica de leitura baseada na extensão
                if file_path.suffix.lower() == ".csv":
                    df = pd.read_csv(file_path, sep=";", nrows=15, engine="python", on_bad_lines="skip")
                    if len(df.columns) < 2:
                        df = pd.read_csv(file_path, sep=",", nrows=15, engine="python", on_bad_lines="skip")
                elif file_path.suffix.lower() == ".xlsx":
                    df = pd.read_excel(file_path, nrows=15, engine="openpyxl")
                elif file_path.suffix.lower() == ".ods":
                    df = pd.read_excel(file_path, nrows=15, engine="odf")
                else:
                    continue

                # Fallback inteligente: se a tabela for do governo e tiver logomarca/cabeçalho sujo (muitas colunas "Unnamed")
                unnamed_cols = sum("Unnamed" in str(c) for c in df.columns)
                if unnamed_cols > len(df.columns) / 2 and file_path.suffix.lower() in [".xlsx", ".ods"]:
                    engine_type = "openpyxl" if file_path.suffix.lower() == ".xlsx" else "odf"
                    
                    # Tenta pular 5 linhas
                    df = pd.read_excel(file_path, skiprows=5, nrows=10, engine=engine_type)
                    unnamed_cols = sum("Unnamed" in str(c) for c in df.columns)
                    
                    # Se ainda estiver sujo, tenta pular 10 linhas (Padrão SINISA)
                    if unnamed_cols > len(df.columns) / 2:
                        df = pd.read_excel(file_path, skiprows=10, nrows=10, engine=engine_type)

                # Remove colunas 100% vazias para limpar a visualização
                df.dropna(how='all', axis=1, inplace=True)
                
                # Salva no Markdown em formato de bloco de texto para não quebrar a formatação
                f.write("```text\n")
                f.write(df.head(3).to_string(index=False))
                f.write("\n```\n\n")
                
            except Exception as e:
                f.write(f"> ⚠️ **Erro ao ler arquivo:** `{str(e)}`\n\n")
                
    print(f"\n✅ Varredura concluída! Relatório gerado com sucesso em: {output_file}")

if __name__ == "__main__":
    inspect_tables()