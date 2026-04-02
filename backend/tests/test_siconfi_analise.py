"""
Analisar estrutura detalhada da API SICONFI para encontrar campos corretos.
"""

import asyncio
import httpx
import json

DEFAULT_TIMEOUT = 30.0

async def analise_detalhada():
    """Análise profunda dos dados retornados"""
    
    print("=" * 100)
    print("🔍 ANÁLISE DETALHADA DOS DADOS SICONFI")
    print("=" * 100)
    
    url_base = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    params = {
        "id_ente": "4101408",       # Apucarana
        "an_exercicio": 2023,
        "nr_periodo": 6,
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 01"
    }
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        response = await client.get(url_base, params=params)
        
        if response.status_code != 200:
            print(f"❌ Erro: {response.status_code}")
            return
        
        data = response.json()
        items = data.get("items", [])
        
        print(f"\n✅ Total de items: {len(items)}")
        
        # 1. Análise de COLUNAS (coluna)
        print("\n" + "=" * 100)
        print("📊 COLUNAS DISPONÍVEIS:")
        print("=" * 100)
        
        colunas_unicas = set()
        for item in items:
            colunas_unicas.add(item.get("coluna", ""))
        
        for i, coluna in enumerate(sorted(colunas_unicas), 1):
            # Contar quantos items têm essa coluna
            count = sum(1 for item in items if item.get("coluna") == coluna)
            print(f"{i:2d}. {coluna:50s} ({count:3d} items)")
        
        # 2. Análise de CONTAS (conta)
        print("\n" + "=" * 100)
        print("💼 CONTAS DISPONÍVEIS:")
        print("=" * 100)
        
        contas_unicas = set()
        for item in items:
            contas_unicas.add(item.get("conta", ""))
        
        # Filtrar por RECEITA
        receitas = [c for c in contas_unicas if "RECEITA" in c.upper()]
        despesas = [c for c in contas_unicas if "DESPESA" in c.upper()]
        
        print(f"\n🟢 RECEITAS ({len(receitas)}):")
        for conta in sorted(receitas)[:10]:  # Top 10
            print(f"   - {conta}")
        if len(receitas) > 10:
            print(f"   ... e mais {len(receitas) - 10}")
        
        print(f"\n🔴 DESPESAS ({len(despesas)}):")
        for conta in sorted(despesas)[:10]:  # Top 10
            print(f"   - {conta}")
        if len(despesas) > 10:
            print(f"   ... e mais {len(despesas) - 10}")
        
        # 3. Analisar valores RECEITA com coluna específica
        print("\n" + "=" * 100)
        print("🔎 ANÁLISE: RECEITAS POR COLUNA")
        print("=" * 100)
        
        # Filtrar receitas com coluna "PREVISÃO INICIAL"
        receitas_previsao = [item for item in items 
                            if "RECEITA" in item.get("conta", "").upper() 
                            and "PREVISÃO INICIAL" in item.get("coluna", "").upper()]
        
        print(f"\n📌 Receitas com coluna 'PREVISÃO INICIAL': {len(receitas_previsao)}")
        for item in receitas_previsao[:5]:
            print(f"   {item['conta']}: R$ {item['valor']:,.2f}")
        
        # 4. Procurar campos com "TOTAL DE RECEITAS"
        print("\n" + "=" * 100)
        print("🎯 PROCURANDO: 'TOTAL DE RECEITAS'")
        print("=" * 100)
        
        total_receitas = [item for item in items if "TOTAL DE RECEITAS" in item.get("conta", "").upper()]
        print(f"\nEncontrados {len(total_receitas)} items com 'TOTAL DE RECEITAS':")
        
        for item in total_receitas:
            print(f"\n   Coluna: {item['coluna']}")
            print(f"   Valor: R$ {item['valor']:,.2f}")
        
        # 5. Procurar DESPESAS DE CAPITAL
        print("\n" + "=" * 100)
        print("🏗️  PROCURANDO: 'DESPESAS DE CAPITAL'")
        print("=" * 100)
        
        despesas_capital = [item for item in items if "DESPESAS DE CAPITAL" in item.get("conta", "").upper()]
        print(f"\nEncontrados {len(despesas_capital)} items com 'DESPESAS DE CAPITAL':")
        
        for item in despesas_capital[:10]:
            print(f"   Coluna: {item['coluna']:40s} | Valor: R$ {item['valor']:15,.2f}")
        
        # 6. Procurar RECEITAS EXCEPTO INTRA-ORÇAMENTÁRIAS
        print("\n" + "=" * 100)
        print("💰 PROCURANDO: 'RECEITAS (EXCETO INTRA-ORÇAMENTÁRIAS)'")
        print("=" * 100)
        
        receitas_intra = [item for item in items 
                         if "RECEITAS (EXCETO INTRA-ORÇAMENTÁRIAS)" in item.get("conta", "").upper()]
        print(f"\nEncontrados {len(receitas_intra)} items:")
        
        for item in receitas_intra[:10]:
            print(f"   Coluna: {item['coluna']:40s} | Valor: R$ {item['valor']:15,.2f}")


if __name__ == "__main__":
    asyncio.run(analise_detalhada())
