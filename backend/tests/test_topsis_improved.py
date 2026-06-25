"""
Script de teste para validar as melhorias do endpoint TOPSIS
Verifica se os indicadores estão sendo coletados e injetados corretamente
"""

import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1/topsis"

async def test_ranking():
    """Testa o endpoint de ranking com Apucarana e São Paulo"""
    
    # Dados de entrada (sem indicadores manuais - deve carregar do banco)
    payload = [
        {
            "codigo_ibge": "4101408",
            "nome_cidade": "Apucarana",
            "manual_indicators": None  # Sem dados manuais!
        },
        {
            "codigo_ibge": "3550308",
            "nome_cidade": "São Paulo",
            "manual_indicators": None  # Sem dados manuais!
        }
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        print("📊 Enviando requisição para ranking híbrido...")
        print(f"   Payload: {json.dumps(payload, indent=2)}\n")
        
        try:
            response = await client.post(
                f"{BASE_URL}/ranking-hibrido",
                json=payload
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("\n✅ SUCESSO!")
                print(f"   Cidades ranqueadas: {len(data.get('cidades_ranqueadas', []))}")
                
                # Mostrar alguns indicadores da primeira cidade
                if data.get('cidades_ranqueadas'):
                    cidade = data['cidades_ranqueadas'][0]
                    print(f"\n   🏙️  {cidade.get('nome_cidade')}:")
                    print(f"      Índice Smart: {cidade.get('indice_smart', 0):.4f}")
                    print(f"      Status: {cidade.get('status', 'N/A')}")
                    
                    # Contar indicadores com dados > 0
                    indicadores = cidade.get('indicadores_normalizados', {})
                    indicadores_com_dados = sum(1 for v in indicadores.values() if v > 0)
                    print(f"      Indicadores com dados: {indicadores_com_dados}/{len(indicadores)}")
                    
                    # Mostrar alguns indicadores
                    print(f"\n      Indicadores (amostra):")
                    for i, (nome, valor) in enumerate(list(indicadores.items())[:10]):
                        print(f"        • {nome}: {valor:.4f}")
            else:
                print(f"\n❌ ERRO {response.status_code}:")
                print(response.text)
                
        except Exception as e:
            print(f"\n❌ Erro ao conectar: {str(e)}")
            print("   Verifique se o servidor está rodando em http://localhost:8000")

if __name__ == "__main__":
    asyncio.run(test_ranking())
