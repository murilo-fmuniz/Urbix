# Urbix Frontend

Aplicação React/Vite para seleção de municípios, simulações manuais e visualização do ranking TOPSIS.

## Stack

- React 18;
- Vite;
- Axios;
- Chart.js e `react-chartjs-2`;
- React Router;
- Tailwind/CSS.

## Executar localmente

```powershell
cd frontend
npm install
npm run dev
```

Crie `frontend/.env.local`:

```text
VITE_API_URL=http://localhost:8000
```

Build de produção:

```powershell
npm run build
```

## API consumida

O frontend envia para:

`POST /topsis/ranking-hibrido`

Payload:

```json
{
  "cidades_ibge": ["4101408", "4113700", "4115200"],
  "simulacoes": [
    {
      "codigo_ibge": "4101408",
      "valores_brutos": {}
    }
  ]
}
```

A resposta é um array ordenado com:

- `codigo_ibge`;
- `nome_cidade`;
- `pontuacao_topsis`;
- `distancia_positiva`;
- `distancia_negativa`;
- `valores_calculados`.

## Componentes principais

- `src/pages/RankingPage.jsx`: fluxo de ranking e estado da resposta.
- `src/components/CityInputForm.jsx`: seleção de municípios e valores manuais.
- `src/components/RankingTable.jsx`: ranking final.
- `src/components/IndicatorsComparisonChart.jsx`: comparação por eixos.
- `src/services/api.js`: cliente Axios e tratamento de erros.

## Deploy atual

- Frontend: `https://urbix-two.vercel.app/`
- Backend: `https://urbix-api.onrender.com/`

A variável de produção deve ser:

```text
VITE_API_URL=https://urbix-api.onrender.com
```

## Observações

O backend atualmente retorna 19 indicadores calculáveis. A tela mostra somente os indicadores presentes em `valores_calculados`; indicadores pendentes ou sem cobertura não devem ser preenchidos artificialmente.
