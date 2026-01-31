"""
Legacy database support for backward compatibility
"""
from typing import List, Optional, Dict, Any

from .operations import get_all_indicators, get_indicator_by_id


class Database:
    """Classe legada para compatibilidade com código antigo"""
    
    def __init__(self):
        self._db = None
    
    def get_all_indicators(self) -> List[Dict[str, Any]]:
        """Retorna todos os indicadores no formato JSON antigo"""
        from config import SessionLocal
        db = SessionLocal()
        try:
            indicators = get_all_indicators(db)
            return [
                {
                    'id': ind.id,
                    'name': ind.name,
                    'category': ind.category.name if ind.category else None,
                    'description': ind.description,
                    'unit': ind.unit,
                    'target': ind.target_value
                }
                for ind in indicators
            ]
        finally:
            db.close()
    
    def get_indicator_by_id(self, indicator_id: int) -> Optional[Dict[str, Any]]:
        """Retorna um indicador por ID no formato JSON antigo"""
        from config import SessionLocal
        db = SessionLocal()
        try:
            ind = get_indicator_by_id(db, indicator_id)
            if ind:
                return {
                    'id': ind.id,
                    'name': ind.name,
                    'category': ind.category.name if ind.category else None,
                    'description': ind.description,
                    'unit': ind.unit,
                    'target': ind.target_value
                }
            return None
        finally:
            db.close()


# Instância global para compatibilidade
db = Database()
