# Urbix

> Sistema de análise e visualização de indicadores de maturidade para Cidades Sustentáveis, baseado na Norma ISO 37100.

## 🎯 Sobre o Projeto

O Urbix é uma ferramenta desenvolvida como parte de um **projeto de Iniciação Científica**, focada na análise e visualização de indicadores de maturidade para Cidades Sustentáveis. O projeto utiliza como base a Norma ISO 37100, que fornece diretrizes e métricas para avaliação do desenvolvimento sustentável em comunidades urbanas.

A ISO 37100 estabelece uma terminologia padronizada e frameworks para mensurar e avaliar o desempenho das cidades em diferentes aspectos de sustentabilidade e inteligência urbana.

### Natureza do Projeto

> 📚 **Projeto de Pesquisa Acadêmica**
>
> Este sistema foi desenvolvido em contexto acadêmico como prova de conceito para análise de indicadores urbanos. A infraestrutura está preparada para escalabilidade, mas a cobertura atual de dados reflete as limitações típicas de um projeto de Iniciação Científica: recursos limitados, acesso restrito a fontes de dados oficiais e foco em validação metodológica.
>
> A ampliação da cobertura para todos os municípios brasileiros demandaria recursos significativos para coleta, validação e manutenção contínua de dados de múltiplas fontes governamentais.

## 📊 Funcionalidades

### Sistema de Banco de Dados
- **SQLAlchemy ORM**: Suporte para SQLite (desenvolvimento) e PostgreSQL (produção)
- **Estrutura Modular**: Organização em módulos separados (models, config, database, etl, scripts)
- **ETL Automatizado**: Integração com API do IBGE para dados de estados e municípios
- **Sistema de Logs**: Rastreamento de sincronizações e operações

### Dados Geográficos
- **Estados**: Todos os 27 estados brasileiros com códigos IBGE
- **Municípios**: Mais de 5.500 municípios com informações demográficas e geográficas
- **Regiões**: Organização por região (Norte, Nordeste, Centro-Oeste, Sudeste, Sul)

### Indicadores
Sistema extensível para múltiplos indicadores urbanos:
- **Categorias**: Organização por categorias (Economia, Saúde, Educação, etc.)
- **Metadados Completos**: Descrição, unidade, fonte de dados, valores-alvo
- **Valores por Cidade**: Histórico de valores com referência temporal
- **Qualidade de Dados**: Rastreamento da qualidade e fonte dos dados

#### Indicadores Trabalhados no Projeto

O projeto contempla indicadores organizados segundo as normas ISO 37120, 37122 e 37123 para Cidades Sustentáveis e Inteligentes:

##### ISO 37120 - Indicadores de Desenvolvimento Sustentável

| Código | Indicador | Categoria | Descrição | Fonte de Dados |
|--------|-----------|-----------|-----------|----------------|
| **37120** | **Saúde - Leitos e Médicos** | Social | Número de leitos hospitalares e médicos por habitante | CNES/DATASUS |
| **37120** | **Saúde - Mortalidade Infantil** | Social | Taxa de mortalidade infantil | DATASUS |
| **37120** | **Segurança - Tempo Resposta Bombeiros** | Segurança | Tempo médio de resposta dos bombeiros | Corpo de Bombeiros |
| **37120** | **Segurança - Homicídios/Crimes** | Segurança | Taxa de homicídios e crimes violentos | Atlas da Violência/SSP |

##### ISO 37122 - Indicadores para Cidades Inteligentes

| Código | Indicador | Categoria | Descrição | Fonte de Dados |
|--------|-----------|-----------|-----------|----------------|
| **37122-4.1** | **Contratos com Dados Abertos** | Governança | % contratos públicos em formato aberto | Portal Transparência |
| **37122-6.2** | **Pagamentos Eletrônicos** | Economia | % pagamentos municipais aceitos eletronicamente | Prefeitura |
| **37122-7.1** | **Computadores por Aluno** | Educação | Número de computadores por aluno na rede pública | Censo Escolar |
| **37122-10.1** | **Visitas Portal Dados Abertos** | Governança | Número de visitas ao portal de transparência | Portal Transparência |
| **37122-10.2** | **Serviços Online Solicitados** | Governança | % serviços municipais solicitados online | Carta de Serviços |
| **37122-12.1** | **Coleta Lixo com Telemetria** | Ambiental | % veículos de coleta com rastreamento GPS | Limpeza Urbana |
| **37122-15.1** | **Edifícios Verdes** | Ambiental | Número de edificações com certificação verde | IPTU Verde |
| **37122-16.1** | **Estações Monit. Ar** | Ambiental | Número de estações de monitoramento de qualidade do ar | IAP/CETESB |
| **37122-19.1** | **Semáforos Inteligentes** | Infraestrutura | % semáforos com controle inteligente | Trânsito Municipal |

