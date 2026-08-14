"""
Serviço de Cálculo TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)

Este módulo implementa o algoritmo TOPSIS para calcular um Índice de Maturidade Smart
combinando múltiplos indicadores de Smart Cities.

Referência: HWANG, C. L.; YOON, K. Methods for Multiple Attribute Decision Making.
In: Multiple Attribute Decision Making. Springer, Berlin, Heidelberg, 1981.
"""

import numpy as np
from typing import List, Dict, Tuple
from app.schemas import TOPSISInput, TOPSISResult, CitySmartIndex


def _normalize_decision_matrix(decision_matrix: np.ndarray) -> np.ndarray:
    """
    Normaliza a matriz de decisão usando normalização vetorial.
    
    Fórmula:
    r_ij = a_ij / sqrt(sum(a_ij^2)) para cada coluna j
    
    Args:
        decision_matrix: Matriz numpy de decisão (cidades x critérios)
    
    Returns:
        np.ndarray: Matriz normalizada
    """
    # Calcular a raiz quadrada da soma dos quadrados para cada coluna
    column_sums_squared = np.sqrt(np.sum(decision_matrix ** 2, axis=0))
    
    # Evitar divisão por zero
    column_sums_squared[column_sums_squared == 0] = 1
    
    # Normalizar cada coluna
    normalized_matrix = decision_matrix / column_sums_squared
    
    return normalized_matrix


def _apply_weights(normalized_matrix: np.ndarray, weights: np.ndarray) -> np.ndarray:
    """
    Aplica os pesos à matriz normalizada.
    
    Fórmula:
    v_ij = w_j * r_ij
    
    Args:
        normalized_matrix: Matriz normalizada
        weights: Vetor de pesos para cada critério
    
    Returns:
        np.ndarray: Matriz ponderada
    """
    weighted_matrix = normalized_matrix * weights
    return weighted_matrix


