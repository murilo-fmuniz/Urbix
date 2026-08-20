"""
Configuração central de roteamento do Datalake Urbix.
Separa as Variáveis Base (Denominadores) dos Indicadores TOPSIS (Calculados).
"""

# ==========================================
# 📊 1. DADOS BASE (Variáveis de Normalização)
# ==========================================
# Estes dados são extraídos primeiro e usados como denominador nos cálculos matemáticos.
# Política de dados ausentes: ausência de valor não gera zero artificial.
# Valores reais devem ser mantidos; cadeias sem apoio documental continuam marcadas como pendentes.

DADOS_BASE = {
    "populacao_total": {
        "arquivo": "Estimativas de Pupulacao/POP2025_20260113.xls",
        "coluna_codigo": "COD. MUNIC",
        "coluna_valor": "POPULAÇÃO ESTIMADA",
        "pandas_kwargs": {"sheet_name": "Municípios", "header": 1, "engine": "xlrd"},
        "status": "validado_via_api_sidra",
        "fonte": "IBGE / SIDRA"
    },
    "pib_absoluto": {
        "arquivo": "PIB_Municipios/base_de_dados_2010_2023_xlsx/PIB dos Municípios - base de dados 2010-2023.xlsx",
        "coluna_codigo": "Código do Município",
        "coluna_valor": "Produto Interno Bruto, a preços correntes (R$ 1,00)",
        "pandas_kwargs": {"sheet_name": "PIB dos Municípios", "header": 0},
        "status": "validado_localmente",
        "fonte": "IBGE / PIB municipal"
    },
    "forca_de_trabalho": {
        "arquivo": "NÃO_BAIXADO",
        "fonte_necessaria": "IBGE / CAGED - População Economicamente Ativa",
        "status": "pendente_implementacao_api",
        "fonte": "IBGE / SIDRA + CAGED"
    },
    "receita_total_municipio": {
        "arquivo": "NÃO_BAIXADO",
        "fonte_necessaria": "SICONFI / RREO (Receita Corrente Líquida)",
        "status": "em_implementacao_api_siconfi",
        "fonte": "SICONFI / Tesouro"
    },
    "total_domicilios": {
        "arquivo": "NÃO_BAIXADO",
        "fonte_necessaria": "IBGE Censo - Total de Domicílios Permanentes",
        "status": "pendente_implementacao_api",
        "fonte": "IBGE / Censo municipal"
    }
}


# ==========================================
# 🎯 2. INDICADORES TOPSIS (50 Indicadores)
# ==========================================
# Cada indicador define se é "direto" (já vem calculado da fonte) ou se depende
# de um "numerador" da planilha cruzado com um "denominador" dos DADOS_BASE.