##### ISO 37123 - Indicadores para Cidades Resilientes

| Código | Indicador | Categoria | Descrição | Fonte de Dados |
|--------|-----------|-----------|-----------|----------------|
| **37123-1.1** | **Áreas Naturais Avaliadas** | Ambiental | % áreas naturais protegidas com avaliação | Plano de Manejo |
| **37123-2.1** | **Perda Econômica Desastres** | Resiliência | Perdas econômicas por desastres naturais | Defesa Civil/S2iD |
| **37123-3.1** | **Propriedades com Seguro** | Resiliência | % propriedades com seguro contra desastres | SUSEP |
| **37123-8.1** | **Escolas com Plano Emergência** | Educação | % escolas com plano de emergência implementado | Defesa Civil |
| **37123-11.1** | **Interrupção Educacional** | Educação | Dias letivos perdidos por emergências | Secretaria Educação |
| **37123-20/21** | **Eventos Climáticos Extremos** | Resiliência | Frequência de ondas calor/frio e enchentes | Defesa Civil/S2iD |
| **37123-29** | **Despesas Serviços Sociais** | Social | % orçamento em serviços sociais de emergência | LOA/Assistência Social |

##### Outros Indicadores

| Código | Indicador | Categoria | Descrição | Fonte de Dados |
|--------|-----------|-----------|-----------|----------------|
| **24** | **Orçamento Manutenção Ativos** | Infraestrutura | % orçamento para manutenção de ativos públicos | LOA Municipal |

> **⚠️ Nota Importante sobre Coleta de Dados**
> 
> Este é um **projeto de pesquisa em desenvolvimento** como parte de uma Iniciação Científica. Atualmente, a base de dados contempla um conjunto limitado de municípios com dados completos e validados. 
>
> Para uma **cobertura mais abrangente** dos mais de 5.500 municípios brasileiros, seria necessária uma infraestrutura robusta de coleta de dados que incluísse:
> - Integração automatizada com múltiplas APIs governamentais (DATASUS, INEP, SNIS, etc.)
> - Parcerias com prefeituras para acesso a dados municipais
> - Equipe dedicada para validação e atualização periódica dos dados
> - Infraestrutura de armazenamento e processamento escalável
>
> O sistema está preparado para escalar, mas a disponibilidade e qualidade dos dados públicos brasileiros ainda é um desafio significativo para pesquisas desta natureza.

## 🎨 Design e Paleta

O projeto utiliza uma paleta "Acadêmico Minimalista" que prioriza clareza e legibilidade:

