import sqlite3

conn = sqlite3.connect('urbix.db')
cur = conn.cursor()

print('REGISTROS DE total_domicilios:')
print('=' * 80)
cur.execute('SELECT codigo_ibge, ano_referencia, valor FROM valores_indicadores WHERE id_indicador LIKE "%domicili%" ORDER BY codigo_ibge')
for row in cur.fetchall():
    print(f'Codigo: {row[0]}, Ano: {row[1]}, Valor: {row[2]}')

print('\nTOTAL:', cur.rowcount)

# Verifica todos os IDs únicos que contêm "domicili"
cur.execute('SELECT DISTINCT id_indicador FROM valores_indicadores WHERE id_indicador LIKE "%domicili%"')
print('\nIDs únicos com domicili:')
for row in cur.fetchall():
    cur.execute('SELECT COUNT(*) FROM valores_indicadores WHERE id_indicador = ?', (row[0],))
    print(f'  {row[0]}: {cur.fetchone()[0]} registros')

conn.close()
