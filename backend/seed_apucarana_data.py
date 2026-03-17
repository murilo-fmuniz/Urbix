"""
Script para importar dados de coleta de Apucarana ao banco de dados.

Uso:
    python seed_apucarana_data.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from app import models
from app.database import SessionLocal


def seed_apucarana_data():
    """Carrega os dados de Apucarana do arquivo JSON para o banco."""
    
    # Carrega dados do arquivo
    seed_file = Path(__file__).parent / "data" / "seed_apucarana.json"
    
    if not seed_file.exists():
        print(f"❌ Arquivo não encontrado: {seed_file}")
        return False
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        coletas_data = json.load(f)
    
    # Conecta ao banco
    db = SessionLocal()
    
    try:
        total_criados = 0
        total_existentes = 0
        total_erros = 0
        
        for coleta_info in coletas_data:
            codigo = coleta_info['codigo_indicador']
            
            # Encontra o indicador
            indicador = db.query(models.Indicador).filter(
                models.Indicador.codigo_indicador.ilike(codigo)
            ).first()
            
            if not indicador:
                print(f"❌ Indicador {codigo} não encontrado, pulando...")
                total_erros += 1
                continue
            
            # Verifica se já existe coleta para esta cidade/indicador/ano
            existing = db.query(models.DadosColeta).filter(
                models.DadosColeta.indicador_id == indicador.id,
                models.DadosColeta.cidade.ilike(coleta_info['dados_coleta']['cidade']),
                models.DadosColeta.ano_referencia == coleta_info['dados_coleta']['ano_referencia']
            ).first()
            
            if existing:
                print(f"⏭️  {codigo} - Apucarana ({coleta_info['dados_coleta']['ano_referencia']}) já existe, pulando...")
                total_existentes += 1
                continue
            
            # Cria a coleta
            coleta = models.DadosColeta(
                indicador_id=indicador.id,
                **coleta_info['dados_coleta']
            )
            
            # Adiciona auditoria se existir
            if 'auditoria' in coleta_info and coleta_info['auditoria']:
                auditoria_data = coleta_info['auditoria'].copy()
                # Converter data_extracao de string para date object
                if auditoria_data.get('data_extracao') and isinstance(auditoria_data['data_extracao'], str):
                    auditoria_data['data_extracao'] = datetime.strptime(
                        auditoria_data['data_extracao'], '%Y-%m-%d'
                    ).date()
                auditoria = models.Auditoria(**auditoria_data)
                coleta.auditoria = auditoria
            
            db.add(coleta)
            db.commit()
            db.refresh(coleta)
            
            print(f"✅ Coleta inserida: {codigo} - Apucarana ({coleta_info['dados_coleta']['ano_referencia']})")
            total_criados += 1
        
        print(f"\n{'='*60}")
        print(f"📊 Resumo:")
        print(f"  ✅ Coletas criadas: {total_criados}")
        print(f"  ⏭️  Coletas existentes: {total_existentes}")
        print(f"  ❌ Erros: {total_erros}")
        print(f"  📈 Total de coletas no arquivo: {len(coletas_data)}")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao semear dados: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Iniciando importação de dados de Apucarana...")
    print()
    
    success = seed_apucarana_data()
    
    sys.exit(0 if success else 1)
