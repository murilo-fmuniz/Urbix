#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_raw_apis.py

Script de auditoria para inspecionar respostas brutas (raw) das APIs externas.

Objetivo: Capturar e exibir as respostas exatas retornadas por cada API
(SICONFI, IBGE, DataSUS, INEP) antes de qualquer processamento pelo motor TOPSIS.

Uso:
    python test_raw_apis.py

Saída: Respostas formatadas em JSON bem indentado para cada API.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Configurar encoding UTF-8 para Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Adicionar o backend ao path para importar app
# Script está em backend/tests, então parent.parent nos leva ao backend
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.external_apis import (
    get_ibge_population,
    get_siconfi_finances,
    get_datasus_health_infrastructure,
    get_inep_education,
    get_local_analytics,
)


async def audit_apis(codigo_ibge: str = "4113700") -> None:
    """
    Auditoria de APIs externas - Coleta e exibe respostas brutas.
    
    Args:
        codigo_ibge: Código IBGE da cidade para teste (padrão: 4113700 = Londrina)
    """
    print("\n--- Testando Analytics Locais (CAGED/TSE) ---")
    caged_tse_result = await get_local_analytics("4113700")
    print(json.dumps(caged_tse_result, indent=4, ensure_ascii=False))
    print("\n" + "=" * 90)
    print("[AUDITORIA] APIs EXTERNAS - RESPOSTAS BRUTAS")
    print("=" * 90)
    print(f"\n[MUNICIPIO] Código IBGE: {codigo_ibge}")
    print(f"[DATA] {__import__('datetime').datetime.now().isoformat()}\n")

    # =========================================================================
    # 1. TESTE IBGE (População)
    # =========================================================================
    print("\n" + "-" * 90)
    print("[API 1] IBGE - Dados Populacionais")
    print("-" * 90)
    try:
        print("[COLETANDO] Dados IBGE...")
        ibge_data = await get_ibge_population(codigo_ibge)
        print("\n[SUCESSO] Resposta IBGE (raw):\n")
        print(json.dumps(ibge_data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"\n[ERRO] IBGE - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    # =========================================================================
    # 2. TESTE SICONFI (Finanças)
    # =========================================================================
    print("\n" + "-" * 90)
    print("[API 2] SICONFI - Dados Financeiros (Execução Orçamentária)")
    print("-" * 90)
    try:
        print("[COLETANDO] Dados SICONFI...")
        siconfi_data = await get_siconfi_finances(codigo_ibge)
        print("\n[SUCESSO] Resposta SICONFI (raw):\n")
        print(json.dumps(siconfi_data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"\n[ERRO] SICONFI - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    # =========================================================================
    # 3. TESTE DataSUS (Infraestrutura de Saúde)
    # =========================================================================
    print("\n" + "-" * 90)
    print("[API 3] DataSUS - Infraestrutura de Saúde")
    print("-" * 90)
    try:
        print("[COLETANDO] Dados DataSUS...")
        datasus_data = await get_datasus_health_infrastructure(codigo_ibge)
        print("\n[SUCESSO] Resposta DataSUS (raw):\n")
        print(json.dumps(datasus_data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"\n[ERRO] DataSUS - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    # =========================================================================
    # 4. TESTE INEP (Educação)
    # =========================================================================
    print("\n" + "-" * 90)
    print("[API 4] INEP/MEC - Indicadores de Educação")
    print("-" * 90)
    try:
        print("[COLETANDO] Dados INEP...")
        inep_data = await get_inep_education(codigo_ibge)
        print("\n[SUCESSO] Resposta INEP (raw):\n")
        print(json.dumps(inep_data, indent=4, ensure_ascii=False))
    except Exception as e:
        print(f"\n[ERRO] INEP - {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

    # =========================================================================
    # RESUMO FINAL
    # =========================================================================
    print("\n" + "=" * 90)
    print("[RESULTADO] Auditoria Concluida")
    print("=" * 90)
    print("\n[CHECKLIST] Proximas acoes:")
    print("   1. Verificar se todas as chaves estao presentes")
    print("   2. Validar tipos de dados (string, float, int, dict, list)")
    print("   3. Confirmar estrutura esperada pelo motor TOPSIS")
    print("   4. Identificar fallbacks implementados")
    print("\n")


async def main() -> None:
    """Função principal de entrada."""
    # Permitir override do código IBGE via argumentos de linha de comando
    teste_cidades = [
        ("4113700", "Londrina - PR"),
        ("4101408", "Apucarana - PR"),
    ]

    for codigo_ibge, nome_cidade in teste_cidades:
        print(f"\n\n[CIDADE] Testando: {nome_cidade}")
        await audit_apis(codigo_ibge)
        await asyncio.sleep(2)  # Delay entre requisições


if __name__ == "__main__":
    print("\n" + "=" * 90)
    print("[INICIO] AUDITOR DE APIs EXTERNAS - URBIX SMART CITIES")
    print("=" * 90)
    
    # Executar auditoria
    asyncio.run(main())
    
    print("\n" + "=" * 90)
    print("[FIM] Execucao finalizada")
    print("=" * 90 + "\n")
    
