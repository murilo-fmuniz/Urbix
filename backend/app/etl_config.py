"""
Configuração central de roteamento do Datalake Urbix.
Mapeamento com a estrutura completa de todos os indicadores das normas ISO.
Indicadores sem dados recebem a flag "NÃO_BAIXADO" e são ignorados em tempo de execução pelo ETL.
"""

# ==========================================
# 📊 1. DADOS BASE (Variáveis de Normalização)
# ==========================================
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
        "coluna_valor": "Produto Interno Bruto, a preços correntes (R$ 1.000)",
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
# 🎯 2. INDICADORES TOPSIS (Estrutura Completa)
# ==========================================
INDICADORES = {
    
    # ------------------------------------------
    # 💰 ECONOMIA E GOVERNANÇA
    # ------------------------------------------
    "economia": {
        "taxa_geracao_empregos": { # 🚀 NOME ALTERADO AQUI!
            "tipo_calculo": "taxa_100k",
            "status": "validado_localmente",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "saldomovimentação" # 🚀 VOLTAMOS PARA O SALDO!
            },
            "denominador": "forca_de_trabalho",
            "multiplicador": 100000
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
            "status": "validado_via_api_siconfi", # <-- Mude o status!
            "numerador": {"arquivo": "API", "fonte": "SICONFI - Investimentos"},
            "denominador": "receita_total_municipio",
            "multiplicador": 100
        },
        "receita_propria": {
            "tipo_calculo": "porcentagem",
            "status": "validado_via_api_siconfi", # <-- Mude o status!
            "numerador": {"arquivo": "API", "fonte": "SICONFI - Impostos Municipais"},
            "denominador": "receita_total_municipio",
            "multiplicador": 100
        },
        "orcamento_per_capita": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "PIB_Municipios/base_de_dados_2010_2023_xlsx/PIB dos Municípios - base de dados 2010-2023.xlsx",
                "coluna_codigo": "Código do Município",
                "coluna_valor": "Produto Interno Bruto per capita, a preços correntes (R$ 1,00)",
                "coluna_ano": "Ano",
                "filtros": {"Ano": 2023},
                "agregacao": "latest"
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
            "tipo_calculo": "direto", 
            "status": "pendente_coluna_semantica",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mhab03",
                "pandas_kwargs": {"sheet_name": "Habitacao", "header": 0}
            }
        },
        "sem_teto": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_arquivo_ausente",
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
            "status": "validado_localmente", 
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "MREH012", 
                "pandas_kwargs": {"sheet_name": "Recursos humanos", "header": 0}
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "homicidios": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_cobertura_insuficiente",
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
            "status": "pendente_confirmacao_fonte", # Manter pendente até mapearmos o Ministério do Trabalho
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
            "status": "pendente_arquivo_ausente",
            "variavel_direta": {
                "arquivo": "divulgacao_anos_iniciais_municipios_2023/divulgacao_anos_iniciais_municipios_2023.xlsx",
                "coluna_codigo": "CO_MUNICIPIO",
                "coluna_valor": "IDEB 2023 (N x P)",
                "pandas_kwargs": {"sheet_name": "IDEB_AI_MUNICÍPIOS", "header": 9}
            }
        },
        "sobrevivencia_negocios": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_proxy_inadequado",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "saldomovimentação"
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "empregos_tic": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_filtro_cbo",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "saldomovimentação" 
            },
            "denominador": "forca_de_trabalho",
            "multiplicador": 100000
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
    # 🌳 SUSTENTABILIDADE E SMART CITY
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
            "tipo_calculo": "direto", 
            "status": "pendente_coluna_semantica",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "Cod Munic",
                "coluna_valor": "Mtic06",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0}
            }
        },
        "medidores_inteligentes_energia": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "ANEEL"},
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "edificios_vulneraveis": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_coluna_semantica",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mers10", 
                "pandas_kwargs": {"sheet_name": "Evento climático RS", "header": 0}
            },
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "monitoramento_ar": {
            "tipo_calculo": "direto",
            "status": "pendente_confirmacao_fonte",
            "variavel_direta": {"arquivo": "NÃO_BAIXADO", "fonte": "Ministério do Meio Ambiente"}
        },
        "servicos_urbanos_online": {
            "tipo_calculo": "direto",
            "status": "pendente_coluna_semantica",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "Cod Munic",
                "coluna_valor": "Mtic10",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0}
            }
        },
        "prontuario_eletronico": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_proxy_inadequado",
            "numerador": {
                "arquivo": "CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv",
                "coluna_codigo": "CO_IBGE",
                "coluna_valor": "ST_ATEND_AMBULATORIAL",
                "pandas_kwargs": {"encoding": "latin1", "sep": ";"} 
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "consultas_remotas": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_proxy_inadequado",
            "numerador": {
                "arquivo": "CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv",
                "coluna_codigo": "CO_IBGE",
                "coluna_valor": "ST_ATEND_AMBULATORIAL",
                "pandas_kwargs": {"encoding": "latin1", "sep": ";"} 
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
        },
        "medidores_inteligentes_agua": {
            "tipo_calculo": "direto", 
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "indice_hidrometracao",
                "coluna_ano": "ano",
                "agregacao": "latest",
                "faixa_valida": [0, 100]
            }
        },
        "atendimento_agua_snis": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "indice_atendimento_total_agua",
                "coluna_ano": "ano",
                "agregacao": "latest",
                "faixa_valida": [0, 100]
            }
        },
        "atendimento_esgoto_snis": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "indice_atendimento_esgoto_agua",
                "coluna_ano": "ano",
                "agregacao": "latest",
                "faixa_valida": [0, 100]
            }
        },
        "perdas_distribuicao_agua_snis": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "indice_perda_distribuicao_agua",
                "coluna_ano": "ano",
                "agregacao": "latest",
                "faixa_valida": [0, 100]
            }
        },
        "coleta_esgoto_snis": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "indice_coleta_esgoto",
                "coluna_ano": "ano",
                "agregacao": "latest",
                "faixa_valida": [0, 100]
            }
        },
        "tratamento_esgoto_snis": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "indice_tratamento_esgoto",
                "coluna_ano": "ano",
                "agregacao": "latest",
                "faixa_valida": [0, 100]
            }
        },
        "investimento_saneamento_snis": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "investimento_total_municipio",
                "coluna_ano": "ano",
                "agregacao": "latest"
            }
        },
        "despesa_saneamento_snis": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz",
                "coluna_codigo": "id_municipio",
                "coluna_valor": "despesa_total_servico",
                "coluna_ano": "ano",
                "agregacao": "latest"
            }
        },
        "estrutura_tic_municipal": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "Cod Munic",
                "coluna_valor": "Mtic06",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0},
                "mapa_qualitativo": {"Sim": "1", "Não": "0"}
            }
        },
        "servicos_informativos_municipio": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "Cod Munic",
                "coluna_valor": "Mtic12a1",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0},
                "mapa_qualitativo": {"Sim": "1", "Não": "0"}
            }
        },
        "canal_telefonico_municipal": {
            "tipo_calculo": "direto",
            "status": "validado_localmente",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "Cod Munic",
                "coluna_valor": "Mtic181",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0},
                "mapa_qualitativo": {"Sim": "1", "Não": "0"}
            }
        },
        "areas_cobertas_cameras": {
            "tipo_calculo": "direto",
            "status": "pendente_coluna_semantica",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "Cod Munic",
                "coluna_valor": "Mtic181",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0}
            }
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
            "tipo_calculo": "direto",
            "status": "pendente_coluna_semantica",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "Cod Munic",
                "coluna_valor": "Mtic12a1",
                "pandas_kwargs": {"sheet_name": "Informática e comunicação", "header": 0}
            }
        },
        "seguros_ameacas": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_confirmacao_fonte",
            "numerador": {"arquivo": "NÃO_BAIXADO", "fonte": "SUSEP"},
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "empregos_informais": {
            "tipo_calculo": "taxa_100k",
            "status": "pendente_proxy_inadequado",
            "numerador": {
                "arquivo": "CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt",
                "coluna_codigo": "município",
                "coluna_valor": "indtrabintermitente"
            },
            "denominador": "forca_de_trabalho",
            "multiplicador": 100000
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
            "tipo_calculo": "taxa_100k",
            "status": "pendente_proxy_inadequado",
            "numerador": {
                "arquivo": "CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv",
                "coluna_codigo": "CO_IBGE",
                "coluna_valor": "ST_ATEND_HOSPITALAR",
                "pandas_kwargs": {"encoding": "latin1", "sep": ";"} 
            },
            "denominador": "populacao_total",
            "multiplicador": 100000
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
            "tipo_calculo": "direto",
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mers04",
                "pandas_kwargs": {"sheet_name": "Evento climático RS", "header": 0}
            }
        },
        "edificios_vulneraveis": {
            "tipo_calculo": "porcentagem",
            "status": "pendente_coluna_semantica",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "COLE_AQUI_O_CODIGO", # Procure no .md na aba Evento climático RS
                "pandas_kwargs": {"sheet_name": "Evento climático RS", "header": 0}
            },
            "denominador": "total_domicilios",
            "multiplicador": 100
        },
        "rotas_evacuacao": {
            "tipo_calculo": "taxa_100k",
            "status": "validado_localmente",
            "numerador": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mers111", 
                "pandas_kwargs": {"sheet_name": "Evento climático RS", "header": 0}
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
            "variavel_direta": {
                "arquivo": "MUNIC_2024/Base_MUNIC_2024_20251107.xlsx",
                "coluna_codigo": "CodMun",
                "coluna_valor": "Mers01",
                "pandas_kwargs": {"sheet_name": "Evento climático RS", "header": 0}
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
            "tipo_calculo": "taxa_100", 
            "numerador": {
                "arquivo": "acessos_banda_larga_fixa/Acessos_Banda_Larga_Fixa_2021.csv",
                "coluna_codigo": "Código IBGE Município",
                "coluna_valor": "Acessos",
                "pandas_kwargs": {"sep": ";", "encoding": "utf-8"}
            },
            "denominador": "populacao_total",
            "multiplicador": 100
        }
    }
}