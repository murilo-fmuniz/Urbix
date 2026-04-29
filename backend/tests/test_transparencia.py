#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_transparencia.py

Script de teste para a nova integração com o Portal da Transparência do Governo Federal.

Objetivo: Testar a coleta de datos de Bolsa Família e CEIS para diferentes municípios.

Uso:
    python test_transparencia.py

Saída: Respostas formatadas em JSON bem indentado.
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

from app.services.external_apis import get_transparencia_social


async def test_transparencia(codigo_ibge: str, nome_cidade: str) -> None:
    """
    Testa a integração com o Portal da Transparência.
    
    Args:
        codigo_ibge: Código IBGE do município
        nome_cidade: Nome do município para exibição
    """
    print("\n" + "=" * 90)
    print("[TESTE] Portal da Transparência - Dados Sociais")
    print("=" * 90)
    print(f"\n[MUNICIPIO] {nome_cidade} (IBGE: {codigo_ibge})")
    print(f"[DATA] {__import__('datetime').datetime.now().isoformat()}\n")
    
    try:
        print("[COLETANDO] Dados de Bolsa Família e CEIS...")
        resultado = await get_transparencia_social(codigo_ibge)
        
        print("\n[SUCESSO] Resposta Portal da Transparência (raw):\n")
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
        
        # Análise dos dados
        print("\n" + "-" * 90)
        print("[ANALISE] Interpretação dos Dados")
        print("-" * 90)
        print(f"   Beneficiados Bolsa Família: {resultado['beneficiados_bolsa_familia']:,}")
        print(f"   Sanções CEIS: {resultado['sancoes_ceis']}")
        print(f"   Fonte: {resultado['fonte']}")
        
    except Exception as e:
        print(f"\n[ERRO] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n")


async def main() -> None:
    """Função principal de entrada."""
    
    # Testar 3 municípios do Paraná
    teste_cidades = [
        ("4113700", "Londrina - PR"),
        ("4101408", "Apucarana - PR"),
        ("4115200", "Maringá - PR"),
    ]
    
    for codigo_ibge, nome_cidade in teste_cidades:
        await test_transparencia(codigo_ibge, nome_cidade)
        await asyncio.sleep(1)  # Delay entre requisições


if __name__ == "__main__":
    print("\n" + "=" * 90)
    print("[INICIO] TESTE - Portal da Transparência (Gov.br)")
    print("=" * 90)
    print("\n[INFO] Testando integração com API de Bolsa Família e CEIS")
    print("[INFO] Coletando dados para 3 cidades de teste\n")
    
    # Executar testes
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CANCELADO] Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n[ERRO CRITICO] {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 90)
    print("[FIM] Teste concluído")
    print("=" * 90 + "\n")
