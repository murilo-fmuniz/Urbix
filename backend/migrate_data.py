"""
Script de migração dos dados existentes (db.json) para o novo banco de dados SQL
"""
import json
from pathlib import Path
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from models import Indicator, IndicatorCategory, CityIndicator, City
from db_config import get_db, init_db

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataMigrator:
    """Migra dados do formato JSON antigo para o banco de dados SQL"""
    
    def __init__(self, db: Session):
        self.db = db
        self.json_path = Path(__file__).parent / "data" / "db.json"
        self.stats = {
            'categories_created': 0,
            'indicators_migrated': 0,
            'errors': 0
        }
    
    def load_json_data(self) -> dict:
        """Carrega dados do arquivo JSON"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✓ Dados JSON carregados: {len(data.get('indicators', []))} indicadores")
            return data
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {self.json_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON: {e}")
            raise
    
    def get_or_create_category(self, category_name: str) -> IndicatorCategory:
        """Obtém ou cria uma categoria de indicador"""
        # Mapear cores para cada categoria
        category_colors = {
            'Ambiental': '#10b981',      # Verde
            'Social': '#3b82f6',         # Azul
            'Governança': '#8b5cf6',     # Roxo
            'Infraestrutura': '#f59e0b', # Laranja
            'Econômico': '#ef4444',      # Vermelho
            'Saúde': '#ec4899',          # Rosa
            'Educação': '#14b8a6',       # Teal
        }
        
        category = self.db.query(IndicatorCategory).filter_by(name=category_name).first()
        
        if not category:
            category = IndicatorCategory(
                name=category_name,
                description=f"Indicadores da categoria {category_name}",
                color=category_colors.get(category_name, '#6b7280')  # Cinza padrão
            )
            self.db.add(category)
            self.db.commit()
            self.stats['categories_created'] += 1
            logger.info(f"✓ Categoria criada: {category_name}")
        
        return category
    
    def migrate_indicators(self) -> None:
        """Migra indicadores do JSON para o banco SQL"""
        logger.info("=== Iniciando migração de indicadores ===")
        
        try:
            json_data = self.load_json_data()
            indicators_data = json_data.get('indicators', [])
            
            for idx, indicator_json in enumerate(indicators_data, 1):
                try:
                    # Obter ou criar categoria
                    category_name = indicator_json.get('category', 'Outros')
                    category = self.get_or_create_category(category_name)
                    
                    # Criar código ISO (slug do nome)
                    iso_code = indicator_json['name'].upper().replace(' ', '_').replace('Ã', 'A')
                    iso_code = f"URB_{iso_code}"
                    
                    # Verificar se indicador já existe
                    existing_indicator = self.db.query(Indicator).filter_by(
                        iso_code=iso_code
                    ).first()
                    
                    if existing_indicator:
                        # Atualizar indicador existente
                        existing_indicator.name = indicator_json['name']
                        existing_indicator.description = indicator_json.get('description', '')
                        existing_indicator.category_id = category.id
                        existing_indicator.target_value = indicator_json.get('target')
                        existing_indicator.unit = '%'  # Assumindo percentual
                        logger.debug(f"Indicador atualizado: {indicator_json['name']}")
                    else:
                        # Criar novo indicador
                        new_indicator = Indicator(
                            iso_code=iso_code,
                            name=indicator_json['name'],
                            description=indicator_json.get('description', ''),
                            category_id=category.id,
                            unit='%',  # Ajustar conforme necessário
                            target_value=indicator_json.get('target'),
                            is_higher_better=True,
                            data_source='Dados históricos',
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        self.db.add(new_indicator)
                        logger.debug(f"Indicador criado: {indicator_json['name']}")
                    
                    self.db.commit()
                    self.stats['indicators_migrated'] += 1
                
                except Exception as e:
                    logger.error(f"Erro ao migrar indicador {indicator_json.get('name', 'unknown')}: {e}")
                    self.stats['errors'] += 1
                    self.db.rollback()
            
            logger.info(f"✓ Indicadores migrados: {self.stats['indicators_migrated']}")
            logger.info(f"✓ Categorias criadas: {self.stats['categories_created']}")
            if self.stats['errors'] > 0:
                logger.warning(f"⚠ Erros durante migração: {self.stats['errors']}")
        
        except Exception as e:
            logger.error(f"Erro na migração de indicadores: {e}")
            raise
    
    def create_sample_city_indicators(self) -> None:
        """
        Cria alguns indicadores de exemplo para cidades (opcional)
        Útil para testes iniciais
        """
        logger.info("=== Criando indicadores de exemplo para cidades ===")
        
        try:
            # Buscar algumas cidades de exemplo
            sample_cities = self.db.query(City).limit(5).all()
            
            if not sample_cities:
                logger.warning("Nenhuma cidade encontrada. Execute o ETL primeiro.")
                return
            
            # Buscar indicadores
            indicators = self.db.query(Indicator).all()
            
            if not indicators:
                logger.warning("Nenhum indicador encontrado. Execute a migração de indicadores primeiro.")
                return
            
            # Criar valores de exemplo
            for city in sample_cities:
                for indicator in indicators[:3]:  # Apenas os 3 primeiros indicadores
                    # Verificar se já existe
                    existing = self.db.query(CityIndicator).filter_by(
                        city_id=city.id,
                        indicator_id=indicator.id
                    ).first()
                    
                    if not existing:
                        city_indicator = CityIndicator(
                            city_id=city.id,
                            indicator_id=indicator.id,
                            value=70.0 + (city.id * 2) % 30,  # Valor fictício
                            year=2024,
                            reference_date=datetime.utcnow(),
                            last_updated=datetime.utcnow(),
                            data_quality='good',
                            notes='Dados de exemplo para testes'
                        )
                        self.db.add(city_indicator)
            
            self.db.commit()
            logger.info(f"✓ Indicadores de exemplo criados para {len(sample_cities)} cidades")
        
        except Exception as e:
            logger.error(f"Erro ao criar indicadores de exemplo: {e}")
            self.db.rollback()


def run_migration(include_samples: bool = False):
    """Executa a migração completa"""
    logger.info("=" * 60)
    logger.info("INICIANDO MIGRAÇÃO DE DADOS")
    logger.info("=" * 60)
    
    try:
        # Inicializar banco de dados
        init_db()
        
        with get_db() as db:
            migrator = DataMigrator(db)
            
            # Migrar indicadores
            migrator.migrate_indicators()
            
            # Criar dados de exemplo (opcional)
            if include_samples:
                migrator.create_sample_city_indicators()
            
            logger.info("=" * 60)
            logger.info("MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            logger.info(f"Categorias criadas: {migrator.stats['categories_created']}")
            logger.info(f"Indicadores migrados: {migrator.stats['indicators_migrated']}")
            logger.info(f"Erros: {migrator.stats['errors']}")
            logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"MIGRAÇÃO FALHOU: {e}")
        raise


if __name__ == "__main__":
    # Executar migração
    # Mude para True se quiser criar dados de exemplo
    run_migration(include_samples=False)