INDICADORES = {
    
    # ------------------------------------------
    # 💰 ECONOMIA E GOVERNANÇA
    # ------------------------------------------
    "economia": {
        "taxa_desemprego": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "saldomovimentação"
            },
            "denominador": "forca_de_trabalho",
            "multiplicador": 100
        },
        "taxa_endividamento": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "SICONFI (Dívida Consolidada)"},
            "denominador": "receita_total_municipio",
            "multiplicador": 100
        },
        "despesas_capital": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "SICONFI (Investimentos)"},
            "denominador": "receita_total_municipio",
            "multiplicador": 100
        },
        "receita_propria": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "SICONFI (Impostos Municipais)"},
            "denominador": "receita_total_municipio",
            "multiplicador": 100
        },
        "orcamento_per_capita": {
            "tipo_calculo": "direto", # Já fornecido calculado pelo IBGE
            "variavel_direta": {
                "arquivo": "PIB_Municipios/base_de_dados_2010_2023_xlsx/PIB dos Municípios - base de dados 2010-2023.xlsx",
                "coluna_codigo": "Código do Município",
                "coluna_valor": "Produto Interno Bruto per capita, a preços correntes (R$ 1,00)"
            }
        },
        "mulheres_eleitas": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "TSE (Candidatas Eleitas)"},
            "denominador": "TSE (Total Cadeiras Legislativo)",
            "multiplicador": 100
        },
        "condenacoes_corrupcao": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "CNJ (Processos Transitados)"},
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "participacao_eleitoral": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "TSE (Votos Válidos)"},
            "denominador": "TSE (Eleitores Aptos)",
            "multiplicador": 100
        }
    },

    # ------------------------------------------
    # 🏘️ URBANISMO E SEGURANÇA
    # ------------------------------------------
    "sociedade_seguranca": {
        "moradias_inadequadas": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mhab03",
                "pandas_kwargs": {"sheet_name": "Habitacao", "header": 0}
            },
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "sem_teto": {
            "tipo_calculo": "taxa_100k",
            "numerador": {
                "arquivo": "cad_unico/cad_unico.txt",
                "coluna_codigo": "codigo_ibge",
                "coluna_valor": "cadun_qtd_pessoas_cadastradas_i"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "bombeiros": {
            "tipo_calculo": "taxa_100k",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "MREH011",
                "pandas_kwargs": {"sheet_name": "Recursos humanos"}
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "mortes_incendio": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "DataSUS SIM"},
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "agentes_policia": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Base_MUNIC Recursos humanos - coluna policial não confirmada"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "homicidios": {
            "tipo_calculo": "taxa_100k",
            "numerador": {
                "arquivo": "FBSP/br_fbsp_absp_municipio.csv/br_fbsp_absp_municipio.csv",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "quantidade_homicidio_doloso"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "acidentes_industriais": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "Ministério do Trabalho"},
            "denominador": "populacao_total",
            "multiplicador": 100000
        }
    },

    # ------------------------------------------
    # 📚 EDUCAÇÃO E INOVAÇÃO
    # ------------------------------------------
    "educacao_inovacao": {
        "relacao_estudante_professor": {
            "tipo_calculo": "direto", 
            "variavel_direta": {
                "arquivo": "ATU_2025_MUNICIPIOS/ATU_MUNICIPIOS_2025.xlsx",
                "coluna_codigo": "Código do Município",
                "coluna_valor": "Média de Alunos por Turma / Etapas de Ensino",
                "pandas_kwargs": {"sheet_name": "MUNICIPIO", "header": 5}
            }
        },
        "ideb_iniciais": {
            "tipo_calculo": "direto",
            "variavel_direta": {
                "arquivo": "divulgacao_anos_iniciais_municipios_2023/divulgacao_anos_iniciais_municipios_2023.xlsx",
                "coluna_codigo": "CO_MUNICIPIO",
                "coluna_valor": "IDEB 2023 (N x P)",
                "pandas_kwargs": {"sheet_name": "IDEB_AI_MUNICÍPIOS", "header": 9}
            }
        },
        "sobrevivencia_negocios": {
            "tipo_calculo": "taxa_100k",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "saldomovimentação"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "empregos_tic": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "saldomovimentação" # Requer filtro de CBO no script
            },
            "denominador": "forca_de_trabalho",
            "multiplicador": 100
        },
        "graduados_stem": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "INEP Superior"},
            "denominador": "populacao_total",
            "multiplicador": 100000
        }
    },

    # ------------------------------------------
    # 🌳 SUSTENTABILIDADE E SMART CITY (ISO 37122)
    # ------------------------------------------
    "sustentabilidade_smart_city": {
        "energia_residuos": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "SINISA Resíduos - layout não municipal confirmado"
            },
            "denominador": "Consumo Total Energia (ANEEL)",
            "multiplicador": 100
        },
        "iluminacao_telegestao": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mtic06",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0}
            },
            "denominador": "Total Pontos Iluminação (MUNIC)",
            "multiplicador": 100
        },
        "medidores_inteligentes_energia": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "ANEEL"},
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "edificios_verdes": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "GBC Brasil"},
            "denominador": "Total Edifícios Comerciais (IBGE)",
            "multiplicador": 100
        },
        "monitoramento_ar": {
            "tipo_calculo": "direto",
            "status": "pendente_confirmacao_fonte",
            "variavel_direta": {"arquivo": "NÃO_BAIXADO", "fonte": "Ministério do Meio Ambiente"}
        },
        "servicos_urbanos_online": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mtic10",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0}
            },
            "denominador": "Total Serviços Ofertados (MUNIC)",
            "multiplicador": 100
        },
        "prontuario_eletronico": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv",
                "coluna_codigo": "CO_IBGE",
                "coluna_valor": "ST_ATEND_AMBULATORIAL"
            },
            "denominador": "Total Unidades Saúde (CNES)",
            "multiplicador": 100
        },
        "consultas_remotas": {
            "tipo_calculo": "taxa_100k",
            "numerador": {
                "arquivo": "CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv",
                "coluna_codigo": "CO_IBGE",
                "coluna_valor": "ST_ATEND_AMBULATORIAL"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "medidores_inteligentes_agua": {
            "tipo_calculo": "direto", 
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "indice_hidrometracao"
            }
        },
        "areas_cobertas_cameras": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Base_MUNIC - indicador não confirmado no layout explorado"
            },
            "denominador": "Área Total do Município (IBGE)",
            "multiplicador": 100
        },
        "lixeiras_sensores": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "SINISA Resíduos - indicador não confirmado"
            },
            "denominador": "Total Lixeiras (SINISA)",
            "multiplicador": 100
        },
        "semaforos_inteligentes": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Base_MUNIC - coluna sem confirmação suficiente"
            },
            "denominador": "Total Semáforos (Denatran)",
            "multiplicador": 100
        },
        "frota_onibus_zero_emissao": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Frota por município - layout sem código IBGE confirmado"
            },
            "denominador": "Total Ônibus (Senatran)",
            "multiplicador": 100
        },
        "escolas_conectadas_telegestao": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mtic12a1",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0}
            },
            "denominador": "Total Escolas (INEP)",
            "multiplicador": 100
        },
        "seguros_ameacas": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "SUSEP"},
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "empregos_informais": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "indtrabintermitente"
            },
            "denominador": "forca_de_trabalho",
            "multiplicador": 100
        }
    },

    # ------------------------------------------
    # 🚨 RESILIÊNCIA A DESASTRES (ISO 37123)
    # ------------------------------------------
    "resiliencia_desastres": {
        "escolas_plano_emergencia": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Evento climático RS - layout não numérico confirmado"
            },
            "denominador": "Total Escolas (INEP)",
            "multiplicador": 100
        },
        "populacao_treinada_emergencia": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Evento climático RS - layout não numérico confirmado"
            },
            "denominador": "populacao_total",
            "multiplicador": 100
        },
        "hospitais_gerador_backup": {
            "tipo_calculo": "porcentagem",
            "numerador": {
                "arquivo": "CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv",
                "coluna_codigo": "CO_IBGE",
                "coluna_valor": "ST_ATEND_HOSPITALAR"
            },
            "denominador": "Total Hospitais (CNES)",
            "multiplicador": 100
        },
        "seguro_saude_basico": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "ANS (Vidas Seguradas)"},
            "denominador": "populacao_total",
            "multiplicador": 100
        },
        "taxa_imunizacao": {
            "tipo_calculo": "direto",
            "status": "pendente_confirmacao_fonte",
            "variavel_direta": {"arquivo": "NÃO_BAIXADO", "fonte": "DataSUS PNI"}
        },
        "abrigos_emergencia": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Evento climático RS - layout não numérico confirmado"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "edificios_vulneraveis": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Evento climático RS - layout não numérico confirmado"
            },
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "rotas_evacuacao": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Evento climático RS - layout não numérico confirmado"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "reservas_alimentos_72h": {
            "tipo_calculo": "direto",
            "status": "pendente_confirmacao_fonte",
            "variavel_direta": {"arquivo": "NÃO_BAIXADO", "fonte": "Defesa Civil"}
        },
        "mapas_ameacas_publicos": {
            "tipo_calculo": "direto",
            "status": "pendente_confirmacao_fonte",
            "variavel_direta": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Evento climático RS - layout não numérico confirmado"
            }
        },
        "mortalidade_desastres": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "S2ID (Óbitos)"},
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "pessoas_afetadas_desastres": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "S2ID (Desalojados/Desabrigados)"},
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "perdas_desastres_pib": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "S2ID (Danos Materiais R$)"},
            "denominador": "pib_absoluto",
            "multiplicador": 100
        },
        "danos_infraestrutura": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {
                "arquivo": "NÃO_BAIXADO",
                "fonte": "Evento climático RS - layout não numérico confirmado"
            },
            "denominador": "Infraestrutura Total Declarada",
            "multiplicador": 100
        }
    },

    # ------------------------------------------
    # 📶 CONECTIVIDADE
    # ------------------------------------------
    "conectividade": {
        "densidade_banda_larga": {
            "tipo_calculo": "direto", 
            "variavel_direta": {
                "arquivo": "acessos_banda_larga_fixa/Densidade_Banda_Larga_Fixa.csv",
                "coluna_codigo": "Código IBGE",
                "coluna_valor": "Densidade",
                "pandas_kwargs": {}
            }
        }
    }
}