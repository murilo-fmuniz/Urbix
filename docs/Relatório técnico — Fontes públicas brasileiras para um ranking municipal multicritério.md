# Relatório técnico — Fontes públicas brasileiras para um ranking municipal multicritério

**Escopo:** levantamento de fontes oficiais e complementares capazes de alimentar um sistema de indicadores municipais para um projeto de IC em Ciência de Dados, com foco em **TOPSIS/MCDA**, ETL reprodutível, cobertura dos municípios brasileiros e atualização automatizada.

**Data da pesquisa:** 17/08/2026.

> **Nota de escopo:** “todos os endpoints” não é uma propriedade estática do ecossistema de dados públicos brasileiro — portais alteram rotas, criam novos datasets e descontinuam arquivos. Portanto, o levantamento abaixo cobre as **principais fontes nacionais oficiais e os conjuntos que efetivamente têm potencial para um índice municipal**, incluindo APIs, portais, microdados e arquivos estruturados. Para um projeto de IC, isso é mais útil do que uma enumeração literal de milhares de arquivos.

---

# 1. Resumo executivo

A arquitetura que eu adotaria para o projeto não seria baseada em uma única API.

O desenho mais robusto é:

**IBGE → dimensão territorial/populacional e denominadores**

**SICONFI → finanças municipais**

**INEP → educação**

**DATASUS/OpenDataSUS → saúde**

**Sinesp/MJSP → segurança**

**RAIS/Novo Caged → mercado de trabalho**

**SINISA → saneamento**

**ANEEL → energia**

**ANATEL → conectividade**

**Senatran → mobilidade/frota**

**TSE → perfil eleitoral/participação política, se fizer sentido metodológico**

**Receita Federal → atividade econômica/formalização**

**MDS/CadÚnico → vulnerabilidade social**

**CNJ/DataJud → justiça**

**IBAMA/ICMBio/INPE/MCTI → meio ambiente, território e inovação**

O ponto mais importante para o ETL é estabelecer **IBGE `cod_municipio` de 7 dígitos como chave primária territorial canônica**. A API de localidades do IBGE fornece municípios, UFs e hierarquias territoriais em JSON e sem autenticação.

---

# 2. Ranking de prioridade das fontes

| Prioridade | Fonte | Motivo |
|---|---|---|
| **ALTA** | IBGE/SIDRA | População, renda, demografia, domicílios, trabalho, urbanização e denominadores |
| **ALTA** | SICONFI/STN | Receita, despesa, investimento, dívida, resultado fiscal e capacidade financeira |
| **ALTA** | INEP | IDEB, Censo Escolar, docentes, matrículas, infraestrutura e educação superior |
| **ALTA** | DATASUS/OpenDataSUS | Mortalidade, natalidade, internações, estabelecimentos e indicadores de saúde |
| **ALTA** | SINISA/SNIS | Água, esgoto, resíduos e drenagem |
| **ALTA** | Novo Caged/RAIS | Emprego formal, salários, admissões, desligamentos e estrutura econômica |
| **ALTA** | Sinesp/MJSP | Criminalidade e segurança pública |
| **ALTA** | Senatran | Frota, mobilidade e acidentes/trânsito |
| **ALTA** | ANATEL | Banda larga, telefonia, cobertura e conectividade |
| **MÉDIA** | ANEEL | Energia elétrica, consumidores, qualidade e infraestrutura |
| **MÉDIA** | CadÚnico/MDS | Vulnerabilidade e pobreza |
| **MÉDIA** | Receita Federal/CNPJ | Densidade empresarial e atividade econômica |
| **MÉDIA** | Portal da Transparência/CGU | Transferências, benefícios, convênios e recursos federais |
| **MÉDIA** | TSE | Eleitorado, participação e resultados eleitorais |
| **MÉDIA** | CNJ/DataJud | Judicialização e estrutura/atividade do Judiciário |
| **MÉDIA** | INPE | Desmatamento, queimadas e uso da terra |
| **MÉDIA** | IBAMA | Infrações, fiscalização e pressão ambiental |
| **MÉDIA** | ICMBio | Unidades de conservação e biodiversidade |
| **MÉDIA** | MCTI | Ciência, tecnologia e inovação |
| **BAIXA/MÉDIA** | INPI | Patentes, marcas e propriedade intelectual |
| **BAIXA** | TSE — filiação/candidaturas | Mais útil para análises institucionais do que qualidade urbana |
| **BAIXA** | DataJud em nível processual | Grande volume e maior complexidade metodológica |
| **BAIXA** | Bases federais temáticas isoladas | Úteis somente se houver indicador correspondente |

---

# 3. Chave territorial: IBGE

## 3.1 API de Localidades

