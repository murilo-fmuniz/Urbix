import json
from datetime import datetime
from app.database import SessionLocal
from app.models import Indicador, DadosColeta, Auditoria


def importar_dados_cidade():
    db = SessionLocal()
    
    try:
        # Lê o arquivo JSON com os dados da cidade
        with open('data/seed_apucarana.json', 'r', encoding='utf-8') as f:
            dados = json.load(f)
            
        inseridos = 0
        atualizados = 0
            
        for item in dados:
            codigo = item['codigo_indicador']
            
            # 1. Busca o Indicador Mestre
            indicador = db.query(Indicador).filter(Indicador.codigo_indicador == codigo).first()
            
            if not indicador:
                print(f"⚠️ Aviso: Indicador {codigo} não encontrado na base mestre. Pulei.")
                continue
                
            coleta_data = item['dados_coleta']
            
            # 2. Verifica se a coleta já existe para essa cidade e ano
            coleta = db.query(DadosColeta).filter(
                DadosColeta.indicador_id == indicador.id,
                DadosColeta.cidade == coleta_data['cidade'],
                DadosColeta.ano_referencia == coleta_data['ano_referencia']
            ).first()
            
            if not coleta:
                # Cria nova coleta
                coleta = DadosColeta(indicador_id=indicador.id, **coleta_data)
                db.add(coleta)
                db.flush() # Força a ida ao banco para gerar o ID da coleta
                inseridos += 1
            else:
                # Atualiza a coleta existente
                for key, value in coleta_data.items():
                    setattr(coleta, key, value)
                atualizados += 1
                
            # 3. Trata a Auditoria
            auditoria_data = item['auditoria']
            
            # Converte a string de data (YYYY-MM-DD) para objeto Date do Python
            if auditoria_data.get('data_extracao'):
                auditoria_data['data_extracao'] = datetime.strptime(auditoria_data['data_extracao'], '%Y-%m-%d').date()
                
            # Associa a auditoria à coleta
            if not coleta.auditoria:
                auditoria = Auditoria(dados_coleta_id=coleta.id, **auditoria_data)
                db.add(auditoria)
            else:
                for key, value in auditoria_data.items():
                    setattr(coleta.auditoria, key, value)
                    
        db.commit()
        print(f"✅ Importação finalizada! Inseridos: {inseridos} | Atualizados: {atualizados}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao importar: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    importar_dados_cidade()