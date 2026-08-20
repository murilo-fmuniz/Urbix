# Matriz de Fontes Públicas para o Urbix

## Objetivo

Mapear as principais fontes públicas brasileiras que podem alimentar o ranking municipal multicritério do projeto Urbix, com foco em indicadores úteis para o método TOPSIS, cobertura por município e viabilidade de ETL.

## Visão geral

A arquitetura mais adequada para o projeto é híbrida:
- dados locais e planilhas internas quando disponíveis;
- APIs públicas do governo quando houver cobertura municipal e atualização consistente;
- tratamento explícito de ausência de dado, sem converter valores faltantes em zero;
- priorização de indicadores que realmente tenham cobertura em município por município.

## Estado atual da matriz TOPSIS

A revisão atual da base mostrou que a matriz deve operar apenas com indicadores com fonte mapeada e status validado. Nesta etapa, os indicadores liberados para a matriz são:

- bombeiros
- consultas_remotas
- densidade_banda_larga
- empregos_informais
- empregos_tic
- escolas_conectadas_telegestao
- homicidios
- hospitais_gerador_backup
- ideb_iniciais
- iluminacao_telegestao
- medidores_inteligentes_agua
- moradias_inadequadas
- orcamento_per_capita
- prontuario_eletronico
- relacao_estudante_professor
- sem_teto
- servicos_urbanos_online
- sobrevivencia_negocios
- taxa_desemprego

Indicadores ainda pendentes de confirmação de fonte, mapeamento municipal ou status final para uso no cálculo:

- abrigos_emergencia
- acidentes_industriais
- agentes_policia
- areas_cobertas_cameras
- condenacoes_corrupcao
- danos_infraestrutura
- despesas_capital
- edificios_verdes
- edificios_vulneraveis
- energia_residuos
- escolas_plano_emergencia
- frota_onibus_zero_emissao
- graduados_stem
- lixeiras_sensores
- mapas_ameacas_publicos
- medidores_inteligentes_energia
- monitoramento_ar
- mortalidade_desastres
- mortes_incendio
- mulheres_eleitas
- participacao_eleitoral
- perdas_desastres_pib
- pessoas_afetadas_desastres
- populacao_treinada_emergencia
- receita_propria
- reservas_alimentos_72h
- rotas_evacuacao
- seguro_saude_basico
- seguros_ameacas
- semaforos_inteligentes
- taxa_endividamento
- taxa_imunizacao

A regra metodológica é simples: ausência de suporte documental não vira zero e nem entra no ranking antes de ser validada.

---

## Matriz principal de fontes

| Prioridade | Categoria | Fonte | URL oficial | Tipo | Cobertura | Atualização | Indicadores relevantes | Viabilidade ETL | Observações |
|---|---|---|---|---|---|---|---|---|---|
| Alta | Demografia / Economia | IBGE - SIDRA | https://servicodados.ibge.gov.br/api/v3/agregados | API REST JSON | Nacional, municipal | anual e periódica | população total, PIB, renda, densidade, estrutura urbana | Alta | Fonte central para normalização e denominadores do modelo |
| Alta | Economia | IBGE - Cidades e Estados | https://www.ibge.gov.br/estatisticas/sociais/ | Portal + dados | Nacional, municipal | anual | PIB, renda, emprego, infraestrutura básica | Alta | Boa base para dados municipais consolidados |
| Alta | Finanças públicas | SICONFI / Tesouro Nacional | https://apidatalake.tesouro.gov.br/ords/siconfi/tt/ | API JSON | Municípios brasileiros | anual / trimestral | receita, despesa, investimento, dívida, gasto com pessoal | Alta | Muito importante para governança e sustentabilidade fiscal |
| Alta | Educação | INEP | https://download.inep.gov.br/dados_abertos/ e http://api.dadosabertosinep.org/v1/ | CSV/JSON | Municipal, escolar | anual | IDEB, abandono, proficiência, estrutura escolar | Alta | Excelente para capital humano e educação |
| Alta | Saúde | DATASUS / Tabnet / SIM / SIH | http://tabnet.datasus.gov.br/ | CSV/DBF/DBC | municipal | mensal/anual | mortalidade infantil, internações, doenças, saúde básica | Média/Alta | Exige cuidado na leitura de bases antigas e códigos municipais |
| Alta | Segurança | Sinesp / MJSP | portals do Ministério da Justiça e Segurança Pública | CSV/JSON | municipal | mensal | homicídios, furto, roubo, violência | Média/Alta | Bom para segurança, mas depende de padronização dos arquivos |
| Alta | TrabalhO / emprego | MTE / Novo CAGED / RAIS | http://pdet.mte.gov.br/novo-caged e ftp://ftp.mtps.gov.br/pdet/microdados/RAIS/ | TXT/CSV | municipal | mensal/anual | empregos formais, saldo de empregos, salário | Média | Volume alto; ETL mais complexo |
| Alta | Infraestrutura elétrica | ANEEL | https://dadosabertos.aneel.gov.br/ | CKAN API / CSV | municipal | mensal/anual | DEC, FEC, interrupções, qualidade do serviço | Alta | Muito útil para infraestrutura e qualidade urbana |
| Média | Meio ambiente | MapBiomas | https://brasil.mapbiomas.org/ | rasters e dados geoespaciais | municipal, territorial | anual | cobertura vegetal, desmatamento, uso do solo | Média | Exige processamento geoespacial |
| Média | Meio ambiente | MMA / dados ambientais | portais do Ministério do Meio Ambiente | CSV/geo | municipal | anual | saneamento, resíduos, áreas protegidas, risco ambiental | Média | Importante para sustentabilidade urbana |
| Média | Governança democrática | TSE | https://dadosabertos.tse.jus.br/ | API/CSV | municipal | eleitoral/anual | abstenção, participação, candidaturas e eleitos | Alta | Muito bom para governança e participação cidadã |
| Média | Justiça / governança | CNJ / DataJud | http://www.cnj.jus.br/ | dados institucionais | municipal, judiciário | anual | processos, morosidade, judicialização | Média | relevante, mas menos central para o ranking básico |
| Média | Saneamento / moradia | SNIS / Ministério das Cidades | https://www.gov.br/mdr/pt-br/assuntos/saneamento | CSV/API | município | anual | saneamento, abastecimento, esgoto, coleta | Média/Alta | essencial para qualidade urbana |
| Média | Habitação | IBGE / Censo / PNAD | https://www.ibge.gov.br/ | microdados + agregados | municipal | periódica | domicílios, moradia precária, acesso à infraestrutura | Média | muito útil para moradia e urbanismo |
| Média | Infraestrutura urbana | Cadastro Único / outros dados municipais | dados federais e municipais | CSV/TXT | municipal | variável | população em situação vulnerável, cadastro social | Média | depende de qualidade do dado e do mapeamento |

