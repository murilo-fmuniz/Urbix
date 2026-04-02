# Mapa Visual da Estrutura do Projeto Urbix

```
Urbix Project (Padrão Produção v1.0)
========================================================================================

D:\Docs\Faculdade\IC\Urbix\
│
├─ 📄 README.md                              ← ENTRADA PRINCIPAL (mantido na raiz)
│
├─ 📁 docs/                                  ← DOCUMENTAÇÃO CENTRALIZADA
│  ├─ .gitkeep
│  ├─ DOCUMENTATION_INDEX.md                 ← Índice de documentação
│  ├─ PROJECT_STATUS.md                      ← Status atual do projeto
│  ├─ TECHNICAL_SUMMARY.md                   ← Resumo técnico
│  ├─ IMPLEMENTATION_SUMMARY.md              ← Resumo de implementação
│  ├─ SETUP_CHECKLIST.md                     ← Checklist de setup
│  ├─ INTEGRATION_CHECKLIST.md               ← Checklist de integração
│  ├─ SESSION_COMPLETION.md                  ← Conclusões de sessão
│  ├─ RESUMO_EXECUTIVO.md                    ← Resumo executivo
│  ├─ PHASE4_ROADMAP.md                      ← Roadmap fase 4
│  ├─ ENTREGA_REFATORACAO_FRONTEND.md        ← Entrega refatoração frontend
│  ├─ FIX_FRONTEND_BACKEND_INTEGRATION.md    ← Fixes de integração
│  ├─ FIX_TOPSIS_FRONTEND.md                 ← Fixes TOPSIS frontend
│  ├─ roadmap_coleta.md                      ← Roadmap coleta dados
│  ├─ REORGANIZACAO_ESTRUTURA.md             ← Este documento (novo)
│  │
│  └─ 📁 examples/                           ← EXEMPLOS E PAYLOADS
│     ├─ .gitkeep
│     ├─ payload_teste_ranking_hibrido.json  ← Payload exemplo TOPSIS
│     └─ PAYLOAD_EXAMPLES.md                 ← Exemplos de eventos
│
├─ 📁 backend/                               ← BACKEND (API FastAPI)
│  ├─ 📁 app/                                ← Código-fonte da aplicação
│  │  ├─ __init__.py
│  │  ├─ main.py                             ← Entry point da API
│  │  ├─ database.py                         ← Configuração SQLAlchemy
│  │  ├─ models.py                           ← Modelos SQLAlchemy
│  │  ├─ schemas.py                          ← Schemas Pydantic
│  │  ├─ utils.py                            ← Utilitários gerais
│  │  │
│  │  ├─ 📁 routers/                         ← Service layers (endpoints)
│  │  │  ├─ indicadores.py                   ← Endpoints de indicadores
│  │  │  ├─ topsis.py                        ← Endpoints TOPSIS (47 indicadores)
│  │  │  ├─ manual_data.py                   ← Gerenciamento de dados manuais
│  │  │  └─ ...
│  │  │
│  │  └─ 📁 services/                        ← Business logic
│  │     ├─ indicators.py                    ← Cálculo de indicadores
│  │     ├─ topsis.py                        ← Algoritmo TOPSIS
│  │     ├─ external_apis.py                 ← Integrações com APIs externas
│  │     └─ ...
│  │
│  ├─ 📁 alembic/                            ← Migrações de banco de dados
│  │  ├─ env.py
│  │  ├─ README
│  │  ├─ script.py.mako
│  │  │
│  │  └─ 📁 versions/                        ← Histórico de migrações
│  │     ├─ a62ea43bc525_...py
│  │     └─ ...
│  │
│  ├─ 📁 data/                               ← Dados de seed/exemplo
│  │  ├─ seed_apucarana.json
│  │  └─ seed_indicadores_iso37122.json
│  │
│  ├─ 📁 tests/                              ← ⭐ TESTES REORGANIZADOS
│  │  ├─ .gitkeep
│  │  ├─ __init__.py                         ← Pytest package marker
│  │  ├─ __pycache__/
│  │  │
│  │  ├─ 📋 TESTES UNITÁRIOS (15 arquivos)
│  │  ├─ test_api_local.py                   ← Testes da API local
│  │  ├─ test_converter_indicadores.py       ← Conversor de indicadores
│  │  ├─ test_endpoint_hibrido.py            ← Endpoint TOPSIS híbrido
│  │  ├─ test_integration_frontend.py        ← Integração com frontend
│  │  ├─ test_londrina.py                    ← Testes específicos Londrina
│  │  ├─ test_manual_data_workflow.py        ← Workflow dados manuais
│  │  ├─ test_pipeline_hibrido.py            ← Pipeline híbrido TOPSIS
│  │  ├─ test_ranking_hibrido.py             ← Ranking híbrido
│  │  ├─ test_siconfi_analise.py             ← Análise SICONFI
│  │  ├─ test_siconfi_api.py                 ← API SICONFI
│  │  ├─ test_siconfi_completo.py            ← SICONFI completo
│  │  ├─ test_siconfi_debug.py               ← Debug SICONFI
│  │  ├─ test_startup.py                     ← Startup da aplicação
│  │  ├─ test_indicadores.py                 ← Cálculo indicadores
│  │  └─ test_normalizacao.py                ← Normalização dados
│  │
│  │  ├─ 📋 UTILITÁRIOS/DIAGNÓSTICO (4 arquivos)
│  │  ├─ diagnostico_siconfi.py              ← Diagnóstico API SICONFI
│  │  ├─ find_londrina.py                    ← Buscar dados Londrina
│  │  ├─ limpar_dados_fake.py                ← Limpar dados de teste
│  │  └─ quick_test_ssl.py                   ← Teste rápido SSL
│  │
│  ├─ main.py                                ← Entry point backend (fora de app/)
│  ├─ requirements.txt                       ← Dependências Python
│  ├─ alembic.ini                            ← Configuração Alembic
│  ├─ run_server.bat                         ← Script para rodar servidor
│  │
│  ├─ 📋 ARQUIVOS HISTÓRICOS (não reorganizados)
│  ├─ ARQUITETURA_TECNICA.md
│  ├─ CACHE_OPTIMIZATION_SUMMARY.md
│  ├─ CHECKLIST_IMPLEMENTACAO.md
│  ├─ DADOS_MANUAIS_HISTORICOS.md
│  ├─ dicionario_indicadores.md
│  ├─ INTEGRACAO_CONCLUIDA.md
│  ├─ OPTIMIZATION_CACHE_FAILFAST.md
│  ├─ RELATORIO_TESTES_ARQUITETURA_HIBRIDA.md
│  ├─ RESUMO_IMPLEMENTACAO.md
│  ├─ REVISAO_INDICADORES_TOPSIS.md
│  ├─ TEST_INTEGRACAO_BANCO_TOPSIS.md
│  ├─ TOPSIS_HIBRIDO_REFATORADO.md
│  └─ VISUALIZACAO_FLUXO_REFATORADO.md
│
├─ 📁 frontend/                              ← FRONTEND (React + Vite)
│  ├─ index.html                             ← HTML entry point
│  ├─ package.json                           ← Dependências NPM
│  ├─ postcss.config.js                      ← Configuração PostCSS
│  ├─ tailwind.config.js                     ← Configuração Tailwind CSS
│  │
│  ├─ 📁 src/                                ← Código-fonte React
│  │  ├─ App.jsx                             ← Componente raiz
│  │  ├─ main.jsx                            ← Entry point Vite
│  │  │
│  │  ├─ 📁 components/                      ← Componentes React
│  │  │  ├─ SmartCityDashboard.jsx           ← Dashboard principal (refatorado)
│  │  │  ├─ ManualDataForm.jsx               ← Formulário dados manuais
│  │  │  ├─ Navbar.jsx
│  │  │  ├─ Sidebar.jsx
│  │  │  └─ ...
│  │  │
│  │  ├─ 📁 constants/                       ← Constantes e configurações
│  │  │  └─ INDICADORES_CONFIG.js            ← Config 47 indicadores ISO
│  │  │
│  │  ├─ 📁 pages/                           ← Páginas React
│  │  │  ├─ Home.jsx
│  │  │  ├─ Dashboard.jsx
│  │  │  └─ ...
│  │  │
│  │  ├─ 📁 services/                        ← API clients
│  │  │  └─ api.js                           ← Cliente Axios
│  │  │
│  │  └─ 📁 styles/                          ← Estilos CSS
│  │     └─ ...
│  │
│  └─ 📋 DOCUMENTAÇÃO FRONTEND
│     ├─ ADMIN_PANEL_GUIDE.md
│     ├─ REFACTOR_MANUAL_DATA_FORM.md
│     ├─ REFACTOR_NAVBAR_LAYOUT.md
│     ├─ SIDEBAR_GUIDE.md
│     ├─ SIDEBAR_QUICKSTART.md
│     ├─ SIDEBAR_VISUAL_GUIDE.md
│     └─ SMARTCITY_QUICKSTART.md
│
└─ 📁 etc/                                   ← Miscellâneos (se houver)

========================================================================================

RESUMO RÁPIDO
═════════════════════════════════════════════════════════════════════════════════════

✅ RAIZ LIMPA
   - Apenas README.md e diretórios principais

✅ DOCUMENTAÇÃO CENTRALIZADA (docs/)
   - 13 arquivos .md de documentação
   - 2 payloads de exemplo em docs/examples/

✅ TESTES ORGANIZADOS (backend/tests/)
   - 13 arquivos de testes unitários
   - 4 utilitários de diagnóstico
   - Total: 21 arquivos

✅ CÓDIGO ESTRUTURADO
   - app/ contém código-fonte
   - routers/ para endpoints
   - services/ para business logic
   - models/, schemas/ para dados

========================================================================================

ESTATÍSTICAS
═════════════════════════════════════════════════════════════════════════════════════

Total de Pastas: 10 principais
├─ 1 raiz (.)
├─ 1 docs/
├─ 1 docs/examples/
├─ 1 backend/
├─ 1 backend/app/
├─ 1 backend/alembic/
├─ 1 backend/data/
├─ 1 backend/tests/        ⭐ NOVA
├─ 1 frontend/
└─ 1 etc/

Total de Arquivos Reorganizados: 32
├─ 13 documentos movidos para docs/
├─ 2 exemplos movidos para docs/examples/
├─ 13 testes movidos para backend/tests/
├─ 4 utilitários movidos para backend/tests/

Status: ✅ PADRÃO DE PRODUÇÃO IMPLEMENTADO

========================================================================================
```

