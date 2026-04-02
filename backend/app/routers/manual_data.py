"""
Router Manual Data - Endpoints para gerenciar dados manuais de cidades

Este módulo contém endpoints para:
- Criar/atualizar dados manuais de cidades
- Visualizar histórico de alterações (auditoria)
- Obter séries histórica de indicadores
- Obter série histórica de rankings
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CityManualData, CityManualDataHistory, IndicatorSnapshot, RankingSnapshot
from app.schemas import (
    CityManualDataCreate,
    CityManualDataUpdate,
    CityManualDataResponse,
    ManualDataHistoryResponse,
    IndicatorSnapshotResponse,
    RankingSnapshotResponse,
)

logger = logging.getLogger(__name__)

manual_data_router = APIRouter(prefix="/manual-data", tags=["Manual Data"])


# ==========================================
# DADOS MANUAIS - CRUD
# ==========================================

@manual_data_router.post("/{codigo_ibge}", response_model=CityManualDataResponse)
async def criar_ou_atualizar_dados_manuais(
    codigo_ibge: str,
    data: CityManualDataCreate,
    db: Session = Depends(get_db)
):
    """
    Cria ou atualiza dados manuais de uma cidade com suporte a 47 indicadores ISO.
    
    A estrutura agora suporta indicadores_manuais como JSON para flexibilidade:
    - 16 indicadores ISO 37120 (Sustentabilidade)
    - 15 indicadores ISO 37122 (Smart Cities)
    - 16 indicadores ISO 37123 + Sendai (Resiliência)
    
    Args:
        codigo_ibge: Código IBGE da cidade
        data: CityManualDataCreate com optional dados (ManualCityIndicators)
    
    Returns:
        CityManualDataResponse com dados salvos em JSON
    """
    try:
        # Converter indicadores para dicionário (se fornecido)
        indicadores_dict = data.dados.model_dump() if data.dados else {}
        
        # Buscar dados existentes
        existing = db.query(CityManualData).filter(
            CityManualData.codigo_ibge == codigo_ibge
        ).first()
        
        if existing:
            # ATUALIZAÇÃO: registrar histórico antes de mudar
            dados_antigos = existing.indicadores_manuais or {}
            dados_novos = indicadores_dict
            
            # Gerar resumo legível das alterações comparando os dicts
            alteracoes = []
            for key in set(list(dados_novos.keys()) + list(dados_antigos.keys())):
                valor_antigo = dados_antigos.get(key)
                valor_novo = dados_novos.get(key)
                if valor_antigo != valor_novo:
                    alteracoes.append(f"{key}: {valor_antigo} → {valor_novo}")
            
            # Criar registro de histórico somente se houver mudanças
            if alteracoes:
                history = CityManualDataHistory(
                    codigo_ibge=codigo_ibge,
                    dados_antigos=dados_antigos,
                    dados_novos=dados_novos,
                    alteracoes_resumo=" | ".join(alteracoes[:10]),  # Limitar a 10 mudanças no resumo
                    usuario_atualizou=data.usuario_atualizou,
                    motivo_atualizacao=None,
                )
                db.add(history)
                logger.info(f"✅ Histórico criado para {codigo_ibge}: {len(alteracoes)} campo(s) alterado(s)")
            
            # Atualizar indicadores_manuais JSON
            existing.indicadores_manuais = dados_novos
            existing.usuario_atualizou = data.usuario_atualizou
            
            if data.nome_cidade:
                existing.nome_cidade = data.nome_cidade
            
            db.commit()
            db.refresh(existing)
            logger.info(f"✅ Dados manuais atualizados para {codigo_ibge} (47 indicadores)")
            return existing
        
        else:
            # CRIAÇÃO: novo registro
            novo = CityManualData(
                codigo_ibge=codigo_ibge,
                nome_cidade=data.nome_cidade,
                indicadores_manuais=indicadores_dict,  # JSON com 47 indicadores
                usuario_atualizou=data.usuario_atualizou,
                fonte="prefeitura",
            )
            db.add(novo)
            db.commit()
            db.refresh(novo)
            logger.info(f"✅ Dados manuais criados para {codigo_ibge} (47 indicadores em JSON)")
            return novo
    
    except Exception as e:
        logger.error(f"❌ Erro ao criar/atualizar dados manuais: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar dados: {str(e)}")


@manual_data_router.get("/{codigo_ibge}", response_model=CityManualDataResponse)
async def obter_dados_manuais(
    codigo_ibge: str,
    db: Session = Depends(get_db)
):
    """
    Obtém dados manuais atuais de uma cidade.
    
    Args:
        codigo_ibge: Código IBGE da cidade
    
    Returns:
        CityManualDataResponse com dados atuais
    """
    dados = db.query(CityManualData).filter(
        CityManualData.codigo_ibge == codigo_ibge
    ).first()
    
    if not dados:
        raise HTTPException(
            status_code=404,
            detail=f"Dados manuais não encontrados para IBGE {codigo_ibge}"
        )
    
    return dados


@manual_data_router.patch("/{codigo_ibge}", response_model=CityManualDataResponse)
async def atualizar_dados_manuais(
    codigo_ibge: str,
    data: CityManualDataUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza parcialmente dados manuais de uma cidade (PATCH) com suporte a 47 indicadores.
    
    Apenas campos fornecidos em 'dados' (ManualCityIndicators) são atualizados dinamicamente.
    A atualização é feita no dicionário JSON de indicadores_manuais, mantendo outros campos.
    
    Args:
        codigo_ibge: Código IBGE da cidade
        data: CityManualDataUpdate com optional dados (ManualCityIndicators)
    
    Returns:
        CityManualDataResponse com dados atualizados
    """
    dados = db.query(CityManualData).filter(
        CityManualData.codigo_ibge == codigo_ibge
    ).first()
    
    if not dados:
        raise HTTPException(
            status_code=404,
            detail=f"Dados manuais não encontrados para IBGE {codigo_ibge}"
        )
    
    # Registrar histórico - guardar estado anterior
    dados_antigos = dados.indicadores_manuais or {}
    
    # Se 'dados' foi fornecido, atualizar apenas os campos que vieram nele
    if data.dados:
        # Converter ManualCityIndicators para dict
        novos_indicadores = data.dados.model_dump(exclude_unset=False)
        
        # Fazer merge: manter indicadores existentes + sobrescrever com novos
        dados_novos = {**dados_antigos, **novos_indicadores}
        
        # Atualizar o JSON na coluna indicadores_manuais
        dados.indicadores_manuais = dados_novos
        
        # Gerar resumo das alterações
        alteracoes = []
        for key in set(list(novos_indicadores.keys()) + list(dados_antigos.keys())):
            valor_antigo = dados_antigos.get(key)
            valor_novo = dados_novos.get(key)
            if valor_antigo != valor_novo:
                alteracoes.append(f"{key}: {valor_antigo} → {valor_novo}")
        
        # Salvar histórico
        if alteracoes:
            history = CityManualDataHistory(
                codigo_ibge=codigo_ibge,
                dados_antigos=dados_antigos,
                dados_novos=dados_novos,
                alteracoes_resumo=" | ".join(alteracoes[:10]),  # Limitar a 10 mudanças
                usuario_atualizou=data.usuario_atualizou,
                motivo_atualizacao=data.motivo_atualizacao,
            )
            db.add(history)
            logger.info(f"✅ Histórico PATCH criado para {codigo_ibge}: {len(alteracoes)} campo(s) alterado(s)")
    
    # Atualizar metadados (mesmo que 'dados' não tenha sido fornecido)
    if data.usuario_atualizou:
        dados.usuario_atualizou = data.usuario_atualizou
    
    db.commit()
    db.refresh(dados)
    logger.info(f"✅ Dados manuais atualizados via PATCH para {codigo_ibge}")
    
    return dados


