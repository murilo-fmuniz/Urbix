# Urbix

> Sistema de análise e visualização de indicadores de maturidade para Cidades Sustentáveis, baseado na Norma ISO 37100.

## 🎯 Sobre o Projeto

O Urbix é uma ferramenta desenvolvida como parte de um projeto de Iniciação Científica, focada na análise e visualização de indicadores de maturidade para Cidades Sustentáveis. O projeto utiliza como base a Norma ISO 37100, que fornece diretrizes e métricas para avaliação do desenvolvimento sustentável em comunidades urbanas.

A ISO 37100 estabelece uma terminologia padronizada e frameworks para mensurar e avaliar o desempenho das cidades em diferentes aspectos de sustentabilidade e inteligência urbana.

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
- Integração com mais fontes de dados (DATASUS, INEP, etc.)
- Cálculo de índices compostos
- Análise temporal de indicadores

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
