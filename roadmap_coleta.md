# Roadmap de Coleta de Dados - Indicadores ISO 37120/37122/37123

Este documento mapeia os indicadores das normas ISO para Cidades Sustentáveis, Inteligentes e Resilientes, com estratégias de busca para coleta de dados em municípios brasileiros.

## Estrutura

- **Norma**: Norma ISO de referência (37120, 37122, 37123)
- **Indicador**: Código e descrição resumida do indicador
- **Termo de Pesquisa**: Estratégia para buscar dados em portais governamentais e motores de busca

## Indicadores Mapeados

| Norma | Indicador (Resumido) | Termo de Pesquisa (Google/Portal) |
|-------|---------------------|-----------------------------------|
| 37122 | 10.1 - Visitas ao portal de dados abertos | "Estatísticas acesso portal transparência [Cidade]" |
| 37122 | 10.2 - Serviços solicitados online | "Carta de serviços ao usuário [Cidade] online" |
| 37122 | 19.1 - % Semáforos inteligentes | "Licitação semáforos inteligentes [Cidade]" ou notícias locais |
| 37122 | 6.2 - Pagamentos eletrônicos cidade | "Pagamento IPTU PIX cartão crédito [Cidade]" |
| 37123 | 8.1 - Escolas com plano de emergência | "Programa brigada escolar defesa civil [Cidade]" |
| 37123 | 11.1 - Interrupção educacional (dias parados) | "Calendário escolar [Ano] dias letivos cumpridos" |
| 37123 | 20/21 - Freq. ondas calor/frio/enchentes | "Histórico decretos emergência S2iD [Cidade]" |
| 24 | % Orçamento manutenção ativos | "LOA [Ano] despesas manutenção infraestrutura" |
| 37122 | 16.1 - Estações monitoramento ar | "IAP monitoramento qualidade ar [Cidade]" |
| 37122 | 7.1 - Computadores por aluno | "Censo escolar [Cidade] equipamentos informática" |
| 37120 | Segurança - Tempo resposta bombeiros | "Relatório estatístico Corpo de Bombeiros [Estado/Cidade]" |
| 37120 | Segurança - Homicídios/Crimes | "Atlas da Violência [Cidade]" ou "Secretaria Segurança Pública estatísticas" |
| 37120 | Saúde - Leitos e Médicos | "CNES leitos SUS [Cidade]" |
| 37120 | Saúde - Mortalidade Infantil | "DATASUS Tabnet mortalidade infantil [Cidade]" |
| 37122 | 4.1 - Contratos com dados abertos | "Decreto dados abertos contratos administrativos [Cidade]" |
| 37123 | 3.1 - Propriedades com seguro | Difícil. Tentar: "Dados SUSEP seguros residenciais por região" |
| 37123 | 29 - Despesas serviços sociais | "LOA [Ano] Fundo Municipal Assistência Social" |
| 37122 | 12.1 - Coleta lixo com telemetria | "Contrato concessão limpeza urbana [Cidade] rastreamento GPS" |
| 37122 | 15.1 - Edifícios verdes (Green building) | "Certificação IPTU Verde [Cidade]" |
| 37123 | 2.1 - Perda econômica por desastres | "Relatório danos materiais defesa civil S2iD [Cidade]" |
| 37123 | 1.1 - % Áreas naturais avaliadas | "Plano de Manejo áreas proteção ambiental [Cidade]" |

## Fontes de Dados Principais

### Dados Nacionais (APIs e Portais)
- **IBGE**: Dados demográficos e geográficos
- **DATASUS**: Dados de saúde pública
- **INEP**: Censo escolar e educação
- **SNIS**: Saneamento básico
- **S2iD**: Sistema de defesa civil
- **CNES**: Cadastro nacional de estabelecimentos de saúde
- **Atlas da Violência**: Dados de segurança pública
- **SUSEP**: Dados de seguros

### Dados Municipais
- **Portal de Transparência**: Orçamento, licitações, contratos
- **Carta de Serviços**: Serviços digitais
- **Secretarias Municipais**: Dados específicos locais
- **Defesa Civil Municipal**: Emergências e desastres

## Desafios de Coleta

⚠️ **Indicadores com maior dificuldade:**
1. **37123-3.1 (Seguros)**: Dados agregados por região, não por município
2. **37122-19.1 (Semáforos inteligentes)**: Dependente de licitações e notícias locais
3. **37122-10.1/10.2 (Serviços online)**: Nem todos os municípios possuem portal robusto
4. **37123-2.1 (Perdas econômicas)**: Registro incompleto em municípios menores

## Próximos Passos

1. **Automatizar coleta** onde APIs estão disponíveis (IBGE, DATASUS, INEP)
2. **Web scraping** para portais municipais padronizados
3. **Parcerias** com prefeituras para acesso direto a dados
4. **Validação manual** para dados coletados de fontes não estruturadas