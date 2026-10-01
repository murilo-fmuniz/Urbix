# Auditoria do ETL Urbix — Relatório para a IC

> Gerado em 30/09/2026 21:46:34 a partir do PostgreSQL do backend.

## Resumo executivo

- Municípios cadastrados: **5.571**
- Registros históricos com valor: **130.890**
- Registros no snapshot atual: **130.890**
- Indicadores configurados: **65**
- APIs SIDRA configuradas: **4**
- SICONFI habilitado: **sim**

A cobertura abaixo usa `valores_indicadores_latest`, o valor mais recente usado pelo TOPSIS.

## Cobertura por eixo

| Eixo | Com dados | Configurados | Cobertura média | Melhor | Menor |
|---|---:|---:|---:|---:|---:|
| Economia e Governança | 4 | 8 | 39,37% | 99,98% | 0,00% |
| Sociedade e Segurança | 3 | 7 | 28,56% | 99,71% | 0,00% |
| Educação e Inovação | 1 | 5 | 20,00% | 100,00% | 0,00% |
| Sustentabilidade e Smart City | 11 | 26 | 36,79% | 99,71% | 0,00% |
| Resiliência e Desastres | 3 | 14 | 1,52% | 8,90% | 0,00% |
| Conectividade | 1 | 1 | 99,98% | 99,98% | 99,98% |
| Bases de normalização | 4 | 4 | 99,99% | 100,00% | 99,98% |

## Indicadores ativos e cobertura municipal

| Eixo | Indicador | Municípios | Cobertura | Ano mais recente | Fonte |
|---|---|---:|---:|---:|---|
| Bases de normalização | `populacao_total` | 5.571 | 100,00% | 2025 | SIDRA (6579) |
| Educação e Inovação | `relacao_estudante_professor` | 5.571 | 100,00% | 2024 | ATU_2025_MUNICIPIOS/ATU_MUNICIPIOS_2025.xlsx |
| Conectividade | `densidade_banda_larga` | 5.570 | 99,98% | 2024 | acessos_banda_larga_fixa/Acessos_Banda_Larga_Fixa_2021.csv |
| Bases de normalização | `forca_de_trabalho` | 5.570 | 99,98% | 2022 | SIDRA Censo (6580) |
| Economia e Governança | `orcamento_per_capita` | 5.570 | 99,98% | 2023 | PIB_Municipios/base_de_dados_2010_2023_xlsx/PIB dos Municípios - base de dados 2010-2023.xlsx |
| Bases de normalização | `pib_absoluto` | 5.570 | 99,98% | 2023 | SIDRA (5938) |
| Bases de normalização | `total_domicilios` | 5.570 | 99,98% | 2022 | SIDRA Censo (9922) |
| Sociedade e Segurança | `bombeiros` | 5.555 | 99,71% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Sustentabilidade e Smart City | `estrutura_tic_municipal` | 5.555 | 99,71% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Sociedade e Segurança | `agentes_policia` | 5.554 | 99,69% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Sustentabilidade e Smart City | `atendimento_agua_snis` | 5.542 | 99,48% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Sustentabilidade e Smart City | `medidores_inteligentes_agua` | 5.542 | 99,48% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Sustentabilidade e Smart City | `despesa_saneamento_snis` | 5.540 | 99,44% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Sustentabilidade e Smart City | `perdas_distribuicao_agua_snis` | 5.538 | 99,41% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Sustentabilidade e Smart City | `investimento_saneamento_snis` | 5.528 | 99,23% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Sustentabilidade e Smart City | `servicos_informativos_municipio` | 5.492 | 98,58% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Economia e Governança | `taxa_geracao_empregos` | 5.482 | 98,40% | 2024 | CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt |
| Sustentabilidade e Smart City | `canal_telefonico_municipal` | 4.275 | 76,74% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Sustentabilidade e Smart City | `atendimento_esgoto_snis` | 3.453 | 61,98% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Sustentabilidade e Smart City | `tratamento_esgoto_snis` | 3.420 | 61,39% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Sustentabilidade e Smart City | `coleta_esgoto_snis` | 3.408 | 61,17% | 2022 | SNIS/br_mdr_snis_municipio_agua_esgoto.csv.gz |
| Economia e Governança | `despesas_capital` | 3.254 | 58,41% | 2023 | SICONFI - Investimentos |
| Economia e Governança | `receita_propria` | 3.241 | 58,18% | 2023 | SICONFI - Impostos Municipais |
| Resiliência e Desastres | `mapas_ameacas_publicos` | 496 | 8,90% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Resiliência e Desastres | `rotas_evacuacao` | 403 | 7,23% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Resiliência e Desastres | `abrigos_emergencia` | 289 | 5,19% | 2024 | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx |
| Sociedade e Segurança | `homicidios` | 27 | 0,48% | 2024 | FBSP/br_fbsp_absp_municipio.csv/br_fbsp_absp_municipio.csv |

## Indicadores pendentes ou sem dados atuais

