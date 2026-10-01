from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

backend = Path(__file__).resolve().parent.parent
load_dotenv(backend / '.env')
engine = create_engine(os.environ['DATABASE_URL'], pool_pre_ping=True)
ids = [
    'taxa_geracao_empregos_numerador', 'orcamento_per_capita',
    'medidores_inteligentes_agua', 'atendimento_agua_snis',
    'atendimento_esgoto_snis', 'perdas_distribuicao_agua_snis',
    'coleta_esgoto_snis', 'tratamento_esgoto_snis',
    'investimento_saneamento_snis', 'despesa_saneamento_snis',
    'estrutura_tic_municipal', 'servicos_informativos_municipio',
    'canal_telefonico_municipal', 'abrigos_emergencia',
    'rotas_evacuacao_numerador', 'mapas_ameacas_publicos',
]
with engine.connect() as conn:
    print('ID|count|municipios|min|max|ano_min|ano_max')
    for indicator in ids:
        row = conn.execute(text('''
            SELECT COUNT(*), COUNT(DISTINCT codigo_ibge), MIN(valor), MAX(valor),
                   MIN(ano_referencia), MAX(ano_referencia)
            FROM valores_indicadores WHERE id_indicador=:id AND valor IS NOT NULL
        '''), {'id': indicator}).one()
        print(f'{indicator}|{row[0]}|{row[1]}|{row[2]}|{row[3]}|{row[4]}|{row[5]}')
    print('\nAPUCARANA|4101408')
    rows = conn.execute(text('''
        SELECT id_indicador, valor, ano_referencia, fonte
        FROM valores_indicadores_latest
        WHERE codigo_ibge='4101408'
        ORDER BY id_indicador
    ''')).all()
    for row in rows:
        print(f'{row[0]}|{row[1]}|{row[2]}|{row[3]}')
    print('\nSNAPSHOT_TOTAL', conn.execute(text('SELECT COUNT(*) FROM valores_indicadores_latest')).scalar())
