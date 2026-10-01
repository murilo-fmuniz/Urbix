from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text

backend = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend))
load_dotenv(backend / '.env')

from app.database import SessionLocal, engine
from app.etl_config import FONTES_API, INDICADORES
from app.models import ValorIndicador
from tools.local_etl_service import (
    extrair_dado_base_sidra,
    extrair_dados_locais,
    extrair_receita_siconfi,
)

CIDADE = '4101408'
CIDADES = {CIDADE}


def atualizar_snapshot_cidade(codigo: str) -> None:
    with engine.begin() as conn:
        conn.execute(text('DELETE FROM valores_indicadores_latest WHERE codigo_ibge = :codigo'), {'codigo': codigo})
        conn.execute(text('''
            INSERT INTO valores_indicadores_latest
                (codigo_ibge, id_indicador, ano_referencia, valor, fonte, id_origem)
            SELECT codigo_ibge, id_indicador, ano_referencia, valor, fonte, id
            FROM (
                SELECT v.*, ROW_NUMBER() OVER (
                    PARTITION BY codigo_ibge, id_indicador
                    ORDER BY ano_referencia DESC, id DESC
                ) AS rn
                FROM valores_indicadores v
                WHERE codigo_ibge = :codigo
            ) ranked
            WHERE rn = 1
        '''), {'codigo': codigo})


def main() -> None:
    print(f'ETL LIMITADO | município={CIDADE} | cidade_alvo={CIDADES}')

    with SessionLocal() as db:
        for indicador, config in FONTES_API['sidra'].items():
            extrair_dado_base_sidra(indicador, config, db, cidades_alvo=CIDADES)

    if FONTES_API['siconfi'].get('habilitado'):
        extrair_receita_siconfi(
            ['receita_total_municipio', 'receita_propria_numerador', 'despesas_capital_numerador'],
            cidades_alvo=CIDADES,
        )

    with SessionLocal() as db:
        for dominio, indicadores in INDICADORES.items():
            for indicador, regra in indicadores.items():
                status = str(regra.get('status', '')).lower()
                if any(token in status for token in ('pendente', 'incompleto', 'nao_baixado', 'implementacao')):
                    continue
                config = regra.get('variavel_direta') if regra.get('tipo_calculo') == 'direto' else regra.get('numerador')
                if not config or config.get('arquivo') in {'API', 'NÃO_BAIXADO'}:
                    continue
                id_variavel = indicador if regra.get('tipo_calculo') == 'direto' else f'{indicador}_numerador'
                extrair_dados_locais(id_variavel, config, db, cidades_alvo=CIDADES)

    atualizar_snapshot_cidade(CIDADE)

    with engine.connect() as conn:
        rows = conn.execute(text('''
            SELECT id_indicador, valor, ano_referencia, fonte
            FROM valores_indicadores_latest
            WHERE codigo_ibge = :codigo
            ORDER BY id_indicador
        '''), {'codigo': CIDADE}).all()
        print(f'APUCARANA_SNAPSHOT_TOTAL={len(rows)}')
        for row in rows:
            print(f'{row[0]}|valor={row[1]}|ano={row[2]}|fonte={row[3]}')


if __name__ == '__main__':
    main()
