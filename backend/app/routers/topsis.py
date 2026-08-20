import unicodedata
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.schemas import TopsisSimulationRequest, TopsisRankingResponse
from app.services.topsis_core import (
    preparar_matriz_decisao,
    aplicar_topsis,
    _buscar_historico_por_cidade,
    _buscar_mais_recente_por_cidade,
)
from app.models import Municipio, Indicador, ValorIndicador

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/topsis", tags=["TOPSIS"])


def _normalizar_busca(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = texto.encode("ascii", "ignore").decode("ascii")
    return texto.strip().lower()


@router.get("/cidades")
def buscar_cidades(q: str = Query(default="", description="Texto para buscar cidade pelo nome ou código IBGE"), limit: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    """Busca cidades por nome ou código IBGE, útil para montar o filtro do frontend."""
    termo = _normalizar_busca(q)
    query = db.query(Municipio).order_by(Municipio.nome.asc()).yield_per(1000)
    cidades = []

    for cidade in query:
        if termo:
            if not (
                termo in _normalizar_busca(cidade.nome)
                or termo in _normalizar_busca(cidade.codigo_ibge)
                or termo in _normalizar_busca(cidade.estado)
            ):
                continue

        cidades.append(cidade)
        if len(cidades) >= limit:
            break

    return [{
        "codigo_ibge": cidade.codigo_ibge,
        "nome": cidade.nome,
        "estado": cidade.estado,
    } for cidade in cidades]


@router.get("/cidade/{codigo_ibge}/historico")
def historico_cidade_topsis(codigo_ibge: str, db: Session = Depends(get_db)):
    """Retorna a série histórica por indicador para uma cidade, incluindo o valor mais recente usado no cálculo TOPSIS."""
    cidade = db.query(Municipio).filter(Municipio.codigo_ibge == codigo_ibge).first()
    if not cidade:
        raise HTTPException(status_code=404, detail=f"Cidade {codigo_ibge} não encontrada.")

    historico = _buscar_historico_por_cidade(db, codigo_ibge)
    recente = _buscar_mais_recente_por_cidade(db, codigo_ibge)

    return {
        "codigo_ibge": cidade.codigo_ibge,
        "nome_cidade": cidade.nome,
        "estado": cidade.estado,
        "indicadores": historico,
        "valor_mais_recente_usado_no_calculo": recente,
    }


@router.post("/ranking-hibrido", response_model=List[TopsisRankingResponse])
def calcular_ranking_topsis(request: TopsisSimulationRequest, db: Session = Depends(get_db)):
    """
    Motor Central do Urbix.
    Gera o ranking TOPSIS buscando os dados reais do banco (Data Lake) e 
    mesclando em memória com qualquer simulação enviada pelo usuário (Frontend).
    Nenhum dado simulado é salvo no banco, preservando o histórico oficial.
    """
    if not request.cidades_ibge:
        raise HTTPException(status_code=400, detail="Nenhuma cidade selecionada para o cálculo.")

    # 1. Busca os nomes das cidades para a interface
    cidades = db.query(Municipio).filter(Municipio.codigo_ibge.in_(request.cidades_ibge)).all()
    cidades_encontradas = {c.codigo_ibge: c.nome for c in cidades}

    if not cidades_encontradas:
        # Fallback de segurança se a tabela de Municípios ainda não foi populada
        cidades_encontradas = {ibge: f"IBGE {ibge}" for ibge in request.cidades_ibge}

    # 2. Busca os Metadados dos Indicadores (Pesos e Impactos) do Banco
    indicadores_db = db.query(Indicador).all()
    pesos = {}
    impactos = {}

    if indicadores_db:
        for ind in indicadores_db:
            pesos[ind.id] = ind.peso
            impactos[ind.id] = ind.impacto

    # Converte os modelos Pydantic de simulação para dicionários Python
    simulacoes_dict = [sim.model_dump() for sim in request.simulacoes] if request.simulacoes else []

    # 3. Constroi a Matriz de Decisão
    try:
        df_matriz = preparar_matriz_decisao(request.cidades_ibge, simulacoes_dict, db)
    except Exception as e:
        logger.error(f"Erro ao preparar matriz: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao construir a matriz matemática.")

    if df_matriz.empty:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado para as cidades solicitadas.")

    # Se a matriz existe mas nenhum indicador foi encontrado para as cidades
    # solicitadas, o ranking não tem base matemática para ser calculado.
    if df_matriz.dropna(how="all").empty:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado para as cidades solicitadas.")

    # Fallback Dinâmico: Se a tabela Indicador estiver vazia, define regras lógicas
    for col in df_matriz.columns:
        if col not in pesos:
            pesos[col] = 0.02 # Peso igualitário padrão (1/50)
        if col not in impactos:
            # Se a palavra do indicador remeter a "custo/dano", o impacto é negativo (-1)
            termos_negativos = ["desemprego", "endividamento", "homicidios", "mortes", 
                                "inadequadas", "sem_teto", "acidentes", "corrupcao", 
                                "mortalidade", "afetadas", "perdas", "danos"]
            if any(termo in col for termo in termos_negativos):
                impactos[col] = -1
            else:
                impactos[col] = 1 # Maior é melhor

    # 4. Executa o Algoritmo TOPSIS
    try:
        resultados = aplicar_topsis(df_matriz, pesos, impactos)
    except Exception as e:
        logger.error(f"Erro no algoritmo TOPSIS: {e}")
        raise HTTPException(status_code=500, detail="Erro interno durante o cálculo matemático.")

    # 5. Formata e Devolve a Resposta
    resposta_final = []
    for res in resultados:
        res["nome_cidade"] = cidades_encontradas.get(res["codigo_ibge"], f"IBGE {res['codigo_ibge']}")
        resposta_final.append(TopsisRankingResponse(**res))

    return resposta_final