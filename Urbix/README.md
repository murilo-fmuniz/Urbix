# Urbix

> Sistema de análise e visualização de indicadores de maturidade para Cidades Sustentáveis, baseado na Norma ISO 37100.

## 🎯 Sobre o Projeto

O Urbix é uma ferramenta desenvolvida como parte de um projeto de Iniciação Científica, focada na análise e visualização de indicadores de maturidade para Cidades Sustentáveis. O projeto utiliza como base a Norma ISO 37100, que fornece diretrizes e métricas para avaliação do desenvolvimento sustentável em comunidades urbanas.

A ISO 37100 estabelece uma terminologia padronizada e frameworks para mensurar e avaliar o desempenho das cidades em diferentes aspectos de sustentabilidade e inteligência urbana.

## 🎨 Design e Paleta

O projeto utiliza uma paleta "Acadêmico Minimalista" que prioriza clareza e legibilidade:

- Fundo: Branco (#FFFFFF) - Proporciona clareza e legibilidade
- Texto Principal: Grafite (#222222) - Alto contraste para leitura
- Elementos Secundários: Cinza "Concreto" (#B2B2B2) - Para elementos de suporte
- Destaque: Laranja Queimado (#E65100) - Para elementos interativos e gráficos

## 🛠️ Tecnologias Utilizadas

### Backend
- FastAPI (Python)
- Pydantic para validação de dados
- JSON para armazenamento local

### Frontend
- React (com Vite)
- React Router para navegação
- Axios para requisições HTTP
- CSS Modules para estilização

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
   .\\venv\\Scripts\\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie o servidor:
   ```bash
   uvicorn main:app --reload
   ```

O servidor estará rodando em `http://localhost:8000`

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

## 📈 Pontos Futuros (A Desenvolver)

1. **Autenticação e Autorização**
   - Implementar sistema de login
   - Diferentes níveis de acesso (administrador, gestor, visualizador)

2. **Expansão do Dashboard**
   - Adicionar mais tipos de visualizações (gráficos, mapas)
   - Filtros por categoria e período
   - Comparação entre diferentes períodos

3. **Gestão de Dados**
   - Migrar para um banco de dados relacional
   - Sistema de backup e versionamento de dados
   - Importação/exportação de dados em diferentes formatos

4. **Melhorias na Interface**
   - Modo escuro
   - Responsividade para dispositivos móveis
   - Acessibilidade (WCAG 2.1)

5. **Funcionalidades Avançadas**
   - Geração de relatórios em PDF
   - API pública com documentação
   - Integração com outras fontes de dados urbanos

6. **Análise e Machine Learning**
   - Previsões de tendências
   - Identificação de padrões
   - Recomendações automáticas

7. **Internacionalização**
   - Suporte a múltiplos idiomas
   - Adaptação para diferentes padrões regionais