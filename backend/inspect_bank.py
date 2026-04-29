"""
Debug: Inspecionar estrutura dos dados no banco
"""

import sys
sys.path.insert(0, 'd:\\Docs\\Faculdade\\IC\\Urbix\\backend')

import json
from app.database import SessionLocal
from app.models import CityManualData
from app.schemas import ManualCityIndicators

def inspect_bank_data():
    """Inspeciona os dados do banco em detalhes"""
    db = SessionLocal()
    
    for codigo in ["4101408", "3550308"]:
        print(f"\n{'='*70}")
        print(f"INSPECAO: {codigo}")
        print('='*70)
        
        cidade = db.query(CityManualData).filter_by(codigo_ibge=codigo).first()
        if cidade:
            print(f"Nome: {cidade.nome_cidade}")
            print(f"Data: {cidade.data_atualizacao}")
            
            if cidade.indicadores_manuais:
                dados = cidade.indicadores_manuais
                print(f"\nEstrutura JSON (raw):")
                print(json.dumps(dados, indent=2)[:1500])  # Primeiros 1500 chars
                
                # Contar campos
                iso37120_count = len(dados.get("iso_37120", {}))
                iso37122_count = len(dados.get("iso_37122", {}))
                iso37123_count = len(dados.get("iso_37123", {}))
                
                print(f"\nCampos por ISO:")
                print(f"  iso_37120: {iso37120_count}")
                print(f"  iso_37122: {iso37122_count}")
                print(f"  iso_37123: {iso37123_count}")
                print(f"  Total: {iso37120_count + iso37122_count + iso37123_count}")
                
                # Converter para ManualCityIndicators
                try:
                    manual = ManualCityIndicators(**dados)
                    print(f"\nOK - Conversao para ManualCityIndicators")
                    
                    # Contar valores nao-zero
                    iso_37120 = manual.iso_37120
                    iso_37122 = manual.iso_37122
                    iso_37123 = manual.iso_37123
                    
                    nao_zero_37120 = sum(1 for v in [getattr(iso_37120, f) for f in iso_37120.model_fields] if v > 0)
                    nao_zero_37122 = sum(1 for v in [getattr(iso_37122, f) for f in iso_37122.model_fields] if v > 0)
                    nao_zero_37123 = sum(1 for v in [getattr(iso_37123, f) for f in iso_37123.model_fields] if v > 0)
                    
                    print(f"\nValores nao-zero:")
                    print(f"  iso_37120: {nao_zero_37120}/{iso37120_count}")
                    print(f"  iso_37122: {nao_zero_37122}/{iso37122_count}")
                    print(f"  iso_37123: {nao_zero_37123}/{iso37123_count}")
                    print(f"  Total: {nao_zero_37120 + nao_zero_37122 + nao_zero_37123}/{iso37120_count + iso37122_count + iso37123_count}")
                    
                    # Listar os valores nao-zero
                    print(f"\n Indicadores nao-zero:")
                    for field in iso_37120.model_fields:
                        val = getattr(iso_37120, field)
                        if val > 0:
                            print(f"    iso_37120.{field}: {val}")
                    for field in iso_37122.model_fields:
                        val = getattr(iso_37122, field)
                        if val > 0:
                            print(f"    iso_37122.{field}: {val}")
                    for field in iso_37123.model_fields:
                        val = getattr(iso_37123, field)
                        if val > 0:
                            print(f"    iso_37123.{field}: {val}")
                    
                except Exception as e:
                    print(f"\nERRO na conversao: {e}")
    
    db.close()

if __name__ == "__main__":
    inspect_bank_data()