def _calculate_ideal_solutions(
    weighted_matrix: np.ndarray,
    impacts: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula as soluções ideal positiva (PIS) e ideal negativa (NIS).
    
    Para critérios de benefício (impacto = 1):
        - PIS = máximo valor
        - NIS = mínimo valor
    
    Para critérios de custo (impacto = -1):
        - PIS = mínimo valor
        - NIS = máximo valor
    
    Args:
        weighted_matrix: Matriz ponderada
        impacts: Vetor de impactos (1 para benefício, -1 para custo)
    
    Returns:
        Tuple[np.ndarray, np.ndarray]: (solução ideal positiva, solução ideal negativa)
    """
    n_criteria = weighted_matrix.shape[1]
    
    ideal_positive = np.zeros(n_criteria)
    ideal_negative = np.zeros(n_criteria)
    
    for j in range(n_criteria):
        column = weighted_matrix[:, j]
        
        if impacts[j] == 1:  # Critério de benefício
            ideal_positive[j] = np.max(column)
            ideal_negative[j] = np.min(column)
        else:  # Critério de custo (impacto = -1)
            ideal_positive[j] = np.min(column)
            ideal_negative[j] = np.max(column)
    
    return ideal_positive, ideal_negative


def _calculate_euclidean_distances(
    weighted_matrix: np.ndarray,
    ideal_positive: np.ndarray,
    ideal_negative: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcula as distâncias euclidianas de cada alternativa para
    as soluções ideal positiva e ideal negativa.
    
    Fórmula:
    S_i+ = sqrt(sum((v_ij - v_j+)^2))
    S_i- = sqrt(sum((v_ij - v_j-)^2))
    
    Args:
        weighted_matrix: Matriz ponderada (cidades x critérios)
        ideal_positive: Solução ideal positiva
        ideal_negative: Solução ideal negativa
    
    Returns:
        Tuple[np.ndarray, np.ndarray]: (distâncias para PIS, distâncias para NIS)
    """
    distance_to_positive = np.sqrt(
        np.sum((weighted_matrix - ideal_positive) ** 2, axis=1)
    )
    distance_to_negative = np.sqrt(
        np.sum((weighted_matrix - ideal_negative) ** 2, axis=1)
    )
    
    return distance_to_positive, distance_to_negative


def _calculate_similarity_coefficient(
    distance_to_negative: np.ndarray,
    distance_to_positive: np.ndarray
) -> np.ndarray:
    """
    Calcula o coeficiente de similaridade com a solução ideal.
    
    Fórmula:
    C_i = S_i- / (S_i+ + S_i-)
    
    onde:
    - C_i é o Índice Smart (varia de 0 a 1)
    - S_i- é a distância para a solução ideal negativa
    - S_i+ é a distância para a solução ideal positiva
    
    Args:
        distance_to_negative: Distâncias para a solução ideal negativa
        distance_to_positive: Distâncias para a solução ideal positiva
    
    Returns:
        np.ndarray: Coeficiente de similaridade (Índice Smart) para cada cidade
    """
    # EARLY RETURN: Proteção contra divisão por zero quando dados são idênticos
    denominator = distance_to_positive + distance_to_negative
    
    # Cria array de resultado inicializado com zeros
    similarity = np.zeros_like(denominator, dtype=float)
    
    # Calcula similaridade apenas onde denominador != 0
    valid_indices = denominator > 0
    if np.any(valid_indices):
        similarity[valid_indices] = distance_to_negative[valid_indices] / denominator[valid_indices]
    
    return similarity


def calculate_topsis(topsis_input: TOPSISInput) -> TOPSISResult:
    """
    Executa o cálculo completo do TOPSIS e retorna o ranking de cidades.
    
    Este é o ponto de entrada principal do algoritmo TOPSIS.
    Segue os seguintes passos:
    1. Normalização da matriz de decisão
    2. Ponderação pelos pesos
    3. Cálculo das soluções ideal e anti-ideal
    4. Cálculo das distâncias euclidianas
    5. Cálculo do índice smart (coeficiente de similaridade)
    6. Ranking das cidades
    
    ⚠️  IMPORTANTE: TOPSIS requer MÍNIMO 2 alternativas (cidades) para ser válido.
    Com apenas 1 cidade, não há comparação possível e o método perde sentido conceitual.
    
    Args:
        topsis_input: Objeto TOPSISInput contendo:
            - cidades: Lista de nomes de cidades (MÍNIMO 2)
            - indicadores_nomes: Lista de nomes dos indicadores
            - matriz_decisao: Matriz de decisão (cidades x indicadores)
            - pesos: Pesos para cada indicador
            - impactos: Impactos de cada indicador (1 ou -1)
    
    Returns:
        TOPSISResult: Resultado com ranking ordenado e detalhes do cálculo
    
    Raises:
        ValueError: Se os dados de entrada forem inválidos ou < 2 cidades
    """
    # ===== VALIDAÇÃO DE NÚMERO MÍNIMO DE CIDADES =====
    if len(topsis_input.cidades) < 2:
        raise ValueError(
            f"TOPSIS requer MÍNIMO 2 alternativas (cidades) para comparação. "
            f"Recebido: {len(topsis_input.cidades)} cidade(s). "
            f"Com apenas 1 cidade, não há base matemática para o algoritmo TOPSIS."
        )
    
    # Validar entrada
    if len(topsis_input.pesos) != len(topsis_input.matriz_decisao[0]):
        raise ValueError(
            "Número de pesos deve corresponder ao número de indicadores"
        )
    
    if len(topsis_input.impactos) != len(topsis_input.matriz_decisao[0]):
        raise ValueError(
            "Número de impactos deve corresponder ao número de indicadores"
        )
    
    # Converter para numpy arrays
    decision_matrix = np.array(topsis_input.matriz_decisao, dtype=float)
    weights = np.array(topsis_input.pesos, dtype=float)
    impacts = np.array(topsis_input.impactos, dtype=int)
    
    # Normalizar pesos (somar a 1)
    weights = weights / np.sum(weights)
    
    # Passo 1: Normalizar a matriz de decisão
    normalized_matrix = _normalize_decision_matrix(decision_matrix)
    
    # Passo 2: Aplicar pesos
    weighted_matrix = _apply_weights(normalized_matrix, weights)
    
    # Passo 3: Calcular soluções ideal positiva e negativa
    ideal_positive, ideal_negative = _calculate_ideal_solutions(
        weighted_matrix, impacts
    )
    
    # Passo 4: Calcular distâncias euclidianas
    distance_to_positive, distance_to_negative = _calculate_euclidean_distances(
        weighted_matrix, ideal_positive, ideal_negative
    )
    
    # Passo 5: Calcular coeficiente de similaridade (Índice Smart)
    similarity_scores = _calculate_similarity_coefficient(
        distance_to_negative, distance_to_positive
    )
    
    # Passo 6: Criar ranking
    ranking_data = [
        CitySmartIndex(
            nome_cidade=topsis_input.cidades[i],
            indice_smart=round(float(similarity_scores[i]), 4)
        )
        for i in range(len(topsis_input.cidades))
    ]
    
    # Ordenar por índice smart descendente
    ranking_data.sort(key=lambda x: x.indice_smart, reverse=True)
    
    # Detalhes do cálculo para auditoria
    detalhes = {
        "matriz_normalizada": normalized_matrix.tolist(),
        "matriz_ponderada": weighted_matrix.tolist(),
        "solucao_ideal_positiva": ideal_positive.tolist(),
        "solucao_ideal_negativa": ideal_negative.tolist(),
        "distancia_para_positiva": distance_to_positive.tolist(),
        "distancia_para_negativa": distance_to_negative.tolist(),
        "pesos_normalizados": weights.tolist(),
        "indicadores": topsis_input.indicadores_nomes,
    }
    
    return TOPSISResult(
        ranking=ranking_data,
        detalhes_calculo=detalhes
    )
