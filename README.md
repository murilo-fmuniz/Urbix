# 🏙️ Urbix: Plataforma Híbrida de Monitoramento de Smart Cities

**Urbix** é um sistema avançado desenvolvido no âmbito de Iniciação Científica (Engenharia de Computação - UTFPR), desenhado para avaliar, monitorar e ranquear o nível de maturidade de Cidades Inteligentes (*Smart Cities*) utilizando o método multicritério **TOPSIS**.

A plataforma integra dados governamentais em tempo real com coletas manuais, ancorando sua matriz de avaliação estritamente nas normas internacionais **ISO 37120**, **ISO 37122** e **ISO 37123 / Marco de Sendai**.

---

## 📊 Status atual do projeto

| Métrica | Resultado |
|---------|-----------|
| **Erro 502 Bad Gateway** | ✅ Corrigido |
| **APIs Operacionais** | ✅ 3 integradas (SICONFI, TSE, INEP) + fallbacks resilientes |
| **Indicadores disponíveis** | ✅ 50 no total (47 ISO + 3 educacionais/INEP) |
| **Admin page CRUD** | ✅ Criada e integrada ao banco |
| **Séries históricas** | ✅ Rankings e indicadores persistidos em snapshots |
| **Cidade de teste** | ✅ UTFPRCity (9999999) seedada para validação |
| **Testes** | ✅ Validação manual e build do frontend aprovados |

📖 **Documentação completa:** veja os relatórios em `docs/reports/`.

---

## ✨ Características Principais

* 🔄 **Ciclo de Persistência 4-Tier** — Dados de cidades já processadas permanecem em cache local para rápido acesso
* 🛡️ **Resiliência Automática** — Fallback automático quando APIs governamentais falham
* 📊 **50 Indicadores** — 47 indicadores ISO + 3 campos educacionais adicionais usados na consolidação atual
* 🚀 **Motor TOPSIS de Alta Performance** — Ranking multicritério baseado em rigor científico
* 🔍 **Debug em Tempo Real** — Endpoint `/debug-apis` para diagnosticar coleta de dados
* 📈 **Snapshots Históricos** — Persistência de rankings para análise temporal
* 🌍 **Cobertura Nacional** — Dados de 5.570 municípios brasileiros
* ⚡ **Operações Assíncronas** — Requisições paralelas para máxima eficiência

---

## 🎯 Arquitetura Híbrida e Resiliência com Ciclo de Persistência Fechado

O diferencial arquitetural do Urbix é a sua capacidade de ingestão de dados híbridos com tolerância a falhas (*Fail-Fast*) e um **4-tier fallback system** que garante disponibilidade até mesmo quando as APIs governamentais estão offline.

### 🔄 Ciclo de Persistência Fechado (Novo)

O sistema implementa uma arquitetura circular de persistência de dados:

```
Requisição de Ranking
        ↓
   [API Real] ← Tenacity retry + timeout 10s
        ↓ (se timeout/erro)
   [Banco Local] ← CityManualData (dados previamente sincronizados)
        ↓ (se não encontrado)
   [Fallback Específico] ← 3 cidades pré-configuradas
        ↓ (se não disponível)
   [Fallback Universal] ← Média nacional de 5.570 cidades
        ✅ GARANTIDO nunca retornar zero
```

**Benefício:** Uma vez que uma cidade é processada, seus dados reais ficam persistidos no banco local, garantindo que futuras falhas de API não resultem em perda de informação. O sistema recupera dados de origens mais confiáveis ANTES de recorrer a médias nacionais.

### 🧠 Rigor Metodológico (Motor TOPSIS)
O algoritmo de ranqueamento foi construído com rigor científico para lidar com dados do mundo real:
* **Mapeamento de Impacto:** O sistema compreende a polaridade de 50 indicadores distintos (ex: Receita Própria é um benefício [+1], Taxa de Desemprego é um custo [-1]).
* **Preservação da matriz original:** o TOPSIS trabalha com a matriz recebida, sem imputação pela média na comparação, evitando achatar diferenças entre cidades com muitos fallbacks.
* **Rastreamento de Fonte:** Cada dado retornado identifica sua origem (API, Banco, Fallback), permitindo auditoria completa da cadeia de dados.

---

## 🛠️ Stack Tecnológica

