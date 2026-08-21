import requests
import json

def testar_siconfi():
    # Código IBGE de Itapema/SC
    ibge_teste = "4208203" 
    
    url = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt/rreo"
    
    # Exatamente os mesmos parâmetros que o seu ETL usa
    params = {
        "an_exercicio": 2023,
        "nr_periodo": 6,
        "co_tipo_demonstrativo": "RREO",
        "no_anexo": "RREO-Anexo 03",
        "id_ente": ibge_teste,
    }

    print(f"🌐 Buscando dados no SICONFI para a cidade: {ibge_teste}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"Status Code: {response.status_code}\n")
        
        if response.status_code == 200:
            payload = response.json()
            items = payload.get("items", [])
            
            print(f"📦 Total de linhas contábeis retornadas: {len(items)}\n")
            
            if items:
                print("🔍 Estrutura bruta de um item retornado pelo Tesouro:")
                # Imprime apenas o primeiro item formatado bonito
                print(json.dumps(items[0], indent=2, ensure_ascii=False))
            
            print("\n🎯 Procurando o indicador 'Receita Corrente Líquida'...")
            
            # O laço que o seu código faz para achar a agulha no palheiro
            encontrou = False
            for item in items:
                if item.get("cod_conta") == "RREO3ReceitaCorrenteLiquida":
                    valor = item.get("valor")
                    print(f"✅ SUCESSO! Valor encontrado: R$ {valor:,.2f}")
                    encontrou = True
                    break
            
            if not encontrou:
                print("⚠️ Conta 'RREO3ReceitaCorrenteLiquida' não encontrada.")
                
        else:
            print(f"❌ Erro na requisição: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro ao conectar na API: {e}")

if __name__ == "__main__":
    testar_siconfi()