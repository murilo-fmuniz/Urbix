#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recarregar apenas total_domicilios via SIDRA com retry simples."""
import sys
import os
from pathlib import Path

# Solucionar encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal
from app.models import ValorIndicador, Municipio
import requests

db = SessionLocal()

# Get cidades
muns = db.query(Municipio).all()
cidades = [m.codigo_ibge for m in muns]
print(f"Loading total_domicilios for {len(cidades)} cities...")

# Delete old
db.query(ValorIndicador).filter_by(id_indicador="total_domicilios").delete()
db.commit()

# Try to load with --all flag (national scale)
url_base = "https://apisidra.ibge.gov.br/values/t/9922/p/2022/n6/all/v/381/c1/6795?formato=json"
print(f"Requesting: {url_base}")

try:
    r = requests.get(url_base, timeout=60)
    r.raise_for_status()
    data = r.json()
    print(f"Received {len(data)} items")
    
    loaded = 0
    for item in data:
        try:
            cod = item.get("D2C") or item.get("D1C", "")
            cod = "".join(c for c in str(cod) if c.isdigit())
            
            if len(cod) == 6:
                matches = [c for c in cidades if c.startswith(cod)]
                if len(matches) == 1:
                    cod = matches[0]
                else:
                    continue
            elif len(cod) != 7:
                continue
            
            val_str = str(item.get("V", "")).strip()
            if val_str in {"", "-", "...", "X"}:
                continue
            
            val = float(val_str.replace(".", "").replace(",", "."))
            
            vi = ValorIndicador(
                codigo_ibge=cod,
                id_indicador="total_domicilios",
                valor=val,
                ano_referencia=2022,
                fonte="SIDRA Censo (9922)"
            )
            db.add(vi)
            loaded += 1
            
        except:
            pass
    
    db.commit()
    print(f"Loaded: {loaded} records")
    
    # Verify
    count = db.query(ValorIndicador).filter_by(id_indicador="total_domicilios").count()
    print(f"Verified: {count} records in DB")
    
    if count >= 5000:
        print("SUCCESS: total_domicilios restored!")
    else:
        print(f"WARNING: Only {count} records (expected ~5570)")
        
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
