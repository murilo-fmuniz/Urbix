#!/usr/bin/env python3
"""
Test para validar as 5 indicadores reais expandidos
- Taxa Endividamento (divida_consolidada)
- Despesas de Capital 
- Receita Própria
- Orçamento per capita
- Hospitais por 100k habitantes
"""

import asyncio
import sys

async def main():
    print("\n" + "=" * 80)
    print("TEST: 5 Indicadores Reais Expandidos")
    print("=" * 80)
    
    try:
        # Test 1: Validar FALLBACK_SICONFI com divida_consolidada
        print("\n1. Validando FALLBACK_SICONFI com divida_consolidada...")
        from app.services.external_apis import FALLBACK_SICONFI
        
        for codigo, dados in FALLBACK_SICONFI.items():
            assert "divida_consolidada" in dados, f"divida_consolidada missing for {codigo}"
            assert dados["divida_consolidada"] > 0, f"divida_consolidada must be > 0 for {codigo}"
            print(f"   [OK] {codigo}: divida_consolidada = R$ {dados['divida_consolidada']:,.0f}")
        
        # Test 2: Testar get_siconfi_finances retorna divida_consolidada
        print("\n2. Testando get_siconfi_finances return with divida_consolidada...")
        from app.services.external_apis import get_siconfi_finances
        
        resultado = await get_siconfi_finances("4101408")
        
        assert isinstance(resultado, dict), "Resultado deve ser dict"
        assert "receita_propria" in resultado, "Missing receita_propria"
        assert "receita_total" in resultado, "Missing receita_total"
        assert "despesas_capital" in resultado, "Missing despesas_capital"
        assert "servico_divida" in resultado, "Missing servico_divida"
        assert "divida_consolidada" in resultado, "Missing divida_consolidada (NEW!)"
        
        print(f"   [OK] Resultado SICONFI valido:")
        print(f"       - receita_propria: R$ {resultado['receita_propria']:,.0f}")
        print(f"       - receita_total: R$ {resultado['receita_total']:,.0f}")
        print(f"       - despesas_capital: R$ {resultado['despesas_capital']:,.0f}")
        print(f"       - servico_divida: R$ {resultado['servico_divida']:,.0f}")
        print(f"       - divida_consolidada: R$ {resultado['divida_consolidada']:,.0f} (NEW!)")
        
        # Test 3: Testar inject_api_data_into_flat_list com novo indicador
        print("\n3. Testando inject_api_data_into_flat_list com 5 indicadores...")
        from app.routers.topsis import inject_api_data_into_flat_list
        from app.schemas import ManualCityIndicators
        
        # Criar lista vazia (all zeros)
        indicadores_base = list(ManualCityIndicators().model_dump().values())[0]
        
        # Simular dados das APIs
        siconfi_test = {
            "receita_propria": 500000000.0,
            "receita_total": 1000000000.0,
            "despesas_capital": 100000000.0,
            "servico_divida": 50000000.0,
            "divida_consolidada": 200000000.0,  # NEW!
        }
        
        ibge_test = {"populacao": 100000.0}
        datasus_test = {"num_hospitais": 10}
        
        # Simular lista plana com 47 valores (todos zeros)
        flat_list = [0.0] * 47
        
        # Injeta dados
        resultado_inject = inject_api_data_into_flat_list(
            flat_list,
            siconfi_test,
            ibge_test,
            datasus_test,
            "Cidade Teste"
        )
        
        # Validar injeções
        print("\n   Verificando injeções nos índices corretos:")
        
        # [1] Taxa Endividamento (%)
        taxa_endiv_esperada = (200000000.0 / 1000000000.0 * 100)  # 20%
        assert resultado_inject[1] == taxa_endiv_esperada, f"Índice 1 incorreto: {resultado_inject[1]} != {taxa_endiv_esperada}"
        print(f"   [OK] Índice [1] Taxa Endividamento: {resultado_inject[1]:.2f}%")
        
        # [2] Despesas Capital (%)
        desp_cap_esperada = (100000000.0 / 1000000000.0 * 100)  # 10%
        assert resultado_inject[2] == desp_cap_esperada, f"Índice 2 incorreto: {resultado_inject[2]} != {desp_cap_esperada}"
        print(f"   [OK] Índice [2] Despesas Capital: {resultado_inject[2]:.2f}%")
        
        # [3] Receita Própria (%)
        rec_prop_esperada = (500000000.0 / 1000000000.0 * 100)  # 50%
        assert resultado_inject[3] == rec_prop_esperada, f"Índice 3 incorreto: {resultado_inject[3]} != {rec_prop_esperada}"
        print(f"   [OK] Índice [3] Receita Própria: {resultado_inject[3]:.2f}%")
        
        # [4] Orçamento per capita (R$)
        orcam_pc_esperado = 1000000000.0 / 100000.0  # R$ 10000
        assert resultado_inject[4] == orcam_pc_esperado, f"Índice 4 incorreto: {resultado_inject[4]} != {orcam_pc_esperado}"
        print(f"   [OK] Índice [4] Orçamento per capita: R$ {resultado_inject[4]:.2f}")
        
        # [35] Hospitais por 100k habitantes
        hosp_100k_esperado = (10 / 100000.0 * 100000)  # 10
        assert resultado_inject[35] == hosp_100k_esperado, f"Índice 35 incorreto: {resultado_inject[35]} != {hosp_100k_esperado}"
        print(f"   [OK] Índice [35] Hospitais/100k: {resultado_inject[35]:.2f}")
        
        # Test 4: Validar que dados manuais têm prioridade
        print("\n4. Validando prioridade de dados manuais...")
        flat_list_manual = [0.0] * 47
        flat_list_manual[1] = 15.0  # Valor manual para Taxa Endividamento
        flat_list_manual[35] = 5.0  # Valor manual para Hospitais
        
        resultado_manual = inject_api_data_into_flat_list(
            flat_list_manual,
            siconfi_test,
            ibge_test,
            datasus_test,
            "Cidade Teste 2"
        )
        
        # Verificar que valores manuais não foram sobrescritos
        assert resultado_manual[1] == 15.0, "Valor manual para [1] foi sobrescrito!"
        assert resultado_manual[35] == 5.0, "Valor manual para [35] foi sobrescrito!"
        print(f"   [OK] Valores manuais preservados:")
        print(f"       - Índice [1] mantém valor manual: {resultado_manual[1]:.2f}%")
        print(f"       - Índice [35] mantém valor manual: {resultado_manual[35]:.2f}%")
        
        print("\n" + "=" * 80)
        print("SUCCESS: Todos os testes passaram!")
        print("=" * 80)
        print("\n✓ 5 indicadores reais implementados com sucesso:")
        print("  1. Taxa Endividamento (SICONFI RGF - Divida Consolidada)")
        print("  2. Despesas de Capital (SICONFI RREO)")
        print("  3. Receita Própria (SICONFI RREO)")
        print("  4. Orçamento per capita (SICONFI RREO)")
        print("  5. Hospitais por 100k hab (DataSUS + IBGE)")
        print("=" * 80 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\nFAILURE: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