---

## Categorias do Urbix e fontes mais adequadas

### 1) Economia e emprego
- IBGE - SIDRA
- MTE - CAGED / RAIS
- SICONFI
- IBGE - Cidades

Indicadores-chave:
- PIB per capita
- emprego formal
- rendimento
- crescimento econômico
- investimento público

### 2) Educação
- INEP
- IBGE

Indicadores-chave:
- IDEB
- taxa de evasão
- média de alunos por turma
- infraestrutura escolar

### 3) Saúde
- DATASUS
- SIM / SIH
- IBGE

Indicadores-chave:
- mortalidade infantil
- internações sensíveis
- taxa de mortalidade
- atendimento básico

### 4) Segurança
- Sinesp / MJSP
- TSE (governança/instituições)

Indicadores-chave:
- homicídios
- roubos
- violência urbana
- presença institucional

### 5) Finanças e governança
- SICONFI
- TSE
- CNJ

Indicadores-chave:
- gasto com pessoal
- investimento
- receitas próprias
- participação eleitoral

### 6) Infraestrutura urbana e saneamento
- ANEEL
- SNIS
- IBGE
- MapBiomas

Indicadores-chave:
- qualidade da energia
- saneamento
- moradia inadequada
- uso do solo

### 7) Meio ambiente e sustentabilidade
- MapBiomas
- MMA
- IBGE

Indicadores-chave:
- desmatamento
- cobertura vegetal
- risco ambiental
- área urbana e áreas protegidas

---

## Prioridade de implementação para o projeto

### Alta prioridade
Essas fontes devem entrar primeiro no ETL e no ranking:
1. IBGE - SIDRA
2. SICONFI
3. INEP
4. DATASUS
5. MTE - CAGED / RAIS
6. ANEEL
7. TSE
8. Sinesp / MJSP

### Média prioridade
1. MapBiomas
2. MMA
3. SNIS
4. CNJ
5. IBGE - Censo / PNAD

### Baixa prioridade
1. dados complementares municipais
2. bases mais dispersas e menos padronizadas
3. indicadores de nicho ou pouco consistentes no nível municipal

---

## Recomendação de arquitetura ETL

O melhor desenho para o Urbix é:

1. Fonte primária local
   - quando o dado já estiver baixado e padronizado no datalake

2. Fonte pública oficial via API
   - quando houver disponibilidade robusta e código IBGE municipal

3. Tratamento de missing data
   - ausência de dado não vira zero
   - o dado deve ficar ausente e ser tratado na camada analítica

4. Padronização de códigos geográficos
   - conversão para código IBGE de 7 dígitos
   - unificação de nomenclaturas e anos de referência

