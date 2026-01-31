# Urbix Backend

Sistema de análise de indicadores de Cidades Sustentáveis

## 📁 Estrutura do Projeto

```
backend/
├── 📄 main.py                 # Entry point da aplicação FastAPI
├── 📄 requirements.txt        # Dependências do projeto
├── 📄 DATABASE.md            # Documentação do banco de dados
├── 📄 README.md              # Este arquivo
│
├── 📁 config/                # Configurações
│   ├── __init__.py
│   └── database.py           # Configuração do SQLAlchemy
│
├── 📁 models/                # Modelos do banco de dados
│   ├── __init__.py
│   ├── base.py              # Base declarativa
│   ├── city.py              # Modelo de cidades
│   ├── state.py             # Modelo de estados
│   ├── indicator.py         # Modelos de indicadores
│   └── sync_log.py          # Logs de sincronização
│
├── 📁 database/             # Operações de banco de dados
│   ├── __init__.py
│   ├── operations.py        # Funções CRUD
│   └── legacy.py            # Compatibilidade com código antigo
│
├── 📁 api/                  # Endpoints da API
│   ├── __init__.py
│   └── indicators.py        # Endpoints de indicadores
│
├── 📁 etl/                  # Extract, Transform, Load
│   ├── __init__.py
│   └── ibge_etl.py         # ETL da API do IBGE
│
├── 📁 scripts/              # Scripts utilitários
│   ├── __init__.py
│   ├── init_database.py    # Inicialização completa
│   └── migrate_data.py     # Migração de dados
│
└── 📁 data/                 # Dados persistidos
    ├── urbix.db            # Banco SQLite
    └── db.json             # Dados legados (migrado)
```

## 🚀 Início Rápido

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Inicializar Banco de Dados

```bash
# Opção 1: Script completo (recomendado para primeira vez)
python -m scripts.init_database

# Opção 2: Passo a passo
python -c "from config import init_db; init_db()"
python -m etl.ibge_etl
python -m scripts.migrate_data
```

### 3. Executar Servidor

```bash
uvicorn main:app --reload
```

Acesse a documentação interativa em: http://localhost:8000/docs

## 📦 Módulos

### Config
Configurações de banco de dados e aplicação

```python
from config import init_db, get_db, get_db_dependency
```

### Models
Modelos SQLAlchemy do banco de dados

```python
from models import City, State, Indicator, IndicatorCategory, CityIndicator
```

### Database
Operações de alto nível no banco de dados

```python
from database import get_all_cities, get_city_indicators, upsert_city_indicator
```

### ETL
Extração, transformação e carga de dados

```python
from etl import run_full_etl, IBGEExtractor, IBGELoader
```

### Scripts
Scripts utilitários de manutenção

```python
from scripts import init_database, run_migration
```

## 🔧 Configuração

### Banco de Dados

Por padrão, usa SQLite em `data/urbix.db`

Para usar PostgreSQL em produção:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/urbix"
```

Ou edite [config/database.py](config/database.py)

### Variáveis de Ambiente

```bash
DATABASE_URL=sqlite:///./data/urbix.db  # ou postgresql://...
```

## 📊 Uso

### Criar nova sessão do banco

```python
from config import get_db

with get_db() as db:
    cities = db.query(City).all()
```

### Usar em endpoints FastAPI

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from config import get_db_dependency
from database import get_all_cities

@app.get("/cities")
def list_cities(db: Session = Depends(get_db_dependency)):
    return get_all_cities(db)
```

### Executar ETL

```python
# Via linha de comando
python -m etl.ibge_etl

# Via código
from etl import run_full_etl
run_full_etl()
```

## 🛠️ Scripts Úteis

### Inicializar banco completo
```bash
python -m scripts.init_database
```

### Atualizar dados do IBGE
```bash
python -m etl.ibge_etl
```

### Migrar dados antigos
```bash
python -m scripts.migrate_data
```

### Resetar banco (CUIDADO!)
```python
from config import drop_all_tables, init_db
drop_all_tables()
init_db()
```

## 📝 Migração de Código Antigo

### Antes (estrutura antiga)
```python
from database import db
from models import City
from db_config import get_db

indicators = db.get_all_indicators()
```

### Depois (nova estrutura)
```python
from database import db  # Ainda funciona! (compatibilidade)
from models import City
from config import get_db

indicators = db.get_all_indicators()
```

A nova estrutura mantém compatibilidade com código antigo via módulo `database.legacy`

## 🔍 Detalhes dos Módulos

### config/
- **database.py**: Configuração SQLAlchemy, engine, sessões

### models/
- **base.py**: Base declarativa do SQLAlchemy
- **city.py**: Modelo de cidades (ibge_code, name, population, etc.)
- **state.py**: Modelo de estados brasileiros
- **indicator.py**: Modelos de indicadores e categorias
- **sync_log.py**: Logs de sincronização de APIs

### database/
- **operations.py**: Funções CRUD (get_all_cities, get_city_indicators, etc.)
- **legacy.py**: Classe Database para compatibilidade

### etl/
- **ibge_etl.py**: ETL completo da API do IBGE (estados + municípios)

### scripts/
- **init_database.py**: Inicialização completa do banco
- **migrate_data.py**: Migração de dados do db.json

## 📚 Documentação Adicional

- [DATABASE.md](DATABASE.md) - Documentação completa do banco de dados
- [API Docs](http://localhost:8000/docs) - Documentação interativa (após iniciar servidor)

## 🧪 Testes

```bash
# Testar conexão ao banco
python -c "from config import init_db; init_db(); print('✓ OK')"

# Verificar modelos
python -c "from models import *; print('✓ Models OK')"

# Testar operações
python -c "from database import *; print('✓ Database OK')"
```

## 🤝 Contribuindo

1. Mantenha a estrutura modular
2. Use type hints em todas as funções
3. Adicione docstrings
4. Mantenha compatibilidade com código legado quando possível

## 📄 Licença

Projeto acadêmico - Urbix
