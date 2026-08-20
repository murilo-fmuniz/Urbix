# Urbix — Relatório de Continuidade da IC

> Documento de transição para pesquisadores e desenvolvedores que desejarem continuar a evolução do projeto Urbix.

- **Projeto:** Urbix
- **Escopo:** ranking municipal multicritério com TOPSIS
- **Data de consolidação:** 18/08/2026
- **Diretório principal de dados:** `backend/data/`

---

## 1. Objetivo deste documento

Este relatório registra:

- o estado atual do sistema;
- as fontes de dados disponíveis no datalake;
- os indicadores já carregados e utilizados;
- as oportunidades de novos indicadores;
- as limitações metodológicas conhecidas;
- as regras que devem ser respeitadas para evitar dados inventados ou proxies indevidos;
- um roteiro recomendado para a continuidade da Iniciação Científica.

A regra principal para qualquer continuação é:

> Um arquivo disponível não significa automaticamente que um indicador está pronto para uso. O dado precisa ter definição, código municipal, valor, ano, fonte e regra de cálculo verificáveis.

---

## 2. Estado atual do sistema

O Urbix possui uma API em FastAPI com cálculo TOPSIS integrado ao banco SQLite.

### Endpoint principal

`POST /topsis/ranking-hibrido`

Payload mínimo:

```json
{
  "cidades_ibge": ["3550308", "4106902", "4113700"]
}
```

O endpoint foi testado com São Paulo, Curitiba e Londrina e apresentou:

- status HTTP `200`;
- aproximadamente 4,6 segundos de latência no teste realizado;
- 11 indicadores efetivamente calculados por cidade.

### Indicadores atualmente observados no ranking

- `taxa_desemprego`
- `orcamento_per_capita`
- `sem_teto`
- `bombeiros`
- `homicidios`
- `relacao_estudante_professor`
- `sobrevivencia_negocios`
- `empregos_tic`
- `medidores_inteligentes_agua`
- `empregos_informais`
- `densidade_banda_larga`

A nomenclatura de alguns indicadores deve ser revisada antes da versão final. Em particular, alguns valores atualmente calculados são proxies ou dependem de interpretações que ainda precisam ser documentadas.

---

## 3. Arquitetura de dados

O sistema utiliza duas camadas principais:

### 3.1. Histórico bruto/analítico

Tabela: `valores_indicadores`

Armazena registros por:

- código IBGE;
- indicador;
- ano de referência;
- valor;
- fonte.

Esta é a camada que preserva histórico e origem dos dados.

### 3.2. Snapshot de valores mais recentes

Tabela: `valores_indicadores_latest`

Mantém o registro mais recente por município e indicador para acelerar as consultas do TOPSIS.

### 3.3. Configuração do ETL

Arquivo principal:

`backend/app/etl_config.py`

Serviço de processamento local:

`backend/tools/local_etl_service.py`

O arquivo `backend/scripts/map_data_lake.py` não foi localizado na estrutura atual. A lógica de mapeamento está atualmente distribuída principalmente entre `etl_config.py`, `local_etl_service.py` e scripts específicos de extração.

---

## 4. Fontes disponíveis em `backend/data/`

O inventário do dicionário ETL registra aproximadamente 153 arquivos analisados. As fontes mais relevantes são:

### 4.1. IBGE / SIDRA / PIB

Arquivos e APIs relacionados a:

- população;
- PIB municipal;
- PIB per capita;
- valor adicionado por setor;
- domicílios;
- força de trabalho;
- classificação territorial.

O arquivo `PIB dos Municípios - base de dados 2010-2023.xlsx` possui dados municipais de 2010 a 2023 e pode gerar séries econômicas além do PIB absoluto.

### 4.2. MUNIC 2024

A base `Base_MUNIC_2024_20251107.xlsx` possui abas de:

- recursos humanos;
- informática e comunicação;
- governança;
- habitação;
- transporte e mobilidade;
- agropecuária;
- gestão migratória;
- igualdade racial;
- eventos climáticos.

As colunas possuem nomes codificados, como `MREH011`, `Mhab03`, `Mtic06`, `Mtic10` e `Mtic12a1`. Esses códigos devem ser conferidos no dicionário oficial da planilha antes de qualquer uso.

### 4.3. SNIS

O arquivo `br_mdr_snis_municipio_agua_esgoto.csv` possui aproximadamente 133 colunas municipais sobre água, esgoto, receitas, despesas e investimentos.

Campos potencialmente úteis:

- população atendida por água;
- população atendida por esgoto;
- ligações ativas;
- extensão da rede;
- índice de hidrometração;
- índices de perdas;
- índice de coleta de esgoto;
- índice de tratamento de esgoto;
- consumo de água per capita;
- despesas;
- investimentos;
- receitas;
- quantidade de empregados;
- consumo de energia.

Esta é uma das maiores oportunidades de expansão do projeto.

### 4.4. CNES

O arquivo `cnes_estabelecimentos.csv` possui dados de estabelecimentos de saúde, incluindo:

- código IBGE;
- tipo de unidade;
- atendimento hospitalar;
- atendimento ambulatorial;
- centro cirúrgico;
- centro obstétrico;
- centro neonatal;
- serviços de apoio;
- natureza administrativa;
- localização.

É adequado para indicadores de infraestrutura de saúde. Entretanto, os campos disponíveis não comprovam necessariamente prontuário eletrônico ou consultas remotas.

### 4.5. CAGED/RAIS

Os arquivos de movimentação possuem:

- município;
- seção econômica;
- subclasse;
- CBO;
- salário;
- escolaridade;
- idade;
- sexo;
- tipo de movimentação;
- saldo de movimentação.

Podem gerar indicadores de emprego formal, composição setorial, salários e movimentações. O saldo CAGED não deve ser chamado automaticamente de taxa de desemprego, pois não representa toda a população economicamente ativa.

### 4.6. Banda larga

Os arquivos de acessos de banda larga possuem séries mensais por município, tecnologia, velocidade, empresa e tipo de produto.

Podem gerar:

- acessos por município;
- densidade de acessos;
- evolução temporal;
- participação de tecnologias;
- conectividade residencial e empresarial.

### 4.7. CadÚnico

O arquivo `cad_unico.txt` possui código IBGE, período e quantidade de pessoas cadastradas.

Pode gerar indicadores de cobertura e vulnerabilidade social. Porém, pessoas cadastradas não devem ser automaticamente interpretadas como pessoas sem-teto.

### 4.8. FBSP

A base municipal do FBSP possui homicídio doloso, latrocínio, mortes violentas, feminicídio, estupro, roubos e outros registros de segurança.

Além de homicídios, há possibilidade de ampliar o bloco de segurança, desde que os conceitos sejam documentados e haja cobertura adequada.

### 4.9. Bases de eventos climáticos e enchentes

As planilhas `Tab1.xlsx` a `Tab27.xlsx` e arquivos MUNIC de eventos climáticos incluem informações sobre:

- domicílios afetados;
- domicílios inacessíveis;
- deslocamento de moradores;
- interrupção de estudos;
- impacto no trabalho;
- resgate;
- alertas e canais de comunicação;
- impactos em bairros e ruas.

Esses arquivos podem sustentar indicadores de resiliência, mas exigem uma etapa própria de interpretação e extração.

### 4.10. PDFs de indicadores de desenvolvimento sustentável

Os PDFs organizados por tema podem ajudar na definição conceitual e no dicionário de indicadores. Eles não devem ser tratados como fonte tabular automaticamente sem extração, validação e identificação da unidade geográfica.

---

## 5. Dados já carregados

Com base nas verificações anteriores, existem registros reais em aproximadamente 20 IDs, totalizando cerca de 19,5 milhões de registros históricos contabilizados.

Entre os volumes confirmados estão:

| Indicador ou base | Registros aproximados |
|---|---:|
| empregos informais | 4.504.137 |
| empregos TIC | 4.504.137 |
| sobrevivência de negócios | 4.504.137 |
| taxa de desemprego | 4.504.137 |
| densidade de banda larga | 1.171.839 |
| medidores inteligentes de água | 105.325 |
| relação estudante/professor | 56.895 |
| orçamento per capita | 83.535 |
| sem-teto/CadÚnico | 38.997 |
| bombeiros | 11.110 |
| população | 5.572 |
| PIB | 5.571 |
| força de trabalho | 5.570 |
| denominadores MUNIC/CNES | aproximadamente 5.570–5.585 cada |

O total é de registros, não de municípios únicos. Uma mesma cidade pode ter vários anos, indicadores ou observações.

---

## 6. Oportunidades prioritárias de novos indicadores

### Prioridade 1 — IDEB

Arquivo:

`divulgacao_anos_iniciais_municipios_2023/divulgacao_anos_iniciais_municipios_2023.xlsx`

Indicador alvo:

`ideb_iniciais`

É um indicador direto, com fonte oficial, código municipal e ano explícito. Deve ser validado e carregado antes dos indicadores mais ambíguos.

### Prioridade 2 — MUNIC

Validar semanticamente e extrair, se confirmado pelo dicionário:

