"""
ETL para popular o banco de dados com dados do IBGE
API Documentation: https://servicodados.ibge.gov.br/api/docs/localidades
"""
import requests
from datetime import datetime
from typing import List, Dict, Optional
import time
import logging
from sqlalchemy.orm import Session

from models import State, City, ApiSyncLog
from db_config import get_db, init_db

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URLs da API do IBGE
IBGE_BASE_URL = "https://servicodados.ibge.gov.br/api/v1"
ESTADOS_URL = f"{IBGE_BASE_URL}/localidades/estados"
MUNICIPIOS_URL = f"{IBGE_BASE_URL}/localidades/municipios"


class IBGEExtractor:
    """Extrator de dados da API do IBGE"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Urbix/1.0 (Academic Research Project)'
        })
    
    def get_estados(self) -> List[Dict]:
        """Busca todos os estados brasileiros"""
        try:
            logger.info("Buscando estados do IBGE...")
            response = self.session.get(ESTADOS_URL, timeout=30)
            response.raise_for_status()
            estados = response.json()
            logger.info(f"✓ {len(estados)} estados encontrados")
            return estados
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar estados: {e}")
            raise
    
    def get_municipios(self, estado_id: Optional[str] = None) -> List[Dict]:
        """
        Busca municípios
        
        Args:
            estado_id: Código do estado (UF). Se None, busca todos os municípios do Brasil
        """
        try:
            url = MUNICIPIOS_URL
            if estado_id:
                url = f"{IBGE_BASE_URL}/localidades/estados/{estado_id}/municipios"
                logger.info(f"Buscando municípios do estado {estado_id}...")
            else:
                logger.info("Buscando todos os municípios do Brasil...")
            
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            municipios = response.json()
            logger.info(f"✓ {len(municipios)} municípios encontrados")
            return municipios
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar municípios: {e}")
            raise
    
    def get_municipio_detalhes(self, municipio_id: str) -> Dict:
        """Busca detalhes de um município específico"""
        try:
            url = f"{MUNICIPIOS_URL}/{municipio_id}"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Erro ao buscar detalhes do município {municipio_id}: {e}")
            raise


class IBGELoader:
    """Carrega dados do IBGE no banco de dados"""
    
    def __init__(self, db: Session):
        self.db = db
        self.extractor = IBGEExtractor()
        self.stats = {
            'states_inserted': 0,
            'states_updated': 0,
            'cities_inserted': 0,
            'cities_updated': 0,
            'errors': 0
        }
    
    def load_states(self) -> None:
        """Carrega estados no banco de dados"""
        logger.info("=== Iniciando carga de estados ===")
        
        try:
            estados_data = self.extractor.get_estados()
            
            for estado in estados_data:
                try:
                    # Verificar se o estado já existe
                    existing_state = self.db.query(State).filter_by(
                        ibge_code=str(estado['id'])
                    ).first()
                    
                    if existing_state:
                        # Atualizar
                        existing_state.name = estado['nome']
                        existing_state.abbreviation = estado['sigla']
                        existing_state.region = estado['regiao']['nome']
                        self.stats['states_updated'] += 1
                        logger.debug(f"Estado atualizado: {estado['sigla']}")
                    else:
                        # Inserir novo
                        new_state = State(
                            ibge_code=str(estado['id']),
                            name=estado['nome'],
                            abbreviation=estado['sigla'],
                            region=estado['regiao']['nome']
                        )
                        self.db.add(new_state)
                        self.stats['states_inserted'] += 1
                        logger.debug(f"Estado inserido: {estado['sigla']}")
                    
                    self.db.commit()
                    
                except Exception as e:
                    logger.error(f"Erro ao processar estado {estado.get('sigla', 'unknown')}: {e}")
                    self.stats['errors'] += 1
                    self.db.rollback()
            
            logger.info(f"✓ Estados processados: {self.stats['states_inserted']} inseridos, "
                       f"{self.stats['states_updated']} atualizados")
        
        except Exception as e:
            logger.error(f"Erro na carga de estados: {e}")
            raise
    
    def load_cities(self, batch_size: int = 100) -> None:
        """Carrega municípios no banco de dados"""
        logger.info("=== Iniciando carga de municípios ===")
        
        try:
            municipios_data = self.extractor.get_municipios()
            total = len(municipios_data)
            
            for idx, municipio in enumerate(municipios_data, 1):
                try:
                    # Buscar o estado correspondente
                    estado_ibge_code = str(municipio['microrregiao']['mesorregiao']['UF']['id'])
                    state = self.db.query(State).filter_by(
                        ibge_code=estado_ibge_code
                    ).first()
                    
                    if not state:
                        logger.warning(f"Estado não encontrado para o município {municipio['nome']}")
                        self.stats['errors'] += 1
                        continue
                    
                    # Verificar se o município já existe
                    municipio_ibge_code = str(municipio['id'])
                    existing_city = self.db.query(City).filter_by(
                        ibge_code=municipio_ibge_code
                    ).first()
                    
                    if existing_city:
                        # Atualizar
                        existing_city.name = municipio['nome']
                        existing_city.state_id = state.id
                        self.stats['cities_updated'] += 1
                    else:
                        # Inserir novo
                        new_city = City(
                            ibge_code=municipio_ibge_code,
                            name=municipio['nome'],
                            state_id=state.id,
                            country='Brasil'
                        )
                        self.db.add(new_city)
                        self.stats['cities_inserted'] += 1
                    
                    # Commit em lotes
                    if idx % batch_size == 0:
                        self.db.commit()
                        logger.info(f"Progresso: {idx}/{total} municípios processados "
                                  f"({idx/total*100:.1f}%)")
                
                except Exception as e:
                    logger.error(f"Erro ao processar município {municipio.get('nome', 'unknown')}: {e}")
                    self.stats['errors'] += 1
                    self.db.rollback()
            
            # Commit final
            self.db.commit()
            
            logger.info(f"✓ Municípios processados: {self.stats['cities_inserted']} inseridos, "
                       f"{self.stats['cities_updated']} atualizados")
        
        except Exception as e:
            logger.error(f"Erro na carga de municípios: {e}")
            raise
    
    def create_sync_log(self, api_name: str, status: str, execution_time: float) -> None:
        """Cria registro de log da sincronização"""
        log = ApiSyncLog(
            api_name=api_name,
            endpoint=IBGE_BASE_URL,
            status=status,
            records_processed=self.stats['cities_inserted'] + self.stats['cities_updated'],
            records_inserted=self.stats['cities_inserted'] + self.stats['states_inserted'],
            records_updated=self.stats['cities_updated'] + self.stats['states_updated'],
            records_failed=self.stats['errors'],
            execution_time_seconds=execution_time,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()
        logger.info(f"✓ Log de sincronização criado")


def run_full_etl():
    """Executa o ETL completo"""
    logger.info("=" * 60)
    logger.info("INICIANDO ETL - IBGE LOCALIDADES")
    logger.info("=" * 60)
    
    start_time = time.time()
    
    try:
        # Inicializar banco de dados
        init_db()
        
        with get_db() as db:
            loader = IBGELoader(db)
            
            # 1. Carregar estados
            loader.load_states()
            
            # 2. Carregar municípios
            loader.load_cities(batch_size=100)
            
            # 3. Criar log
            execution_time = time.time() - start_time
            loader.create_sync_log('IBGE', 'success', execution_time)
            
            logger.info("=" * 60)
            logger.info("ETL CONCLUÍDO COM SUCESSO!")
            logger.info(f"Tempo de execução: {execution_time:.2f} segundos")
            logger.info(f"Estados: {loader.stats['states_inserted']} inseridos, "
                       f"{loader.stats['states_updated']} atualizados")
            logger.info(f"Municípios: {loader.stats['cities_inserted']} inseridos, "
                       f"{loader.stats['cities_updated']} atualizados")
            logger.info(f"Erros: {loader.stats['errors']}")
            logger.info("=" * 60)
    
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"ETL FALHOU: {e}")
        
        # Tentar criar log de erro
        try:
            with get_db() as db:
                log = ApiSyncLog(
                    api_name='IBGE',
                    endpoint=IBGE_BASE_URL,
                    status='error',
                    error_message=str(e),
                    execution_time_seconds=execution_time,
                    started_at=datetime.utcnow(),
                    completed_at=datetime.utcnow()
                )
                db.add(log)
                db.commit()
        except Exception as log_error:
            logger.error(f"Erro ao criar log: {log_error}")
        
        raise


if __name__ == "__main__":
    run_full_etl()
