"""
Urbix Backend - Estrutura Organizada

Este arquivo serve como referência visual da nova estrutura modular.
"""

# ==============================================================================
# ESTRUTURA DO PROJETO
# ==============================================================================

"""
backend/
│
├── 📄 main.py                    # FastAPI application entry point
├── 📄 requirements.txt           # Python dependencies
├── 📄 README.md                  # Main documentation
├── 📄 DATABASE.md                # Database schema documentation
├── 📄 MIGRATION_GUIDE.md         # Migration guide (old → new)
│
├── 📁 config/                    # ⚙️ Configuration modules
│   ├── __init__.py              # Exports: init_db, get_db, SessionLocal, etc.
│   └── database.py              # SQLAlchemy configuration & session management
│
├── 📁 models/                    # 🗄️ Database models (SQLAlchemy ORM)
│   ├── __init__.py              # Exports: Base, City, State, Indicator, etc.
│   ├── base.py                  # Base declarative class
│   ├── city.py                  # City model (ibge_code, name, population...)
│   ├── state.py                 # State model (Brazilian states)
│   ├── indicator.py             # Indicator models (Indicator, Category, CityIndicator)
│   └── sync_log.py              # API sync log model
│
├── 📁 database/                  # 💾 Database operations
│   ├── __init__.py              # Exports: all CRUD functions
│   ├── operations.py            # High-level database operations
│   └── legacy.py                # Backward compatibility (Database class)
│
├── 📁 api/                       # 🌐 API endpoints
│   ├── __init__.py
│   └── indicators.py            # Indicator endpoints (existing)
│
├── 📁 etl/                       # 🔄 ETL pipelines
│   ├── __init__.py              # Exports: run_full_etl, IBGEExtractor, etc.
│   └── ibge_etl.py              # IBGE API ETL (states + cities)
│
├── 📁 scripts/                   # 🔧 Utility scripts
│   ├── __init__.py              # Exports: init_database, run_migration
│   ├── init_database.py         # Complete database initialization
│   └── migrate_data.py          # Data migration from db.json
│
└── 📁 data/                      # 💿 Persisted data
    ├── urbix.db                 # SQLite database
    └── db.json                  # Legacy data (migrated)
"""

# ==============================================================================
# IMPORT PATTERNS
# ==============================================================================

# Configuration
"""
from config import init_db, get_db, get_db_dependency, SessionLocal, DATABASE_URL
"""

# Models
"""
from models import (
    Base,
    City, State,
    Indicator, IndicatorCategory, CityIndicator,
    ApiSyncLog
)
"""

# Database Operations
"""
from database import (
    # City operations
    get_all_cities, get_city_by_id, get_city_by_ibge_code, search_cities,
    
    # Indicator operations
    get_all_indicators, get_indicator_by_id, get_indicator_by_iso_code,
    get_indicators_by_category,
    
    # City-Indicator operations
    get_city_indicators, get_indicator_for_city, upsert_city_indicator,
    
    # Category operations
    get_all_categories, get_category_by_name,
    
    # Statistics
    get_city_statistics,
    
    # Legacy support
    db  # Database class instance
)
"""

# ETL
"""
from etl import run_full_etl, IBGEExtractor, IBGELoader
"""

# Scripts
"""
from scripts import init_database, run_migration
"""

# ==============================================================================
# MODULE RESPONSIBILITIES
# ==============================================================================

MODULES = {
    "config": {
        "purpose": "Application and database configuration",
        "key_files": ["database.py"],
        "exports": ["init_db", "get_db", "get_db_dependency", "SessionLocal", "engine"]
    },
    
    "models": {
        "purpose": "SQLAlchemy ORM models",
        "key_files": ["base.py", "city.py", "state.py", "indicator.py", "sync_log.py"],
        "exports": ["Base", "City", "State", "Indicator", "IndicatorCategory", "CityIndicator", "ApiSyncLog"]
    },
    
    "database": {
        "purpose": "High-level database operations (CRUD)",
        "key_files": ["operations.py", "legacy.py"],
        "exports": ["get_all_cities", "get_city_indicators", "upsert_city_indicator", "db"]
    },
    
    "api": {
        "purpose": "FastAPI endpoints",
        "key_files": ["indicators.py"],
        "exports": ["router"]
    },
    
    "etl": {
        "purpose": "Extract, Transform, Load pipelines",
        "key_files": ["ibge_etl.py"],
        "exports": ["run_full_etl", "IBGEExtractor", "IBGELoader"]
    },
    
    "scripts": {
        "purpose": "Utility and maintenance scripts",
        "key_files": ["init_database.py", "migrate_data.py"],
        "exports": ["init_database", "run_migration", "DataMigrator"]
    }
}

# ==============================================================================
# QUICK START COMMANDS
# ==============================================================================

COMMANDS = """
# Install dependencies
pip install -r requirements.txt

# Initialize database (complete setup)
python -m scripts.init_database

# Run individual scripts
python -c "from config import init_db; init_db()"
python -m etl.ibge_etl
python -m scripts.migrate_data

# Start server
uvicorn main:app --reload

# Access API docs
http://localhost:8000/docs
"""

# ==============================================================================
# MIGRATION FROM OLD STRUCTURE
# ==============================================================================

MIGRATION_MAP = {
    "db_config": "config",
    "models": "models",  # No change
    "database": "database",  # No change (but reorganized internally)
    "etl_ibge": "etl.ibge_etl",
    "init_database": "scripts.init_database",
    "migrate_data": "scripts.migrate_data"
}

"""
Old import:           New import:
------------------    --------------------
from db_config        from config
from models           from models (no change)
from database         from database (no change)
from etl_ibge         from etl
"""

# ==============================================================================
# DESIGN PRINCIPLES
# ==============================================================================

PRINCIPLES = """
1. Separation of Concerns
   - Each module has a single, well-defined responsibility
   
2. Modularity
   - Easy to add new features without modifying existing code
   
3. Backward Compatibility
   - Legacy code still works via database.legacy module
   
4. Clear Hierarchy
   - config → models → database → api
   - Dependency flow is always downward
   
5. Explicit Exports
   - All __init__.py files explicitly define __all__
   
6. Documentation
   - Every module, class, and function has docstrings
"""

if __name__ == "__main__":
    print(__doc__)
    print("\n" + "="*70)
    print("URBIX BACKEND - STRUCTURE OVERVIEW")
    print("="*70)
    
    for module_name, info in MODULES.items():
        print(f"\n📦 {module_name}/")
        print(f"   Purpose: {info['purpose']}")
        print(f"   Files: {', '.join(info['key_files'])}")
        print(f"   Exports: {len(info['exports'])} items")
    
    print("\n" + "="*70)
    print("✅ Structure is ready to use!")
    print("="*70)