- `iluminacao_telegestao`;
- `servicos_urbanos_online`;
- `escolas_conectadas_telegestao`;
- `moradias_inadequadas`;
- recursos humanos municipais;
- governança e resposta a eventos climáticos.

### Prioridade 3 — SNIS

Adicionar indicadores de:

- atendimento de água;
- atendimento de esgoto;
- tratamento de esgoto;
- perdas de água;
- hidrometração;
- investimento em saneamento;
- despesas de saneamento;
- consumo de água per capita.

Esses indicadores devem ser adicionados inicialmente como indicadores próprios, sem forçar correspondência com nomes existentes.

### Prioridade 4 — PIB e banda larga

Criar séries e indicadores derivados:

- PIB per capita;
- crescimento do PIB;
- participação setorial;
- densidade de banda larga por população;
- evolução da conectividade;
- participação de fibra ou outras tecnologias.

### Prioridade 5 — Eventos climáticos

Criar um módulo separado de extração para resiliência. Não misturar esses dados diretamente ao TOPSIS antes de confirmar:

- unidade geográfica;
- período;
- população de referência;
- numerador;
- denominador;
- interpretação da categoria.

---

## 7. Regras metodológicas obrigatórias

Para um indicador entrar no banco e no TOPSIS, deve possuir:

1. fonte identificada;
2. arquivo ou endpoint reproduzível;
3. coluna ou regra de cálculo documentada;
4. código IBGE municipal válido;
5. ano de referência;
6. valor numérico não artificial;
7. definição semântica confirmada;
8. cobertura municipal calculada;
9. tratamento explícito de nulos;
10. fonte gravada no campo `fonte`.

### Não fazer

- não converter ausentes em zero;
- não usar uma coluna apenas porque o nome parece semelhante;
- não usar `ST_ATEND_AMBULATORIAL` como prova de prontuário eletrônico;
- não usar `ST_ATEND_AMBULATORIAL` como prova de consultas remotas;
- não usar saldo CAGED como taxa de desemprego sem justificativa;
- não usar pessoas CadÚnico como sinônimo automático de pessoas sem-teto;
- não usar proxies sem marcá-los como proxy;
- não misturar anos sem registrar a referência temporal;
- não inserir dado estimado como se fosse dado observado.

### Política recomendada para proxies

Se um proxy for cientificamente necessário, ele deve ter:

- nome próprio, diferente do indicador original;
- justificativa documental;
- descrição da diferença conceitual;
- indicação explícita na apresentação e no banco;
- análise de sensibilidade, quando entrar no ranking.

---

## 8. Pendências críticas atuais

### 8.1. `total_domicilios`

O indicador apresentou cardinalidade incorreta em tentativas anteriores. Ele deve ser reprocessado e validado antes de ser usado como denominador de moradia ou medidores de energia.

Critério mínimo:

- aproximadamente 5.000 ou mais municípios válidos;
- códigos IBGE conferidos;
- valores positivos e plausíveis;
- ano e fonte registrados;
- snapshot reconstruído após a carga.

### 8.2. Numeradores MUNIC ausentes

Os denominadores MUNIC foram carregados, mas os numeradores abaixo ainda não estavam disponíveis no ranking:

- `escolas_conectadas_telegestao_numerador`;
- `iluminacao_telegestao_numerador`;
- `servicos_urbanos_online_numerador`.

A existência das colunas no `etl_config.py` não comprova que a extração foi concluída nem que o significado foi validado.

### 8.3. Indicadores CNES ambíguos

Os seguintes indicadores precisam de revisão semântica:

- `consultas_remotas`;
- `prontuario_eletronico`;
- `hospitais_gerador_backup`.

O CNES pode sustentar infraestrutura de saúde, mas não necessariamente todos esses recursos digitais ou de resiliência.

### 8.4. Relatório automatizado de inventário

Deve ser criado um relatório que liste, para cada candidato:

- nome do indicador;
- fonte;
- arquivo;
- coluna;
- número de registros;
- municípios cobertos;
- anos;
- nulos;
- mínimos e máximos;
- regra de cálculo;
- status de aprovação.

---

## 9. Plano de execução recomendado

### Fase 1 — auditoria

1. Confirmar o caminho real e a finalidade do mapeador do datalake.
2. Catalogar arquivos e abas.
3. Ler os dicionários oficiais das fontes.
4. Criar uma matriz de candidatos.
5. Não inserir dados nesta fase.

### Fase 2 — indicadores diretos

1. IDEB;
2. PIB per capita;
3. séries de banda larga;
4. indicadores diretos SNIS;
5. validar cobertura e distribuição.

### Fase 3 — indicadores derivados