5. Normalização por município
   - usar população como denominador sempre que necessário
   - calcular indicadores do tipo taxa, percentual ou per capita

6. Aplicação do TOPSIS somente sobre colunas informativas
   - excluir colunas com dados faltantes massivos ou sem variação real

---

## Conclusão

O projeto Urbix tem um conjunto muito forte de fontes públicas disponíveis para alimentar um ranking municipal multicritério. A combinação de IBGE, SICONFI, INEP, DATASUS, ANEEL, MTE, TSE e Sinesp cobre a maior parte das dimensões relevantes do modelo.

A direção correta não é zerar dados ausentes; a direção correta é ampliar a cobertura com fontes oficiais, padronizar os indicadores e tratar ausência como informação metodológica, preservando a integridade do cálculo TOPSIS.

---

## Mapeamento indicador x fonte pública

A tabela abaixo conecta cada indicador do sistema Urbix à fonte pública mais adequada para alimentar o ETL e o cálculo TOPSIS, mantendo a lógica de usar dados reais quando existirem e registrar ausência quando não houver suporte.

| Indicador Urbix | Categoria | Fonte principal | Fonte alternativa | Observação |
|---|---|---|---|---|
| taxa_desemprego | Economia | IBGE / SIDRA + CAGED | MTE | Pode ser calculado como população ocupada/força de trabalho por município |
| taxa_endividamento | Economia | SICONFI | Tesouro / RREO | Indicador fiscal; deve usar dívida consolidada sobre receita total |
| despesas_capital | Economia | SICONFI | Tesouro | Orçamento e investimento municipal |
| receita_propria | Economia | SICONFI | Tesouro | Receita própria sobre receita total |
| orcamento_per_capita | Economia | IBGE | SICONFI | Variável direta ou calculada por município |
| mulheres_eleitas | Economia / Governança | TSE | Tribunal Superior Eleitoral | Proporção de candidatas eleitas por município |
| condenacoes_corrupcao | Economia / Justiça | CNJ | DataJud | Indicador sensível e menos difundido; uso por município é mais difícil |
| participacao_eleitoral | Governança | TSE | IBGE | Relação entre eleitores aptos e comparecimento eleitoral |
| moradias_inadequadas | Urbanismo / Habitação | IBGE / Censo | MUNIC_2024 | Base local já mapeada pela estrutura atual |
| sem_teto | Urbanismo / Habitação | Cadastro Único | IBGE / dados sociais | Mede população em situação de vulnerabilidade urbana |
| bombeiros | Segurança / Infraestrutura | MUNIC_2024 | Corpo de Bombeiros / dados locais | Recurso humano de proteção civil |
| mortes_incendio | Segurança / Saúde | DATASUS / SIM | Defesa Civil | Taxa por 100 mil habitantes |
| agentes_policia | Segurança | dados municipais / MJSP | Sinesp | Pode ser variável de cobertura institucional |
| homicidios | Segurança | Sinesp / MJSP | FBSP | Fonte já usada no projeto e excelente para comparação municipal |
| acidentes_industriais | Trabalho / Segurança | Ministério do Trabalho | MTE / CAGED | Indicador de risco ocupacional |
| relacao_estudante_professor | Educação | INEP | Censo Escolar | Indicador de carga docente e escala escolar |
| ideb_iniciais | Educação | INEP | MEC | Indicador de desempenho educacional municipal |
| sobrevivencia_negocios | Economia / Emprego | CAGED / RAIS | MTE | Indicador de continuidade do negócio e formalização |
| empregos_tic | Emprego / Inovação | CAGED / RAIS | MTE | Empregos em área de tecnologia e inovação |
| graduados_stem | Educação / Inovação | INEP | MEC | Número de graduados em áreas STEM por município |
| energia_residuos | Sustentabilidade | SNIS / MMA | ANEEL | Indicador de resíduos e energia; depende de dado municipal confiável |
| iluminacao_telegestao | Smart city | MUNIC_2024 | dados municipais | Base já mapeada e apta a uso direto |
| medidores_inteligentes_energia | Smart city | ANEEL | dados municipais / distribuidoras | Cobertura de medição inteligente e gestão energética |
| edificios_verdes | Sustentabilidade | GBC Brasil | IBGE | Uso de certificação ambiental em edifícios |
| monitoramento_ar | Meio ambiente | MMA | INEA / CETESB / estados | Indicadores de qualidade do ar ou rede de monitoramento |
| servicos_urbanos_online | Smart city | MUNIC_2024 | dados municipais | Mapeamento da presença digital dos serviços municipais |
| prontuario_eletronico | Saúde digital | CNES | DATASUS | Indicador de digitalização da atenção básica |
| consultas_remotas | Saúde digital | CNES | DATASUS | Acesso remoto à saúde ou telemedicina |
| medidores_inteligentes_agua | Saneamento / Smart city | SNIS | ANA / municípios | Recurso de hidrômetros e gestão de água |
| areas_cobertas_cameras | Segurança / Smart city | dados municipais | segurança pública | Indicador de cobertura de vigilância urbana |
| lixeiras_sensores | Saneamento / Smart city | SINISA / MMA | municípios | Indicador de coleta inteligente e gestão de resíduos |
| semaforos_inteligentes | Mobilidade / Smart city | Denatran / municípios | dados urbanos | Cobertura de semáforos inteligentes |
| frota_onibus_zero_emissao | Mobilidade | Denatran / municípios | transporte público | Indicador de modernização da frota |
| escolas_conectadas_telegestao | Educação digital | MUNIC_2024 | INEP | Conectividade e gestão digital escolar |
| seguros_ameacas | Resiliência | SUSEP | mercados / seguradoras | Indicador de proteção e capacidade de resposta |
| empregos_informais | Trabalho | CAGED / RAIS | MTE | Percentual de trabalhadores sem vínculo formal |
| escolas_plano_emergencia | Resiliência | Defesa Civil | MEC / escolas | Cobertura de plano de emergência nas escolas |
| populacao_treinada_emergencia | Resiliência | Defesa Civil | municípios | Capacitação da população em risco |
| hospitais_gerador_backup | Saúde / Resiliência | CNES | DATASUS | infraestrutura hospitalar de respaldo |
| seguro_saude_basico | Saúde / Resiliência | ANS | DATASUS | cobertura de saúde suplementar / assistência |
| taxa_imunizacao | Saúde | DATASUS / PNI | MS | Indicador de imunização por município |
| abrigos_emergencia | Resiliência | Defesa Civil | municípios | estrutura de apoio e abrigo |
| edificios_vulneraveis | Urbanismo / risco | Defesa Civil | municípios | vulnerabilidade de edificações e risco urbano |
| rotas_evacuacao | Resiliência | Defesa Civil | municípios | planejamento e capacidade de evacuação |
| reservas_alimentos_72h | Resiliência | Defesa Civil | municípios | logística de suprimento e contingência |
| mapas_ameacas_publicos | Resiliência | Defesa Civil | municípios | disponibilidade de mapas de risco |
| mortalidade_desastres | Resiliência / Saúde | S2ID | Defesa Civil | óbitos por eventos de desastre |
| pessoas_afetadas_desastres | Resiliência | S2ID | Defesa Civil | desalojados/desabrigados e afetados |
| perdas_desastres_pib | Resiliência / Economia | S2ID | Defesa Civil | perdas materiais sobre PIB municipal |
| danos_infraestrutura | Resiliência | Defesa Civil | municípios | dano material em infraestrutura pública |
| densidade_banda_larga | Conectividade | dados públicos de telecom | ANATEL | acessos de banda larga por município |

