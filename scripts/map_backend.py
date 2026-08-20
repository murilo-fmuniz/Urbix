import os
from pathlib import Path

def map_backend():
    # Encontra a raiz do projeto de forma dinâmica
    script_path = Path(__file__).resolve()
    
    # Se estiver dentro da pasta 'scripts', sobe um nível. Se não, usa a pasta atual.
    if script_path.parent.name == "scripts":
        project_root = script_path.parent.parent
    else:
        project_root = script_path.parent
        
    backend_dir = project_root / "backend"
    output_file = project_root / "estrutura_backend.md"
    
    if not backend_dir.exists():
        print(f"❌ Pasta '{backend_dir}' não encontrada!")
        return

    # Pastas e extensões que não precisamos mapear (ambiente virtual, cache do Python, SQLite)
    ignore_dirs = {".git", "venv", ".venv", "__pycache__", ".pytest_cache", "alembic"}
    ignore_exts = {".pyc", ".pyo", ".pyd", ".db", ".sqlite", ".db-shm", ".db-wal"}
    
    print(f"🔍 Mapeando estrutura da pasta: {backend_dir}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 🗺️ Estrutura de Arquivos do Backend\n\n")
        f.write("```text\n")
        
        for root, dirs, files in os.walk(backend_dir):
            # Filtra as pastas ignoradas
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Calcula o nível de indentação
            level = str(Path(root).relative_to(backend_dir)).count(os.sep)
            if str(Path(root).relative_to(backend_dir)) == '.':
                level = 0
            else:
                level += 1
                
            indent = "    " * level
            folder_name = os.path.basename(root) if root != str(backend_dir) else "backend"
            f.write(f"{indent}📂 {folder_name}/\n")
            
            subindent = "    " * (level + 1)
            for file in sorted(files):
                # Ignora arquivos de banco de dados e cache compilado
                if not any(file.endswith(ext) for ext in ignore_exts):
                    f.write(f"{subindent}📄 {file}\n")
        
        f.write("```\n")
        
    print(f"\n✅ Mapeamento concluído! Arquivo gerado com sucesso em: {output_file}")

if __name__ == "__main__":
    map_backend()