import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Set
from sqlalchemy import and_, func, text


def _rebuild_snapshot_latest(db_session, cidades_ibge: List[str], ids_indicadores: Optional[Set[str]] = None) -> None:
    """Garante que o snapshot recente exista para o subconjunto de cidades/indicadores solicitado."""
    from app.models import ValorIndicador, ValorIndicadorLatest

    if not cidades_ibge:
        return

    query_latest = db_session.query(ValorIndicadorLatest).filter(ValorIndicadorLatest.codigo_ibge.in_(cidades_ibge))
    if ids_indicadores:
        query_latest = query_latest.filter(ValorIndicadorLatest.id_indicador.in_(list(ids_indicadores)))
    if query_latest.first():
        return

    query_base = db_session.query(ValorIndicador).filter(ValorIndicador.codigo_ibge.in_(cidades_ibge))
    if ids_indicadores:
        query_base = query_base.filter(ValorIndicador.id_indicador.in_(list(ids_indicadores)))

    # Limita o custo para o subset estritamente necessário antes de materializar o snapshot.
    registros = query_base.order_by(
        ValorIndicador.codigo_ibge.asc(),
        ValorIndicador.id_indicador.asc(),
        ValorIndicador.ano_referencia.desc(),
        ValorIndicador.id.desc(),
    ).limit(5000).all()

    if not registros:
        return

    # Remove apenas as entradas do subconjunto solicitado, evitando apagar snapshot inteiro da base.
    db_session.query(ValorIndicadorLatest).filter(ValorIndicadorLatest.codigo_ibge.in_(cidades_ibge)).delete(synchronize_session=False)

    melhor_por_chave: Dict[tuple[str, str], ValorIndicadorLatest] = {}
    for reg in registros:
        chave = (reg.codigo_ibge, reg.id_indicador)
        if chave in melhor_por_chave:
            continue
        melhor_por_chave[chave] = ValorIndicadorLatest(
            codigo_ibge=reg.codigo_ibge,
            id_indicador=reg.id_indicador,
            ano_referencia=reg.ano_referencia,
            valor=reg.valor,
            fonte=reg.fonte,
            id_origem=reg.id,
        )

    if melhor_por_chave:
        db_session.bulk_save_objects(list(melhor_por_chave.values()))
        db_session.commit()