- Fundo: Branco (#FFFFFF) - Proporciona clareza e legibilidade
- Texto Principal: Grafite (#222222) - Alto contraste para leitura
- Elementos Secundários: Cinza "Concreto" (#B2B2B2) - Para elementos de suporte
- Destaque: Laranja Queimado (#E65100) - Para elementos interativos e gráficos

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e de alta performance
- **SQLAlchemy**: ORM para manipulação do banco de dados
- **Pydantic**: Validação de dados e serialização
- **SQLite/PostgreSQL**: Bancos de dados suportados
- **Requests**: Integração com APIs externas (IBGE)
- **Logging**: Sistema estruturado de logs

### Frontend
- **React 18**: Biblioteca para interfaces de usuário
- **Vite**: Build tool e dev server ultrarrápido
- **React Router**: Navegação entre páginas
- **Axios**: Cliente HTTP para requisições
- **CSS Modules**: Estilização modular e escopo local

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.8 ou superior
- Node.js 14.0 ou superior
- NPM ou Yarn

### Backend (FastAPI)

1. Entre na pasta do backend:
   ```bash
   cd backend
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicialize o banco de dados (primeira vez):
   ```bash
   python -m scripts.init_database
   ```
   Este comando irá:
   - Criar a estrutura do banco de dados
   - Buscar dados de estados e municípios do IBGE
   - Migrar indicadores existentes

5. Inicie o servidor:
   ```bash
   uvicorn main:app --reload
   ```

O servidor estará rodando em `http://localhost:8000`

**Documentação Interativa**: Acesse `http://localhost:8000/docs` para a interface Swagger UI

### Frontend (React)

1. Entre na pasta do frontend:
   ```bash
   cd frontend
   ```

2. Instale as dependências:
   ```bash
   npm install
   ```

3. Inicie o servidor de desenvolvimento:
   ```bash
   npm run dev
   ```

O frontend estará disponível em `http://localhost:5173`

## 📍 API Endpoints

### Indicadores
- **GET /api/indicators**: Lista todos os indicadores cadastrados
- **GET /api/indicators/{indicator_id}**: Detalhes de um indicador específico
- **GET /api/indicators/category/{category}**: Indicadores por categoria

### Cidades
- **GET /api/cities**: Lista todas as cidades (com paginação)
- **GET /api/cities/{city_id}**: Detalhes de uma cidade
- **GET /api/cities/search?q={query}**: Busca cidades por nome
- **GET /api/cities/{city_id}/indicators**: Indicadores de uma cidade específica

### Estados
- **GET /api/states**: Lista todos os estados
- **GET /api/states/{state_id}**: Detalhes de um estado
- **GET /api/states/{state_id}/cities**: Cidades de um estado

**Documentação Completa**: Acesse `/docs` para a documentação interativa Swagger

## 📂 Estrutura do Backend

```
backend/
├── config/           # Configurações (database)
├── models/           # Modelos SQLAlchemy (State, City, Indicator, etc.)
├── database/         # Operações CRUD e queries
├── api/              # Endpoints FastAPI
├── etl/              # Pipelines ETL (IBGE, etc.)
├── scripts/          # Scripts utilitários (init_database, migrate_data)
└── data/             # Banco de dados SQLite
```

**Documentação Detalhada**: Consulte [backend/README.md](backend/README.md) para mais informações sobre a arquitetura e uso dos módulos.

## 🔧 Scripts Úteis

### Backend
```bash
# Inicializar banco de dados do zero
python -m scripts.init_database

# Atualizar dados do IBGE
python -m etl.ibge_etl

# Migrar dados existentes
python -m scripts.migrate_data

# Validar estrutura do projeto
python validate_structure.py

# Executar servidor
uvicorn main:app --reload
```

### Frontend
```bash
# Instalar dependências
npm install

# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview da build
npm run preview
```

## 📈 Roadmap

### ✅ Implementado
- [x] Estrutura modular do backend
- [x] Integração com API do IBGE
- [x] Sistema de banco de dados com SQLAlchemy
- [x] ETL automatizado para estados e municípios
- [x] API RESTful com FastAPI
- [x] Documentação interativa (Swagger)
- [x] Sistema de logs e sincronização

### 🚧 Em Desenvolvimento
- [ ] Interface frontend completa
- [ ] Visualizações de dados (gráficos, mapas)
- [ ] Integração frontend-backend completa

### 📋 Planejado

#### 1. Dados e Indicadores
- Integração com mais fontes de dados (DATASUS, INEP, SNIS, etc.)
- Expandir cobertura de municípios com dados completos e validados
- Estabelecer parcerias com órgãos governamentais para acesso a APIs oficiais
- Implementar sistema de validação e qualidade de dados em larga escala
- Cálculo de índices compostos
- Análise temporal de indicadores
- Pipeline automatizado de atualização periódica de dados

#### 2. Interface de Usuário
- Dashboard interativo
- Comparação entre cidades
- Filtros avançados
- Exportação de relatórios

#### 3. Funcionalidades Avançadas
- Autenticação e autorização
- API pública com rate limiting
- Cache de dados
- Modo offline

#### 4. Análise e Insights
- Rankings de cidades
- Identificação de padrões
- Alertas e notificações
- Previsões baseadas em ML

## 📝 Logs e Monitoramento

O sistema implementa logs estruturados com diferentes níveis:
- **INFO**: Informações gerais de operação
- **DEBUG**: Detalhes técnicos para desenvolvimento
- **WARNING**: Alertas sobre problemas não críticos
- **ERROR**: Erros que requerem atenção

Todos os logs de sincronização com APIs externas são registrados na tabela `api_sync_logs`.

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto é desenvolvido como parte de uma Iniciação Científica.

## 👥 Autores

Projeto de Iniciação Científica - Universidade

---

**Nota**: Para mais informações sobre o backend, consulte a [documentação do backend](backend/README.md).
