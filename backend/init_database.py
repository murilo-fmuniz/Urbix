"""
Script de inicialização do banco de dados
Executa todas as etapas necessárias para configurar o banco de dados do zero
"""
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Executa todos os scripts de inicialização do banco de dados"""
    
    print("=" * 70)
    print("INICIALIZAÇÃO DO BANCO DE DADOS URBIX")
    print("=" * 70)
    print()
    
    # Verificar se o diretório data existe
    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        logger.info("Criando diretório data/...")
        data_dir.mkdir(exist_ok=True)
    
    try:
        # Passo 1: Inicializar estrutura do banco
        logger.info("\n[1/3] Inicializando estrutura do banco de dados...")
        from db_config import init_db
        init_db()
        
        # Passo 2: Executar ETL do IBGE (cidades e estados)
        logger.info("\n[2/3] Executando ETL - IBGE Localidades...")
        logger.info("Isso pode levar alguns minutos...")
        from etl_ibge import run_full_etl
        run_full_etl()
        
        # Passo 3: Migrar dados existentes
        logger.info("\n[3/3] Migrando dados existentes (indicadores)...")
        from migrate_data import run_migration
        run_migration(include_samples=False)
        
        print()
        print("=" * 70)
        print("✓ BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("=" * 70)
        print()
        
        return 0
    
    except Exception as e:
        logger.error(f"\n❌ ERRO na inicialização: {e}", exc_info=True)
        print()
        print("=" * 70)
        print("❌ FALHA NA INICIALIZAÇÃO DO BANCO DE DADOS")
        print("=" * 70)
        print(f"\nErro: {e}")
        print("\nVerifique os logs acima para mais detalhes.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
