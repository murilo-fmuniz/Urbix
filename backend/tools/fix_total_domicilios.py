#!/usr/bin/env python
"""Reprocessar total_domicilios via SIDRA com chunking."""
import sys
from pathlib import Path
import requests
import time

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import ValorIndicador, Municipio

db_session = SessionLocal()

# Obter lista de cidades 
municipios = db_session.query(Municipio).all()
cidades_ibge = [m.codigo_ibge for m in municipios]
print(f"Total de municípios: {len(cidades_ibge)}")

# Deletar registros antigos
db_session.query(ValorIndicador).filter(
    ValorIndicador.id_indicador == "total_domicilios"
).delete()
db_session.commit()
print("Deletados registros antigos de total_domicilios\n")

# Processar em chunks
chunk_size = 50
total_loaded = 0

for chunk_start in range(0, len(cidades_ibge), chunk_size):
    chunk = cidades_ibge[chunk_start:chunk_start + chunk_size]
    territorio = ",".join(chunk)
    
    url = f"https://apisidra.ibge.gov.br/values/t/9922/p/2022/n6/{territorio}/v/381/c1/6795?formato=json"
    
    chunk_num = chunk_start // chunk_size + 1
    print(f"Chunk {chunk_num}: {len(chunk)} municípios...", end=" ", flush=True)
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        loaded_chunk = 0
        for item in data:
            try:
                if "D2C" not in item and "D1C" not in item:
                    continue
                
                codigo_ibge = item.get("D2C") or item.get("D1C")
                if not codigo_ibge:
                    continue
                
                # Normalizar para 7 dígitos
                codigo_ibge = "".join(c for c in str(codigo_ibge) if c.isdigit())
                if len(codigo_ibge) == 6:
                    # Procurar municipio com esse prefixo
                    cand = [c for c in cidades_ibge if c.startswith(codigo_ibge)]
                    if len(cand) == 1:
                        codigo_ibge = cand[0]
                    else:
                        continue
                elif len(codigo_ibge) != 7:
                    continue
                
                valor_str = item.get("V", "").strip()
                if not valor_str or valor_str in {"-", "...", "X"}:
                    continue
                
                valor = float(valor_str.replace(".", "").replace(",", "."))
                
                vi = ValorIndicador(
                    codigo_ibge=codigo_ibge,
                    id_indicador="total_domicilios",
                    valor=valor,
                    ano_referencia=2022,
                    fonte="SIDRA Censo (9922)"
                )
                db_session.add(vi)
                loaded_chunk += 1
                total_loaded += 1
                
            except Exception:
                pass  # Silenciar erros individuais
        
        db_session.commit()
        print(f"OK ({loaded_chunk} registros)")
        
    except requests.exceptions.RequestException as e:
        print(f"ERRO: {e}")
        db_session.rollback()
    
    time.sleep(0.5)  # Throttle para não sobrecarregar SIDRA

print(f"\n✓ Total carregado: {total_loaded} registros")

# Validar
count = db_session.query(ValorIndicador).filter(
    ValorIndicador.id_indicador == "total_domicilios"
).count()
print(f"Verificação: {count} registros no banco")

if count < 4000:
    print(f"AVISO: Cardinalidade baixa ({count})")
elif count >= 5000:
    print("✓ Carregamento validado! (cardinalidade esperada ~5570)")

db_session.close()
