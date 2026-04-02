#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
🔄 SINCRONIZAÇÃO AUTÔNOMA DE APIs GOVERNAMENTAIS

Script de sincronização que executa periodicamente para:
1. Consultar APIs governamentais (SICONFI, IBGE, DataSUS)
2. Calcular indicadores ISO 37120 (receita_propria_pct, despesas_capital_pct, orcamento_per_capita)
3. Salvar dados frescos no banco de dados (CityManualData)
4. Implementar fallback inteligente em caso de falhas

CIDADES PADRÃO:
- Apucarana (4101408) - PR
- Londrina (4113700) - PR
- Maringá (4115200) - PR

USO:
    python sync_gov_apis.py                   # Sincroniza cidades padrão
    python sync_gov_apis.py --codigos 4101408 4113700  # Sincroniza cidades específicas
    python sync_gov_apis.py --cron            # Modo cron (sem confirmação)

AGENDAMENTO (Linux/Mac):
    # A cada 24 horas, às 02:00 da manhã
    0 2 * * * cd /caminho/urbix && python backend/sync_gov_apis.py --cron

IMPORTANTE:
- Timeout de 10s por API (fail-fast) - usa fallback se lento
- Intervalo de 2s entre cidades (respeita rate limits)
- Cache em memória evita requisições redundantes
- Auditoria completa em CityManualDataHistory
"""

import asyncio
import logging
import argparse
import sys
import tempfile
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

# Configurar path para importar módulos da app
sys.path.insert(0, '/'.join(__file__.split('/')[:-1]))

from app.database import SessionLocal
from app.models import CityManualData, CityManualDataHistory
from app.schemas import ManualCityIndicators, ISO37120Indicators
from app.services.external_apis import (
    get_siconfi_finances,
    get_ibge_population,
    get_datasus_health_infrastructure,
    FALLBACK_SICONFI,
    FALLBACK_IBGE,
    FALLBACK_DATASUS,
)

# ==========================================
# CONFIGURAÇÃO DE LOGGING
# ==========================================

# ✅ Cross-platform: usa temp dir apropriado para Windows/Linux/Mac
LOG_DIR = tempfile.gettempdir()
LOG_FILE = os.path.join(LOG_DIR, 'urbix_sync_gov_apis.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"📝 Log file: {LOG_FILE}")

# ==========================================
# CIDADES PADRÃO PARA SINCRONIZAÇÃO
# ==========================================

CIDADES_PADRAO = [
    {"codigo_ibge": "4101408", "nome_cidade": "Apucarana"},
    {"codigo_ibge": "4113700", "nome_cidade": "Londrina"},
    {"codigo_ibge": "4115200", "nome_cidade": "Maringá"},
]

# ==========================================
# CONFIGURAÇÕES
# ==========================================

# Intervalo entre requisições (em segundos) - respeita rate limits das APIs
INTERVALO_ENTRE_CIDADES = 2.0

# Timeout para cada chamada de API (em segundos)
TIMEOUT_API = 10.0


# ==========================================
# FUNÇÕES DE SINCRONIZAÇÃO
# ==========================================

async def sincronizar_cidade(
    codigo_ibge: str,
    nome_cidade: str,
    db_session
) -> bool:
    """
    Sincroniza dados de uma única cidade do governo para o banco de dados local.
    
    Processo:
    1. Chama APIs (SICONFI, IBGE, DataSUS) em paralelo com timeout
    2. Calcula os 3 indicadores ISO 37120 (receita_propria_pct, despesas_capital_pct, orcamento_per_capita)
    3. Gera dict completo com 47 indicadores
    4. Salva/atualiza registro em CityManualData
    5. Registra auditoria em CityManualDataHistory
    
    Args:
        codigo_ibge: Código IBGE da cidade (ex: "4101408")
        nome_cidade: Nome da cidade (ex: "Apucarana")
        db_session: Sessão SQLAlchemy para banco de dados
    
    Returns:
        bool: True se sincronização bem-sucedida, False caso contrário
    
    Raises:
        Exception: Erros críticos
    
    Example:
        >>> db = SessionLocal()
        >>> sucesso = await sincronizar_cidade("4101408", "Apucarana", db)
        >>> print(f"Sincronização: {'✅ Sucesso' if sucesso else '❌ Falho'}")
    """
    try:
        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 SINCRONIZANDO: {nome_cidade} ({codigo_ibge})")
        logger.info(f"{'='*80}")
        
        # ===================================================================
        # 📡 CHAMAR APIs EXTERNAS EM PARALELO
        # ===================================================================
        logger.info(f"📡 Buscando dados em APIs governamentais (timeout: {TIMEOUT_API}s cada)...")
        
        try:
            # Chamar APIs em paralelo usando asyncio.gather
            siconfi_data, populacao, num_hospitais = await asyncio.gather(
                asyncio.wait_for(get_siconfi_finances(codigo_ibge), timeout=TIMEOUT_API),
                asyncio.wait_for(get_ibge_population(codigo_ibge), timeout=TIMEOUT_API),
                asyncio.wait_for(get_datasus_health_infrastructure(codigo_ibge), timeout=TIMEOUT_API),
                return_exceptions=True
            )
            
            # Verificar se alguma chamada retornou Exception (timeout ou erro)
            if isinstance(siconfi_data, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO SICONFI: {type(siconfi_data).__name__}")
                # Usar fallback quando timeout
                siconfi_data = FALLBACK_SICONFI.get(codigo_ibge, {})
                logger.info(f"   🔄 Usando FALLBACK SICONFI para {nome_cidade}")
            else:
                logger.info(f"   ✅ SICONFI: Dados recebidos")
            
            if isinstance(populacao, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO IBGE: {type(populacao).__name__}")
                # Usar fallback quando timeout
                populacao = FALLBACK_IBGE.get(codigo_ibge, 100000)
                logger.info(f"   🔄 Usando FALLBACK IBGE para {nome_cidade}")
            else:
                logger.info(f"   ✅ IBGE: População = {populacao}")
            
            if isinstance(num_hospitais, Exception):
                logger.warning(f"   ⏱️  TIMEOUT/ERRO DATASUS: {type(num_hospitais).__name__}")
                # Usar fallback quando timeout
                num_hospitais = FALLBACK_DATASUS.get(codigo_ibge, 0)
                logger.info(f"   🔄 Usando FALLBACK DATASUS para {nome_cidade}")
            else:
                logger.info(f"   ✅ DataSUS: Hospitais = {num_hospitais}")
        
        except Exception as e:
            logger.error(f"   ❌ ERRO ao chamar APIs: {str(e)}")
            return False
        
        # Normalizar dados - agora as funções retornam dicts com a chave "fonte"
        siconfi_data = siconfi_data or {}
        
        # Extrair valor de populacao do dict retornado por get_ibge_population()
        # Novo formato: {"populacao": float, "fonte": "ibge"|"fallback"|"fallback_error"}
        if isinstance(populacao, dict) and "populacao" in populacao:
            populacao = float(populacao["populacao"]) if populacao["populacao"] > 0 else 100000
        elif isinstance(populacao, (int, float)):
            populacao = float(populacao) if populacao > 0 else 100000
        else:
            populacao = 100000
        
        # Extrair valor de num_hospitais do dict retornado por get_datasus_health_infrastructure()
        # Novo formato: {"num_hospitais": int, "fonte": "datasus"|"fallback"|"fallback_error"}
        if isinstance(num_hospitais, dict) and "num_hospitais" in num_hospitais:
            num_hospitais = int(num_hospitais["num_hospitais"]) if num_hospitais["num_hospitais"] > 0 else 0
        elif isinstance(num_hospitais, int):
            num_hospitais = int(num_hospitais) if num_hospitais > 0 else 0
        else:
            num_hospitais = 0
        
        # ===================================================================
        # 📊 CALCULAR INDICADORES ISO 37120
        # ===================================================================
        logger.info(f"\n📊 Calculando indicadores ISO 37120...")
        
        # Extrair valores do SICONFI
        receita_propria = siconfi_data.get("receita_propria", 0) or 0
        despesas_capital = siconfi_data.get("despesas_capital", 0) or 0
        receita_total = siconfi_data.get("receita_total", 0) or 1  # Evitar divisão por zero
        
        # Calcular percentuais
        receita_propria_pct = (receita_propria / receita_total * 100) if receita_total > 0 else 0.0
        despesas_capital_pct = (despesas_capital / receita_total * 100) if receita_total > 0 else 0.0
        orcamento_per_capita = (receita_total / populacao) if populacao > 0 else 0.0
        
        logger.info(f"   ✅ Taxa de Receita Própria: {receita_propria_pct:.2f}%")
        logger.info(f"   ✅ Taxa de Despesas de Capital: {despesas_capital_pct:.2f}%")
        logger.info(f"   ✅ Orçamento per capita: R$ {orcamento_per_capita:.2f}")
        
        # ===================================================================
        # 🔧 GERAR DICT COM 47 INDICADORES
        # ===================================================================
        logger.info(f"\n🔧 Gerando dicionário com 47 indicadores...")
        
        # Criar schema com defaults
        manual_indicators = ManualCityIndicators()
        
        # Sobrescrever apenas os valores calculados (os 3 indicadores)
        manual_indicators.iso_37120.receita_propria_pct = receita_propria_pct
        manual_indicators.iso_37120.despesas_capital_pct = despesas_capital_pct
        manual_indicators.iso_37120.orcamento_per_capita = orcamento_per_capita
        
        # Converter para dict para salvar no JSON da coluna
        indicadores_dict = manual_indicators.model_dump()
        
        logger.info(f"   ✅ 47 indicadores gerados (ISO 37120: 16 + ISO 37122: 15 + ISO 37123: 16)")
        logger.info(f"   📋 Estrutura: iso_37120, iso_37122, iso_37123")
        
        # ===================================================================
        # 💾 SALVAR/ATUALIZAR NO BANCO DE DADOS
        # ===================================================================
        logger.info(f"\n💾 Salvando dados no banco de dados...")
        
        # Buscar registro existente
        cidade_existente = db_session.query(CityManualData).filter_by(
            codigo_ibge=codigo_ibge
        ).first()
        
        if cidade_existente:
            # ===== ATUALIZAR REGISTRO EXISTENTE =====
            logger.info(f"   🔄 Atualizando registro existente...")
            
            # Capturar dados antigos para auditoria
            dados_antigos = cidade_existente.indicadores_manuais or {}
            dados_novos = indicadores_dict
            
            # Atualizar o registro
            cidade_existente.indicadores_manuais = dados_novos
            cidade_existente.usuario_atualizou = "sync_gov_apis_v1"
            cidade_existente.data_atualizacao = datetime.utcnow()
            
            # Registrar auditoria
            alteracoes = []
            if dados_antigos.get("iso_37120", {}).get("receita_propria_pct", 0) != receita_propria_pct:
                alteracoes.append(f"receita_propria_pct: {dados_antigos.get('iso_37120', {}).get('receita_propria_pct', 0):.2f}% → {receita_propria_pct:.2f}%")
            if dados_antigos.get("iso_37120", {}).get("despesas_capital_pct", 0) != despesas_capital_pct:
                alteracoes.append(f"despesas_capital_pct: {dados_antigos.get('iso_37120', {}).get('despesas_capital_pct', 0):.2f}% → {despesas_capital_pct:.2f}%")
            if dados_antigos.get("iso_37120", {}).get("orcamento_per_capita", 0) != orcamento_per_capita:
                alteracoes.append(f"orcamento_per_capita: R$ {dados_antigos.get('iso_37120', {}).get('orcamento_per_capita', 0):.2f} → R$ {orcamento_per_capita:.2f}")
            
            historico = CityManualDataHistory(
                codigo_ibge=codigo_ibge,
                dados_antigos=dados_antigos,
                dados_novos=dados_novos,
                alteracoes_resumo=" | ".join(alteracoes) if alteracoes else "Sincronização rotineira (sem mudanças)",
                usuario_atualizou="sync_gov_apis_v1",
                motivo_atualizacao="Sincronização automática de APIs governamentais (SICONFI, IBGE, DataSUS)",
                data_alteracao=datetime.utcnow()
            )
            
            db_session.add(historico)
            logger.info(f"   ✅ Histórico registrado: {len(alteracoes)} mudança(s)")
            
        else:
            # ===== CRIAR NOVO REGISTRO =====
            logger.info(f"   ✨ Criando novo registro...")
            
            nova_cidade = CityManualData(
                codigo_ibge=codigo_ibge,
                nome_cidade=nome_cidade,
                indicadores_manuais=indicadores_dict,
                fonte="apis_governamentais",
                usuario_atualizou="sync_gov_apis_v1",
                data_criacao=datetime.utcnow(),
                data_atualizacao=datetime.utcnow()
            )
            
            db_session.add(nova_cidade)
            
            # Registrar primeiro histórico
            historico = CityManualDataHistory(
                codigo_ibge=codigo_ibge,
                dados_antigos={},
                dados_novos=indicadores_dict,
                alteracoes_resumo=f"Criação inicial via sincronização: receita_propria_pct={receita_propria_pct:.2f}% | despesas_capital_pct={despesas_capital_pct:.2f}% | orcamento_per_capita=R${orcamento_per_capita:.2f}",
                usuario_atualizou="sync_gov_apis_v1",
                motivo_atualizacao="Sincronização automática inicial de APIs governamentais",
                data_alteracao=datetime.utcnow()
            )
            
            db_session.add(historico)
            logger.info(f"   ✅ Novo registro criado")
        
        # Salvar no banco
        db_session.commit()
        logger.info(f"   ✅ Banco de dados sincronizado")
        
        logger.info(f"\n✅ {nome_cidade} sincronizada com SUCESSO")
        return True
    
    except Exception as e:
        logger.error(f"❌ ERRO ao sincronizar {nome_cidade}: {str(e)}", exc_info=True)
        db_session.rollback()
        return False


async def sincronizar_lote_cidades(cidades: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Sincroniza um lote de cidades sequencialmente com intervalo entre elas.
    
    Respeita rate limits das APIs governamentais.
    
    Args:
        cidades: Lista de dicts com 'codigo_ibge' e 'nome_cidade'
    
    Returns:
        Dict com estatísticas de sincronização
        {
            "total": 3,
            "sucesso": 2,
            "falha": 1,
            "taxa_sucesso": 66.67,
            "tempo_total": 15.42,
            "detalhes": [...]
        }
    """
    db_session = SessionLocal()
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# SYNCRONIZAÇÃO DE LOTE: {len(cidades)} cidade(s)")
    logger.info(f"# Intervalo entre cidades: {INTERVALO_ENTRE_CIDADES}s")
    logger.info(f"# Timeout por API: {TIMEOUT_API}s")
    logger.info(f"{'#'*80}\n")
    
    resultado_geral = {
        "total": len(cidades),
        "sucesso": 0,
        "falha": 0,
        "detalhes": []
    }
    
    tempo_inicio = asyncio.get_event_loop().time()
    
    for idx, cidade in enumerate(cidades, 1):
        codigo_ibge = cidade.get("codigo_ibge")
        nome_cidade = cidade.get("nome_cidade")
        
        logger.info(f"\n[{idx}/{len(cidades)}] Processando {nome_cidade}...")
        
        sucesso = await sincronizar_cidade(codigo_ibge, nome_cidade, db_session)
        
        if sucesso:
            resultado_geral["sucesso"] += 1
            resultado_geral["detalhes"].append({
                "cidade": nome_cidade,
                "codigo_ibge": codigo_ibge,
                "status": "✅ SUCESSO"
            })
        else:
            resultado_geral["falha"] += 1
            resultado_geral["detalhes"].append({
                "cidade": nome_cidade,
                "codigo_ibge": codigo_ibge,
                "status": "❌ FALHA"
            })
        
        # Aguardar intervalo antes de próxima cidade (menos na última)
        if idx < len(cidades):
            logger.info(f"⏰ Aguardando {INTERVALO_ENTRE_CIDADES}s antes da próxima cidade...")
            await asyncio.sleep(INTERVALO_ENTRE_CIDADES)
    
    db_session.close()
    
    tempo_total = asyncio.get_event_loop().time() - tempo_inicio
    taxa_sucesso = (resultado_geral["sucesso"] / resultado_geral["total"] * 100) if resultado_geral["total"] > 0 else 0
    
    resultado_geral["tempo_total"] = tempo_total
    resultado_geral["taxa_sucesso"] = taxa_sucesso
    
    return resultado_geral


