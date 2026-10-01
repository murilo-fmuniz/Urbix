from __future__ import annotations

import gzip
import json
import os
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

backend = Path(__file__).resolve().parent.parent
load_dotenv(backend / ".env")
output = backend / f"urbix_postgres_backup_{datetime.now():%Y%m%d_%H%M%S}.jsonl.gz"
url = os.environ.get("DATABASE_URL")
if not url or not url.startswith("postgresql"):
    raise SystemExit("DATABASE_URL não aponta para PostgreSQL")

engine = create_engine(url, pool_pre_ping=True)
tables = ["indicadores", "municipios", "valores_indicadores", "valores_indicadores_latest"]
with engine.connect() as conn, gzip.open(output, "wt", encoding="utf-8") as handle:
    for table in tables:
        rows = conn.execute(text(f"SELECT * FROM {table}"))
        columns = list(rows.keys())
        count = 0
        for row in rows.mappings():
            handle.write(json.dumps({"table": table, "columns": columns, "row": dict(row)}, default=str, ensure_ascii=False) + "\n")
            count += 1
        print(f"{table}: {count} linhas")
print(f"BACKUP={output}")
