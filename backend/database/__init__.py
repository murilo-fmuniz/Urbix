"""Database operations module"""
from .operations import (
    get_all_cities,
    get_city_by_id,
    get_city_by_ibge_code,
    search_cities,
    get_all_indicators,
    get_indicator_by_id,
    get_indicator_by_iso_code,
    get_indicators_by_category,
    get_city_indicators,
    get_indicator_for_city,
    upsert_city_indicator,
    get_all_categories,
    get_category_by_name,
    get_city_statistics
)
from .legacy import Database, db

__all__ = [
    # City operations
    'get_all_cities',
    'get_city_by_id',
    'get_city_by_ibge_code',
    'search_cities',
    # Indicator operations
    'get_all_indicators',
    'get_indicator_by_id',
    'get_indicator_by_iso_code',
    'get_indicators_by_category',
    # City indicator operations
    'get_city_indicators',
    'get_indicator_for_city',
    'upsert_city_indicator',
    # Category operations
    'get_all_categories',
    'get_category_by_name',
    # Statistics
    'get_city_statistics',
    # Legacy
    'Database',
    'db'
]
