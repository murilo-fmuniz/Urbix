"""
Script para semear (seed) os indicadores ISO 37122 no banco de dados.

Uso:
    python seed_indicadores.py
    
Ou, se estiver em um venv:
    .\venv\Scripts\python seed_indicadores.py (Windows)
    source venv/bin/activate && python seed_indicadores.py (Linux/Mac)
"""

import json
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar app
sys.path.insert(0, str(Path(__file__).parent))

from app import models, schemas
from app.database import SessionLocal


def seed_indicadores():
    """Carrega os indicadores ISO 37122 do arquivo JSON para o banco."""
    
    # Carrega dados do arquivo
    seed_file = Path(__file__).parent / "data" / "seed_indicadores_iso37122.json"
    
    if not seed_file.exists():
        print(f"❌ Arquivo não encontrado: {seed_file}")
        return False
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        indicadores_data = json.load(f)
    
    # Conecta ao banco
    db = SessionLocal()
    
    try:
        total_criados = 0
        total_existentes = 0
        
        for ind_data in indicadores_data:
            codigo = ind_data['codigo_indicador']
            
            # Verifica se indicador já existe (case-insensitive)
            existing = db.query(models.Indicador).filter(
                models.Indicador.codigo_indicador.ilike(codigo)
            ).first()
            
            if existing:
                print(f"⏭️  Indicador {codigo} já existe, pulando...")
                total_existentes += 1
                continue
            
            # Cria novo indicador
            indicador = models.Indicador(
                codigo_indicador=ind_data['codigo_indicador'],
                nome=ind_data['nome'],
                norma=ind_data['norma'],
                grande_area=ind_data['grande_area'],
                eixo=ind_data['eixo'],
                tipo=ind_data['tipo'],
                descricao=ind_data['descricao'],
            )
            
            # Adiciona metodologia se existir
            if 'metodologia' in ind_data and ind_data['metodologia']:
                metodologia = models.Metodologia(
                    **ind_data['metodologia']
                )
                indicador.metodologia = metodologia
            
            db.add(indicador)
            db.commit()
            db.refresh(indicador)
            
            print(f"✅ Indicador criado: {codigo} - {ind_data['nome']}")
            total_criados += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Resumo:")
        print(f"  ✅ Indicadores criados: {total_criados}")
        print(f"  ⏭️  Indicadores existentes: {total_existentes}")
        print(f"  📈 Total de indicadores no arquivo: {len(indicadores_data)}")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao semear indicadores: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Iniciando semeadura de indicadores ISO 37122...")
    print()
    
    success = seed_indicadores()
    
    sys.exit(0 if success else 1)
