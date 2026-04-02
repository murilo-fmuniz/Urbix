# 📊 Documentação - Sistema de Dados Manuais e Históricos

## 🎯 Overview

O novo sistema permite:
1. ✅ **Persistência de Dados Manuais** - Salvar dados que a prefeitura insere
2. ✅ **Auditoria Completa** - Histórico de todas alterações (quem, quando, por quê)
3. ✅ **Séries Históricas** - Rastrear evolução dos indicadores ao longo do tempo
4. ✅ **Histórico de Rankings** - Comparar rankings de diferentes períodos

---

## 📋 Endpoints Disponíveis

### 1️⃣ Gerenciar Dados Manuais

#### Criar ou Atualizar Dados Manuais
```http
POST /api/v1/manual-data/{codigo_ibge}
```

**Request Body:**
```json
{
  "codigo_ibge": "4101408",
  "nome_cidade": "Apucarana",
  "pontos_iluminacao_telegestao": 85.5,
  "medidores_inteligentes_energia": 60.0,
  "bombeiros_por_100k": 45.3,
  "area_verde_mapeada": 32.1,
  "usuario_atualizou": "joao@prefeitura.local",
  "motivo_atualizacao": "Atualização trimestral Q1 2025"
}
```

**Response:**
```json
{
  "id": 1,
  "codigo_ibge": "4101408",
  "nome_cidade": "Apucarana",
  "pontos_iluminacao_telegestao": 85.5,
  "medidores_inteligentes_energia": 60.0,
  "bombeiros_por_100k": 45.3,
  "area_verde_mapeada": 32.1,
  "fonte": "prefeitura",
  "usuario_atualizou": "joao@prefeitura.local",
  "data_criacao": "2025-03-28T10:30:00",
  "data_atualizacao": "2025-03-28T10:30:00"
}
```

**Status Codes:**
- `200` - OK (atualização bem-sucedida)
- `201` - Created (novo registro criado)
- `500` - Erro no servidor

---

#### Obter Dados Manuais Atuais
```http
GET /api/v1/manual-data/{codigo_ibge}
```

**Exemplo:**
```bash
curl -X GET "http://localhost:8000/api/v1/manual-data/4101408"
```

**Response:** (mesmo schema de criação)

---

#### Atualizar Parcialmente (PATCH)
```http
PATCH /api/v1/manual-data/{codigo_ibge}
```

**Request Body (apenas campos a atualizar):**
```json
{
  "pontos_iluminacao_telegestao": 90.0,
  "usuario_atualizou": "maria@prefeitura.local",
  "motivo_atualizacao": "Correção de dados Q1"
}
```

---

### 2️⃣ Histórico e Auditoria

#### Obter Histórico Completo de Alterações
```http
GET /api/v1/manual-data/{codigo_ibge}/history?limit=50
```

**Response:**
```json
[
  {
    "id": 5,
    "codigo_ibge": "4101408",
    "dados_antigos": {
      "pontos_iluminacao_telegestao": 85.5,
      "medidores_inteligentes_energia": 60.0,
      "bombeiros_por_100k": 45.3,
      "area_verde_mapeada": 32.1
    },
    "dados_novos": {
      "pontos_iluminacao_telegestao": 90.0,
      "medidores_inteligentes_energia": 60.0,
      "bombeiros_por_100k": 45.3,
      "area_verde_mapeada": 32.1
    },
    "alteracoes_resumo": "Iluminação Telegestão: 85.50 → 90.00",
    "usuario_atualizou": "maria@prefeitura.local",
    "motivo_atualizacao": "Correção de dados Q1",
    "data_alteracao": "2025-03-28T11:15:00"
  }
]
```

**Query Parameters:**
- `limit` - Número máximo de registros (padrão: 50, máximo: 500)

---

### 3️⃣ Série Histórica - Indicadores

#### Obter Histórico de Indicadores de uma Cidade
```http
GET /api/v1/manual-data/{codigo_ibge}/indicadores/historico?limit=52
```

**Response:**
```json
[
  {
    "id": 1,
    "codigo_ibge": "4101408",
    "taxa_endividamento": 15.5,
    "despesas_capital_percentual": 25.3,
    "mulheres_eleitas_percentual": 23.1,
    "hospitais_por_100mil": 3.8,
    "independencia_financeira": 42.1,
    "orcamento_per_capita": 1250.50,
    "pontos_iluminacao_telegestao": 85.5,
    "medidores_inteligentes_energia": 60.0,
    "bombeiros_por_100k": 45.3,
    "area_verde_mapeada": 32.1,
    "data_calculo": "2025-03-28T10:30:00",
    "fonte_dados": "hibrido",
    "periodo_referencia": "2025-03"
  }
]
```

**Query Parameters:**
- `limit` - Número máximo de snapshots (padrão: 52 = ~1 ano, máximo: 500)

**Casos de Uso:**
- Análise de tendências anuais
- Comparação de evolução entre cidades
- Relatórios de desempenho histórico

---

### 4️⃣ Série Histórica - Rankings

#### Obter Histórico de Rankings (últimos N períodos)
```http
GET /api/v1/manual-data/rankings/historico?limit=24
```