1. água e esgoto;
2. perdas e hidrometração;
3. crescimento econômico;
4. densidade de conectividade;
5. MUNIC após confirmação semântica.

### Fase 4 — integração no TOPSIS

1. adicionar somente indicadores aprovados;
2. manter pesos documentados;
3. verificar impactos positivo/negativo;
4. reconstruir snapshot;
5. executar testes unitários;
6. testar o endpoint com cidades de diferentes regiões;
7. comparar ranking antes e depois.

### Fase 5 — resiliência e fontes complexas

1. eventos climáticos;
2. SINISA;
3. CAGED/RAIS com metodologia revisada;
4. CNES com indicadores semânticos confirmados;
5. demais fontes públicas.

---

## 10. Critério de aprovação de um indicador

Cada indicador deve ter uma ficha semelhante a esta:

| Campo | Exemplo |
|---|---|
| ID | `ideb_iniciais` |
| Nome | IDEB dos anos iniciais |
| Fonte | INEP |
| Arquivo | nome completo do arquivo |
| Aba | `IDEB_AI_MUNICÍPIOS` |
| Coluna | nome original da coluna |
| Código geográfico | `CO_MUNICIPIO` |
| Ano | 2023 |
| Tipo | direto |
| Registros | quantidade |
| Municípios | quantidade |
| Nulos | quantidade |
| Mínimo/máximo | faixa observada |
| Unidade | escala ou percentual |
| Status | aprovado, proxy ou pendente |
| Observações | limitações conhecidas |

Um indicador só deve ser marcado como `aprovado` quando todos os campos essenciais estiverem preenchidos.

---

## 11. Testes mínimos após qualquer carga

Após inserir ou alterar dados:

1. confirmar quantidade de registros;
2. confirmar municípios distintos;
3. verificar nulos;
4. verificar duplicidades por município, indicador e ano;
5. verificar códigos IBGE inválidos;
6. verificar valores negativos ou fora da faixa esperada;
7. reconstruir `valores_indicadores_latest`;
8. executar `pytest`;
9. testar `POST /topsis/ranking-hibrido`;
10. comparar a quantidade de indicadores retornados;
11. registrar o tempo de resposta;
12. salvar relatório da execução.

Não considerar uma carga concluída apenas porque o script terminou sem erro.

---

## 12. Roteiro para apresentação da IC

A apresentação pode demonstrar:

1. problema de comparação entre municípios;
2. fontes públicas e datalake;
3. padronização por código IBGE;
4. tratamento de valores ausentes;
5. matriz TOPSIS;
6. endpoint da API;
7. valores reais utilizados no cálculo;
8. ranking de três ou mais municípios;
9. fonte e ano dos indicadores;
10. limitações e plano de expansão.

Formulação recomendada:

> O Urbix possui um núcleo funcional de ingestão, normalização e ranking TOPSIS com dados municipais reais. A cobertura dos indicadores está em expansão e somente variáveis com fonte, unidade, período e cobertura verificáveis devem ser liberadas para o cálculo.

Essa formulação é tecnicamente defensável e não promete uma cobertura que ainda não foi validada.

---

## 13. Checklist para quem continuar a pesquisa

- [ ] Ler este relatório antes de alterar o ETL.
- [ ] Ler `dicionario_de_dados_etl.md`.
- [ ] Ler `backend/app/etl_config.py`.
- [ ] Ler `backend/tools/local_etl_service.py`.
- [ ] Confirmar o caminho atual do mapeador do datalake.
- [ ] Não assumir que nomes de colunas são indicadores.
- [ ] Definir unidade, ano e denominador.
- [ ] Fazer auditoria antes da carga.
- [ ] Preservar nulos.
- [ ] Registrar a fonte em todos os registros.
- [ ] Validar cobertura municipal.
- [ ] Reconstruir o snapshot.
- [ ] Executar testes.
- [ ] Testar o endpoint.
- [ ] Atualizar a matriz de fontes.
- [ ] Documentar limitações e decisões.

---

## 14. Conclusão

O Urbix já possui uma base significativa de dados públicos e locais. O próximo ganho não depende apenas de baixar novas fontes: depende principalmente de transformar arquivos existentes em indicadores municipais com significado comprovado.

As melhores próximas fontes são:

1. INEP/IDEB;
2. MUNIC 2024;
3. SNIS;
4. PIB municipal;
5. banda larga;
6. CadÚnico;
7. eventos climáticos.

A expansão deve ser incremental, auditável e reversível. O projeto não deve tentar colocar todos os arquivos no TOPSIS de uma vez. O caminho mais seguro é validar poucos indicadores por vez, medir cobertura, testar o ranking e registrar cada decisão metodológica.
