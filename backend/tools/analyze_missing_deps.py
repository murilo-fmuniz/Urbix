#!/usr/bin/env python3
"""Análise de faltantes: IDs necessários, indicadores bloqueados e fontes."""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(backend_dir))

from app.etl_config import INDICADORES
from app.services.topsis_core import _indicadores_validos_para_topsis


def analyze_missing_ids():
    """Mapeia IDs faltantes → indicadores bloqueados → fontes."""
    
    validos = set(_indicadores_validos_para_topsis())
    
    # ID faltante -> lista de (indicador_id, tipo_uso, coluna_fonte)
    missing_deps = {}
    
    for dominio, indicadores in INDICADORES.items():
        for ind_id, regras in indicadores.items():
            if ind_id not in validos:
                continue
            
            status = str(regras.get("status", "")).strip().lower()
            
            # Pula indicadores sem implementação ou incompletos
            if any(s in status for s in ["pendente", "não_baixado", "em_implementacao"]):
                continue
            
            tipo = regras.get("tipo_calculo")
            
            # Indicador direto
            if tipo == "direto":
                var_direta = regras.get("variavel_direta", {})
                arquivo = var_direta.get("arquivo", "?")
                if arquivo == "NÃO_BAIXADO":
                    chave = f"{ind_id}_direto"
                    if chave not in missing_deps:
                        missing_deps[chave] = []
                    missing_deps[chave].append((ind_id, "DIRETO", var_direta.get("fonte", "?")))
            else:
                # Indicador calculado (numerador/denominador)
                num_id = f"{ind_id}_numerador"
                if num_id not in missing_deps:
                    missing_deps[num_id] = []
                missing_deps[num_id].append((ind_id, "NUMERADOR", "?"))
                
                denominador = regras.get("denominador")
                if denominador:
                    if denominador not in missing_deps:
                        missing_deps[denominador] = []
                    missing_deps[denominador].append((ind_id, "DENOMINADOR", "?"))
    
    print("=" * 100)
    print("ANÁLISE DE FALTANTES: IDs NECESSÁRIOS AO TOPSIS")
    print("=" * 100)
    print()
    
    for id_faltante in sorted(missing_deps.keys()):
        deps = missing_deps[id_faltante]
        print(f"[MISSING] {id_faltante}")
        print(f"  Bloqueados ({len(deps)}):")
        for ind, tipo_uso, fonte in sorted(set(deps)):
            print(f"    - {ind} ({tipo_uso}) | Fonte: {fonte}")
        print()


if __name__ == "__main__":
    analyze_missing_ids()
