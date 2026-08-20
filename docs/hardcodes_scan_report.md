# Varredura de hardcodes IBGE/UF

## Já normalizados para catálogo compartilhado

- `scripts/process_local_data.py` — municípios padrão passam a vir do catálogo IBGE local.
- `backend/app/services/local_data_service.py` — busca vazia retorna `None`.
- `backend/app/routers/topsis.py` — capitais do ranking derivadas do catálogo IBGE.
- `backend/sync_gov_apis.py` — cidades padrão derivadas do catálogo IBGE.
- `backend/app/services/tse_api.py` — fallback estadual resolve UF pelo catálogo IBGE, sem lista fixa de códigos.
- `frontend/src/components/CityInputForm.jsx` — lista de cidades vem do catálogo IBGE completo.
- `frontend/src/pages/AdminCidadesPage.jsx` — presets resolvidos pelo catálogo IBGE.
- `frontend/src/components/SmartCityDashboard.jsx` — cidades iniciais resolvidas pelo catálogo IBGE.
- `backend/app/data/ibge_catalog.json` e `frontend/src/data/ibge_catalog.json` — catálogo compartilhado de estados e municípios.

## Hardcodes que ainda existem por serem intencionais

### Fallbacks de dados reais / dados de teste

Arquivos com dicionários de fallback por cidade continuam usando códigos IBGE porque são fontes de segurança e não lógica de seleção:

- `backend/app/services/external_apis.py`
- `backend/app/services/datasus_api_expanded.py`
- `backend/app/services/inep_api.py`
- `backend/app/services/portal_transparencia_expanded.py`

### Exemplos e docs

- `backend/app/routers/local_data.py` — exemplos de documentação e response examples.
- `backend/app/services/demo_city_seed.py` — cidade de demonstração `UTFPRCity`.
- `backend/app/routers/topsis.py` — `UTFPRCity` permanece como cidade de demo.
- `frontend/src/pages/CityIndicatorsHistoryPage.jsx`
- `frontend/src/pages/HistoricalSeriesPage.jsx`
- `frontend/src/components/ManualDataForm.jsx`
- `frontend/src/components/HistoricoIndicadores.jsx`
- `frontend/src/components/CityInputForm.jsx`

### Testes e scripts de debug

Os testes e scripts de validação ainda usam códigos IBGE fixos por design para manter cenários reprodutíveis:

- `backend/tests/**`
- `frontend/src/components/SmartCityDashboard.examples.jsx`
- `backend/api_inspector_simple.py`
- `backend/inspect_bank.py`

## Observação

Depois da limpeza, não há mais hardcode relevante na lógica de seleção das cidades da aplicação. O que sobra é, em geral:
- fallback de dados,
- exemplos/documentação,
- testes,
- cidade demo.