def _buscar_valores_mais_recentes(
    db_session,
    cidades_ibge: List[str],
    ids_indicadores: Optional[Set[str]] = None,
):
    """Retorna apenas o registro mais recente por cidade + indicador com base em ano_referencia."""
    from app.models import ValorIndicador, ValorIndicadorLatest

    if not cidades_ibge:
        return []

    # Caminho rápido: snapshot materializado (1 linha por cidade+indicador)
    query_latest = db_session.query(ValorIndicadorLatest).filter(ValorIndicadorLatest.codigo_ibge.in_(cidades_ibge))
    if ids_indicadores:
        query_latest = query_latest.filter(ValorIndicadorLatest.id_indicador.in_(list(ids_indicadores)))

    registros_latest = query_latest.all()
    if registros_latest and not ids_indicadores:
        return registros_latest

    latest_por_chave: Dict[tuple[str, str], object] = {}
    if registros_latest:
        latest_por_chave = {
            (reg.codigo_ibge, reg.id_indicador): reg
            for reg in registros_latest
        }

        # Se o snapshot já cobre todos os pares pedidos, evita fallback na tabela fato.
        if ids_indicadores:
            cobertura_completa = True
            for cidade in cidades_ibge:
                presentes = {
                    ind
                    for (codigo, ind) in latest_por_chave.keys()
                    if codigo == cidade
                }
                if not ids_indicadores.issubset(presentes):
                    cobertura_completa = False
                    break
            if cobertura_completa:
                return list(latest_por_chave.values())

    # Fallback: reconstrução em tempo real a partir da tabela fato completa
    query_base = db_session.query(ValorIndicador).filter(ValorIndicador.codigo_ibge.in_(cidades_ibge))
    ids_para_fallback = ids_indicadores

    if ids_indicadores and latest_por_chave:
        faltantes_por_cidade: Set[str] = set()
        for cidade in cidades_ibge:
            presentes = {
                ind
                for (codigo, ind) in latest_por_chave.keys()
                if codigo == cidade
            }
            faltantes_por_cidade.update(ids_indicadores - presentes)
        ids_para_fallback = faltantes_por_cidade

    if ids_para_fallback:
        query_base = query_base.filter(ValorIndicador.id_indicador.in_(list(ids_para_fallback)))

    sub_ano = (
        query_base.with_entities(
            ValorIndicador.codigo_ibge.label("codigo_ibge"),
            ValorIndicador.id_indicador.label("id_indicador"),
            func.max(ValorIndicador.ano_referencia).label("ano_max"),
        )
        .group_by(ValorIndicador.codigo_ibge, ValorIndicador.id_indicador)
        .subquery()
    )

    sub_id = (
        query_base.with_entities(
            ValorIndicador.codigo_ibge.label("codigo_ibge"),
            ValorIndicador.id_indicador.label("id_indicador"),
            ValorIndicador.ano_referencia.label("ano_referencia"),
            func.max(ValorIndicador.id).label("id_max"),
        )
        .join(
            sub_ano,
            and_(
                ValorIndicador.codigo_ibge == sub_ano.c.codigo_ibge,
                ValorIndicador.id_indicador == sub_ano.c.id_indicador,
                ValorIndicador.ano_referencia == sub_ano.c.ano_max,
            ),
        )
        .group_by(
            ValorIndicador.codigo_ibge,
            ValorIndicador.id_indicador,
            ValorIndicador.ano_referencia,
        )
        .subquery()
    )

    registros_fallback = (
        db_session.query(ValorIndicador)
        .join(
            sub_id,
            and_(
                ValorIndicador.codigo_ibge == sub_id.c.codigo_ibge,
                ValorIndicador.id_indicador == sub_id.c.id_indicador,
                ValorIndicador.ano_referencia == sub_id.c.ano_referencia,
                ValorIndicador.id == sub_id.c.id_max,
            ),
        )
        .all()
    )

    if not latest_por_chave:
        return registros_fallback

    for reg in registros_fallback:
        chave = (reg.codigo_ibge, reg.id_indicador)
        if chave not in latest_por_chave:
            latest_por_chave[chave] = reg

    return list(latest_por_chave.values())


def _buscar_historico_por_cidade(db_session, codigo_ibge: str) -> Dict[str, List[dict]]:
    """Retorna a série histórica completa de valores para uma cidade, agrupada por indicador."""
    from app.models import ValorIndicador

    historico: Dict[str, List[dict]] = {}
    registros = (
        db_session.query(ValorIndicador)
        .filter(ValorIndicador.codigo_ibge == codigo_ibge)
        .order_by(ValorIndicador.id_indicador.asc(), ValorIndicador.ano_referencia.asc(), ValorIndicador.id.asc())
        .all()
    )

    for reg in registros:
        historico.setdefault(reg.id_indicador, []).append({
            "id": reg.id,
            "ano_referencia": reg.ano_referencia,
            "valor": reg.valor,
            "fonte": reg.fonte,
        })

    for indicador in historico:
        historico[indicador].sort(key=lambda item: (item["ano_referencia"], item["id"]))

    return historico


def _buscar_mais_recente_por_cidade(db_session, codigo_ibge: str) -> Dict[str, float]:
    """Retorna o valor mais recente por indicador para a cidade, conforme o critério do TOPSIS."""
    historico = _buscar_historico_por_cidade(db_session, codigo_ibge)
    mais_recente: Dict[str, float] = {}

    for id_indicador, series in historico.items():
        if series:
            mais_recente[id_indicador] = series[-1]["valor"]

    return mais_recente


