import sqlite3
from pathlib import Path

path = (Path(__file__).resolve().parent.parent / 'urbix.db').resolve()
uri = f'file:{path.as_posix()}?mode=ro'
conn = sqlite3.connect(uri, uri=True, timeout=2)
cur = conn.cursor()

print('INVENTARIO RAPIDO DE DADOS REAIS', flush=True)
for table in ('valores_indicadores', 'valores_indicadores_latest'):
    print(f'[{table}]', flush=True)
    for label, sql in [
        ('registros', f'SELECT COUNT(*) FROM {table}'),
        ('com_valor', f'SELECT COUNT(*) FROM {table} WHERE valor IS NOT NULL'),
        ('indicadores', f'SELECT COUNT(DISTINCT id_indicador) FROM {table}'),
        ('municipios', f'SELECT COUNT(DISTINCT codigo_ibge) FROM {table}'),
    ]:
        try:
            print(label, cur.execute(sql).fetchone()[0], flush=True)
        except Exception as exc:
            print(label, 'ERRO', exc, flush=True)

print('[indicadores com valor]', flush=True)
cur.execute('SELECT id_indicador, COUNT(*) FROM valores_indicadores WHERE valor IS NOT NULL GROUP BY id_indicador ORDER BY COUNT(*) DESC')
rows = cur.fetchall()
print('quantidade', len(rows), flush=True)
print('top10', rows[:10], flush=True)
print('total_por_indicador', sum(row[1] for row in rows), flush=True)

print('[fontes]', flush=True)
cur.execute('SELECT COALESCE(fonte, "[sem fonte]"), COUNT(*) FROM valores_indicadores WHERE valor IS NOT NULL GROUP BY fonte ORDER BY COUNT(*) DESC')
for row in cur.fetchall():
    print(row, flush=True)
conn.close()
