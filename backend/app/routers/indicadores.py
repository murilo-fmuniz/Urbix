from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app import models, schemas
from app.database import get_db
from app.utils import normalize_indicator_code, normalize_city_name, normalize_comparison_value


indicators_router = APIRouter(prefix="/indicadores", tags=["Indicadores"])


# ==========================================
# ROTAS DE CONSULTA (GET) - React/Frontend
# ==========================================

@indicators_router.get("/", response_model=List[schemas.IndicadorResponse])
def list_indicadores(
    cidade: Optional[str] = None,
    norma: Optional[str] = None,
    grande_area: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Listagem geral com filtros.
    
    Filtros suportados (case-insensitive):
    - ?cidade=Apucarana (ou "apucarana", "APUCARANA", etc)
    - ?norma=ISO 37122 (ou "iso 37122", "ISO37122", etc)
    - ?grande_area=Saúde (ou "saúde", "SAÚDE", etc)
    
    Retorna a árvore completa: Indicador → Metodologia → Coletas → Auditoria
    """
    query = db.query(models.Indicador).options(
        joinedload(models.Indicador.metodologia),
        joinedload(models.Indicador.dados_coleta).joinedload(models.DadosColeta.auditoria),
    )

    if norma:
        norma_normalized = normalize_comparison_value(norma)
        query = query.filter(models.Indicador.norma.ilike(f'%{norma_normalized}%'))
    
    if grande_area:
        grande_area_normalized = normalize_comparison_value(grande_area)
        query = query.filter(models.Indicador.grande_area.ilike(f'%{grande_area_normalized}%'))
    
    if cidade:
        cidade_normalized = normalize_city_name(cidade)
        query = query.join(models.DadosColeta).filter(
            models.DadosColeta.cidade.ilike(f'%{cidade_normalized}%')
        )

    results = query.all()
    return results


@indicators_router.get("/{codigo_indicador}", response_model=schemas.IndicadorResponse)
def get_indicador_detalhes(
    codigo_indicador: str,
    db: Session = Depends(get_db)
):
    """
    Retorna os detalhes completos de um indicador específico.
    
    Exemplo: GET /api/v1/indicadores/ECO.1 (ou "eco.1", "eco1", etc)
    
    Aceita qualquer formato de código (case-insensitive, com ou sem ponto, com ou sem acentos).
    Retorna a estrutura completa com metodologia, coletas de todas as cidades e auditoria.
    """
    # Normaliza o código do indicador para busca
    codigo_normalized = normalize_indicator_code(codigo_indicador)
    
    indicador = db.query(models.Indicador).options(
        joinedload(models.Indicador.metodologia),
        joinedload(models.Indicador.dados_coleta).joinedload(models.DadosColeta.auditoria),
    ).filter(models.Indicador.codigo_indicador.ilike(codigo_normalized)).first()

    if not indicador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicador com código '{codigo_indicador}' não encontrado"
        )

    return indicador


# ==========================================
# ROTAS DE INSERÇÃO E ATUALIZAÇÃO (Admin)
# ==========================================

@indicators_router.post("/", response_model=schemas.IndicadorResponse, status_code=status.HTTP_201_CREATED)
def create_indicador(
    payload: schemas.IndicadorCreate,
    db: Session = Depends(get_db)
):
    """
    Criar um indicador mestre com sua metodologia.
    
    Recebe a estrutura base (Indicador + Metodologia) e cria em banco.
    Dados de coleta podem ser adicionados depois via POST /indicadores/{codigo_indicador}/coletas
    
    O código é normalizado automaticamente (case-insensitive, com ou sem ponto, removendo acentos).
    """
    # Normaliza código para verificação
    codigo_normalized = normalize_indicator_code(payload.codigo_indicador)
    
    # Verifica se indicador já existe (case-insensitive)
    existing = db.query(models.Indicador).filter(
        models.Indicador.codigo_indicador.ilike(codigo_normalized)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Indicador com código '{payload.codigo_indicador}' já existe"
        )

    try:
        # Cria o Indicador mestre (normalização automática via event listener)
        indicador = models.Indicador(
            codigo_indicador=payload.codigo_indicador,
            nome=payload.nome,
            norma=payload.norma,
            grande_area=payload.grande_area,
            eixo=payload.eixo,
            tipo=payload.tipo,
            descricao=payload.descricao,
        )

        # Metodologia (opcional)
        if payload.metodologia:
            indicador.metodologia = models.Metodologia(**payload.metodologia.model_dump())

        # Dados de coleta (lista) - normalização automática via event listener
        for dc in payload.dados_coleta:
            dc_dict = dc.model_dump(exclude={"auditoria"})
            coleta = models.DadosColeta(**dc_dict)
            # Auditoria (opcional)
            if dc.auditoria:
                coleta.auditoria = models.Auditoria(**dc.auditoria.model_dump())
            indicador.dados_coleta.append(coleta)

        db.add(indicador)
        db.commit()
        db.refresh(indicador)
        return indicador

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar indicador. Verifique os dados enviados."
        )


@indicators_router.post("/{codigo_indicador}/coletas", response_model=schemas.DadosColetaResponse, status_code=status.HTTP_201_CREATED)
def criar_coleta(
    codigo_indicador: str,
    payload: schemas.DadosColetaCreate,
    db: Session = Depends(get_db)
):
    """
    Inserir dados de uma coleta para um indicador específico.
    
    Exemplo: POST /api/v1/indicadores/ECO.1/coletas (ou "eco.1", "eco1", etc)
    
    Payload: { cidade, estado, ano_referencia, valor_numerador, valor_denominador, valor_final, dado_disponivel, auditoria }
    
    Vital para adicionar dados de novas cidades (Maringá, Londrina, etc.) sem reenviar o indicador inteiro.
    Aceita qualquer formato de código e cidade (case-insensitive, removendo acentos de códigos).
    """
    # Normaliza código do indicador
    codigo_normalized = normalize_indicator_code(codigo_indicador)
    
    # Verifica se indicador existe (case-insensitive)
    indicador = db.query(models.Indicador).filter(
        models.Indicador.codigo_indicador.ilike(codigo_normalized)
    ).first()

    if not indicador:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Indicador com código '{codigo_indicador}' não encontrado"
        )

    try:
        # Cria a coleta (normalização automática via event listener)
        dc_dict = payload.model_dump(exclude={"auditoria"})
        coleta = models.DadosColeta(indicador_id=indicador.id, **dc_dict)

        # Auditoria (opcional)
        if payload.auditoria:
            coleta.auditoria = models.Auditoria(**payload.auditoria.model_dump())

        db.add(coleta)
        db.commit()
        db.refresh(coleta)
        return coleta

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao criar coleta. Verifique os dados enviados."
        )


@indicators_router.put("/coletas/{coleta_id}", response_model=schemas.DadosColetaResponse)
def atualizar_coleta(
    coleta_id: int,
    payload: schemas.DadosColetaCreate,
    db: Session = Depends(get_db)
):
    """
    Atualizar/corrigir dados de uma coleta específica.
    
    Exemplo: PUT /api/v1/indicadores/coletas/42
    
    Permite corrigir um dado específico (ex: taxa de desemprego atualizada) sem quebrar o resto.
    Aceita qualquer formato de cidade/estado - normalização automática (mantendo acentos em cidades).
    """
    # Verifica se coleta existe
    coleta = db.query(models.DadosColeta).filter(
        models.DadosColeta.id == coleta_id
    ).first()

    if not coleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Coleta com ID {coleta_id} não encontrada"
        )

    try:
        # Atualiza campos da coleta (normalização automática via event listener)
        for key, value in payload.model_dump(exclude={"auditoria"}).items():
            setattr(coleta, key, value)

        # Se auditoria for fornecida, atualiza ou cria
        if payload.auditoria:
            if coleta.auditoria:
                # Atualiza auditoria existente
                for key, value in payload.auditoria.model_dump().items():
                    setattr(coleta.auditoria, key, value)
            else:
                # Cria nova auditoria
                coleta.auditoria = models.Auditoria(**payload.auditoria.model_dump())

        db.commit()
        db.refresh(coleta)
        return coleta

    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar coleta. Verifique os dados enviados."
        )