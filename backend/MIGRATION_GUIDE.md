# Guia de Migração - Estrutura Antiga → Nova

Este guia explica como migrar seu código que usa a estrutura antiga para a nova estrutura organizada.

## 📊 Comparação de Estruturas

### Estrutura Antiga
```
backend/
├── main.py
├── database.py
├── db_config.py
├── models.py
├── etl_ibge.py
├── migrate_data.py
├── init_database.py
└── api/
    └── indicators.py
```

### Nova Estrutura
```
backend/
├── main.py
├── config/
│   └── database.py
├── models/
│   ├── base.py
│   ├── city.py
│   ├── state.py
│   ├── indicator.py
│   └── sync_log.py
├── database/
│   ├── operations.py
│   └── legacy.py
├── etl/
│   └── ibge_etl.py
└── scripts/
    ├── init_database.py
    └── migrate_data.py
```

## 🔄 Mudanças de Imports

### 1. Configuração do Banco de Dados

**Antes:**
```python
from db_config import init_db, get_db, get_db_dependency, SessionLocal
```

**Depois:**
```python
from config import init_db, get_db, get_db_dependency, SessionLocal
```

---

### 2. Models

**Antes:**
```python
from models import Base, City, State, Indicator, CityIndicator, IndicatorCategory, ApiSyncLog
```

**Depois:**
```python
from models import Base, City, State, Indicator, CityIndicator, IndicatorCategory, ApiSyncLog
```

✅ **Sem mudanças!** Os models continuam sendo importados da mesma forma.

---

### 3. Operações de Banco de Dados

**Antes:**
```python
from database import db, get_all_cities, get_city_indicators
```

**Depois:**
```python
from database import db, get_all_cities, get_city_indicators
```

✅ **Sem mudanças!** As funções continuam sendo importadas da mesma forma.

---

### 4. ETL

**Antes:**
```python
from etl_ibge import run_full_etl, IBGEExtractor, IBGELoader
```

**Depois:**
```python
from etl import run_full_etl, IBGEExtractor, IBGELoader
# OU
from etl.ibge_etl import run_full_etl, IBGEExtractor, IBGELoader
```

---

### 5. Scripts

**Antes:**
```python
from init_database import main as init_database
from migrate_data import run_migration
```

**Depois:**
```python
from scripts import init_database, run_migration
# OU
from scripts.init_database import main as init_database
from scripts.migrate_data import run_migration
```

---

## 📝 Exemplos Práticos

### Exemplo 1: Endpoint FastAPI

**Antes:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db_config import get_db_dependency
from database import get_all_cities

router = APIRouter()

@router.get("/cities")
def list_cities(db: Session = Depends(get_db_dependency)):
    return get_all_cities(db)
```

**Depois:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from config import get_db_dependency  # ← Mudou!
from database import get_all_cities

router = APIRouter()

@router.get("/cities")
def list_cities(db: Session = Depends(get_db_dependency)):
    return get_all_cities(db)
```

---

### Exemplo 2: Script de ETL

**Antes:**
```python
from models import City, State
from db_config import get_db, init_db
from etl_ibge import run_full_etl

init_db()
run_full_etl()
```

**Depois:**
```python
from models import City, State
from config import get_db, init_db  # ← Mudou!
from etl import run_full_etl         # ← Mudou!

init_db()
run_full_etl()
```

---

### Exemplo 3: Operações de Banco

**Antes:**
```python
from database import db
from db_config import get_db
from models import City

# Método legado
indicators = db.get_all_indicators()

# Ou com sessão
with get_db() as session:
    cities = session.query(City).all()
```

**Depois:**
```python
from database import db
from config import get_db  # ← Mudou!
from models import City

# Método legado - AINDA FUNCIONA!
indicators = db.get_all_indicators()

# Ou com sessão
with get_db() as session:
    cities = session.query(City).all()
```

---

## 🎯 Checklist de Migração

Siga este checklist para migrar seu código:

- [ ] Substituir `from db_config import` por `from config import`
- [ ] Substituir `from etl_ibge import` por `from etl import`
- [ ] Verificar se scripts usam `from scripts import`
- [ ] Testar imports: `python -c "from config import *; from models import *; from database import *"`
- [ ] Testar aplicação: `uvicorn main:app --reload`

---

## 🆘 Resolução de Problemas

### Erro: `ModuleNotFoundError: No module named 'db_config'`

**Solução:** Altere o import de `from db_config import` para `from config import`

---

### Erro: `ModuleNotFoundError: No module named 'etl_ibge'`

**Solução:** Altere o import de `from etl_ibge import` para `from etl import`

---

### Erro: `ModuleNotFoundError: No module named 'models'`

**Solução:** Certifique-se de que está executando os scripts a partir da pasta `backend/`:

```bash
cd backend
python -m scripts.init_database
```

---

## ✅ Compatibilidade

A nova estrutura mantém **100% de compatibilidade** com código que usa:

- `from database import db` (classe legada)
- `from models import City, State, etc.` (exports no `__init__.py`)
- Funções de database: `get_all_cities()`, `get_city_indicators()`, etc.

## 🚀 Vantagens da Nova Estrutura

1. **Organização**: Código agrupado por responsabilidade
2. **Escalabilidade**: Fácil adicionar novos módulos
3. **Manutenção**: Arquivos menores e mais focados
4. **Imports limpos**: Hierarquia clara de módulos
5. **Testabilidade**: Módulos independentes são mais fáceis de testar

## 📚 Referências

- [README.md](README.md) - Documentação principal
- [DATABASE.md](DATABASE.md) - Documentação do banco de dados
- [config/database.py](config/database.py) - Nova localização da configuração
- [models/__init__.py](models/__init__.py) - Exports dos models
- [database/__init__.py](database/__init__.py) - Exports das operações

---

**Nota:** Se encontrar algum problema durante a migração, verifique os arquivos `__init__.py` de cada módulo para confirmar os exports disponíveis.
