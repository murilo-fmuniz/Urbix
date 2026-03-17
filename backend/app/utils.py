"""
Utilitários para normalização de dados de entrada.
Aceita variados formatos (camelCase, UPPERCASE, lowercase, etc) e padroniza.
"""

import re
import unicodedata


def remove_accents(text: str) -> str:
    """
    Remove acentos e caracteres diacríticos.
    
    Exemplos:
    - "São Paulo" → "Sao Paulo"
    - "Maringá" → "Maringa"
    
    Args:
        text: Texto com possíveis acentos
        
    Returns:
        Texto sem acentos
    """
    if not text:
        return text
    
    # Normaliza para NFD (decompõe caracteres com acentos)
    nfd = unicodedata.normalize('NFD', text)
    # Remove caracteres diacríticos (categoria Mn = Mark, Nonspacing)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    
    return without_accents


def normalize_indicator_code(code: str) -> str:
    """
    Normaliza código de indicador para formato padrão (UPPERCASE com ponto, sem acentos).
    
    Exemplos:
    - "eco.1" → "ECO.1"
    - "ECO1" → "ECO.1"
    - "eço.1" → "ECO.1" (remove acentos)
    - "EcO.1" → "ECO.1"
    
    Args:
        code: Código do indicador em qualquer formato
        
    Returns:
        Código normalizado (UPPERCASE com ponto, sem acentos)
    """
    if not code:
        return code
    
    # Remove espaços extras
    code = code.strip()
    
    # Remove acentos
    code = remove_accents(code)
    
    # Converte para maiúscula
    code = code.upper()
    
    # Se não tem ponto, tenta adicionar (ex: ECO1 → ECO.1)
    # Padrão: letras seguidas de números, sem ponto entre eles
    if '.' not in code:
        # Encontra transição de letra para número
        code = re.sub(r'([A-Z]+)(\d+)', r'\1.\2', code)
    
    return code


def normalize_city_name(city: str) -> str:
    """
    Normaliza nome de cidade para Título Caso (Title Case).
    
    Exemplos:
    - "apucarana" → "Apucarana"
    - "APUCARANA" → "Apucarana"
    - "são paulo" → "São Paulo"
    - "MARINGÁ" → "Maringá"
    
    Args:
        city: Nome da cidade em qualquer formato
        
    Returns:
        Cidade normalizada (Título Caso)
    """
    if not city:
        return city
    
    # Remove espaços extras
    city = city.strip()
    
    # Converte cada palavra para Título Caso
    # Mantém acentos e caracteres especiais
    city = city.title()
    
    return city


def normalize_state(state: str) -> str:
    """
    Normaliza sigla de estado para formato padrão (UPPERCASE, 2 caracteres).
    
    Exemplos:
    - "pr" → "PR"
    - "PR" → "PR"
    - "são paulo" → "SP"
    - "paraná" → "PR"
    
    Args:
        state: Sigla ou nome do estado
        
    Returns:
        Sigla normalizada (UPPERCASE)
    """
    if not state:
        return state
    
    state = state.strip().upper()
    
    # Se for sigla com 2 caracteres, retorna
    if len(state) == 2:
        return state
    
    # Mapa de nomes para siglas (para nomes de estados)
    state_map = {
        "PARANÁ": "PR",
        "SÃO PAULO": "SP",
        "MARINGÁ": "PR",  # Cidade, não estado, mas consideramos
        "RIO DE JANEIRO": "RJ",
        "MINAS GERAIS": "MG",
        "SANTA CATARINA": "SC",
    }
    
    return state_map.get(state, state[:2].upper())


def normalize_comparison_value(value: str) -> str:
    """
    Normaliza valor para comparação (case-insensitive, sem espaços extras).
    
    Útil para filtros e comparações.
    
    Examples:
    - "ISO 37122" → "iso 37122"
    - "  SAÚDE  " → "saúde"
    
    Args:
        value: Valor a normalizar
        
    Returns:
        Valor normalizado (lowercase, sem espaços extras)
    """
    if not value:
        return value
    
    return value.strip().lower()
