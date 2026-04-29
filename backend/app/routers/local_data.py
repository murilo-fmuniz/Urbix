"""
Router: Local Data Endpoints
=============================

Endpoints REST para consumo de dados locais do arquivo indicators_master.json.
Fornece acesso estruturado aos indicadores por município.

Endpoints:
- GET /municipio/{id}          - Obter dados completos de uma cidade
- GET /municipios              - Listar todos os municípios
- GET /municipio/{id}/indicadores - Obter apenas indicadores
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional

from app.services.local_data_service import LocalDataService

# ============================================================================
# SETUP
# ============================================================================

municipios_router = APIRouter(tags=["Dados Locais"])


# ============================================================================
# SCHEMAS (Type Hints)
# ============================================================================

class MunicipioResponse(Dict[str, Any]):
    """Response com nome + indicadores de um município."""
    pass


class IndicadoresResponse(Dict[str, float]):
    """Response com apenas os indicadores."""
    pass


# ============================================================================
# ENDPOINTS
# ============================================================================

@municipios_router.get(
    "/{city_id}",
    response_model=Dict[str, Any],
    status_code=200,
    summary="Obter dados de um município",
    description="Retorna nome e indicadores de um município pelo código IBGE",
    responses={
        200: {
            "description": "Município encontrado",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "Apucarana",
                        "indicadores": {
                            "densidade_banda_larga": 20.2505
                        }
                    }
                }
            }
        },
        404: {
            "description": "Município não encontrado"
        }
    }
)
def get_municipio(city_id: str) -> Dict[str, Any]:
    """
    Obtém dados completos de um município.
    
    Args:
        city_id: Código IBGE de 7 dígitos (ex: "4101408" para Apucarana)
    
    Returns:
        Dicionário com 'nome' e 'indicadores'
    
    Raises:
        HTTPException 404: Se município não encontrado
    
    Example:
        ```
        GET /municipio/4101408
        
        Response:
        {
            "nome": "Apucarana",
            "indicadores": {
                "densidade_banda_larga": 20.2505
            }
        }
        ```
    """
    municipio_data = LocalDataService.find_by_id(city_id)
    
    if municipio_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Município com código {city_id} não encontrado"
        )
    
    return municipio_data


@municipios_router.get(
    "/{city_id}/indicadores",
    response_model=Dict[str, float],
    status_code=200,
    summary="Obter indicadores de um município",
    description="Retorna apenas os indicadores (sem nome)",
    responses={
        200: {
            "description": "Indicadores encontrados",
            "content": {
                "application/json": {
                    "example": {
                        "densidade_banda_larga": 20.2505
                    }
                }
            }
        },
        404: {
            "description": "Município não encontrado"
        }
    }
)
def get_municipio_indicadores(city_id: str) -> Dict[str, float]:
    """
    Obtém apenas os indicadores de um município.
    
    Args:
        city_id: Código IBGE
    
    Returns:
        Dicionário com indicadores
    
    Raises:
        HTTPException 404: Se município não encontrado
    """
    indicadores = LocalDataService.find_indicadores_by_id(city_id)
    
    if indicadores is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Município com código {city_id} não encontrado"
        )
    
    return indicadores


@municipios_router.get(
    "/{city_id}/nome",
    response_model=str,
    status_code=200,
    summary="Obter nome de um município",
    responses={
        200: {
            "description": "Nome encontrado",
            "content": {
                "application/json": {
                    "example": "Apucarana"
                }
            }
        },
        404: {
            "description": "Município não encontrado"
        }
    }
)
def get_municipio_nome(city_id: str) -> str:
    """
    Obtém apenas o nome de um município.
    
    Args:
        city_id: Código IBGE
    
    Returns:
        Nome da cidade
    
    Raises:
        HTTPException 404: Se município não encontrado
    """
    nome = LocalDataService.find_nome_by_id(city_id)
    
    if nome is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Município com código {city_id} não encontrado"
        )
    
    return nome


@municipios_router.get(
    "s",
    response_model=Dict[str, Any],
    status_code=200,
    summary="Listar todos os municípios",
    description="Retorna todos os dados de municípios com metadados"
)
def list_municipios() -> Dict[str, Any]:
    """
    Retorna todos os dados de indicadores locais.
    
    Returns:
        Dicionário com 'metadata' e 'municipios'
    
    Example:
        ```
        GET /municipios
        
        Response:
        {
            "metadata": {
                "data_processamento": "2026-04-27T19:09:00",
                "total_municipios": 23,
                ...
            },
            "municipios": {
                "4101408": {
                    "nome": "Apucarana",
                    "indicadores": {...}
                },
                ...
            }
        }
        ```
    """
    return LocalDataService.find_all()


@municipios_router.get(
    "/cache/info",
    response_model=Dict[str, Any],
    status_code=200,
    summary="Obter informações de cache",
    description="Retorna status e informações do cache em memória"
)
def get_cache_info() -> Dict[str, Any]:
    """
    Retorna informações de diagnóstico do cache.
    
    Returns:
        Dicionário com is_loaded, timestamp, total_municipios, etc
    
    Example:
        ```
        GET /municipio/cache/info
        
        Response:
        {
            "is_loaded": true,
            "cache_loaded_at": "2026-04-29T10:30:00.123456",
            "total_municipios": 23,
            "json_file_path": "/app/data/indicators_master.json",
            "json_file_exists": true
        }
        ```
    """
    return LocalDataService.get_cache_info()


# ============================================================================
# HEALTH CHECK
# ============================================================================

@municipios_router.get(
    "/health",
    response_model=Dict[str, Any],
    status_code=200,
    summary="Health check do serviço de dados locais"
)
def health_check() -> Dict[str, Any]:
    """
    Verifica se o serviço de dados locais está funcionando.
    
    Returns:
        Status de health check
    """
    try:
        cache_info = LocalDataService.get_cache_info()
        all_data = LocalDataService.find_all()
        
        return {
            "status": "healthy",
            "cache_loaded": cache_info['is_loaded'],
            "total_municipios": cache_info['total_municipios'],
            "json_file_exists": cache_info['json_file_exists'],
            "metadata": all_data.get('metadata', {})
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Serviço indisponível: {str(e)}"
        )