def _indicadores_validos_para_topsis() -> List[str]:
    """Retorna somente indicadores com fonte real e status validado para uso no cálculo TOPSIS."""
    from app.etl_config import INDICADORES

    status_pendentes = {
        "pendente",
        "pendente_implementacao_api",
        "em_implementacao_api",
        "em_implementacao_api_siconfi",
        "incompleto",
        "nao_baixado",
        "nao_baixado_arquivo",
    }

    validos: List[str] = []
    for _, indicadores in INDICADORES.items():
        for id_ind, regras in indicadores.items():
            status = str(regras.get("status", "")).strip().lower()
            if status in status_pendentes:
                continue
            if any(token in status for token in ("pendente", "implementacao", "incompleto", "nao_baixado")):
                continue

            numerador = regras.get("numerador") or {}
            direta = regras.get("variavel_direta") or {}

            if numerador.get("arquivo") == "NÃO_BAIXADO":
                continue
            if direta.get("arquivo") == "NÃO_BAIXADO":
                continue

            validos.append(id_ind)

    return validos


def preparar_matriz_decisao(cidades_ibge: List[str], simulacoes: List[dict], db_session) -> pd.DataFrame:
    """
    Constrói a matriz de dados mesclando o Banco de Dados histórico com as Simulações do Frontend.
    Converte dados brutos em taxas proporcionais (numerador/denominador).
    """
    from app.models import ValorIndicador
    from app.etl_config import INDICADORES

    indicadores_validos = set(_indicadores_validos_para_topsis())

    # Limita o fetch SQL aos IDs realmente usados na matriz atual
    ids_necessarios: Set[str] = set()
    for _, indicadores in INDICADORES.items():
        for id_ind, regras in indicadores.items():
            if id_ind not in indicadores_validos:
                continue
            tipo = regras.get("tipo_calculo")
            if tipo == "direto":
                ids_necessarios.add(id_ind)
            else:
                ids_necessarios.add(f"{id_ind}_numerador")
                denominador_chave = regras.get("denominador")
                if denominador_chave:
                    ids_necessarios.add(denominador_chave)

    # 1. Busca apenas o registro mais recente por cidade + indicador (usa ano_referencia)
    registros = _buscar_valores_mais_recentes(db_session, cidades_ibge, ids_necessarios)

    # Organiza em um dicionário estruturado: dict[cidade][id_indicador] = valor
    dados_brutos = {cidade: {} for cidade in cidades_ibge}
    for reg in registros:
        dados_brutos[reg.codigo_ibge][reg.id_indicador] = reg.valor

    # 2. Aplica as Simulações do Frontend (Sobrescreve o banco temporariamente na RAM)
    if simulacoes:
        for sim in simulacoes:
            ibge = sim.get("codigo_ibge")
            if ibge in dados_brutos:
                for chave, valor_simulado in sim.get("valores_brutos", {}).items():
                    dados_brutos[ibge][chave] = float(valor_simulado)

    # 3. Constrói a Matriz Final calculando as frações (Taxas e Porcentagens)
    matriz_final = []

    for ibge in cidades_ibge:
        linha = {"codigo_ibge": ibge}

        for dominio, indicadores in INDICADORES.items():
            for id_ind, regras in indicadores.items():
                if id_ind not in indicadores_validos:
                    continue

                tipo = regras.get("tipo_calculo")

                if tipo == "direto":
                    valor = dados_brutos[ibge].get(id_ind)
                    linha[id_ind] = valor

                else: # "porcentagem" ou "taxa_100k"
                    numerador = dados_brutos[ibge].get(f"{id_ind}_numerador")
                    denominador_chave = regras.get("denominador")
                    denominador = dados_brutos[ibge].get(denominador_chave)
                    multiplicador = regras.get("multiplicador", 1)

                    if numerador is not None and denominador is not None and denominador > 0:
                        linha[id_ind] = (numerador / denominador) * multiplicador
                    else:
                        linha[id_ind] = None # Ausência de dados

        matriz_final.append(linha)

    df = pd.DataFrame(matriz_final).set_index("codigo_ibge")

    # Descarta colunas sem informação útil para a comparação atual.
    # Isso evita que indicadores faltantes sejam tratados como zeros reais e
    # reduz a carga computacional do TOPSIS para o subconjunto solicitado.
    colunas_uteis = []
    for col in df.columns:
        serie = df[col]
        valores_reais = serie.dropna()
        if valores_reais.empty:
            continue
        if (valores_reais == 0).all():
            continue
        if serie.isna().mean() > 0.5:
            continue
        colunas_uteis.append(col)

    return df[colunas_uteis]

