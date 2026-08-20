import sqlite3

conn = sqlite3.connect('urbix.db')
cur = conn.cursor()

print("RELATÓRIO FINAL: COBERTURA DE TOPSIS IDs (Após 5 Denominadores + Estado Domicílios)")
print("=" * 90)
print()

# 27 IDs esperados
ids_esperados = [
    'Total Escolas (INEP)',
    'Total Hospitais (CNES)',
    'Total Pontos Iluminação (MUNIC)',
    'Total Serviços Ofertados (MUNIC)',
    'Total Unidades Saúde (CNES)',
    'bombeiros_numerador',
    'consultas_remotas_numerador',
    'densidade_banda_larga',
    'empregos_informais_numerador',
    'empregos_tic_numerador',
    'escolas_conectadas_telegestao_numerador',
    'forca_de_trabalho',
    'homicidios_numerador',
    'hospitais_gerador_backup_numerador',
    'ideb_iniciais',
    'iluminacao_telegestao_numerador',
    'medidores_inteligentes_agua',
    'moradias_inadequadas_numerador',
    'orcamento_per_capita',
    'populacao_total',
    'pib_absoluto',
    'prontuario_eletronico_numerador',
    'receita_total_municipio',
    'relacao_estudante_professor',
    'sem_teto_numerador',
    'servicos_urbanos_online_numerador',
    'sobrevivencia_negocios_numerador',
    'taxa_desemprego_numerador',
    'total_domicilios',
]

com_dados = []
sem_dados = []

for id_ind in sorted(ids_esperados):
    cur.execute('SELECT COUNT(*) FROM valores_indicadores WHERE id_indicador = ?', (id_ind,))
    cnt = cur.fetchone()[0]
    
    if cnt > 0:
        com_dados.append((id_ind, cnt))
        status = "✓"
    else:
        sem_dados.append(id_ind)
        status = "✗"
    
    cnt_display = f"{cnt:,}" if cnt > 0 else "0"
    print(f"{status} {id_ind:50s}: {cnt_display:>12s}")

print()
print("=" * 90)
print(f"RESUMO: {len(com_dados)} IDs com dados | {len(sem_dados)} IDs sem dados (total 29)")
print()

if sem_dados:
    print("IDs FALTANDO:")
    for i, id_ind in enumerate(sem_dados, 1):
        print(f"  {i:2d}. {id_ind}")

print()
print("INDICADORES TOPSIS VIÁVEIS (com todos numerador + denominador):")
print("  - Escolas Conectadas: " + ("SIM" if "escolas_conectadas_telegestao_numerador" in dict([(i, 1) for i in com_dados]) and "Total Escolas (INEP)" in dict([(i, 1) for i in com_dados]) else "NÃO"))
print("  - Iluminação Telegestão: " + ("SIM" if "iluminacao_telegestao_numerador" in dict([(i, 1) for i in com_dados]) and "Total Pontos Iluminação (MUNIC)" in dict([(i, 1) for i in com_dados]) else "NÃO"))
print("  - Hospitais Gerador Backup: " + ("SIM" if "hospitais_gerador_backup_numerador" in dict([(i, 1) for i in com_dados]) and "Total Hospitais (CNES)" in dict([(i, 1) for i in com_dados]) else "NÃO"))
print("  - Serviços Urbanos Online: " + ("SIM" if "servicos_urbanos_online_numerador" in dict([(i, 1) for i in com_dados]) and "Total Serviços Ofertados (MUNIC)" in dict([(i, 1) for i in com_dados]) else "NÃO"))
print("  - Prontuário Eletrônico: " + ("SIM" if "prontuario_eletronico_numerador" in dict([(i, 1) for i in com_dados]) and "Total Unidades Saúde (CNES)" in dict([(i, 1) for i in com_dados]) else "NÃO"))

conn.close()
