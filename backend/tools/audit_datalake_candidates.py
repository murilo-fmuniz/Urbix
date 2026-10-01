from __future__ import annotations

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent / 'data' / 'planilhas'

CASES = {
    'MUNIC_recursos_humanos': {
        'file': ROOT / 'MUNIC_2024' / 'Base_MUNIC_2024_20251107.xlsx',
        'sheet': 'Recursos humanos',
        'code': 'CodMun',
        'columns': ['MREH011', 'MREH012', 'MREH013', 'MREH014', 'MREH015', 'MREH016', 'MREH02', 'MREH031', 'MREH032', 'MREH033', 'MREH034', 'MREH035', 'MREH036', 'MREH04', 'MREH05'],
    },
    'MUNIC_informatica': {
        'file': ROOT / 'MUNIC_2024' / 'Base_MUNIC_2024_20251107.xlsx',
        'sheet': 'Informática e comunicação',
        'code': 'Cod Munic',
        'columns': ['Mtic06', 'Mtic10', 'Mtic12a1', 'Mtic181', 'Mtic11', 'Mtic04', 'Mtic08', 'Mtic15'],
    },
    'MUNIC_habitacao': {
        'file': ROOT / 'MUNIC_2024' / 'Base_MUNIC_2024_20251107.xlsx',
        'sheet': 'Habitacao',
        'code': 'CodMun',
        'columns': ['Mhab03'],
    },
    'MUNIC_eventos': {
        'file': ROOT / 'MUNIC_2024' / 'Base_MUNIC_2024_20251107.xlsx',
        'sheet': 'Evento climático RS',
        'code': 'CodMun',
        'columns': ['Mers01', 'Mers04', 'Mers10', 'Mers111'],
    },
    'SNIS': {
        'file': ROOT / 'SNIS' / 'br_mdr_snis_municipio_agua_esgoto.csv.gz',
        'sheet': None,
        'code': 'id_municipio',
        'columns': ['ano', 'populacao_atendida_agua', 'populacao_atentida_esgoto', 'indice_hidrometracao', 'indice_perda_distribuicao_agua', 'indice_coleta_esgoto', 'indice_tratamento_esgoto', 'indice_atendimento_total_agua', 'indice_atendimento_esgoto_agua', 'investimento_total_municipio', 'despesa_total_servico'],
    },
}


def read_case(case):
    path = case['file']
    if not path.exists():
        print(f"MISSING|{path}")
        return
    if path.suffix.lower() in {'.csv', '.gz'}:
        df = pd.read_csv(path, sep=',', compression='gzip' if path.name.endswith('.gz') else None, low_memory=False)
    else:
        df = pd.read_excel(path, sheet_name=case['sheet'], header=0)
    print(f"CASE|{case['sheet'] or path.name}|rows={len(df)}|columns={len(df.columns)}")
    print(f"CODE|requested={case['code']}|exists={case['code'] in df.columns}")
    for col in case['columns']:
        if col not in df.columns:
            print(f"COLUMN|{col}|MISSING")
            continue
        series = df[col]
        numeric = pd.to_numeric(series.astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False), errors='coerce')
        nonnull = series.notna().sum()
        numeric_count = numeric.notna().sum()
        unique = series.dropna().astype(str).nunique()
        sample = series.dropna().astype(str).head(5).tolist()
        print(f"COLUMN|{col}|nonnull={nonnull}|numeric={numeric_count}|unique={unique}|sample={sample}")
    print()


def inspect_munic_dictionary():
    path = ROOT / 'MUNIC_2024' / 'Base_MUNIC_2024_20251107.xlsx'
    if not path.exists():
        return
    df = pd.read_excel(path, sheet_name='Dicionário', header=None)
    print('### MUNIC_dictionary_matches')
    terms = {'Mhab03', 'Mtic06', 'Mtic10', 'Mtic12a1', 'Mtic181', 'MREH011', 'MREH012', 'Mers01', 'Mers04', 'Mers10', 'Mers111'}
    for idx, row in df.iterrows():
        text = ' | '.join(str(value) for value in row.tolist() if pd.notna(value))
        if any(term.lower() in text.lower() for term in terms):
            print(f'ROW|{idx}|{text}')


if __name__ == '__main__':
    for name, case in CASES.items():
        print(f"### {name}")
        read_case(case)
    inspect_munic_dictionary()
