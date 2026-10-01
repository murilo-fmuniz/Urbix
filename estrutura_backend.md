# Estrutura atual do backend

```text
backend/
├── app/
│   ├── main.py                 # FastAPI
│   ├── database.py             # SQLAlchemy/PostgreSQL
│   ├── models.py               # municípios, indicadores e valores
│   ├── schemas.py              # contratos da API
│   ├── etl_config.py           # fontes e regras do ETL
│   ├── routers/
│   │   └── topsis.py           # ranking e histórico
│   └── services/
│       └── topsis_core.py      # matriz e algoritmo TOPSIS
├── tools/
│   ├── local_etl_service.py    # ETL nacional
│   ├── audit_etl_runtime.py    # relatório da IC
│   ├── run_etl_apucarana.py    # teste limitado
│   ├── backfill_base_indicators.py
│   ├── coverage_simple.py
│   ├── prepare_indicator_rebuild.py
│   └── validate_rebuild.py
├── data/
│   ├── planilhas/              # datalake local, fora do Git
│   └── seed_*.json             # dados auxiliares
├── tests/
├── requirements.txt
├── alembic.ini
└── README.md
```

## Banco

O ambiente publicado usa PostgreSQL via `DATABASE_URL`. O histórico fica em `valores_indicadores` e o snapshot mais recente em `valores_indicadores_latest`.

## ETL

O comando padrão processa todos os municípios:

```powershell
cd backend\tools
..\venv\Scripts\python.exe local_etl_service.py
```

O teste limitado de Apucarana não altera o escopo padrão do ETL.
