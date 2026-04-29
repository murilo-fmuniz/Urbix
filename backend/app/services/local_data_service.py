"""
Service Layer: Local Data Management
====================================

Gerencia o carregamento e cache do arquivo indicators_master.json.
Responsável por fornecer acesso estruturado aos indicadores locais.

Características:
- Cache em memória para performance
- Lazy loading (carrega apenas quando necessário)
- Tipagem forte com Python 3.12+
- Tratamento de erros robusto
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class LocalDataService:
    """
    Service para gerenciar dados locais do arquivo indicators_master.json.
    
    Padrão Singleton implícito - mantém cache durante execução da aplicação.
    """
    
    # Cache de dados
    _cache: Optional[Dict[str, Any]] = None
    _cache_loaded_at: Optional[datetime] = None
    _json_file_path: Path = Path(__file__).parent.parent / "data" / "indicators_master.json"
    
    @classmethod
    def _load_cache(cls) -> None:
        """
        Carrega dados do JSON em memória (lazy loading).
        
        Raises:
            FileNotFoundError: Se indicators_master.json não existe
            json.JSONDecodeError: Se JSON é inválido
        """
        if cls._cache is not None:
            return  # Já carregado
        
        if not cls._json_file_path.exists():
            logger.error(f"❌ Arquivo não encontrado: {cls._json_file_path}")
            raise FileNotFoundError(f"indicators_master.json não encontrado em {cls._json_file_path}")
        
        try:
            with open(cls._json_file_path, 'r', encoding='utf-8') as f:
                cls._cache = json.load(f)
            cls._cache_loaded_at = datetime.now()
            
            total = len(cls._cache.get('municipios', {}))
            logger.info(f"✅ Cache de indicadores locais carregado ({total} municípios)")
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ Erro ao parsear JSON: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"❌ Erro inesperado ao carregar cache: {type(e).__name__}: {str(e)}")
            raise
    
    @classmethod
    def find_by_id(cls, city_id: str) -> Optional[Dict[str, Any]]:
        """
        Busca indicadores de uma cidade pelo código IBGE.
        
        Args:
            city_id: Código IBGE de 7 dígitos (ex: "4101408" para Apucarana)
        
        Returns:
            Dicionário com 'nome' e 'indicadores', ou None se não encontrado
            
        Example:
            >>> data = LocalDataService.find_by_id("4101408")
            >>> print(data['nome'])
            'Apucarana'
            >>> print(data['indicadores']['densidade_banda_larga'])
            20.2505
        """
        cls._load_cache()
        
        # Normalizar ID
        city_id_normalized = str(city_id).strip().zfill(7)
        
        # Buscar no cache
        municipios = cls._cache.get('municipios', {})
        municipio_data = municipios.get(city_id_normalized)
        
        if municipio_data is None:
            logger.debug(f"⚠️  Cidade não encontrada: {city_id_normalized}")
            return None
        
        logger.debug(f"✅ Cidade encontrada: {city_id_normalized} - {municipio_data.get('nome')}")
        return municipio_data
    
    @classmethod
    def find_all(cls) -> Dict[str, Any]:
        """
        Retorna todos os dados de indicadores (com metadados).
        
        Returns:
            Dicionário completo com 'metadata' e 'municipios'
        """
        cls._load_cache()
        return cls._cache.copy() if cls._cache else {}
    
    @classmethod
    def find_indicadores_by_id(cls, city_id: str) -> Optional[Dict[str, float]]:
        """
        Retorna apenas os indicadores de uma cidade (sem nome).
        
        Args:
            city_id: Código IBGE
        
        Returns:
            Dicionário com indicadores ou None se cidade não existe
            
        Example:
            >>> indicators = LocalDataService.find_indicadores_by_id("4113700")
            >>> print(indicators)
            {'densidade_banda_larga': 29.0951}
        """
        municipio_data = cls.find_by_id(city_id)
        return municipio_data.get('indicadores') if municipio_data else None
    
    @classmethod
    def find_nome_by_id(cls, city_id: str) -> Optional[str]:
        """
        Retorna apenas o nome de uma cidade.
        
        Args:
            city_id: Código IBGE
        
        Returns:
            Nome da cidade ou None se não encontrada
        """
        municipio_data = cls.find_by_id(city_id)
        return municipio_data.get('nome') if municipio_data else None
    
    @classmethod
    def get_metadata(cls) -> Dict[str, Any]:
        """
        Retorna metadados do processamento.
        
        Returns:
            Dicionário com data_processamento, total_municipios, etc
        """
        cls._load_cache()
        return cls._cache.get('metadata', {})
    
    @classmethod
    def clear_cache(cls) -> None:
        """
        Limpa o cache (para testes ou reload manual).
        """
        cls._cache = None
        cls._cache_loaded_at = None
        logger.info("🧹 Cache de indicadores locais limpo")
    
    @classmethod
    def get_cache_info(cls) -> Dict[str, Any]:
        """
        Retorna informações sobre o cache.
        
        Returns:
            Dict com status, tamanho, timestamp de carregamento
        """
        return {
            "is_loaded": cls._cache is not None,
            "cache_loaded_at": cls._cache_loaded_at.isoformat() if cls._cache_loaded_at else None,
            "total_municipios": len(cls._cache.get('municipios', {})) if cls._cache else 0,
            "json_file_path": str(cls._json_file_path),
            "json_file_exists": cls._json_file_path.exists(),
        }


# Alias para compatibilidade
def get_local_data_service() -> type:
    """Factory para obter o serviço (padrão Dependency Injection)."""
    return LocalDataService