def aplicar_topsis(df: pd.DataFrame, pesos: dict, impactos: dict) -> List[dict]:
    """
    Aplica o algoritmo TOPSIS matemático sobre a matriz preparada.
    Resolve dados ausentes rigorosamente sem inflar resultados.
    """
    if df.empty:
        return []

    df = df.dropna(axis=1, how="all").copy()
    if df.empty:
        return []

    # 1. Tratamento de Ausência de Dados (Null Handling Matemático)
    for col in list(df.columns):
        if df[col].isnull().all():
            df = df.drop(columns=[col])
            continue

        impacto = impactos.get(col, 1)

        # Se o indicador não tem informação útil para a comparação atual,
        # o melhor é removê-lo do cálculo; zeros artificiais não devem dominar a ordem.
        if df[col].notna().sum() <= 1:
            df = df.drop(columns=[col])
            continue

        if impacto == 1:
            pior_valor = 0.0
        else:
            pior_valor = df[col].max()

        df[col] = df[col].fillna(pior_valor)

    # 2. Normalização Vetorial (Divisão pela raiz da soma dos quadrados)
    norm_divisor = np.sqrt((df ** 2).sum(axis=0))
    # Evita divisão por zero
    norm_divisor = norm_divisor.replace(0, 1) 
    df_norm = df / norm_divisor

    # 3. Ponderação (Multiplicação pelos pesos)
    peso_series = pd.Series(pesos)
    df_pond = df_norm * peso_series

    # 4. Soluções Ideais Positiva (SIP) e Negativa (SIN)
    sip = pd.Series(index=df.columns, dtype=float)
    sin = pd.Series(index=df.columns, dtype=float)

    for col in df.columns:
        impacto = impactos.get(col, 1)
        if impacto == 1: # Benefício: maior é melhor
            sip[col] = df_pond[col].max()
            sin[col] = df_pond[col].min()
        else:            # Custo: menor é melhor
            sip[col] = df_pond[col].min()
            sin[col] = df_pond[col].max()

    # 5. Cálculo das Distâncias Euclidianas
    dist_positiva = np.sqrt(((df_pond - sip) ** 2).sum(axis=1))
    dist_negativa = np.sqrt(((df_pond - sin) ** 2).sum(axis=1))

    # 6. Coeficiente de Proximidade (Pontuação Final 0 a 1)
    soma_distancias = dist_positiva + dist_negativa
    # Evita divisão por zero se todas as cidades forem idênticas
    soma_distancias = soma_distancias.replace(0, 1)
    
    pontuacao = dist_negativa / soma_distancias

    # 7. Formatação da Resposta
    resultados = []
    for ibge in df.index:
        resultados.append({
            "codigo_ibge": ibge,
            "pontuacao_topsis": round(pontuacao[ibge], 4),
            "distancia_positiva": round(dist_positiva[ibge], 4),
            "distancia_negativa": round(dist_negativa[ibge], 4),
            "valores_calculados": df.loc[ibge].to_dict()
        })

    # Ordena do melhor (1.0) para o pior (0.0)
    resultados = sorted(resultados, key=lambda x: x["pontuacao_topsis"], reverse=True)
    return resultados