**Backend (API & Data Science)**
* **[FastAPI](https://fastapi.tiangolo.com/):** Roteamento assíncrono e documentação automática (Swagger).
* **[Pydantic](https://docs.pydantic.dev/):** Validação estrita de tipagem de dados das normas ISO.
* **[NumPy](https://numpy.org/):** Processamento vetorial de alta performance para a matriz de decisão TOPSIS.
* **[SQLAlchemy](https://www.sqlalchemy.org/):** ORM para persistência de *snapshots* históricos e auditoria.
* **[Tenacity](https://tenacity.readthedocs.io/):** Retry logic robusto para requisições às APIs governamentais.
* **[AsyncIO](https://docs.python.org/3/library/asyncio.html):** Execução paralela e não-bloqueante de chamadas de API.

**Dados Governamentais Integrados**
* **IBGE SIDRA:** População municipal (indicadores demográficos)
* **SICONFI (Tesouro Nacional):** Finanças municipais - RREO (Receita e Despesas) + RGF (Dívida Consolidada)
* **DataSUS CNES:** Infraestrutura de saúde (hospitais, unidades de saúde)

**Frontend (Interface & Data Viz)**
* **[React](https://reactjs.org/) + Vite:** Componentização dinâmica do painel de controle.
* **Tailwind CSS:** Estilização responsiva.
* **Axios:** Integração com a API RESTful.

---

## 🚀 Como executar o projeto

### 1. Iniciando o Backend
O backend requer Python 3.9+ e utiliza um ambiente virtual.

```bash
cd backend
python -m venv venv

# Ative o ambiente virtual
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor FastAPI
uvicorn app.main:app --reload
```
A documentação interativa da API estará disponível em: `http://localhost:8000/docs`

### 2. Iniciando o Frontend
Em um novo terminal, inicie a interface de usuário:

```bash
cd frontend
npm install
npm run dev
```
Acesse a aplicação em: `http://localhost:5173`

---

## 🔎 Endpoints úteis para demo e Postman

### Séries históricas e ranking

* `GET /api/v1/manual-data/rankings/historico?limit=24` — ranking TOPSIS histórico
* `GET /api/v1/manual-data/rankings/periodo/{periodo_referencia}` — ranking por período (`YYYY-MM`)
* `GET /api/v1/manual-data/{codigo_ibge}/indicadores/historico?limit=52` — histórico de indicadores por cidade
* `GET /api/v1/topsis/snapshots/{codigo_ibge}` — snapshots históricos do TOPSIS por cidade

### TOPSIS e diagnóstico

* `POST /api/v1/topsis/ranking-hibrido` — ranking híbrido com dados reais + manuais
* `GET /api/v1/topsis/cities` — lista de cidades disponíveis no ranking
* `GET /api/v1/topsis/indicators` — lista dos 50 indicadores utilizados
* `GET /api/v1/topsis/debug-apis/{codigo_ibge}` — diagnóstico das APIs externas por cidade

### CRUD de dados manuais

* `GET /api/v1/manual-data/{codigo_ibge}`
* `POST /api/v1/manual-data/{codigo_ibge}`
* `PATCH /api/v1/manual-data/{codigo_ibge}`
* `DELETE /api/v1/manual-data/{codigo_ibge}`
* `GET /api/v1/manual-data/{codigo_ibge}/history`

### Dados locais

* `GET /api/v1/municipio/{city_id}`
* `GET /api/v1/municipio/{city_id}/indicadores`
* `GET /api/v1/municipio/{city_id}/nome`
* `GET /api/v1/municipio/s`
* `GET /api/v1/municipio/cache/info`
* `GET /api/v1/municipio/health`

---

## 🔎 Diagnóstico de coleta de dados

Para debugar e monitorar em tempo real o status das APIs governamentais e o ciclo de persistência, utilize o endpoint de diagnóstico:

### Requisição
```bash
curl -X GET "http://localhost:8000/api/v1/topsis/debug-apis/4106902"
```

### Resposta Exemplo
```json
{
  "codigo_testado": "4106902",
  "timestamp": "2026-04-02T10:30:45",
  "ibge": {
    "dados": { "populacao": 1830795.0, "fonte": "ibge" },
    "status": "API_REAL",
    "fonte": "ibge"
  },
  "siconfi": {
    "dados": { "receita_total": 10200000000.0, ..., "fonte": "siconfi" },
    "status": "API_REAL",
    "fonte": "siconfi"
  },
  "datasus": {
    "dados": { "num_hospitais": 5, "fonte": "fallback universal" },
    "status": "FALLBACK_UNIVERSAL",
    "fonte": "fallback universal"
  },
  "resumo": {
    "total_apis_ok": 2,
    "total_fallbacks": 1,
    "consistencia": "PARCIAL_FALLBACK"
  }
}
```

### Status Possíveis
* `API_REAL` → Dados coletados diretamente da API governamental ✅
* `FALLBACK_BANCO` → Dados persistidos no banco de dados local (cache) ✅
* `FALLBACK_ESPECIFICO` → Dados de fallback para 3 cidades pré-configuradas ⚠️
* `FALLBACK_UNIVERSAL` → Média nacional de 5.570 cidades ⚠️
* `STATUS_DESCONHECIDO` → Falha ao identificar origem (investigar) ❌

**Documentação Completa:** Veja [docs/DEBUG_APIS_ENDPOINT.md](docs/DEBUG_APIS_ENDPOINT.md) para exemplos, troubleshooting e arquitetura detalhada.

---

## 📂 Estrutura Principal do Repositório

* `/backend/app/routers/topsis.py`: Núcleo do motor matemático, agregação de dados, ranking TOPSIS e snapshots históricos.
* `/backend/app/routers/manual_data.py`: CRUD dos dados manuais, histórico de alterações e séries históricas.
* `/backend/app/services/external_apis.py`: Coleta assíncrona de dados (IBGE, SICONFI, DataSUS) com sistema de retry robusto (Tenacity) e 4-tier fallback.
* `/backend/app/models.py`: Modelos SQLAlchemy para persistência (CityManualData, RankingSnapshot, etc).
* `/frontend/src/components/ManualDataForm.jsx`: Interface dinâmica para cadastro dos 47 campos ISO.
* `/frontend/src/pages/AdminCidadesPage.jsx`: Página administrativa com presets, CRUD e ajuda em modal.
* `/frontend/src/pages/RankingPage.jsx`: Envio dos *payloads* híbridos e exibição do ranking.
* `/docs`: Documentação complementar, histórico de implementação e exemplos de integração.

---

## 🌐 Coleta de dados governamentais

O Urbix integra múltiplas fontes oficiais com **resiliência automática**: quando uma API não disponibiliza dados, o sistema recorre a fallbacks estaduais/nacionais pré-calibrados e, quando necessário, ao banco local.

### ✅ SICONFI - Tesouro Nacional (Finanças Municipais)
* **Endpoint:** https://apidatalake.tesouro.gov.br/ords/siconfi
* **Dados Injetados:** [2,3,4] Despesas Capital %, Receita Própria %, Orçamento per Capita
* **Cobertura:** 31 municípios (100%)
* **Timeout:** 10s com retry automático (3 tentativas)
* **Frequência:** Dados anuais (exercício fiscal 2023)

### ✅ TSE - Tribunal Superior Eleitoral (Eleições)
* **Dados Injetados:** [5,7] Mulheres Eleitas %, Participação Eleitoral %
* **Cobertura:** Fallback estadual para todos os municípios
* **Cache:** 30 dias
* **Status:** Operacional com fallback automático

### ✅ INEP - Instituto Nacional de Educação (Educação)
* **Dados Injetados:** [15,16,33] Relação Estudante/Professor, IDEB Anos Iniciais, Escolas Conectadas %
* **Cobertura:** Fallback para 5 cidades (Apucarana, São Paulo, Londrina, Maringá, Curitiba)
* **Cache:** 7 dias
* **Status:** Operacional com fallback automático

### ⚠️ DataSUS CNES (Infraestrutura de Saúde)
* **Status:** Parcialmente integrado com fallbacks e expansão local
* **Target:** ampliar cobertura de imunização, hospitais e desfechos de saúde

### ⚠️ Portal da Transparência (Programas Sociais)
* **Status:** Parcialmente integrado com fallback e cache local
* **Target:** ampliar integração de programas sociais e cobertura municipal

**📊 Cobertura atual:** varia por município e disponibilidade de API/fallback | **Target:** aumentar cobertura com novas fontes e ETL local  
**🛡️ Garantia:** Se API falha, sistema retorna fallback automático. Zero dados perdidos.

---

## 📋 Requisitos do Sistema

### Backend
* Python 3.9+
* SQLite (ou PostgreSQL em produção)
* pip ou conda para gerenciamento de pacotes

### Frontend  
* Node.js 14+
* npm ou yarn

### Dependências Críticas
* FastAPI 0.104.1+
* SQLAlchemy 2.0.23+
* NumPy (processamento vetorial)
* Tenacity (retry logic)
* Pydantic (validação de dados)

---

## 📚 Documentação Complementar

* [DEBUG_APIS_ENDPOINT.md](docs/DEBUG_APIS_ENDPOINT.md) — Guia completo do endpoint de diagnóstico
* [ARCHITECTURE.md](docs/ARCHITECTURE.md) — Arquitetura detalhada do sistema
* [Dicionário de Indicadores](docs/dicionario_indicadores.md) — Mapeamento dos indicadores usados no projeto
* [docs/reports/](docs/reports/) — Relatórios finais, entregas e consolidação da implementação

---

## 🔗 Links Úteis

* **API Docs (Swagger):** http://localhost:8000/docs (após iniciar o backend)
* **Interface Web:** http://localhost:5173 (após iniciar o frontend)
* **Admin page:** `http://localhost:5173/admin` ou o caminho configurado no frontend
* **IBGE SIDRA:** https://sidra.ibge.gov.br/api
* **SICONFI (Tesouro):** https://apidatalake.tesouro.gov.br
* **DataSUS:** https://apidadosabertos.saude.gov.br

---

*Desenvolvido por Murilo Fontana Muniz, via projeto de iniciação científica — Universidade Tecnológica Federal do Paraná (UTFPR).*