| Eixo | Indicador | Status | Arquivo/fonte | Motivo |
|---|---|---|---|---|
| Economia e Governança | `condenacoes_corrupcao` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Economia e Governança | `mulheres_eleitas` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Economia e Governança | `participacao_eleitoral` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Economia e Governança | `taxa_endividamento` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Educação e Inovação | `empregos_tic` | pendente_filtro_cbo | CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt | status pendente |
| Educação e Inovação | `graduados_stem` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Educação e Inovação | `ideb_iniciais` | pendente_arquivo_ausente | divulgacao_anos_iniciais_municipios_2023/divulgacao_anos_iniciais_municipios_2023.xlsx | status pendente |
| Educação e Inovação | `sobrevivencia_negocios` | pendente_proxy_inadequado | CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt | status pendente |
| Resiliência e Desastres | `danos_infraestrutura` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `edificios_vulneraveis` | pendente_coluna_semantica | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx | status pendente |
| Resiliência e Desastres | `escolas_plano_emergencia` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `hospitais_gerador_backup` | pendente_proxy_inadequado | CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv | status pendente |
| Resiliência e Desastres | `mortalidade_desastres` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `perdas_desastres_pib` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `pessoas_afetadas_desastres` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `populacao_treinada_emergencia` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `reservas_alimentos_72h` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `seguro_saude_basico` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Resiliência e Desastres | `taxa_imunizacao` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sociedade e Segurança | `acidentes_industriais` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sociedade e Segurança | `homicidios` | pendente_cobertura_insuficiente | FBSP/br_fbsp_absp_municipio.csv/br_fbsp_absp_municipio.csv | status pendente |
| Sociedade e Segurança | `moradias_inadequadas` | pendente_coluna_semantica | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx | status pendente |
| Sociedade e Segurança | `mortes_incendio` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sociedade e Segurança | `sem_teto` | pendente_arquivo_ausente | cad_unico/cad_unico.txt | status pendente |
| Sustentabilidade e Smart City | `areas_cobertas_cameras` | pendente_coluna_semantica | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx | status pendente |
| Sustentabilidade e Smart City | `consultas_remotas` | pendente_proxy_inadequado | CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv | status pendente |
| Sustentabilidade e Smart City | `edificios_vulneraveis` | pendente_coluna_semantica | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx | status pendente |
| Sustentabilidade e Smart City | `empregos_informais` | pendente_proxy_inadequado | CAGED_RAIS/Caged (2026)/CAGEDMOV202605/CAGEDMOV202605.txt | status pendente |
| Sustentabilidade e Smart City | `energia_residuos` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sustentabilidade e Smart City | `escolas_conectadas_telegestao` | pendente_coluna_semantica | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx | status pendente |
| Sustentabilidade e Smart City | `frota_onibus_zero_emissao` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sustentabilidade e Smart City | `iluminacao_telegestao` | pendente_coluna_semantica | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx | status pendente |
| Sustentabilidade e Smart City | `lixeiras_sensores` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sustentabilidade e Smart City | `medidores_inteligentes_energia` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sustentabilidade e Smart City | `monitoramento_ar` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sustentabilidade e Smart City | `prontuario_eletronico` | pendente_proxy_inadequado | CNES/cnes_estabelecimentos_csv/cnes_estabelecimentos.csv | status pendente |
| Sustentabilidade e Smart City | `seguros_ameacas` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sustentabilidade e Smart City | `semaforos_inteligentes` | pendente_confirmacao_fonte | NÃO_BAIXADO | status pendente |
| Sustentabilidade e Smart City | `servicos_urbanos_online` | pendente_coluna_semantica | MUNIC_2024/Base_MUNIC_2024_20251107.xlsx | status pendente |

## Volume por fonte

| Fonte | Registros | Indicadores | Municípios |
|---|---:|---:|---:|
| Base_MUNIC_2024_20251107.xlsx | 38.666 | 10 | 5.558 |
| br_mdr_snis_municipio_agua_esgoto.csv.gz | 37.971 | 8 | 5.545 |
| API SICONFI / RREO-01 | 9.752 | 3 | 3.257 |
| ATU_MUNICIPIOS_2025.xlsx | 5.571 | 1 | 5.571 |
| SIDRA (6579) | 5.571 | 1 | 5.571 |
| SIDRA Censo (6580) | 5.570 | 1 | 5.570 |
| SIDRA (5938) | 5.570 | 1 | 5.570 |
| Acessos_Banda_Larga_Fixa_2021.csv | 5.570 | 1 | 5.570 |
| PIB dos Municípios - base de dados 2010-2023.xlsx | 5.570 | 1 | 5.570 |
| SIDRA Censo (9922) | 5.570 | 1 | 5.570 |
| CAGEDMOV202605.txt | 5.482 | 1 | 5.482 |
| br_fbsp_absp_municipio.csv | 27 | 1 | 27 |

## APIs e persistência

| API | Situação |
|---|---|
| SIDRA/IBGE | Executada no `run()` e gravada em `valores_indicadores` |
| SICONFI/Tesouro | Habilitada; retries e substituição por ano |

## Notas metodológicas

- Cobertura = municípios com valor no snapshot / total de municípios.
- Ausência não foi convertida em zero nesta auditoria.
- MUNIC binário aparece como 0/1 e representa presença/ausência.
- SNIS usa o último ano disponível por município.
- CAGED representa saldo de movimentações formais, não desemprego populacional.
- Eventos climáticos possuem cobertura regional.
