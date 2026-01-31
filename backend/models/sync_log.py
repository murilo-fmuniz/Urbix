"""Modelo de logs de sincronização de APIs"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime

from .base import Base


class ApiSyncLog(Base):
    """Log de sincronizações com APIs externas"""
    __tablename__ = 'api_sync_logs'
    
    id = Column(Integer, primary_key=True)
    api_name = Column(String(100), nullable=False)  # 'IBGE', 'DATASUS', etc.
    endpoint = Column(String(500))
    
    # Status da sincronização
    status = Column(String(20), nullable=False)  # 'success', 'error', 'partial'
    records_processed = Column(Integer, default=0)
    records_inserted = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Detalhes
    error_message = Column(Text)
    execution_time_seconds = Column(Float)
    
    # Timestamps
    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ApiSyncLog(api_name='{self.api_name}', status='{self.status}')>"
