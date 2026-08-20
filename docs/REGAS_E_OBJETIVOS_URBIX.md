# Regras e Objetivos do Projeto Urbix

## 1. Objetivo geral

O projeto Urbix tem como objetivo construir um sistema de ranqueamento municipal multicritério baseado em indicadores públicos e em um método TOPSIS, com foco em cidades brasileiras, usando dados reais, comparáveis e rastreáveis.

A solução deve permitir:
- comparar municípios usando indicadores públicos;
- usar o valor mais recente disponível por cidade e indicador;
- manter histórico de dados por ano;
- gerar ranking com base em critérios explícitos;
- preservar a integridade dos dados e evitar zero artificial;
- produzir uma base metodologicamente defensável para artigo e banca.

---

## 2. Principais regras de negócio

### 2.1 Regra de integridade dos dados

1. Dado real deve ser preservado.
2. Dado ausente deve permanecer ausente.
3. Zero artificial não deve ser inventado para completar lacunas.
4. O sistema não deve substituir ausência de dado por média arbitrária.
5. Indicadores sem evidência sólida devem ser sinalizados como não cobertos.

### 2.2 Regra de histórico

1. Cada cidade pode ter vários registros por indicador ao longo do tempo.
2. A lógica de uso do dado deve preservar o ano de referência.
3. O cálculo do ranking usa o valor mais recente válido de cada indicador por cidade.
4. O histórico deve ser armazenado de forma rastreável por fonte, ano e município.

### 2.3 Regra de município e indicador

1. O código de município deve ser normalizado para o padrão IBGE de 7 dígitos.
2. A chave principal do dado deve considerar cidade + indicador + ano.
3. Indicadores sem município válido não devem entrar no cálculo.
4. Registros duplicados devem ser consolidados.

### 2.4 Regra de cálculo TOPSIS

1. A matriz deve ser montada somente com indicadores válidos e informativos.
2. Colunas sem variação real devem ser removidas antes do cálculo.
3. Colunas com excesso de dados faltantes devem ser descartadas.
4. O impacto do indicador deve ser explicitamente definido como benefício ou custo.
5. A normalização deve ser aplicada somente após a filtragem dos indicadores relevantes.

### 2.5 Regra de fontes

1. Fontes oficiais do governo têm prioridade.
2. Dados locais só entram quando forem consistentes e rastreáveis.
3. A fonte de cada dado deve ser registrada.
4. Quando não houver dado confiável, a ausência deve ser explicitada e não mascarada.

---

## 3. Objetivos de arquitetura

### 3.1 Objetivo de qualidade dos dados

- garantir consistência intermunicipal;
- evitar duplicidade;
- padronizar ano, fonte e código IBGE;
- manter histórico e valor mais recente.

### 3.2 Objetivo de confiabilidade metodológica

- usar indicadores comparáveis e confiáveis;
- tratar dados ausentes de forma honesta;
- não forçar ranking por dados inventados;
- manter transparência na metodologia.

### 3.3 Objetivo de escalabilidade

- permitir aumento futuro de fontes;
- permitir novos indicadores sem quebrar o fluxo atual;
- manter ETL modular por categoria e por fonte.

### 3.4 Objetivo de apresentação e banca

- o sistema deve ser explicável;
- o ranking deve ter sentido;
- os dados devem ser auditáveis;
- a metodologia deve poder ser defendida em apresentação acadêmica.

---

## 4. Prioridades do projeto

### Prioridade alta

- base municipal
- população
- PIB
- receitas e finanças públicas
- educação
- saúde
- segurança
- emprego
- infraestrutura

### Prioridade média

- saneamento
- meio ambiente
- resiliência
- smart city
- conectividade

### Prioridade baixa

- indicadores complementares com cobertura mais frágil
- dados não totalmente padronizados por município
- indicadores sem base oficial confiável

---

## 5. Estratégia de ETL

A arquitetura deve seguir este fluxo:

