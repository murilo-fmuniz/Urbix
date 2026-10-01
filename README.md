# Urbix — Ranking Municipal com TOPSIS

Projeto de Iniciação Científica da UTFPR para ingestão de dados públicos municipais e comparação multicritério com TOPSIS.

## Resumo do projeto

O Urbix investiga como integrar fontes públicas brasileiras heterogêneas em uma matriz comparável de maturidade municipal. O fluxo combina engenharia de dados, padronização por código IBGE, normalização de indicadores e o método TOPSIS (*Technique for Order Preference by Similarity to Ideal Solution*).

O objetivo não é apenas produzir uma pontuação: é manter a rastreabilidade de cada valor utilizado, incluindo fonte, ano, cobertura municipal e limitações semânticas.

## Metodologia

1. O datalake local é inventariado por `scripts/map_data_lake.py`.
2. O `backend/app/etl_config.py` define fonte, coluna, filtros, agregação e status de cada indicador.
3. O ETL consulta APIs oficiais e processa planilhas/CSV municipais.
4. Os valores são gravados no histórico `valores_indicadores`.
5. O snapshot `valores_indicadores_latest` mantém o dado mais recente por município e indicador.
6. O motor calcula a matriz TOPSIS somente com indicadores aprovados e disponíveis.
7. A auditoria mede cobertura por eixo e impede que ausência de dado seja confundida com zero.

## Estado atual

- Backend FastAPI integrado ao PostgreSQL.
- ETL nacional para municípios brasileiros.
- Frontend React/Vite publicado na Vercel.
- Backend publicado no Render.
- Snapshot de valores mais recentes para acelerar o ranking.
- 19 indicadores atualmente calculáveis no TOPSIS.
- Auditoria de cobertura por eixo em `docs/RELATORIO_AUDITORIA_ETL_IC.md`.

### Resultado auditado em 01/10/2026

- 5.571 municípios cadastrados;
- 130.579 registros com valor no histórico/snapshot;
- 65 indicadores configurados;
- 19 indicadores calculáveis no TOPSIS;
- cobertura superior a 99% para população, PIB, domicílios, força de trabalho, banda larga, água SNIS e vários indicadores MUNIC;
- cobertura parcial para SICONFI e esgoto SNIS;
- indicadores de eventos climáticos com cobertura regional;
- homicídios temporariamente fora do ranking por cobertura insuficiente.

Os valores detalhados por eixo, fonte e ano estão no relatório de auditoria.

## Contribuição da IC

O projeto entrega uma arquitetura reprodutível para transformar dados governamentais dispersos em indicadores municipais auditáveis. A principal contribuição é combinar ingestão, validação de cobertura, tratamento explícito de ausência e ranking multicritério sem ocultar as limitações dos dados.

## Limitações atuais

- O SICONFI não cobre todos os municípios na mesma proporção das bases IBGE/MUNIC.
- As variáveis de esgoto do SNIS têm cobertura menor que as de água.
- Saldo CAGED representa movimentações formais, não a taxa de desemprego da população.
- CNES não é usado como prova de prontuário eletrônico, telemedicina ou gerador hospitalar.
- Bases de eventos climáticos não possuem cobertura nacional completa.
- Indicadores pendentes permanecem fora do TOPSIS até terem fonte e semântica confirmadas.

Os dados mais recentes auditados incluem IBGE/SIDRA, SICONFI, MUNIC, SNIS, CAGED, CNES, FBSP e banda larga. Indicadores sem fonte, cobertura ou semântica confirmada permanecem fora do ranking.

## Estrutura

- `backend/`: FastAPI, ETL, configuração de indicadores e serviços TOPSIS.
- `frontend/`: aplicação React/Vite e visualizações.
- `scripts/`: mapeamento do datalake e utilitários de preparação.
- `docs/`: documentação operacional, metodológica e relatório da IC.
- `dicionario_de_dados_etl.md`: inventário atualizado das planilhas do datalake.

## Execução do backend

```powershell
cd backend
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API local: `http://localhost:8000`
Swagger: `http://localhost:8000/docs`

## Executar o ETL nacional

O comando abaixo processa todos os municípios cadastrados, consulta SIDRA e SICONFI e atualiza o snapshot:

```powershell
cd backend\tools
..\venv\Scripts\python.exe local_etl_service.py
```

Para gerar a auditoria depois da carga:

```powershell
..\venv\Scripts\python.exe audit_etl_runtime.py
```

O runner `run_etl_apucarana.py` é apenas um teste limitado e não deve ser usado para a carga nacional.

## Executar o frontend

```powershell
cd frontend
npm install
npm run dev
```

Configure `frontend/.env.local`:

```text
VITE_API_URL=http://localhost:8000
```

Produção:

- Frontend: `https://urbix-two.vercel.app/`
- Backend: `https://urbix-api.onrender.com/`

## Endpoint principal

`POST /topsis/ranking-hibrido`

```json
{
  "cidades_ibge": ["4101408", "4113700", "4115200"],
  "simulacoes": []
}
```

## Documentação essencial

- `docs/RELATORIO_AUDITORIA_ETL_IC.md`: cobertura, fontes, anos e pendências.
- `docs/PROXIMOS_PASSOS_CONTINUIDADE_IC.md`: continuidade da pesquisa.
- `docs/MATRIZ_FONTES_PUBLICAS_URBIX.md`: fontes públicas e mapeamento metodológico.
- `docs/ARCHITECTURE.md`: arquitetura do sistema.
- `docs/DEPLOYMENT_GUIDE_FINAL.md`: publicação e operação.
- `docs/INTEGRATION_TESTING_GUIDE.md`: testes de integração.

## Regra metodológica

Ausência de dado não vira zero. Proxies sem definição comprovada, cobertura insuficiente ou denominador incompatível não entram no cálculo TOPSIS.
