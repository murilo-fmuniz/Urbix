import os
from pathlib import Path

def map_frontend():
    # Encontra a raiz do projeto de forma dinâmica
    script_path = Path(__file__).resolve()
    
    # Se estiver dentro da pasta 'scripts', sobe um nível. Se não, usa a pasta atual.
    if script_path.parent.name == "scripts":
        project_root = script_path.parent.parent
    else:
        project_root = script_path.parent
        
    frontend_dir = project_root / "frontend"
    output_file = project_root / "estrutura_frontend.md"
    
    if not frontend_dir.exists():
        print(f"❌ Pasta '{frontend_dir}' não encontrada!")
        return

    # Pastas que não precisamos mapear (lixo de compilação)
    ignore_dirs = {".git", "node_modules", "dist", ".vite", "build"}
    
    print(f"🔍 Mapeando estrutura da pasta: {frontend_dir}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# 🗺️ Estrutura de Arquivos do Frontend\n\n")
        f.write("```text\n")
        
        for root, dirs, files in os.walk(frontend_dir):
            # Filtra as pastas ignoradas
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            
            # Calcula o nível de indentação
            level = str(Path(root).relative_to(frontend_dir)).count(os.sep)
            if str(Path(root).relative_to(frontend_dir)) == '.':
                level = 0
            else:
                level += 1
                
            indent = "    " * level
            folder_name = os.path.basename(root) if root != str(frontend_dir) else "frontend"
            f.write(f"{indent}📂 {folder_name}/\n")
            
            subindent = "    " * (level + 1)
            for file in sorted(files):
                # Ignora arquivos de imagem/fonte para não poluir
                if not file.endswith(('.png', '.jpg', '.jpeg', '.svg', '.ico', '.woff', '.ttf')):
                    f.write(f"{subindent}📄 {file}\n")
        
        f.write("```\n")
        
    print(f"\n✅ Mapeamento concluído! Arquivo gerado com sucesso em: {output_file}")

if __name__ == "__main__":
    map_frontend()