1. Coleta de fonte local ou pública
2. Normalização de colunas e códigos geográficos
3. Padronização de tipos numéricos
4. Validação por município e ano
5. Armazenamento em histórico
6. Seleção do valor mais recente por cidade + indicador
7. Filtragem de indicadores não informativos
8. Construção da matriz TOPSIS
9. Cálculo do ranking
10. Exposição via API

---

## 6. Critérios de aceitação do sistema

O projeto só pode ser considerado consistente quando:

- [ ] cada indicador tem fonte documentada;
- [ ] cada dado tem ano e município definidos;
- [ ] a base usa código IBGE padronizado;
- [ ] o valor mais recente é o valor utilizado no cálculo;
- [ ] dados ausentes não viram zero;
- [ ] a matriz TOPSIS não contém colunas irrelevantes;
- [ ] a resposta da API reflete valores reais e auditáveis;
- [ ] a metodologia pode ser explicada sem contradição;
- [ ] o ranking tem coerência com o conjunto de dados usados.

---

## 7. Regras de implementação já validadas

### 7.1 Validações confirmadas

- O projeto já possui estrutura de municípios e indicadores em banco.
- O banco já guarda valores históricos por cidade e indicador.
- A lógica de manter o valor mais recente por cidade + indicador já foi discutida e validada.
- O ETL já é capaz de ler dados locais e algumas APIs públicas.
- O ranking depende de indicadores reais e já existe uma estrutura para o cálculo TOPSIS.

### 7.2 Problemas identificados

- presença excessiva de indicadores sem cobertura real;
- muitos dados ainda não mapeados em [backend/app/etl_config.py](backend/app/etl_config.py);
- excesso de zeros artiﬁciais ou colunas não informativas;
- processamento de cidades e indicadores desnecessários em alguns fluxos;
- falta de clareza sobre ausência de dado versus zero;
- necessidade de priorizar fontes oficiais e redução da matriz de indicadores.

---

## 8. Regras para evolução do projeto

1. Novos indicadores só entram se houver fonte documentada.
2. Novas fontes devem ser adicionadas com categoria, ano e nível de cobertura.
3. Aumentar cobertura deve acontecer por prioridade e por impacto estratégico.
4. Cobertura deve ser medida por cidade + indicador + ano.
5. O sistema nunca deve “preencher tudo” sem evidência.
6. Tudo o que for implementado precisa ter rastreabilidade.

---

## 9. Checklist de implementação atual

### Fase 1 — base consolidada
- [x] estrutura do banco de municípios e indicadores existente
- [x] histórico de valores em base de dados
- [x] lógica de mais recente por município + indicador discutida
- [x] matriz documental de fontes públicas criada
- [x] regras de ausência de dado documentadas

### Fase 2 — organização do ETL
- [ ] revisar e reduzir indicadores sem fonte real em [backend/app/etl_config.py](backend/app/etl_config.py)
- [ ] padronizar cada indicador com fonte, ano e tipo de cálculo
- [ ] separar indicadores base de indicadores TOPSIS
- [ ] melhorar rotina de ingestão em [backend/tools/local_etl_service.py](backend/tools/local_etl_service.py)

### Fase 3 — cálculo e ranking
- [ ] filtrar colunas sem informação real
- [ ] ajustar TOPSIS para evitar zeros artificiais
- [ ] validar ranking por cidades conhecidas
- [ ] validar performance da API

### Fase 4 — documentação e apresentação
- [ ] registrar metodologia final
- [ ] documentar fontes implementadas
- [ ] documentar política de missing data
- [ ] preparar explicação para banca e artigo

---

## 10. Conclusão

O Urbix precisa deixar de ser um projeto “rodando sem rigor” e se tornar um sistema com regras claras, cobertura real, explicabilidade e robustez metodológica. A base da qualidade está em três pontos:

1. dados reais;
2. fontes documentadas;
3. ausência de dado tratada corretamente.

A partir disso, o ETL e o TOPSIS podem ser feitos de forma sólida, defensável e pronta para apresentação.
