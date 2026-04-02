#!/usr/bin/env python
"""
Script para limpar dados fake/históricos de Apucarana do banco de dados.
Objetivo: Manter apenas dados reais provenientes de APIs e entrada manual.

Operações:
1. Listar dados fake de Apucarana
2. Deletar dados_coleta com cidade='Apucarana'
3. Deletar auditorias associadas (cascata automática)
4. Deletar indicadores antigos de "3 por grande_area" do backend antigo
5. Deletar CityManualData de Apucarana
"""

import sys
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.models import Base, DadosColeta, Auditoria, Indicador, CityManualData
from app.database import DATABASE_URL

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

def listar_dados_apucarana():
    """Lista todos os dados de Apucarana no banco"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print_section("1. DADOS DE APUCARANA ENCONTRADOS")
        
        # 1. DadosColeta
        dados_coleta = session.query(DadosColeta).filter(
            DadosColeta.cidade == "Apucarana"
        ).all()
        print(f"\n📊 DadosColeta (Apucarana): {len(dados_coleta)} registros")
        for dc in dados_coleta[:5]:  # Mostra apenas 5 primeiros
            print(f"   - ID: {dc.id}, Indicador: {dc.indicador_id}, Ano: {dc.ano_referencia}")
        if len(dados_coleta) > 5:
            print(f"   ... e mais {len(dados_coleta) - 5} registros")
        
        # 2. CityManualData
        city_manual = session.query(CityManualData).filter(
            CityManualData.nome_cidade == "Apucarana"
        ).all()
        print(f"\n👤 CityManualData (Apucarana): {len(city_manual)} registros")
        for cm in city_manual:
            print(f"   - IBGE Code: {cm.codigo_ibge}, Iluminação: {cm.pontos_iluminacao_telegestao}")
        
        # 3. Indicadores do backend antigo (3 por grande_area)
        indicadores_antigos = session.query(Indicador).filter(
            Indicador.grande_area != None
        ).all()
        print(f"\n📋 Indicadores com grande_area: {len(indicadores_antigos)} registros")
        grandes_areas = set(ind.grande_area for ind in indicadores_antigos if ind.grande_area)
        print(f"   Grandes areas: {', '.join(sorted(grandes_areas))}")
        
        return {
            "dados_coleta_count": len(dados_coleta),
            "city_manual_count": len(city_manual),
            "indicadores_antigos_count": len(indicadores_antigos),
        }
    
    finally:
        session.close()

def deletar_dados_apucarana(confirmar=False):
    """Deleta dados fake de Apucarana"""
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print_section("2. DELETANDO DADOS DE APUCARANA")
        
        # 1. Deletar DadosColeta (cascata deleta Auditoria automaticamente)
        dados_coleta = session.query(DadosColeta).filter(
            DadosColeta.cidade == "Apucarana"
        ).all()
        count_dc = len(dados_coleta)
        
        if confirmar:
            for dc in dados_coleta:
                session.delete(dc)
            session.commit()
            print(f"✅ Deletado: {count_dc} registros de DadosColeta (Apucarana)")
            print(f"✅ Deletado: {count_dc} registros de Auditoria associadas (cascata)")
        else:
            print(f"🔍 Seria deletado: {count_dc} registros de DadosColeta")
            print(f"🔍 Seria deletado: {count_dc} registros de Auditoria (cascata)")
        
        # 2. Deletar CityManualData
        city_manual = session.query(CityManualData).filter(
            CityManualData.nome_cidade == "Apucarana"
        ).all()
        count_cm = len(city_manual)
        
        if confirmar:
            for cm in city_manual:
                session.delete(cm)
            session.commit()
            print(f"✅ Deletado: {count_cm} registros de CityManualData (Apucarana)")
        else:
            print(f"🔍 Seria deletado: {count_cm} registros de CityManualData")
        
        return {
            "dados_coleta_deletados": count_dc,
            "city_manual_deletados": count_cm,
        }
    
    finally:
        session.close()

def main():
    """Execução principal"""
    print("\n🧹 LIMPADOR DE DADOS FAKE - URBIX\n")
    
    # 1. Listar dados
    stats = listar_dados_apucarana()
    
    # 2. Perguntar confirmação
    print_section("3. CONFIRMAÇÃO")
    print(f"\nResumo do que será deletado:")
    print(f"  - DadosColeta (Apucarana): {stats['dados_coleta_count']} registros")
    print(f"  - CityManualData (Apucarana): {stats['city_manual_count']} registros")
    print(f"  - Auditorias associadas: ~{stats['dados_coleta_count']} registros")
    
    resposta = input("\n⚠️  Deseja prosseguir com a limpeza? (s/n): ").lower().strip()
    
    if resposta == 's':
        resultado = deletar_dados_apucarana(confirmar=True)
        
        print_section("✅ LIMPEZA CONCLUÍDA")
        print(f"\n  Deletado com sucesso:")
        print(f"  ✅ DadosColeta: {resultado['dados_coleta_deletados']} registros")
        print(f"  ✅ CityManualData: {resultado['city_manual_deletados']} registros")
        print(f"\n  Próximos passos:")
        print(f"  1. (Manual) Revisar e deletar indicadores antigos se necessário")
        print(f"  2. (Manual) Remover AdminPage.jsx do frontend")
        print(f"  3. (Manual) Remover DashboardPage.jsx do frontend")
        print(f"  4. (Manual) Revisar interpolação no topsis.py\n")
    else:
        print("\n❌ Limpeza cancelada. Nenhum dado foi alterado.\n")

if __name__ == "__main__":
    main()