**Response:**
```json
[
  {
    "id": 3,
    "ranking_data": [
      {
        "nome_cidade": "Londrina",
        "indice_smart": 0.842,
        "posicao": 1
      },
      {
        "nome_cidade": "Apucarana",
        "indice_smart": 0.756,
        "posicao": 2
      }
    ],
    "data_calculo": "2025-03-28T10:40:00",
    "periodo_referencia": "2025-03",
    "quantidade_cidades": 2
  }
]
```

**Query Parameters:**
- `limit` - Número máximo de snapshots (padrão: 24 = ~2 anos, máximo: 500)

---

#### Obter Ranking de um Período Específico
```http
GET /api/v1/manual-data/rankings/periodo/{periodo_referencia}
```

**Exemplo:**
```bash
curl -X GET "http://localhost:8000/api/v1/manual-data/rankings/periodo/2025-03"
```

**Response:** (mesmo schema acima)

---

## 🔄 Fluxo Completo de Uso

### Cenário: Prefeitura Atualiza Dados Trimestralmente

```
1. PREFEITURA INSERE DADOS MANUAIS
   ↓
   POST /api/v1/manual-data/4101408
   
2. DADOS SÃO SALVOS NO DB
   ✓ Criado registro em city_manual_data
   ✓ Se for atualização, histórico criado em city_manual_data_history
   
3. FRONTEND GERA RANKING
   ↓
   POST /api/v1/topsis/ranking-hibrido
   {
     "codigo_ibge": "4101408"
   }
   
4. BACKEND CALCULA E SALVA
   ✓ Recupera dados manuais salvos
   ✓ Consulta APIs externas
   ✓ Calcula indicadores
   ✓ Executa TOPSIS
   ✓ Salva snapshots em:
     - indicator_snapshot
     - ranking_snapshot

5. ANÁLISE HISTÓRICA FICA DISPONÍVEL
   ↓
   GET /api/v1/manual-data/4101408/indicadores/historico
   GET /api/v1/manual-data/rankings/historico
   GET /api/v1/manual-data/4101408/history
```

---

## 📊 Tabelas Criadas

### city_manual_data
Armazena os indicadores manuais **mais recentes** de cada cidade.
- Índice: `codigo_ibge` (único)
- Timestamps: `data_criacao`, `data_atualizacao`

### city_manual_data_history
Registro de **todas as alterações** nos dados manuais (auditoria).
- Índice: `codigo_ibge`, `data_alteracao`
- Campos: `dados_antigos`, `dados_novos` (JSON)
- Rastreamento: `usuario_atualizou`, `motivo_atualizacao`

### indicator_snapshot
**Captura temporal** de indicadores calculados.
- Índice: `codigo_ibge`, `data_calculo`
- Agregação: `periodo_referencia` (ex: "2025-03")
- Permite: análise de séries temporais

### ranking_snapshot
**Captura temporal** de rankings TOPSIS.
- Índice: `data_calculo`, `periodo_referencia`
- Armazena: ranking_data (JSON), matriz_decisao, pesos, impactos
- Permite: comparação de rankings ao longo do tempo

---

## 🔍 Exemplos Práticos

### Exemplo 1: Rastrear Mudanças de Uma Cidade
```bash
# 1. Obter histórico completo
curl -X GET "http://localhost:8000/api/v1/manual-data/4101408/history?limit=100"

# Vê: quem fez mudança, quando, por quê, valores antigos/novos
```

### Exemplo 2: Análise de Evolução Anual
```bash
# 1. Obter últimos 52 snapshots (~1 ano)
curl -X GET "http://localhost:8000/api/v1/manual-data/4101408/indicadores/historico?limit=52"

# Frontend gera gráfico com evolução temporal dos indicadores
```

### Exemplo 3: Comparar Rankings de Diferentes Período
```bash
# 1. Obter ranking Jan 2025
curl -X GET "http://localhost:8000/api/v1/manual-data/rankings/periodo/2025-01"

# 2. Obter ranking Mar 2025
curl -X GET "http://localhost:8000/api/v1/manual-data/rankings/periodo/2025-03"

# Frontend compara posições: Cidade A era 1º, agora é 3º
```

---

## ⚠️ Pontos Importantes

1. **Deduplicação**: Snapshots salvos 1x por período (YYYY-MM) automaticamente
2. **Integridade**: Foreign key garante que snapshots refereciam dados válidos
3. **Performance**: Índices em `codigo_ibge`, `data_calculo`, `periodo_referencia`
4. **Auditoria**: Todas mudanças registradas com usuário e motivo
5. **Backups**: Histórico JSON permite recuperação de dados antigos

---

## 🚀 Próximas Implementações Sugeridas

1. **Gráficos Temporais** - Frontend: linha com evolução dos indicadores
2. **Comparação Trimestral** - Frontend: heatmap mostrando variações
3. **Alertas** - Backend: notificar quando município sai do ranking Top 5
4. **Exportação** - Frontend: CSV/PDF com histórico completo
5. **Previsões** - Backend: ML para prever tendências futuras

---

## 📖 Documentação Automática

A documentação interativa está disponível em:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Onde você pode testar todos os endpoints em tempo real! ✨
