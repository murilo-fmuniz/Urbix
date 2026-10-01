from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

backend = Path(__file__).resolve().parent.parent
load_dotenv(backend / '.env')
engine = create_engine(os.environ['DATABASE_URL'], pool_pre_ping=True)

# IDs com semântica/procedimento corrigidos ou proxies explicitamente rejeitados.
IDS = {
    'orcamento_per_capita',
    'taxa_geracao_empregos_numerador',
    'densidade_banda_larga_numerador',
    'bombeiros_numerador',
    'medidores_inteligentes_agua',
    'iluminacao_telegestao',
    'servicos_urbanos_online',
    'escolas_conectadas_telegestao',
    'consultas_remotas_numerador',
    'prontuario_eletronico_numerador',
    'hospitais_gerador_backup_numerador',
    'taxa_desemprego_numerador',
    'sobrevivencia_negocios_numerador',
    'empregos_tic_numerador',
    'empregos_informais_numerador',
    'moradias_inadequadas',
    'edificios_vulneraveis_numerador',
    'areas_cobertas_cameras',
    'atendimento_agua_snis',
    'atendimento_esgoto_snis',
    'perdas_distribuicao_agua_snis',
    'coleta_esgoto_snis',
    'tratamento_esgoto_snis',
    'investimento_saneamento_snis',
    'despesa_saneamento_snis',
    'estrutura_tic_municipal',
    'servicos_informativos_municipio',
    'canal_telefonico_municipal',
}

with engine.begin() as conn:
    params = {'ids': list(IDS)}
    result = conn.execute(text('DELETE FROM valores_indicadores WHERE id_indicador = ANY(:ids)'), params)
    print(f'valores_indicadores removidos: {result.rowcount}')
    result = conn.execute(text('DELETE FROM valores_indicadores_latest WHERE id_indicador = ANY(:ids)'), params)
    print(f'valores_indicadores_latest removidos: {result.rowcount}')
    print(f'IDs preparados: {len(IDS)}')