# ==========================================
# CLI E FUNÇÃO PRINCIPAL
# ==========================================

def main():
    """Função principal - parse de argumentos e execução"""
    
    parser = argparse.ArgumentParser(
        description="Sincronizar dados de APIs governamentais para banco de dados local"
    )
    
    parser.add_argument(
        "--codigos",
        nargs="+",
        type=str,
        help="Códigos IBGE específicos para sincronizar (ex: 4101408 4113700)"
    )
    
    parser.add_argument(
        "--cron",
        action="store_true",
        help="Modo cron (sem confirmação, saída concisa)"
    )
    
    args = parser.parse_args()
    
    # Determinar cidades a sincronizar
    if args.codigos:
        cidades_para_sincronizar = [
            {"codigo_ibge": codigo, "nome_cidade": f"Código {codigo}"}
            for codigo in args.codigos
        ]
        logger.info(f"🎯 Sincronizando cidades específicas: {', '.join(args.codigos)}")
    else:
        cidades_para_sincronizar = CIDADES_PADRAO
        logger.info(f"🎯 Sincronizando cidades padrão: {', '.join([c['nome_cidade'] for c in CIDADES_PADRAO])}")
    
    if not args.cron:
        logger.info(f"\n⚠️  AVISO: Este script fará requisições às seguintes APIs:")
        logger.info(f"   • SICONFI (Tesouro Nacional) - Dados Financeiros")
        logger.info(f"   • IBGE - SIDRA (População)")
        logger.info(f"   • DataSUS - CNES (Infraestrutura de Saúde)")
        logger.info(f"\n   Cidades: {', '.join([c['nome_cidade'] for c in cidades_para_sincronizar])}")
        logger.info(f"   Timeout por API: {TIMEOUT_API}s")
        logger.info(f"   Intervalo entre cidades: {INTERVALO_ENTRE_CIDADES}s")
        
        confirmacao = input("\n❓ Deseja continuar? (s/n): ").lower().strip()
        if confirmacao != "s":
            logger.info("❌ Operação cancelada pelo usuário")
            return 1
    
    # Executar sincronização
    try:
        logger.info(f"\n🚀 Iniciando sincronização...")
        
        resultado = asyncio.run(sincronizar_lote_cidades(cidades_para_sincronizar))
        
        # Exibir resumo
        logger.info(f"\n{'='*80}")
        logger.info(f"📊 RESUMO DA SINCRONIZAÇÃO")
        logger.info(f"{'='*80}")
        logger.info(f"Total de cidades: {resultado['total']}")
        logger.info(f"✅ Sucesso: {resultado['sucesso']}")
        logger.info(f"❌ Falha: {resultado['falha']}")
        logger.info(f"📈 Taxa de sucesso: {resultado['taxa_sucesso']:.1f}%")
        logger.info(f"⏱️  Tempo total: {resultado['tempo_total']:.2f}s")
        
        logger.info(f"\n📋 DETALHES:")
        for detalhe in resultado['detalhes']:
            logger.info(f"   {detalhe['status']} - {detalhe['cidade']} ({detalhe['codigo_ibge']})")
        
        logger.info(f"\n{'='*80}\n")
        
        # Retornar status apropriado
        return 0 if resultado['falha'] == 0 else 1
    
    except Exception as e:
        logger.error(f"❌ ERRO CRÍTICO: {str(e)}", exc_info=True)
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
