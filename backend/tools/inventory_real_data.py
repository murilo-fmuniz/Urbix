import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / 'urbix.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

print('INVENTARIO DE DADOS REAIS')
print('=' * 70)

for table in ('valores_indicadores', 'valores_indicadores_latest'):
    cur.execute(f'''
        SELECT
            COUNT(*) AS total,
            COUNT(valor) AS com_valor,
            COUNT(DISTINCT id_indicador) AS indicadores,
            COUNT(DISTINCT codigo_ibge) AS municipios,
            COUNT(DISTINCT fonte) AS fontes
        FROM {table}
    ''')
    total, com_valor, indicadores, municipios, fontes = cur.fetchone()
    print(f'{table}:')
    print(f'  registros totais: {total:,}')
    print(f'  registros com valor real: {com_valor:,}')
    print(f'  indicadores distintos: {indicadores:,}')
    print(f'  municípios distintos: {municipios:,}')
    print(f'  fontes distintas: {fontes:,}')

print('\nPOR INDICADOR (histórico, somente valor não nulo):')
print('-' * 70)
cur.execute('''
    SELECT id_indicador, COUNT(*) AS registros,
           COUNT(DISTINCT codigo_ibge) AS municipios,
           MIN(ano_referencia), MAX(ano_referencia)
    FROM valores_indicadores
    WHERE valor IS NOT NULL
    GROUP BY id_indicador
    ORDER BY registros DESC
''')
for indicator, records, cities, min_year, max_year in cur.fetchall():
    print(f'{indicator}|registros={records:,}|municipios={cities:,}|anos={min_year}-{max_year}')

print('\nPOR FONTE (histórico, somente valor não nulo):')
print('-' * 70)
cur.execute('''
    SELECT COALESCE(fonte, '[sem fonte]') AS fonte,
           COUNT(*) AS registros,
           COUNT(DISTINCT id_indicador) AS indicadores,
           COUNT(DISTINCT codigo_ibge) AS municipios
    FROM valores_indicadores
    WHERE valor IS NOT NULL
    GROUP BY fonte
    ORDER BY registros DESC
''')
for source, records, indicators, cities in cur.fetchall():
    print(f'{source}|registros={records:,}|indicadores={indicators:,}|municipios={cities:,}')

print('\nINDICADORES TOPSIS COM DADOS:')
cur.execute('''
    SELECT COUNT(DISTINCT id_indicador)
    FROM valores_indicadores
    WHERE valor IS NOT NULL
      AND id_indicador IN (
        'Total Escolas (INEP)', 'Total Hospitais (CNES)',
        'Total Pontos Iluminação (MUNIC)', 'Total Serviços Ofertados (MUNIC)',
        'Total Unidades Saúde (CNES)', 'bombeiros_numerador',
        'consultas_remotas_numerador', 'densidade_banda_larga',
        'empregos_informais_numerador', 'empregos_tic_numerador',
        'escolas_conectadas_telegestao_numerador', 'forca_de_trabalho',
        'homicidios_numerador', 'hospitais_gerador_backup_numerador',
        'ideb_iniciais', 'iluminacao_telegestao_numerador',
        'medidores_inteligentes_agua', 'moradias_inadequadas_numerador',
        'orcamento_per_capita', 'populacao_total',
        'prontuario_eletronico_numerador', 'relacao_estudante_professor',
        'sem_teto_numerador', 'servicos_urbanos_online_numerador',
        'sobrevivencia_negocios_numerador', 'taxa_desemprego_numerador',
        'total_domicilios'
      )
''')
print(f'  IDs necessários com algum valor: {cur.fetchone()[0]}')

conn.close()
