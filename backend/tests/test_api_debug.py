"""
DIAGNOSTIC SCRIPT - Debug API Data Quality Issues

Testa todas as 7 APIs em paralelo e mostra o formato exato dos dados recebidos.
Ajuda a identificar por que valores globais estão sendo usados ao invés de dados reais.

Uso:
    python3 backend/test_api_debug.py

Resultado:
    - Mostra dados brutos recebidos de cada API
    - Identifica parsing incorretos
    - Sugere ajustes necessários
"""

import asyncio
import logging
from app.services.external_apis import (
    get_siconfi_finances,
    get_ibge_population,
    get_datasus_health_infrastructure,
    get_inep_education,
    get_transparencia_social,
    get_datasus_expanded_wrapper,
    get_portal_transparencia_expanded_wrapper,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Cidades de teste
CIDADES_TESTE = [
    ("4101408", "Apucarana"),
    ("4113700", "Londrina"),
    ("3550308", "São Paulo"),
]

async def test_single_city(codigo_ibge: str, nome_cidade: str):
    """Testa todas as 7 APIs para uma cidade específica"""
    print(f"\n{'='*100}")
    print(f"TESTANDO: {nome_cidade} ({codigo_ibge})")
    print(f"{'='*100}\n")
    
    # Teste 1: SICONFI
    print("TESTE 1: SICONFI (Financas)")
    print("-" * 80)
    try:
        siconfi = await get_siconfi_finances(codigo_ibge)
        print(f"[OK] Retornou: {type(siconfi)}")
        print(f"   Keys: {list(siconfi.keys()) if isinstance(siconfi, dict) else 'N/A'}")
        print(f"   Valores: {siconfi}")
        print(f"   DIAGNOSTICO: DC={siconfi.get('divida_consolidada', 'FALTANDO')}, Receita={siconfi.get('receita_total', 'FALTANDO')}")
        if siconfi.get('divida_consolidada', 0) == 0:
            print(f"   [AVISO] PROBLEMA: Divida Consolidada = 0 (parsing pode estar errado)")
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
    
    # Teste 2: IBGE
    print("\nTESTE 2: IBGE (Populacao)")
    print("-" * 80)
    try:
        ibge = await get_ibge_population(codigo_ibge)
        print(f"[OK] Retornou: {type(ibge)}")
        print(f"   Valor: {ibge}")
        if ibge and ibge > 100000:
            print(f"   [OK] VALIDO: Populacao = {ibge:,.0f}")
        else:
            print(f"   [AVISO] POSSIVEL PROBLEMA: Populacao = {ibge}")
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
    
    # Teste 3: DataSUS (Basico)
    print("\nTESTE 3: DataSUS CNES (Infraestrutura Basica)")
    print("-" * 80)
    try:
        datasus = await get_datasus_health_infrastructure(codigo_ibge)
        print(f"[OK] Retornou: {type(datasus)}")
        print(f"   Keys: {list(datasus.keys()) if isinstance(datasus, dict) else 'N/A'}")
        print(f"   Valores: {datasus}")
        num_hosp = datasus.get('num_hospitais', 0)
        if num_hosp == 0:
            print(f"   [AVISO] PROBLEMA: num_hospitais = 0 (pode estar falhando silenciosamente)")
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
    
    # Teste 4: INEP
    print("\nTESTE 4: INEP (Educacao)")
    print("-" * 80)
    try:
        inep = await get_inep_education(codigo_ibge)
        print(f"[OK] Retornou: {type(inep)}")
        print(f"   Keys: {list(inep.keys()) if isinstance(inep, dict) else 'N/A'}")
        print(f"   Valores: {inep}")
        if inep and (inep.get('relacao_estudante_professor') or inep.get('ideb_anos_iniciais')):
            print(f"   [OK] VALIDO: Tem dados educacionais")
        else:
            print(f"   [AVISO] POSSIVEL FALLBACK: Pode estar usando defaults")
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
    
    # Teste 5: Portal da Transparencia + TSE
    print("\nTESTE 5: Portal da Transparencia + TSE (Social/Eleitoral)")
    print("-" * 80)
    try:
        transparencia = await get_transparencia_social(codigo_ibge)
        print(f"[OK] Retornou: {type(transparencia)}")
        print(f"   Keys: {list(transparencia.keys()) if isinstance(transparencia, dict) else 'N/A'}")
        print(f"   Valores: {transparencia}")
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
    
    # Teste 6: DataSUS Expandido (Phase 2 Task 4)
    print("\nTESTE 6: DataSUS Expandido (5 indicadores de saude)")
    print("-" * 80)
    try:
        datasus_exp = await get_datasus_expanded_wrapper(codigo_ibge)
        print(f"[OK] Retornou: {type(datasus_exp)}")
        print(f"   Keys: {list(datasus_exp.keys()) if isinstance(datasus_exp, dict) else 'N/A'}")
        print(f"   Valores: {datasus_exp}")
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
    
    # Teste 7: Portal Transparencia Expandido (Phase 2 Task 2)
    print("\nTESTE 7: Portal Transparencia Expandido (3 indicadores sociais)")
    print("-" * 80)
    try:
        portal_social = await get_portal_transparencia_expanded_wrapper(codigo_ibge)
        print(f"[OK] Retornou: {type(portal_social)}")
        print(f"   Keys: {list(portal_social.keys()) if isinstance(portal_social, dict) else 'N/A'}")
        print(f"   Valores: {portal_social}")
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
    
    print(f"\n{'='*100}\n")

async def main():
    """Testa as 3 cidades"""
    print("\n" + "DIAGNOSTICO DE APIs - URBIX SMART CITIES".center(100))
    print("Objetivo: Verificar quais APIs retornam dados corretos vs. fallbacks\n")
    
    for codigo_ibge, nome_cidade in CIDADES_TESTE:
        await test_single_city(codigo_ibge, nome_cidade)
    
    print("\n" + "RESUMO DE PROBLEMAS E SOLUCOES".center(100))
    print("""
    
    PROBLEMA 1: DC (Divida Consolidada) = R$ 0
    ├─ Causa: Parsing de RGF nao esta achando "DIVIDA CONSOLIDADA - DC"
    ├─ Solucao: Verificar nomes exatos das contas no endpoint RGF
    └─ Teste: Chame RGF diretamente e mostre o JSON

    PROBLEMA 2: DataSUS falha com ReadError
    ├─ Causa: Parsing HTML/XML corrompido ou endpoint mudou
    ├─ Solucao: Aumentar timeout, melhorar parsing, adicionar retry
    └─ Teste: Chame CNES diretamente e verifique formato

    PROBLEMA 3: INEP usando fallback
    ├─ Causa: API retorna dados invalidos ou estrutura mudou
    ├─ Solucao: Verificar formato exato da resposta INEP
    └─ Teste: Compare resposta real vs. esperada

    PROBLEMA 4: Valores globais (media nacional) em vez de reais
    ├─ Causa: Todas as APIs falhando simultanea ou sequencialmente
    ├─ Solucao: Implementar fallbacks inteligentes (especificos por cidade > universais)
    └─ Resultado: TOPSIS com dados reais, nao medias
    """)

if __name__ == "__main__":
    asyncio.run(main())