**Portal oficial:** [API de Localidades do IBGE](https://servicodados.ibge.gov.br/api/docs/localidades?utm_source=chatgpt.com)

Principais rotas:

```text
GET https://servicodados.ibge.gov.br/api/v1/localidades/municipios

GET https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{codigo_ibge}

GET https://servicodados.ibge.gov.br/api/v1/localidades/estados

GET https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios
```

A API retorna JSON, não exige autenticação e permite recuperar todos os municípios ou municípios de uma UF.

**Prioridade:** ALTA.

**Uso no projeto:**

- `cod_municipio_ibge`
- município
- UF
- região
- região intermediária
- região imediata
- hierarquia territorial
- validação das chaves das outras bases

**Recomendação:** essa tabela deve ser a dimensão `dim_municipio` do Data Warehouse.

---

# 4. IBGE/SIDRA

**Portal:** [SIDRA — IBGE](https://sidra.ibge.gov.br/?utm_source=chatgpt.com)

**API:** [API SIDRA](https://apisidra.ibge.gov.br/?utm_source=chatgpt.com)

Padrão:

```text
https://apisidra.ibge.gov.br/values/t/{TABELA}/n{NIVEL}/{TERRITORIO}/v/{VARIAVEL}/p/{PERIODO}
```

Exemplo estrutural:

```text
GET https://apisidra.ibge.gov.br/values/t/7060/n1/all/v/63/p/last%2012
```

A API SIDRA utiliza URLs parametrizadas por tabela, território, variável e período; há também suporte a classificações e formatos de saída.

### Principais grupos

| Base/tema | Indicadores possíveis | Escala | Formatos |
|---|---|---|---|
| Censo Demográfico | população, idade, sexo | município | API/CSV/XLSX |
| Domicílios | saneamento, ocupação, infraestrutura | município | API/CSV/XLSX |
| Renda | renda domiciliar/per capita | município | API/CSV/XLSX |
| Alfabetização | alfabetização | município | API/CSV/XLSX |
| Trabalho | ocupação/desocupação | município/UF | API/CSV |
| PIB dos Municípios | PIB, VA, setores | município | API/XLSX |
| Demografia | população estimada | município | API/XLSX |
| Cadastro Central de Empresas | empresas, pessoal ocupado | município | arquivos/API conforme produto |
| Urbanização | características territoriais | município | API/arquivos |

O Censo 2022, por exemplo, possui tabelas municipais para população, domicílios, alfabetização, rendimento, cor/raça e deficiência.

**Prioridade:** ALTA.

**TOPSIS:** praticamente obrigatório.

**Ponto crítico:** o SIDRA é excelente para **variáveis agregadas**, mas não deve ser confundido com uma API universal para todos os microdados do IBGE.

---

# 5. SICONFI / Tesouro Nacional

**Portal:** [SICONFI — Tesouro Nacional](https://siconfi.tesouro.gov.br/?utm_source=chatgpt.com)

**Documentação API:** [SICONFI API de Dados Abertos](https://apidatalake.tesouro.gov.br/docs/siconfi/?utm_source=chatgpt.com)

Essa é uma das fontes mais importantes do projeto.

O Tesouro disponibiliza API pública do SICONFI em JSON, sem necessidade de autenticação, com consultas de pequenas frações até grandes volumes. A documentação oficial informa paginação padrão de 5.000 itens e orienta uso responsável para evitar bloqueios.

### Bases

| Base | Indicadores |
|---|---|
| DCA | contas anuais |
| RREO | execução orçamentária |
| RGF | gestão fiscal |
| MSC | matriz de saldos contábeis |
| FINBRA | finanças municipais consolidadas |
| Receitas | receita corrente, tributária etc. |
| Despesas | gasto por função/natureza |
| Investimentos | investimento público |
| Dívida | dívida e operações de crédito |
| Educação | despesas educacionais |
| Saúde | despesas em saúde |

O SICONFI recebe DCA, RREO, RGF e MSC, entre outros dados fiscais e contábeis.

### Indicadores recomendados

```text
receita_corrente_per_capita
receita_tributaria_per_capita
despesa_total_per_capita
investimento_per_capita
despesa_saude_per_capita
despesa_educacao_per_capita
gasto_pessoal_percentual
divida_consolidada_per_capita
resultado_orcamentario
```

**Prioridade:** ALTA.

**TOPSIS:** essencial.

**Risco:** não tratar ausência de declaração como zero.

Uma prefeitura sem informação em determinado período deve gerar:

```text
NULL ≠ 0
```

---

# 6. INEP — Educação

**Portal de microdados:** [Microdados INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados?utm_source=chatgpt.com)

## Censo Escolar

[Censo Escolar — INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar?utm_source=chatgpt.com)

Disponibiliza séries históricas até 2025, incluindo microdados do Censo Escolar da Educação Básica.

**Indicadores:**

- matrículas por 100 habitantes
- alunos/professor
- docentes com formação adequada
- infraestrutura escolar
- acesso à internet
- bibliotecas
- laboratórios
- água/esgoto
- distorção idade-série
- abandono
- aprovação

## IDEB

[IDEB — INEP](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb?utm_source=chatgpt.com)

O IDEB combina fluxo escolar e desempenho no Saeb.

**Indicadores:**

```text
ideb_anos_iniciais
ideb_anos_finais
ideb_ensino_medio
taxa_aprovacao
```

## SAEB

Os resultados são disponibilizados para municípios desde 2005 e incluem planilhas e microdados.

**Prioridade:** ALTA.

## Ensino Superior

[Censo da Educação Superior — INEP](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-da-educacao-superior?utm_source=chatgpt.com)

O Censo Superior possui séries históricas e dados até 2024.

Indicadores:

```text
instituicoes_superiores_por_100k
vagas_superiores_por_100k
matriculas_superiores_por_100k
concluintes_por_100k
```

---

# 7. DATASUS / OpenDataSUS

**Portal:** [Portal de Dados Abertos do SUS](https://dadosabertos.saude.gov.br/?utm_source=chatgpt.com)

É uma das maiores fontes para o índice.

## SIM — Mortalidade

[SIM — Sistema de Informação sobre Mortalidade](https://dadosabertos.saude.gov.br/dataset/sim?utm_source=chatgpt.com)

Os dados são anonimizados e o menor nível público de agregação é o município. O Ministério informa disponibilidade de arquivos `.dbc` e `.csv`.

Indicadores:

```text
mortalidade_geral
mortalidade_infantil
mortalidade_prematura
mortes_por_causas_externas
mortes_por_doencas
```

## SINASC

[SINASC — OpenDataSUS](https://dadosabertos.saude.gov.br/dataset/sistema-de-informacao-sobre-nascidos-vivos-sinasc?utm_source=chatgpt.com)

A base possui arquivos anuais e estava atualizada até maio de 2026, incluindo prévia de 2025.

Indicadores:

```text
nascimentos
baixo_peso_ao_nascer
prematuridade
pre_natal
mortalidade_infantil
```

## CNES

**Cadastro Nacional de Estabelecimentos de Saúde**

Indicadores:

```text
hospitais_por_100k
ubs_por_100k
leitos_por_1000
profissionais_saude_por_1000
equipamentos_saude_por_100k
```

## SIH/SUS

Internações hospitalares:

```text
internacoes_por_1000
mortalidade_hospitalar
internacoes_sensiveis_atencao_basica
```

## SIA/SUS

Procedimentos ambulatoriais:

```text
procedimentos_por_habitante
producao_ambulatorial
```

**Prioridade:** ALTA.

---

# 8. Segurança pública — Sinesp/MJSP

**Portal:** [Dados Abertos do Ministério da Justiça e Segurança Pública](https://www.gov.br/mj/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)

O MJSP disponibiliza oficialmente a base de **Ocorrências Criminais — Sinesp**.

Indicadores:

```text
homicidios_por_100k
roubos_por_100k
furtos_por_100k
estupro_por_100k
lesao_corporal_por_100k
mortes_violentas_por_100k
```

**Prioridade:** ALTA.

**Tratamento:** sempre converter para taxa populacional.

Não utilizar:

```text
quantidade_absoluta_de_crimes
```

quando o objetivo for comparar municípios de tamanhos muito diferentes.

---

# 9. Ministério do Trabalho — RAIS e Novo Caged

**Portal:** [PDET — Ministério do Trabalho e Emprego](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho?utm_source=chatgpt.com)

## RAIS

Microdados em TXT delimitado por `;`.

A RAIS 2025 já possui tabelas XLSX, informações sobre estabelecimentos, vínculos, remuneração e saldo.

Indicadores:

```text
empregos_formais_por_100_hab
remuneracao_media
massa_salarial
estabelecimentos_por_1000_hab
emprego_industrial
emprego_servicos
emprego_comercio
```

## Novo Caged

Atualização mensal.

O painel permite filtros por atividade econômica, UF e município, e as tabelas mensais são disponibilizadas em XLSX.

Indicadores:

```text
saldo_empregos_12m
saldo_empregos_12m_por_1000
taxa_crescimento_emprego
admissoes
desligamentos
```

**Prioridade:** ALTA.

---

# 10. SINISA / antigo SNIS — saneamento

**Portal:** [SINISA — Ministério das Cidades](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/sinisa?utm_source=chatgpt.com)

O SINISA sucedeu o SNIS a partir de 2024.

A primeira coleta SINISA 2024 possui informações de:

- gestão municipal
- abastecimento de água
- esgotamento sanitário
- resíduos sólidos
- águas pluviais



Existem planilhas de informações e indicadores em XLSX.

### Indicadores fundamentais

```text
cobertura_agua
cobertura_esgoto
tratamento_esgoto
perdas_distribuicao
coleta_residuos
destinacao_adequada_residuos
drenagem_urbana
```

**Prioridade:** ALTA.

**Observação importante:** para séries históricas, deve-se integrar:

```text
SNIS até 2023
       ↓
SINISA a partir de 2024
```

criando uma camada de harmonização.

---

# 11. ANEEL — energia

**Portal:** [Portal de Dados Abertos ANEEL](https://dadosabertos.aneel.gov.br/?utm_source=chatgpt.com)

O portal possui dezenas de conjuntos, incluindo dados em CSV, ZIP e Parquet.

Um conjunto particularmente interessante é o **INDGER — Indicadores Gerenciais da Distribuição**, que possui dados comerciais associados a municípios e unidades consumidoras e também pode ser acessado via API.

Indicadores:

```text
unidades_consumidoras_por_100_hab
consumo_energia_per_capita
continuidade_fornecimento
reclamacoes_energia
```

**Prioridade:** MÉDIA/ALTA.

---

# 12. ANATEL — conectividade

**Portal:** [Dados Abertos ANATEL](https://www.gov.br/anatel/pt-br/dados/dados-abertos?utm_source=chatgpt.com)

A ANATEL possui dados de:

- banda larga fixa
- telefonia móvel
- telefonia fixa
- TV
- escolas rurais conectadas
- municípios atendidos
- cobertura móvel
- infraestrutura

A própria Agência disponibiliza indicadores de densidade de acessos por 100 habitantes e dados associados a municípios.

O painel “Meu Município Anatel” permite consultar o panorama de telecomunicações por município.

Indicadores:

```text
banda_larga_fixa_por_100_hab
acessos_moveis_por_100_hab
cobertura_4g
cobertura_5g
escolas_conectadas
```

**Prioridade:** MÉDIA/ALTA.

---

# 13. Senatran — mobilidade

**Portal:** [Estatísticas SENATRAN](https://www.gov.br/transportes/pt-br/assuntos/transito/senatran/estatisticas-senatran?utm_source=chatgpt.com)

A SENATRAN disponibiliza RENAVAM, RENACH, RENAINF e RENAEST.

A frota municipal é publicada em arquivos específicos.

Em junho de 2026, por exemplo, existem arquivos de frota por município/tipo e detalhamentos por ano, combustível, marca, modelo, potência, restrição e demais atributos.

Exemplo de arquivo real:

[Frota por município e tipo — abril/2026 XLSX](https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/Frota_por_municipio_e_tipo_Abril_2026.xlsx/view?utm_source=chatgpt.com)

Indicadores:

```text
veiculos_por_1000_hab
motocicletas_por_1000
automoveis_por_1000
frota_eletrica
acidentes_por_100k
```

**Prioridade:** MÉDIA/ALTA.

---

# 14. TSE — eleições e eleitorado

**Portal:** [Dados Abertos do TSE](https://dadosabertos.tse.jus.br/?utm_source=chatgpt.com)

O grupo de resultados contém arquivos CSV de eleições, boletins de urna, correspondências e resultados por município/zona/seção.

Indicadores possíveis:

```text
eleitores_por_habitante
comparecimento_eleitoral
abstencao
votos_validos
fragmentacao_eleitoral
```

**Prioridade:** MÉDIA.

**Ressalva metodológica:** indicadores eleitorais não são automaticamente indicadores de qualidade urbana. Só incluir se houver hipótese científica explícita.

---

# 15. Receita Federal — CNPJ

**Portal:** [Dados Abertos da Receita Federal](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)

A Receita mantém dados abertos de cadastros, incluindo CNPJ.

Pode gerar:

```text
empresas_ativas_por_1000_hab
estabelecimentos_por_setor
densidade_comercial
densidade_industrial
MEI_por_1000_hab
```

**Prioridade:** MÉDIA.

**ETL:** excelente, mas os arquivos de CNPJ são grandes. Recomendo processamento incremental/Parquet.

---

# 16. MDS — Cadastro Único

**Portal:** [Dados e ferramentas do Cadastro Único](https://www.gov.br/mds/pt-br/orgaos/SAGICAD/dados-e-ferramentas-informacionais/dados-e-ferramentas-do-cadastro-unico/?utm_source=chatgpt.com)

O MDS disponibiliza ferramentas para dados agregados do CadÚnico e o Observatório do Cadastro Único.

Indicadores:

```text
familias_cadunico_por_1000
percentual_baixa_renda
vulnerabilidade_social
familias_beneficiarias
```

**Prioridade:** MÉDIA/ALTA.

É especialmente importante para evitar que o ranking se transforme em um simples “ranking de municípios ricos”.

---

# 17. Portal da Transparência / CGU

**API:** [API do Portal da Transparência](https://portaldatransparencia.gov.br/api-de-dados/?utm_source=chatgpt.com)

**Swagger:** [Swagger da API](https://api.portaldatransparencia.gov.br/?utm_source=chatgpt.com)

Possui consultas para:

- Bolsa Família
- BPC
- Garantia-Safra
- PETI
- despesas
- convênios
- contratos
- licitações
- emendas
- CEIS
- CNEP
- CEPIM
- transferências

A API é REST e exige token. Os limites atuais informados pelo Portal são de 400 requisições/minuto em horário normal, 700/min entre 00h e 06h, e 180/min para APIs restritas.

Exemplos reais de endpoints disponíveis incluem:

```text
GET /api-de-dados/novo-bolsa-familia-por-municipio

GET /api-de-dados/bpc-por-municipio

GET /api-de-dados/safra-beneficiario-por-municipio

GET /api-de-dados/peti-beneficiario-por-municipio
```



**Prioridade:** MÉDIA.

Para cargas grandes, o próprio Portal recomenda downloads de dados abertos em vez de usar a API como mecanismo de bulk ETL.

---

# 18. CNJ — DataJud

**Portal:** [DataJud/CNJ](https://www.cnj.jus.br/sistemas/datajud/?utm_source=chatgpt.com)

**API:** [API Pública DataJud](https://www.cnj.jus.br/sistemas/datajud/api-publica/?utm_source=chatgpt.com)

O DataJud concentra dados processuais do Judiciário e possui API pública para metadados de processos.

Endpoint-base:

```text
https://api-publica.datajud.cnj.jus.br/
```

Por exemplo, a documentação apresenta:

```text
https://api-publica.datajud.cnj.jus.br/api_publica_tst/_search
https://api-publica.datajud.cnj.jus.br/api_publica_tse/_search
https://api-publica.datajud.cnj.jus.br/api_publica_stj/_search
```



A API utiliza chave pública no cabeçalho `Authorization`.

Indicadores:

```text
processos_por_1000_hab
taxa_litigiosidade
tempo_processual
judicializacao_saude
```

**Prioridade:** MÉDIA/BAIXA.

Para uma primeira versão do IC, eu deixaria DataJud fora do núcleo do TOPSIS por causa da complexidade e do risco de criar um indicador de difícil interpretação.

---

# 19. Meio ambiente

## IBAMA

[Dados Abertos IBAMA](https://www.gov.br/ibama/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)

O IBAMA mantém portal próprio de dados abertos e disponibiliza seus conjuntos também pelo Portal Brasileiro de Dados Abertos.

Possíveis indicadores:

```text
autos_infracao_por_1000_km2
valor_multas_ambientais
embargos
pressao_fiscalizatoria
```

**Prioridade:** MÉDIA.

---

## ICMBio

[Dados Abertos ICMBio](https://www.gov.br/icmbio/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)

Bases incluem:

- unidades de conservação
- atributos das UCs
- limites geográficos
- planos de manejo
- áreas queimadas
- desmatamento em UCs
- biodiversidade

O catálogo do ICMBio registra, por exemplo, conjuntos de desmatamento e áreas queimadas em UCs com periodicidade anual.

Exemplo real de arquivo:

[Limites oficiais das UCs federais — CSV](https://www.gov.br/icmbio/pt-br/acesso-a-informacao/dados-abertos/arquivos/limites-oficiais-das-unidades-de-conservacao-federais/limites_oficiais_das_unidades_de_conservacao_federais-1.csv/view?utm_source=chatgpt.com)

Indicadores:

```text
percentual_area_uc
area_protegida_por_municipio
desmatamento
queimadas
```

---

## INPE / TerraBrasilis

**Portal:** [TerraBrasilis — INPE](https://terrabrasilis.dpi.inpe.br/?utm_source=chatgpt.com)

Fontes prioritárias:

- PRODES
- DETER
- queimadas
- uso/cobertura da terra

Indicadores:

```text
desmatamento_km2
percentual_desmatado
focos_de_calor
variacao_desmatamento
```

**Prioridade:** MÉDIA.

Especialmente importante para municípios amazônicos.

---

# 20. MCTI — inovação

**Portal:** [Indicadores Nacionais de CT&I — MCTI](https://www.gov.br/mcti/pt-br/acesso-a-informacao/dados-abertos/dados-abertos/paginas/indicadores-nacionais-de-ciencia-tecnologia-e-inovacao?utm_source=chatgpt.com)

A base é anual e agrega informações de diversas fontes do sistema brasileiro de Ciência, Tecnologia e Inovação.

A publicação 2025 possui arquivos em **Excel, RData e JSON**.

Indicadores:

```text
investimento_cti
pesquisadores
patentes
pos_graduacao
infraestrutura_cti
```

**Prioridade:** MÉDIA.

---

# 21. INPI

[Dados Abertos INPI](https://www.gov.br/inpi/pt-br/acesso-a-informacao/dados-abertos/dados-abertos?utm_source=chatgpt.com)

Indicadores possíveis:

```text
patentes_por_100k
marcas_registradas
atividade_inovadora
propriedade_intelectual
```

**Prioridade:** BAIXA/MÉDIA.

É mais interessante para uma dimensão específica de inovação do que para o núcleo socioeconômico.

---

# 22. Mapa de dados por categoria

| Categoria | Fontes principais | Indicadores candidatos |
|---|---|---|
| **População** | IBGE | população, densidade, crescimento |
| **Demografia** | IBGE | idade, dependência, envelhecimento |
| **Renda** | IBGE | renda per capita, desigualdade |
| **Finanças** | SICONFI | receita, investimento, dívida |
| **Educação** | INEP | IDEB, matrícula, docentes |
| **Saúde** | DATASUS | mortalidade, médicos, leitos |
| **Segurança** | Sinesp | homicídios, roubos, furtos |
| **Trabalho** | RAIS/Caged | emprego, salário, crescimento |
| **Pobreza** | CadÚnico/MDS | vulnerabilidade, famílias |
| **Água** | SINISA | cobertura, perdas |
| **Esgoto** | SINISA | coleta/tratamento |
| **Resíduos** | SINISA | coleta/destinação |
| **Drenagem** | SINISA | cobertura/gestão pluvial |
| **Energia** | ANEEL | consumo, consumidores, qualidade |
| **Internet** | ANATEL | banda larga, cobertura |
| **Mobilidade** | SENATRAN | frota, acidentes |
| **Moradia** | IBGE/SINISA | domicílios, infraestrutura |
| **Meio ambiente** | INPE/IBAMA/ICMBio | desmatamento, queimadas, proteção |
| **Inovação** | MCTI/INPI | patentes, pesquisadores, CT&I |
| **Atividade econômica** | Receita/IBGE/RAIS | empresas, setores, empregos |
| **Assistência social** | MDS/Transparência | CadÚnico, benefícios |
| **Justiça** | CNJ | processos, litigiosidade |
| **Participação política** | TSE | eleitorado, comparecimento |

---

# 23. Matriz de cobertura municipal

Legenda:

- **●** excelente
- **◐** disponível, mas exige processamento
- **○** possível/indireto
- **—** não é o foco

| Indicador | IBGE | SICONFI | INEP | SUS | Sinesp | RAIS | SINISA | ANEEL | ANATEL | MDS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| População | ● | — | ○ | ○ | — | — | — | — | — | ○ |
| Renda | ● | — | — | — | — | ● | — | — | — | ● |
| Receita pública | — | ● | — | — | — | — | — | — | — | — |
| Investimento público | — | ● | — | — | — | — | — | — | — | — |
| IDEB | — | — | ● | — | — | — | — | — | — | — |
| Matrículas | — | — | ● | — | — | — | — | — | — | — |
| Mortalidade | ○ | — | — | ● | — | — | — | — | — | — |
| Hospitais/leitos | — | — | — | ● | — | — | — | — | — | — |
| Homicídios | — | — | — | — | ● | — | — | — | — | — |
| Emprego formal | — | — | — | — | — | ● | — | — | — | — |
| Salário | ○ | — | — | — | — | ● | — | — | — | — |
| Água | ○ | — | ○ | — | — | — | ● | — | — | — |
| Esgoto | ○ | — | ○ | — | — | — | ● | — | — | — |
| Resíduos | ○ | — | — | — | — | — | ● | — | — | — |
| Energia | — | — | — | — | — | — | — | ● | — | — |
| Internet | — | — | ○ | — | — | — | — | — | ● | — |
| Frota | — | — | — | — | — | — | — | — | — | — |
| Vulnerabilidade | ● | — | — | — | — | — | — | — | — | ● |
| Desmatamento | — | — | — | — | — | — | — | — | — | — |
| Patentes/inovação | — | — | ○ | — | — | ○ | — | — | — | — |

---

# 24. Indicadores TOPSIS que eu usaria inicialmente

Para uma primeira versão cientificamente defensável, eu evitaria começar com 100+ indicadores.

Uma matriz inicial de aproximadamente **25–35 indicadores** seria mais adequada.

## Dimensão econômica

```text
PIB_per_capita                         ↑
renda_domiciliar_per_capita            ↑
empregos_formais_por_1000_hab          ↑
remuneracao_media                      ↑
crescimento_emprego                    ↑
empresas_por_1000_hab                  ↑
```

## Dimensão fiscal

```text
receita_corrente_per_capita            ↑
investimento_publico_per_capita       ↑
investimento_percentual_despesa       ↑
despesa_saude_per_capita              ↑
despesa_educacao_per_capita           ↑
divida_per_capita                      ↓
```

## Educação

```text
ideb_anos_iniciais                     ↑
ideb_anos_finais                       ↑
abandono_escolar                       ↓
alunos_por_professor                   ↓
escolas_com_internet                   ↑
```

## Saúde

```text
medicos_por_1000                       ↑
leitos_por_1000                        ↑
mortalidade_infantil                   ↓
mortalidade_prematura                  ↓
internacoes_sensiveis_AB               ↓
```

## Segurança

```text
homicidios_por_100k                    ↓
roubos_por_100k                        ↓
furtos_por_100k                        ↓
```

## Infraestrutura urbana

```text
cobertura_agua                         ↑
cobertura_esgoto                       ↑
tratamento_esgoto                      ↑
coleta_residuos                        ↑
banda_larga_por_100_hab                ↑
```

## Mobilidade

```text
acidentes_por_100k                     ↓
transporte/frota                       ↑/contextual
```

## Sustentabilidade

```text
area_protegida_percentual              ↑
desmatamento_percentual                ↓
queimadas_por_area                     ↓
```

## Inclusão social

```text
vulnerabilidade_cadunico               ↓
familias_baixa_renda                   ↓
```

---

# 25. Um cuidado metodológico extremamente importante

Não misture indiscriminadamente:

```text
indicador de resultado
```

com

```text
indicador de gasto
```

Exemplo:

```text
despesa_saude_per_capita ↑
```

não significa necessariamente:

```text
saude_melhor ↑
```

Da mesma forma:

```text
numero_de_hospitais ↑
```

não significa necessariamente:

```text
qualidade_da_saude ↑
```

O modelo deve separar:

### Inputs/recursos

```text
gasto
infraestrutura
pessoal
capacidade instalada
```

### Outcomes/resultados

```text
mortalidade
IDEB
criminalidade
cobertura
renda
emprego
```

Isso permite construir uma análise muito mais defensável academicamente.

---

# 26. Arquitetura ETL híbrida recomendada

Eu estruturaria assim:

```text
                    ┌───────────────────┐
                    │   Fontes oficiais │
                    └─────────┬─────────┘
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
       APIs REST          CSV/XLSX             Portais
          │                   │                    │
          └───────────────────┼────────────────────┘
                              ↓
                    ┌───────────────────┐
                    │ RAW / BRONZE      │
                    │ dado original     │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ SILVER            │
                    │ padronização      │
                    │ tipos             │
                    │ códigos IBGE      │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ GOLD              │
                    │ indicadores      │
                    │ município/ano     │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ TOPSIS / MCDA     │
                    └─────────┬─────────┘
                              ↓
                    ┌───────────────────┐
                    │ Ranking municipal │
                    └───────────────────┘
```

---

# 27. Estratégia API + arquivo local + fallback

Para cada indicador, manter:

```text
source_priority
source_url
source_type
retrieved_at
reference_year
reference_period
municipio_ibge
value
unit
quality_status
```

Exemplo:

```text
indicator = "ideb"
municipio_ibge = 4205407
reference_year = 2023
value = 6.1
source = "INEP"
source_type = "XLSX"
retrieved_at = "2026-08-17"
quality_status = "VALID"
```

## Regra de fallback

```text
1. API oficial
      ↓ falhou
2. arquivo oficial atualizado
      ↓ falhou
3. snapshot local validado
      ↓ falhou
4. NULL + quality_status = MISSING
```

**Não substituir automaticamente por zero.**

---

# 28. Camadas recomendadas do projeto

## Bronze

Guardar o dado exatamente como veio.

Exemplo:

```text
data/raw/ibge/2026/
data/raw/siconfi/2025/
data/raw/inep/2023/
data/raw/sus/2024/
```

Não fazer limpeza destrutiva nessa camada.

## Silver

Padronizar:

```text
municipio_ibge
ano
mes
valor
unidade
fonte
```

Converter:

```text
"1.234,56" → 1234.56
".."       → NULL
"-"        → NULL
```

## Gold

Criar indicadores derivados:

```text
mortalidade_100k
receita_per_capita
crime_100k
leitos_1000
emprego_1000
```

---

# 29. Data Lake recomendado

Para um projeto de IC, não recomendo armazenar tudo diretamente em PostgreSQL.

Melhor:

```text
RAW:
CSV / XLSX / JSON / ZIP

↓

Parquet

↓

DuckDB / PostgreSQL

↓

Data Mart TOPSIS
```

Estrutura:

```text
data/
├── raw/
│   ├── ibge/
│   ├── siconfi/
│   ├── inep/
│   ├── datasus/
│   ├── sinesp/
│   ├── rais/
│   ├── sinisa/
│   ├── anatel/
│   ├── aneel/
│   └── senatran/
│
├── silver/
│   ├── municipio/
│   ├── educacao/
│   ├── saude/
│   ├── financas/
│   └── trabalho/
│
└── gold/
    ├── indicadores/
    ├── topsis/
    └── ranking/
```

---

# 30. Controle de qualidade

Eu criaria uma tabela:

```text
data_quality
```

com:

| Campo | Função |
|---|---|
| `source` | fonte |
| `indicator` | indicador |
| `year` | ano |
| `municipio_ibge` | município |
| `expected` | deveria existir? |
| `received` | recebeu? |
| `null_rate` | proporção ausente |
| `duplicate_rate` | duplicidade |
| `min_value` | mínimo |
| `max_value` | máximo |
| `last_update` | última atualização |
| `status` | OK/WARN/ERROR |

---

# 31. Tratamento de dados ausentes

Esta é provavelmente uma das partes mais importantes da metodologia.

## Caso A — zero verdadeiro

Exemplo:

```text
focos_de_incendio = 0
```

Pode ser zero real.

## Caso B — ausência

```text
valor = NULL
```

Significa:

> não há informação disponível.

Não significa:

> não existe ocorrência.

## Caso C — não aplicável

```text
valor = NA
```

Exemplo: indicador específico de área protegida que não possui aplicação direta.

## Caso D — dado temporariamente indisponível

```text
status = DELAYED
```

Exemplo: ano corrente ainda não fechado.

---

# 32. Problema da defasagem temporal

O ranking não deve fingir que todos os indicadores representam o mesmo ano.

É perfeitamente possível ter:

```text
População → 2025
Finanças → 2025
RAIS → 2025
Caged → 2026
IDEB → 2023
Censo Escolar → 2025
SINISA → 2024/2023
SIM → 2024/2025 dependendo do fechamento
```

Portanto, recomendo criar:

```text
reference_year
reference_date
publication_date
```

para cada observação.

---

# 33. Índice de atualidade

Uma ideia metodológica interessante para o IC é calcular:

```text
age_years = ano_atual - reference_year
```

e documentar a idade de cada indicador.

Por exemplo:

| Indicador | Ano | Idade |
|---|---:|---:|
| População | 2025 | 1 |
| Caged | 2026 | 0 |
| RAIS | 2025 | 1 |
| IDEB | 2023 | 3 |
| Censo | 2022 | 4 |

Isso permite discutir formalmente a qualidade temporal do ranking.

---

# 34. Normalização para TOPSIS

Depois da construção da matriz:

```text
X = municípios × indicadores
```

separar:

### Benefício

```text
quanto maior, melhor
```

Exemplos:

```text
renda
IDEB
emprego
água
esgoto
banda larga
```

### Custo

```text
quanto menor, melhor
```

Exemplos:

```text
homicídios
mortalidade
desemprego
desmatamento
dívida
```

A direção precisa ser documentada em metadados:

```text
indicator
direction
unit
source
```

---

# 35. Risco de dupla contagem

Outro ponto importante.

Não colocar simultaneamente:

```text
PIB per capita
renda per capita
salário médio
emprego formal
```

com pesos altos e independentes sem testar correlação.

Da mesma forma:

```text
água
esgoto
saneamento
domicílios com água
domicílios com esgoto
```

podem representar praticamente a mesma dimensão.

Recomendo:

```text
correlation matrix
↓
VIF
↓
PCA opcional
↓
seleção de indicadores
↓
TOPSIS
```

---

# 36. Matriz de risco

| Risco | Probabilidade | Impacto | Tratamento |
|---|---|---|---|
| API fora do ar | Alta | Alto | cache + arquivo |
| Mudança de schema | Média | Alto | schema validation |
| Município sem dado | Alta | Alto | NULL + cobertura |
| Ano defasado | Alta | Médio | metadata temporal |
| Zero confundido com missing | Alta | Alto | regras semânticas |
| Código IBGE inconsistente | Média | Alto | dimensão IBGE |
| Duplicidade | Média | Alto | chave composta |
| Retificação de dados | Média | Alto | versionamento |
| Formato XLSX alterado | Média | Alto | testes automatizados |
| Rate limit | Média | Médio | retry/backoff |
| API descontinuada | Baixa/Média | Alto | fallback |
| Indicadores correlacionados | Alta | Alto | análise estatística |
| Municípios muito pequenos | Alta | Médio | taxas + shrinkage/cautela |
| Crime com poucos eventos | Alta | Alto | suavização |
| Diferença de metodologia | Alta | Alto | metadicionário |

---

# 37. Rate limits e autenticação

| Fonte | Autenticação |
|---|---|
| IBGE Localidades | Não |
| SIDRA | Geralmente não |
| SICONFI | Não |
| INEP arquivos | Não |
| OpenDataSUS | Não |
| SINISA arquivos | Não |
| TSE arquivos | Não |
| ANEEL | Não para dados abertos |
| ANATEL | Não para grande parte dos dados |
| SENATRAN arquivos | Não |
| MDS agregados | conforme ferramenta |
| Portal Transparência API | **Token** |
| DataJud | **API Key** |

O Portal da Transparência exige token e possui limites explícitos de requisições.

O DataJud utiliza chave pública no header de autorização.

---

# 38. O que eu colocaria na primeira versão do IC

Para não transformar o projeto em um “monstro de ETL”, sugiro a primeira versão com **10 fontes**:

```text
1. IBGE
2. SICONFI
3. INEP
4. DATASUS
5. Sinesp
6. RAIS/Caged
7. SINISA
8. ANATEL
9. ANEEL
10. MDS
```

Isso já permite construir um ranking multidimensional bastante completo.

### Dimensões

```text
Economia
Finanças
Educação
Saúde
Segurança
Trabalho
Saneamento
Conectividade
Energia
Vulnerabilidade
```

Depois, em uma segunda etapa:

```text
SENATRAN
TSE
CNJ
INPE
IBAMA
ICMBio
MCTI
INPI
Receita Federal
```

---

# 39. Modelo de tabela final

A tabela Gold poderia ser:

```text
municipio_ibge
municipio
uf
ano

populacao

pib_per_capita
renda_per_capita
emprego_formal_1000
remuneracao_media

receita_per_capita
investimento_per_capita
divida_per_capita

ideb
abandono_escolar
alunos_por_professor

medicos_1000
leitos_1000
mortalidade_infantil
internacoes_1000

homicidios_100k
roubos_100k

agua_percent
esgoto_percent
tratamento_esgoto_percent
residuos_percent

banda_larga_100
consumo_energia_per_capita

veiculos_1000
acidentes_100k

vulnerabilidade
desmatamento
area_protegida

topsis_score
ranking
```

---

# 40. Metadados dos indicadores

Além do valor, recomendo manter uma tabela de catálogo:

```text
indicator_catalog
```

com:

```text
indicator_id
indicator_name
description
source
source_url
dataset
variable
unit
geographic_level
frequency
reference_period
direction
is_benefit
denominator
ibge_code_required
aggregation_method
missing_policy
quality_score
```

Exemplo:

```text
indicator_id:
SAUDE_MORTALIDADE_INFANTIL

source:
DATASUS/SINASC/SIM

unit:
óbitos por 1.000 nascidos vivos

direction:
COST

geographic_level:
MUNICIPAL

denominator:
nascidos_vivos

missing_policy:
NULL

quality_score:
HIGH
```

Isso torna o projeto muito mais auditável.

---

# 41. Fontes oficiais principais — mapa de navegação

### IBGE

[IBGE](https://www.ibge.gov.br/?utm_source=chatgpt.com)  
[SIDRA](https://sidra.ibge.gov.br/?utm_source=chatgpt.com)  
[API SIDRA](https://apisidra.ibge.gov.br/?utm_source=chatgpt.com)  
[API Localidades](https://servicodados.ibge.gov.br/api/docs/localidades?utm_source=chatgpt.com)

### Finanças

[SICONFI](https://siconfi.tesouro.gov.br/?utm_source=chatgpt.com)  
[Documentação SICONFI API](https://apidatalake.tesouro.gov.br/docs/siconfi/?utm_source=chatgpt.com)

### Educação

[INEP — Microdados](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados?utm_source=chatgpt.com)  
[INEP — IDEB](https://www.gov.br/inep/pt-br/areas-de-atuacao/pesquisas-estatisticas-e-indicadores/ideb?utm_source=chatgpt.com)

### Saúde

[OpenDataSUS](https://dadosabertos.saude.gov.br/?utm_source=chatgpt.com)  
[DATASUS](https://datasus.saude.gov.br/?utm_source=chatgpt.com)

### Trabalho

[PDET/MTE](https://www.gov.br/trabalho-e-emprego/pt-br/assuntos/estatisticas-trabalho?utm_source=chatgpt.com)

### Saneamento

[SINISA](https://www.gov.br/cidades/pt-br/acesso-a-informacao/acoes-e-programas/saneamento/sinisa/sinisa?utm_source=chatgpt.com)

### Segurança

[MJSP — Dados Abertos](https://www.gov.br/mj/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)

### Energia

[ANEEL — Dados Abertos](https://dadosabertos.aneel.gov.br/?utm_source=chatgpt.com)

### Telecomunicações

[ANATEL — Dados Abertos](https://www.gov.br/anatel/pt-br/dados/dados-abertos?utm_source=chatgpt.com)

### Mobilidade

[SENATRAN — Estatísticas](https://www.gov.br/transportes/pt-br/assuntos/transito/senatran/estatisticas-senatran?utm_source=chatgpt.com)

### Eleições

[TSE — Dados Abertos](https://dadosabertos.tse.jus.br/?utm_source=chatgpt.com)

### Transparência

[Portal da Transparência — API](https://portaldatransparencia.gov.br/api-de-dados/?utm_source=chatgpt.com)

### Justiça

[CNJ — DataJud](https://www.cnj.jus.br/sistemas/datajud/?utm_source=chatgpt.com)

### Meio ambiente

[IBAMA — Dados Abertos](https://www.gov.br/ibama/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)  
[ICMBio — Dados Abertos](https://www.gov.br/icmbio/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)  
[TerraBrasilis/INPE](https://terrabrasilis.dpi.inpe.br/?utm_source=chatgpt.com)

### Inovação

[MCTI — Indicadores de CT&I](https://www.gov.br/mcti/pt-br/acesso-a-informacao/dados-abertos/dados-abertos/paginas/indicadores-nacionais-de-ciencia-tecnologia-e-inovacao?utm_source=chatgpt.com)  
[INPI — Dados Abertos](https://www.gov.br/inpi/pt-br/acesso-a-informacao/dados-abertos/dados-abertos?utm_source=chatgpt.com)

### Empresas

[Receita Federal — Dados Abertos](https://www.gov.br/receitafederal/pt-br/acesso-a-informacao/dados-abertos?utm_source=chatgpt.com)

### Assistência social

[MDS — Cadastro Único e dados](https://www.gov.br/mds/pt-br/orgaos/SAGICAD/dados-e-ferramentas-informacionais/dados-e-ferramentas-do-cadastro-unico/?utm_source=chatgpt.com)

---

# 42. Conclusão e recomendação arquitetural

Para o projeto de IC, eu estruturaria a solução em quatro princípios:

**1. IBGE como chave territorial.**

Toda tabela precisa convergir para:

```text
municipio_ibge = BIGINT(7)
```

**2. SICONFI, IBGE, INEP, DATASUS, Sinesp, RAIS/Caged e SINISA como núcleo.**

Essas fontes cobrem praticamente todas as dimensões fundamentais do índice.

**3. API não significa necessariamente melhor ETL.**

Para grandes volumes:

```text
API → consultas incrementais

CSV/XLSX/Parquet → cargas históricas/bulk
```

O próprio Portal da Transparência recomenda arquivos abertos para grandes volumes, enquanto sua API é mais adequada a consultas filtradas.

**4. Preservar o dado bruto e a proveniência.**

O ranking deve conseguir responder:

> “Por que Florianópolis recebeu esse valor nesse indicador?”

e o sistema deve conseguir voltar até:

```text
ranking
 ↓
indicador
 ↓
tabela Gold
 ↓
tabela Silver
 ↓
arquivo/API
 ↓
fonte governamental
 ↓
variável original
```

Esse encadeamento é particularmente importante em um projeto acadêmico porque transforma o ranking de uma simples aplicação de TOPSIS em uma **pipeline de dados públicos reproduzível, auditável e metodologicamente defensável**.

### Prioridade prática de implementação

```text
FASE 1
IBGE + SICONFI + INEP + DATASUS

FASE 2
Sinesp + RAIS/Caged + SINISA

FASE 3
ANATEL + ANEEL + MDS + SENATRAN

FASE 4
TSE + CNJ + Receita Federal

FASE 5
INPE + IBAMA + ICMBio + MCTI + INPI
```

A partir dessa arquitetura, o próximo passo técnico mais produtivo seria transformar este catálogo em um **`data_dictionary.csv`/`indicator_catalog`**, contendo para cada indicador: `fonte`, `URL`, `endpoint`, `tabela`, `variável`, `código IBGE`, `periodicidade`, `unidade`, `denominador`, `direção TOPSIS`, `tratamento de missing` e `método de agregação`. Isso permitiria sair diretamente da pesquisa documental para a implementação da pipeline ETL.