### Prioridade de integração por bloco

| Bloco | Indicadores principais | Fontes recomendadas | Prioridade |
|---|---|---|---|
| Base municipal e normalização | população_total, pib_absoluto, total_domicilios, forca_de_trabalho | IBGE, SIDRA | Alta |
| Finanças e governança | taxa_endividamento, despesas_capital, receita_propria, mulheres_eleitas, participacao_eleitoral | SICONFI, TSE, CNJ | Alta |
| Educação e inovação | ideb_iniciais, relacao_estudante_professor, graduados_stem, empregos_tic | INEP, MEC, CAGED | Alta |
| Saúde e segurança | homicidios, mortalidade_desastres, mortes_incendio, taxa_imunizacao | DATASUS, SIM, Sinesp, FBSP | Alta |
| Infraestrutura e smart city | medidores_inteligentes_energia, medidores_inteligentes_agua, servicos_urbanos_online, semaforos_inteligentes | ANEEL, SNIS, MUNIC_2024 | Média/Alta |
| Resiliência | abrigos_emergencia, rotas_evacuacao, reservas_alimentos_72h, perdas_desastres_pib | Defesa Civil, S2ID | Média |
| Meio ambiente | monitoramento_ar, energia_residuos, areas_cobertas_cameras | MMA, MapBiomas, SNIS | Média |

## Sugestão final para o desenvolvimento

Para a próxima fase de implementação, eu priorizaria esta ordem de integração:

1. IBGE + população/PIB
2. SICONFI + finanças
3. INEP + educação
4. DATASUS + saúde
5. ANEEL + infraestrutura
6. MTE + emprego
7. TSE + governança
8. Sinesp + segurança
9. MapBiomas + meio ambiente
10. SNIS + saneamento

Isso entrega um núcleo forte, comparável e defensável para o artigo e para a banca.