# ==========================================
# HISTÓRICO - AUDITORIA
# ==========================================

@manual_data_router.get("/{codigo_ibge}/history", response_model=List[ManualDataHistoryResponse])
async def obter_historico_alteracoes(
    codigo_ibge: str,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Obtém histórico completo de alterações dos dados manuais (auditoria).
    
    Args:
        codigo_ibge: Código IBGE da cidade
        limit: Número máximo de registros (padrão 50)
    
    Returns:
        Lista de ManualDataHistoryResponse ordenada por data descendente
    """
    historico = db.query(CityManualDataHistory).filter(
        CityManualDataHistory.codigo_ibge == codigo_ibge
    ).order_by(CityManualDataHistory.data_alteracao.desc()).limit(limit).all()
    
    return historico


# ==========================================
# SÉRIE HISTÓRICA - INDICADORES
# ==========================================

@manual_data_router.get("/{codigo_ibge}/indicadores/historico", response_model=List[IndicatorSnapshotResponse])
async def obter_historico_indicadores(
    codigo_ibge: str,
    limit: int = Query(52, ge=1, le=500),  # 52 = ~1 ano de dados semanais
    db: Session = Depends(get_db)
):
    """
    Obtém série histórica dos indicadores calculados de uma cidade.
    Útil para análise de evolução temporal.
    
    Args:
        codigo_ibge: Código IBGE da cidade
        limit: Número máximo de snapshots (padrão 52 = ~1 ano)
    
    Returns:
        Lista de IndicatorSnapshotResponse ordenada por data descendente
    """
    snapshots = db.query(IndicatorSnapshot).filter(
        IndicatorSnapshot.codigo_ibge == codigo_ibge
    ).order_by(IndicatorSnapshot.data_calculo.desc()).limit(limit).all()
    
    if not snapshots:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum histórico de indicadores encontrado para IBGE {codigo_ibge}"
        )
    
    return snapshots


# ==========================================
# SÉRIE HISTÓRICA - RANKINGS
# ==========================================

@manual_data_router.get("/rankings/historico", response_model=List[RankingSnapshotResponse])
async def obter_historico_rankings(
    limit: int = Query(24, ge=1, le=500),  # 24 = ~2 anos de dados mensais
    db: Session = Depends(get_db)
):
    """
    Obtém série histórica dos rankings TOPSIS calculados.
    Permite análise de evolução das cidades ao longo do tempo.
    
    Args:
        limit: Número máximo de snapshots (padrão 24 = ~2 anos)
    
    Returns:
        Lista de RankingSnapshotResponse ordenada por data descendente
    """
    snapshots = db.query(RankingSnapshot).order_by(
        RankingSnapshot.data_calculo.desc()
    ).limit(limit).all()
    
    if not snapshots:
        raise HTTPException(
            status_code=404,
            detail="Nenhum histórico de rankings encontrado"
        )
    
    return snapshots


@manual_data_router.get("/rankings/periodo/{periodo_referencia}", response_model=RankingSnapshotResponse)
async def obter_ranking_por_periodo(
    periodo_referencia: str,
    db: Session = Depends(get_db)
):
    """
    Obtém ranking de um período específico (ex: "2025-03").
    
    Args:
        periodo_referencia: Período em formato YYYY-MM
    
    Returns:
        RankingSnapshotResponse do período especificado
    """
    snapshot = db.query(RankingSnapshot).filter(
        RankingSnapshot.periodo_referencia == periodo_referencia
    ).first()
    
    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum ranking encontrado para período {periodo_referencia}"
        )
    
    return snapshot
