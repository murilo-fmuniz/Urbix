# 🏙️ Urbix: Plataforma Híbrida de Monitoramento de Smart Cities

**Urbix** é um sistema avançado desenvolvido no âmbito de Iniciação Científica (Engenharia de Computação - UTFPR), desenhado para avaliar, monitorar e ranquear o nível de maturidade de Cidades Inteligentes (*Smart Cities*) utilizando o método multicritério **TOPSIS**.

A plataforma integra dados governamentais em tempo real com coletas manuais, ancorando sua matriz de avaliação estritamente nas normas internacionais **ISO 37120**, **ISO 37122** e **ISO 37123 / Marco de Sendai**.

## ✨ Características Principais

* 🔄 **Ciclo de Persistência 4-Tier** — Dados de cidades já processadas permanecem em cache local para rápido acesso
* 🛡️ **Resiliência Automática** — Fallback automático quando APIs governamentais falham
* 📊 **47 Indicadores ISO** — Cobertura completa das normas internacionais de cidades inteligentes
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

**Benefício:** Uma vez que uma cidade é processada, seus dados reais ficam "eternizados" no banco local, garantindo que futuras falhas de API não resultem em perda de informação. O sistema recupera dados de origens mais confiáveis ANTES de recorrer a médias nacionais.

### 🧠 Rigor Metodológico (Motor TOPSIS)
O algoritmo de ranqueamento foi construído com rigor científico para lidar com dados do mundo real:
* **Mapeamento de Impacto:** O sistema compreende a polaridade de 47 indicadores distintos (ex: Receita Própria é um benefício [+1], Taxa de Desemprego é um custo [-1]).
* **Imputação pela Média (*Mean Imputation*):** Para evitar distorções no ranqueamento causadas por municípios com dados faltantes, a matriz de decisão aplica a média dos dados reais das demais cidades na composição do cenário ideal, mantendo a validade matemática da avaliação multicritério.
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

## 🚀 Como Executar o Projeto

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
uvicorn main:app --reload
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

## � Diagnóstico de Coleta de Dados (Debug Endpoint)

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

## �📂 Estrutura Principal do Repositório

* `/backend/routers/topsis.py`: Núcleo do motor matemático, agregação de dados e cálculo multicritério.
* `/backend/routers/manual_data.py`: Gerenciamento "flat" e veloz dos 47 indicadores ISO reportados pelas prefeituras.
* `/backend/app/services/external_apis.py`: Coleta assíncrona de dados (IBGE, SICONFI, DataSUS) com sistema de retry robusto (Tenacity) e 4-tier fallback.
* `/backend/app/models.py`: Modelos SQLAlchemy para persistência (CityManualData, RankingSnapshot, etc).
* `/frontend/src/components/ManualDataForm.jsx`: Interface dinâmica de mapeamento das normas ISO.
* `/frontend/src/components/SmartCityDashboard.jsx`: Painel de visualização e envio dos *payloads* híbridos.
* `/docs`: Documentação complementar, histórico de implementação e exemplos de integração.

---

## 🌐 Coleta de Dados Governamentais

O Urbix integra três fontes oficiais de dados governamentais brasileiros:

### IBGE SIDRA (População)
* **Endpoint:** https://sidra.ibge.gov.br/api/v1
* **Dados:** População municipal, densidade demográfica
* **Timeout:** 10s com retry automático (3 tentativas)

### SICONFI - Tesouro Nacional (Finanças Municipais)
* **Endpoint:** https://apidatalake.tesouro.gov.br/ords/siconfi
* **Dados:** 
  - RREO: Receita Própria, Receita Total, Despesas de Capital, Serviço da Dívida
  - RGF: Dívida Consolidada
* **Timeout:** 10s com retry automático (3 tentativas)
* **Frequência:** Dados anuais (exercício fiscal 2023)

### DataSUS CNES (Infraestrutura de Saúde)
* **Endpoint:** https://apidadosabertos.saude.gov.br/cnes
* **Dados:** Contagem de hospitais por município
* **Timeout:** 10s com retry automático (3 tentativas)

**Nota:** Se alguma API falhar, o sistema recorre automaticamente ao banco de dados local ou a fallbacks pré-configurados, garantindo disponibilidade 24/7.

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
* [Dicionário de Indicadores](docs/dicionario_indicadores.md) — Mapeamento de 47 indicadores ISO

---

## 🔗 Links Úteis

* **API Docs (Swagger):** http://localhost:8000/docs (após iniciar o backend)
* **Interface Web:** http://localhost:5173 (após iniciar o frontend)
* **IBGE SIDRA:** https://sidra.ibge.gov.br/api
* **SICONFI (Tesouro):** https://apidatalake.tesouro.gov.br
* **DataSUS:** https://apidadosabertos.saude.gov.br

---

*Desenvolvido por Murilo Fontana Muniz, via projeto de iniciação científica — Universidade Tecnológica Federal do Paraná (UTFPR).*