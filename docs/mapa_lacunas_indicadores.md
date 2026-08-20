# Mapa de lacunas dos indicadores

Legenda:
- **Coberto local** = já existe planilha/ETL local com dado aproveitável.
- **Coberto via API** = já existe integração externa estável.
- **Parcial / proxy** = existe valor, mas ainda por fallback, proxy ou campo semânticamente desalinhado.
- **Falta mapear** = não há fonte útil implementada ainda.

> Correção importante: os indicadores **[20] Energia de Resíduos** e **[30] Lixeiras com Sensores** já possuem fonte local na planilha `SINISA_RESIDUOS_Indicadores_2023.xlsx`.

| Indicador | Fonte atual | Status | Ação necessária |
|---|---|---|---|
| [0] Taxa Desemprego (%) | CAGED / ETL local (`saldo_empregos_caged`) | Parcial / proxy | Substituir proxy por dado trabalhista mais direto (RAIS/CAGED consolidado) e documentar a fórmula usada. |
| [1] Taxa Endividamento (%) | SICONFI (RGF) | Coberto via API | Manter integração e registrar a janela temporal usada. |
| [2] Despesas Capital (% orçamento) | SICONFI (RREO) | Coberto via API | Manter integração e validar consistência por exercício. |
| [3] Receita Própria (% receita total) | SICONFI (RREO) | Coberto via API | Manter integração e validar consistência por exercício. |
| [4] Orçamento per capita (R$) | SICONFI + IBGE | Coberto via API | Manter cálculo e registrar população de referência. |
| [5] Mulheres Eleitas em Cargos (%) | TSE / analytics local | Coberto via API | Consolidar a origem definitiva e remover duplicidade com fallback local. |
| [6] Condenações por Corrupção (100k hab) | CNJ | Coberto via API | Manter integração e mapear eventuais filtros por comarca/município. |
| [7] Participação Eleitoral (%) | TSE | Coberto via API | Manter integração e documentar a metodologia de agregação. |
| [8] Moradias Inadequadas (% população) | Portal da Transparência (proxy Bolsa Família) | Parcial / proxy | Trocar proxy por fonte habitacional/domiciliar mais aderente. |
| [9] Sem-teto (100k hab) | Portal da Transparência (proxy Bolsa Família) | Parcial / proxy | Mapear base específica de vulnerabilidade habitacional. |
| [10] Bombeiros (100k hab) | Sem fonte direta | Falta mapear | Buscar base estadual/Defesa Civil/Corpo de Bombeiros. |
| [11] Mortes por Incêndio (100k hab) | Sem fonte direta | Falta mapear | Procurar DATASUS/Defesa Civil/Corpo de Bombeiros. |
| [12] Agentes de Polícia (100k hab) | Sem fonte direta | Falta mapear | Buscar base oficial de segurança pública ou proxy institucional. |
| [13] Homicídios (100k hab) | DATASUS SIM (ETL local) | Coberto local | Manter ETL e validar recortes temporais. |
| [14] Acidentes Industriais (100k hab) | Ministério do Trabalho | Coberto via API | Manter integração e documentar a população usada na normalização. |
| [15] Relação Estudante/Professor | INEP (fallback estruturado) | Parcial / fallback | Extrair dado real do INEP/Censo Escolar e retirar o fallback como fonte principal. |
| [16] IDEB Anos Iniciais (escala 0-10) | INEP (fallback estruturado) | Parcial / fallback | Extrair dado real do INEP/Censo/IDEB e validar séries. |
| [17] Sobrevivência Novos Negócios (100k hab) | Sem fonte direta | Falta mapear | Buscar Junta Comercial/IBGE/Cadastro de empresas/Sebrae. |
| [18] Empregos em TIC (% força trabalho) | Sem fonte direta | Falta mapear | Mapear RAIS/CAGED por CNAE/TIC ou base equivalente. |
| [19] Graduados STEM (100k hab) | Sem fonte direta | Falta mapear | Buscar INEP/MEC por área de formação e normalizar por população. |
| [20] Energia de Resíduos (% energia total) | SINISA_RESIDUOS_Indicadores_2023.xlsx | Coberto local | Implementar extração definitiva no `process_local_data.py` e mapear o código IFR correspondente. |
| [21] Iluminação Pública com Telegestão (%) | Sem fonte direta | Falta mapear | Buscar base municipal/ANEEL/infraestrutura urbana ou manter manual. |
| [22] Medidores Inteligentes Energia (%) | ANEEL | Coberto via API | Manter integração e registrar cobertura por município. |
| [23] Edifícios Verdes Certificados (%) | Sem fonte direta | Falta mapear | Buscar certificações/registro municipal ou aceitar input manual. |
| [24] Monitoramento Ar em Tempo Real (%) | DataSUS / SICONFI proxy | Parcial / proxy | Trocar proxy por base ambiental real ou política municipal de monitoramento. |
| [25] Serviços Urbanos Online (%) | MUNIC_2024 (comunicação/informática) | Parcial / fonte disponível | Criar ETL específico para extrair a tabela certa da `MUNIC_2024`. |
| [26] Prontuário Eletrônico (% população) | Sem fonte direta | Falta mapear | Buscar e-SUS/secretarias de saúde ou base equivalente. |
| [27] Consultas Remotas (100k hab) | Sem fonte direta | Falta mapear | Buscar telemedicina/produção ambulatorial ou base municipal de saúde digital. |
| [28] Medidores Inteligentes Água (%) | DataSUS CNES / expandido | Parcial / API | Validar a métrica real do DataSUS e remover aproximações quando possível. |
| [29] Áreas Cobertas por Câmeras (% cidade) | DataSUS CNES / expandido | Parcial / API | Buscar fonte específica de segurança urbana e substituir aproximação. |
| [30] Lixeiras com Sensores (%) | SINISA_RESIDUOS_Indicadores_2023.xlsx | Coberto local | Implementar extração definitiva no `process_local_data.py` e mapear o código IRS correspondente. |
| [31] Semáforos Inteligentes (%) | MUNIC_2024 (mobilidade) / campo ainda não extraído | Parcial / fonte disponível | Criar ETL específico para mobilidade urbana e realinhar o indicador semântico. |
| [32] Frota Ônibus Zero Emissão (%) | ANTP | Coberto via API | Manter integração e documentar o corte da frota. |
| [33] Escolas Conectadas com TeleGestão (%) | INEP (fallback estruturado) | Parcial / fallback | Extrair dado real do INEP ou do Censo Escolar e manter fallback só como contingência. |
| [34] Seguros contra Ameaças (% população) | Sem fonte direta | Falta mapear | Buscar base de seguros/resiliência ou manter campo manual. |
| [35] Empregos Informais (% força trabalho) | Sem fonte direta | Falta mapear | Mapear PNAD/RAIS/CAGED com classificação de informalidade. |
| [36] Escolas com Plano Emergência (%) | Sem fonte direta | Falta mapear | Buscar base educacional ou cadastro municipal de proteção civil. |
| [37] População Treinada em Emergência (%) | Portal Transparência Expandido | Parcial / proxy | Trocar proxy por base de Defesa Civil/educação para risco. |
| [38] Hospitais com Gerador Backup (%) | Sem fonte direta | Falta mapear | Buscar CNES/infraestrutura hospitalar com gerador backup. |
| [39] Seguro Saúde Básico (% população) | Portal Transparência Expandido | Parcial / proxy | Substituir por fonte de cobertura de saúde mais aderente. |
| [40] Taxa de Imunização (%) | DataSUS expandido | Parcial / API | Validar a métrica real e eliminar aproximações/fallbacks. |
| [41] Abrigos de Emergência (100k hab) | Sem fonte direta | Falta mapear | Buscar cadastro de abrigos/Defesa Civil municipal. |
| [42] Edifícios Vulneráveis a Desastres (%) | Sem fonte direta | Falta mapear | Buscar base de risco/ocupação/Defesa Civil. |
| [43] Rotas de Evacuação Identificadas (100k) | Sem fonte direta | Falta mapear | Buscar planos de contingência e mapeamento geoespacial municipal. |
| [44] Reservas de Alimentos 72h (%) | Portal Transparência Expandido + SNIS | Parcial / API | Validar fórmula e documentar a composição com saneamento social. |
| [45] Mapas de Ameaças Públicos (%) | Sem fonte direta | Falta mapear | Buscar inventário de mapas públicos/Defesa Civil municipal. |
| [46] Mortalidade por Desastres (100k hab) | Defesa Civil / S2ID | Coberto via API | Manter integração e auditar período de ocorrência. |
| [47] Pessoas Afetadas por Desastres (100k hab) | Defesa Civil / S2ID | Coberto via API | Manter integração e auditar período de ocorrência. |
| [48] Perdas por Desastres (% PIB) | Defesa Civil / S2ID | Coberto via API | Manter integração e auditar a metodologia de perdas. |
| [49] Danos à Infraestrutura Básica (%) | Defesa Civil / S2ID | Coberto via API | Manter integração e documentar os critérios de dano. |

## leitura rápida do diagnóstico

- **Cobertos de forma satisfatória:** 17 indicadores.
- **Parciais / proxy / fallback:** 15 indicadores.
- **Ainda sem fonte implementada:** 18 indicadores.

Em outras palavras: o data lake novo já ajuda muito, mas o projeto **ainda não está 100% coberto**. Ele já fecha bem a base de saneamento, educação, saúde, energia e parte de mobilidade/conectividade, mas ainda faltam várias fontes para governança, segurança, resiliência e alguns indicadores smart-city mais específicos.