## Estrutura de Testes Detalhada

```
backend/tests/
├── __init__.py                    ← Package marker
├── .gitkeep
│
├── test_api_local.py              ← Testes da API em localhost
├── test_converter_indicadores.py  ← Conversão entre formatos
├── test_endpoint_hibrido.py       ← Validação endpoint TOPSIS
├── test_integration_frontend.py   ← Integração frontend→backend
├── test_londrina.py               ← Testes específicos Londrina
├── test_manual_data_workflow.py   ← Workflow dados manuais
├── test_pipeline_hibrido.py       ← Pipeline TOPSIS completo
├── test_ranking_hibrido.py        ← Ranking híbrido
├── test_siconfi_analise.py        ← Análise dados SICONFI
├── test_siconfi_api.py            ← API SICONFI
├── test_siconfi_completo.py       ← Test SICONFI end-to-end
├── test_siconfi_debug.py          ← Debug/diagnóstico
├── test_startup.py                ← Inicialização app
├── test_indicadores.py            ← Cálculo indicadores
├── test_normalizacao.py           ← Normalização dados
│
├── diagnostico_siconfi.py         ← Diagnóstico SICONFI
├── find_londrina.py               ← Buscar Londrina
├── limpar_dados_fake.py           ← Cleanup dados
├── quick_test_ssl.py              ← Test SSL
│
└── __pycache__/                   ← Cache Python

```

## Comandos Úteis Pós-Reorganização

```bash
# Executar todos os testes
cd backend
pytest tests/ -v

# Executar testes com cobertura
pytest tests/ --cov=app --cov-report=html

# Executar testes específicos
pytest tests/test_api_local.py -v
pytest tests/test_ranking_hibrido.py::test_nome_funcao

# Executar com logging
pytest tests/ -v -s --log-cli-level=INFO

# Gerar relatório JUnit (para CI/CD)
pytest tests/ --junit-xml=report.xml

# Executar apenas testes rápidos (marker)
pytest tests/ -m "not slow"
```

---

**Versão**: 1.0  
**Data**: 30/03/2026  
**Status**: ✅ Completo
