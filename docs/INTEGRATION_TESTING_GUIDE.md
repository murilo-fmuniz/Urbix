# Guia atual de testes de integração

## 1. Subir o backend

```powershell
cd backend
.\venv\Scripts\activate
python -m uvicorn app.main:app --reload --port 8000
```

Swagger: `http://localhost:8000/docs`

## 2. Testar saúde e cidades

- `GET /`
- `GET /topsis/cidades?q=Apucarana`

## 3. Testar ranking

`POST /topsis/ranking-hibrido`

```json
{
  "cidades_ibge": ["4101408", "4113700", "4115200"],
  "simulacoes": []
}
```

A resposta esperada é um array ordenado com `pontuacao_topsis` e `valores_calculados`. O estado atual possui até 19 indicadores calculáveis, dependendo da cobertura das cidades.

## 4. Testar histórico

`GET /topsis/cidade/4101408/historico`

A resposta deve conter histórico, fonte, ano e o valor mais recente por indicador.

## 5. Subir o frontend

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5173/ranking`.

## 6. Validar o ETL

Depois de uma carga nacional:

```powershell
cd backend\tools
..\venv\Scripts\python.exe audit_etl_runtime.py
```

Confira `docs/RELATORIO_AUDITORIA_ETL_IC.md`.

## Critérios de aceitação

- HTTP `200` para pelo menos duas cidades com dados;
- resposta contendo `codigo_ibge`, `nome_cidade`, pontuação e valores;
- fontes e anos presentes no histórico;
- ausência de dados não convertida artificialmente em zero;
- cobertura documentada por indicador.
