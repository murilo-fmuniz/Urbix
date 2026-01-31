# Urbix Backend - Database Schema

## Estrutura do Banco de Dados

O backend do Urbix utiliza SQLAlchemy ORM com suporte para **SQLite** (desenvolvimento) e **PostgreSQL** (produção).

### 📋 Tabelas

#### 1. **states** - Estados brasileiros
```
- id: Integer (PK)
- ibge_code: String(2) - Código IBGE do estado
- name: String(100) - Nome do estado
- abbreviation: String(2) - Sigla (UF)
- region: String(50) - Região (Norte, Sul, etc.)
```

#### 2. **cities** - Municípios
```
- id: Integer (PK)
- ibge_code: String(7) - Código IBGE único
- name: String(200) - Nome do município
- state_id: Integer (FK → states.id)
- country: String(100) - País (padrão: Brasil)
- latitude: Float
- longitude: Float
- population: Integer
- area_km2: Float
- created_at: DateTime
- updated_at: DateTime
```

#### 3. **indicator_categories** - Categorias de indicadores
```
- id: Integer (PK)
- name: String(100) - Nome da categoria
- description: Text
- color: String(7) - Código de cor hexadecimal
```

#### 4. **indicators** - Definições dos indicadores
```
- id: Integer (PK)
- iso_code: String(50) - Código único do indicador
- name: String(200) - Nome do indicador
- description: Text
- category_id: Integer (FK → indicator_categories.id)
- unit: String(50) - Unidade de medida (%, km², etc.)
- target_value: Float - Valor meta/alvo
- is_higher_better: Boolean
- data_source: String(200)
- data_source_url: Text
- created_at: DateTime
- updated_at: DateTime
```

#### 5. **city_indicators** - Valores dos indicadores por cidade
```
- id: Integer (PK)
- city_id: Integer (FK → cities.id)
- indicator_id: Integer (FK → indicators.id)
- value: Float - Valor do indicador
- year: Integer - Ano de referência
- reference_date: DateTime
- last_updated: DateTime
- data_quality: String(20)
- notes: Text
```

#### 6. **api_sync_logs** - Log de sincronizações
```
- id: Integer (PK)
- api_name: String(100)
- endpoint: String(500)
- status: String(20)
- records_processed: Integer
- records_inserted: Integer
- records_updated: Integer
- records_failed: Integer
- error_message: Text
- execution_time_seconds: Float
- started_at: DateTime
- completed_at: DateTime
```

## 🚀 Inicialização

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Inicializar banco de dados completo

```bash
python init_database.py
```

Este script executa automaticamente:
- Criação das tabelas
- ETL do IBGE (estados e municípios)
- Migração dos dados existentes

### 3. Scripts individuais

```bash
# Apenas criar estrutura
python -c "from db_config import init_db; init_db()"

# Apenas ETL do IBGE
python etl_ibge.py

# Apenas migração de dados
python migrate_data.py
```

## 🔄 ETL - IBGE API

O script `etl_ibge.py` sincroniza dados da API do IBGE:

**Fonte:** https://servicodados.ibge.gov.br/api/docs/localidades

**Dados coletados:**
- 27 estados brasileiros
- 5.570+ municípios
- Regiões geográficas
- Códigos IBGE oficiais

**Execução:**
```bash
python etl_ibge.py
```

**Características:**
- Atualização incremental (insert/update)
- Log de execução
- Tratamento de erros
- Progresso em tempo real

## 🔧 Configuração

### SQLite (Desenvolvimento)

Padrão, não requer configuração adicional. Banco criado em:
```
backend/data/urbix.db
```

### PostgreSQL (Produção)

Configurar variável de ambiente:

```bash
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/urbix"
```

Ou no código:
```python
# db_config.py
DATABASE_URL = "postgresql://usuario:senha@host:porta/dbname"
```

## 📦 Estrutura de Arquivos

```
backend/
├── models.py              # Modelos SQLAlchemy
├── db_config.py           # Configuração do banco
├── database.py            # Operações de alto nível
├── etl_ibge.py           # ETL API IBGE
├── migrate_data.py       # Migração de dados antigos
├── init_database.py      # Inicialização completa
├── main.py               # FastAPI app
└── data/
    ├── urbix.db          # Banco SQLite
    └── db.json           # Dados antigos (migrado)
```

## 🔍 Uso Básico

### Python/FastAPI

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_all_cities, get_city_indicators
from db_config import get_db_dependency

@app.get("/cities")
def list_cities(db: Session = Depends(get_db_dependency)):
    return get_all_cities(db, limit=50)

@app.get("/cities/{city_id}/indicators")
def city_indicators(city_id: int, db: Session = Depends(get_db_dependency)):
    return get_city_indicators(db, city_id)
```

### Direct SQL

```python
from db_config import get_db
from models import City

with get_db() as db:
    cities = db.query(City).filter(City.name.like('%São Paulo%')).all()
    for city in cities:
        print(f"{city.name} - {city.state.abbreviation}")
```

## 📊 Exemplos de Queries

### Buscar cidade por código IBGE
```python
from database import get_city_by_ibge_code
city = get_city_by_ibge_code(db, "3550308")  # São Paulo
```

### Indicadores de uma cidade
```python
from database import get_city_indicators
indicators = get_city_indicators(db, city_id=1)
```

### Estatísticas por categoria
```python
from database import get_city_statistics
stats = get_city_statistics(db, city_id=1)
```

### Adicionar/atualizar indicador
```python
from database import upsert_city_indicator
upsert_city_indicator(
    db,
    city_id=1,
    indicator_id=1,
    value=85.5,
    year=2024,
    data_quality='good'
)
```

## 🎯 Próximos Passos

1. **Adicionar mais ETLs:**
   - DATASUS (saúde)
   - INEP (educação)
   - ANEEL (energia)

2. **Implementar cron jobs:**
   - Atualização automática semanal/mensal

3. **Adicionar validações:**
   - Valores mínimo/máximo
   - Regras de negócio

4. **Implementar cache:**
   - Redis para queries frequentes

5. **Adicionar índices:**
   - Otimizar queries comuns

## ⚠️ Notas Importantes

- SQLite é single-threaded, use PostgreSQL em produção
- Execute `init_database.py` apenas uma vez
- Backup regular do banco de dados
- Monitore logs de sincronização (`api_sync_logs`)
- Configure variáveis de ambiente para produção

## 🆘 Troubleshooting

### Erro "table already exists"
```bash
# Remover banco e reiniciar
rm data/urbix.db
python init_database.py
```

### Erro de conexão PostgreSQL
```bash
# Verificar se PostgreSQL está rodando
psql -h localhost -U usuario -d urbix
```

### ETL IBGE timeout
- Verificar conexão de internet
- API do IBGE pode estar instável
- Executar novamente, o script faz update incremental
