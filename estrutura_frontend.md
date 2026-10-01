# Estrutura atual do frontend

```text
frontend/
├── src/
│   ├── App.jsx
│   ├── main.jsx
│   ├── pages/
│   │   ├── RankingPage.jsx
│   │   ├── HomePage.jsx
│   │   ├── HistoricalSeriesPage.jsx
│   │   └── CityIndicatorsHistoryPage.jsx
│   ├── components/
│   │   ├── CityInputForm.jsx
│   │   ├── RankingTable.jsx
│   │   ├── IndicatorsComparisonChart.jsx
│   │   └── SmartCityDashboard.jsx
│   ├── services/
│   │   └── api.js
│   ├── constants/
│   └── data/
├── package.json
├── vite.config.js
├── .env.local
├── .env.production
└── README.md
```

## Integração principal

`src/services/api.js` envia:

```json
{
  "cidades_ibge": ["4101408", "4113700", "4115200"],
  "simulacoes": []
}
```

para `POST /topsis/ranking-hibrido`.

A resposta contém a pontuação TOPSIS e os valores calculados dos indicadores disponíveis. Atualmente o backend retorna 19 indicadores calculáveis.
