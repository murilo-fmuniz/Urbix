import sqlite3
conn = sqlite3.connect('urbix.db')
count = conn.execute('SELECT COUNT(*) FROM valores_indicadores WHERE id_indicador LIKE "%domicili%"').fetchone()[0]
print(f'total_domicilios count: {count}')
conn.close()
