# 💻 Urbix - Frontend (React & Vite)

Aplicação web interativa focada em Visualização de Dados (Data Viz) para a apresentação dos resultados da avaliação multicritério TOPSIS.

## 🚀 Tecnologias Principais
*   **Core:** React (com Vite para build ultrarrápido).
*   **Estilização:** Tailwind CSS e CSS Modules.
*   **Gráficos e Visualização:** Chart.js (`react-chartjs-2`), com foco em Radar Charts para comparação de eixos temáticos (estilo "Stats de RPG").
*   **Comunicação:** Axios (com tratamento de exceções e interceptors).

## 🧩 Principais Componentes
*   **SmartCityDashboard & RankingPage:** Telas responsáveis por capturar as cidades escolhidas, montar o payload estrito (Pydantic-compliant) e renderizar a tabela de classificação final e os gráficos de desempenho (Radar) com escala de 0 a 100.
*   **ManualDataForm:** Interface administrativa dinâmica gerada a partir das normas ISO (37120, 37122 e 37123) que permite às prefeituras imputarem 47 indicadores manualmente para alimentar a base oficial.

## 💻 Como rodar localmente

1. Certifique-se de ter o Node.js instalado.

2. Instale as dependências:
    npm install

3. Configure a variável de ambiente criando um arquivo `.env.local` na raiz da pasta `frontend`:
    VITE_API_URL=http://localhost:8000

4. Inicie o servidor de desenvolvimento:
    npm run dev

Acesse a interface no navegador através da porta indicada pelo Vite (geralmente `http://localhost:5173`).