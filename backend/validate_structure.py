#!/usr/bin/env python
"""
Script de validação da nova estrutura do backend
Verifica se todos os módulos foram criados corretamente e podem ser importados
"""
import sys
from pathlib import Path

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def check_directory_structure():
    """Verifica se todos os diretórios foram criados"""
    print("\n" + "="*70)
    print("VERIFICANDO ESTRUTURA DE DIRETÓRIOS")
    print("="*70)
    
    required_dirs = [
        'config',
        'models',
        'database',
        'api',
        'etl',
        'scripts',
        'data'
    ]
    
    all_ok = True
    for dir_name in required_dirs:
        path = Path(dir_name)
        if path.exists() and path.is_dir():
            print_success(f"Diretório '{dir_name}/' existe")
        else:
            print_error(f"Diretório '{dir_name}/' NÃO encontrado")
            all_ok = False
    
    return all_ok

def check_init_files():
    """Verifica se todos os __init__.py foram criados"""
    print("\n" + "="*70)
    print("VERIFICANDO ARQUIVOS __init__.py")
    print("="*70)
    
    required_inits = [
        'config/__init__.py',
        'models/__init__.py',
        'database/__init__.py',
        'api/__init__.py',
        'etl/__init__.py',
        'scripts/__init__.py'
    ]
    
    all_ok = True
    for init_file in required_inits:
        path = Path(init_file)
        if path.exists() and path.is_file():
            print_success(f"'{init_file}' existe")
        else:
            print_error(f"'{init_file}' NÃO encontrado")
            all_ok = False
    
    return all_ok

def check_module_files():
    """Verifica se os arquivos dos módulos foram criados"""
    print("\n" + "="*70)
    print("VERIFICANDO ARQUIVOS DOS MÓDULOS")
    print("="*70)
    
    required_files = {
        'config': ['database.py'],
        'models': ['base.py', 'city.py', 'state.py', 'indicator.py', 'sync_log.py'],
        'database': ['operations.py', 'legacy.py'],
        'etl': ['ibge_etl.py'],
        'scripts': ['init_database.py', 'migrate_data.py']
    }
    
    all_ok = True
    for module, files in required_files.items():
        print(f"\n{BLUE}Módulo: {module}/{RESET}")
        for file in files:
            path = Path(module) / file
            if path.exists() and path.is_file():
                print_success(f"  {file}")
            else:
                print_error(f"  {file} NÃO encontrado")
                all_ok = False
    
    return all_ok

def check_imports():
    """Testa se os imports funcionam"""
    print("\n" + "="*70)
    print("TESTANDO IMPORTS")
    print("="*70)
    
    imports_to_test = [
        ("config", ["init_db", "get_db", "SessionLocal"]),
        ("models", ["Base", "City", "State", "Indicator"]),
        ("database", ["get_all_cities", "db"]),
        ("etl", ["run_full_etl"]),
        ("scripts", ["init_database", "run_migration"])
    ]
    
    all_ok = True
    for module_name, items in imports_to_test:
        try:
            module = __import__(module_name)
            print(f"\n{BLUE}Módulo: {module_name}{RESET}")
            
            for item in items:
                if hasattr(module, item):
                    print_success(f"  {item} importado")
                else:
                    print_error(f"  {item} NÃO encontrado no módulo")
                    all_ok = False
        except ImportError as e:
            print_error(f"Erro ao importar '{module_name}': {e}")
            all_ok = False
    
    return all_ok

def check_documentation():
    """Verifica se a documentação foi criada"""
    print("\n" + "="*70)
    print("VERIFICANDO DOCUMENTAÇÃO")
    print("="*70)
    
    doc_files = [
        'README.md',
        'DATABASE.md',
        'MIGRATION_GUIDE.md',
        'REORGANIZATION.md',
        'STRUCTURE.py',
        'SUMMARY.txt',
        '.gitignore'
    ]
    
    all_ok = True
    for doc_file in doc_files:
        path = Path(doc_file)
        if path.exists() and path.is_file():
            size = path.stat().st_size
            print_success(f"'{doc_file}' ({size} bytes)")
        else:
            print_warning(f"'{doc_file}' não encontrado (opcional)")
    
    return all_ok

def main():
    """Executa todas as verificações"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║                                                                      ║")
    print("║          VALIDAÇÃO DA ESTRUTURA DO BACKEND URBIX                     ║")
    print("║                                                                      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    
    results = []
    
    # 1. Estrutura de diretórios
    results.append(("Estrutura de Diretórios", check_directory_structure()))
    
    # 2. Arquivos __init__.py
    results.append(("Arquivos __init__.py", check_init_files()))
    
    # 3. Arquivos dos módulos
    results.append(("Arquivos dos Módulos", check_module_files()))
    
    # 4. Imports
    results.append(("Imports", check_imports()))
    
    # 5. Documentação
    results.append(("Documentação", check_documentation()))
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO DA VALIDAÇÃO")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results:
        if passed:
            print_success(f"{test_name}: OK")
        else:
            print_error(f"{test_name}: FALHOU")
            all_passed = False
    
    print("\n" + "="*70)
    if all_passed:
        print_success("TODAS AS VERIFICAÇÕES PASSARAM! ✨")
        print_info("\nPróximos passos:")
        print("  1. python -m scripts.init_database")
        print("  2. uvicorn main:app --reload")
        print("  3. Acesse http://localhost:8000/docs")
        return 0
    else:
        print_error("ALGUMAS VERIFICAÇÕES FALHARAM")
        print_info("\nConsulte os erros acima e corrija os problemas")
        return 1

if __name__ == "__main__":
    sys.exit(main())
