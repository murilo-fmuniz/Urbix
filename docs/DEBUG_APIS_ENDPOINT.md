📋 DOCUMENTAÇÃO: ENDPOINT DE DIAGNÓSTICO
========================================

## Endpoint: GET /api/v1/topsis/debug-apis/{codigo_ibge}

### Propósito
Endpoint de diagnóstico para debugar a coleta de dados das APIs governamentais em tempo real,
identificando exatamente de onde cada dado está vindo (API real, banco de dados, fallback específico ou universal).

### URL
```
GET http://localhost:8000/api/v1/topsis/debug-apis/{codigo_ibge}
```

### Parâmetros
- **codigo_ibge** (string, required): Código IBGE do município (ex: 4106902 para Apucarana)

### Resposta (JSON)
```json
{
  "codigo_testado": "4106902",
  "timestamp": "2026-04-01T17:55:37.293308",
  
  "ibge": {
    "dados": { "populacao": 1830795.0, "fonte": "ibge" },
    "status": "API_REAL",
    "fonte": "ibge"
  },
  
  "siconfi": {
    "dados": {
      "receita_propria": 4366479000.0,
      "receita_total": 10200000000.0,
      "despesas_capital": 1153425000.0,
      "servico_divida": 0.0,
      "divida_consolidada": 0.0,
      "fonte": "siconfi"
    },
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
    "consistencia": "PARCIAL_FALLBACK",
    "explicacao": {
      "API_REAL": "Dado coletado diretamente da API governamental",
      "FALLBACK_BANCO": "Dado persistido no banco de dados (cache local)",
      "FALLBACK_ESPECIFICO": "Dado de fallback para 3 cidades pré-configuradas",
      "FALLBACK_UNIVERSAL": "Dado de média nacional para 5.570 cidades",
      "ERRO_COLETA": "Erro ao tentar coletar o dado"
    }
  }
}
```

### Status Possíveis

Cada API retorna um dos seguintes status:

| Status | Significado | Ação |
|--------|------------|------|
| `API_REAL` | Dado vem diretamente da API governamental (IBGE/SICONFI/DataSUS) | ✅ Excelente |
| `FALLBACK_BANCO` | Dado persistido no banco local (resultado de uma coleta anterior) | ✅ Bom |
| `FALLBACK_ESPECIFICO` | Fallback para 3 cidades pré-configuradas | ⚠️ Aceitável |
| `FALLBACK_UNIVERSAL` | Fallback com média nacional (5.570 cidades) | ⚠️ Aceitável |
| `STATUS_DESCONHECIDO` | Não conseguiu identificar a fonte (bug a investigar) | ❌ Investigar |
| `ERRO_COLETA` | Erro ao tentar coletar o dado | ❌ Investigar |

### Consistência Geral

```
DADOS_REAIS_COMPLETO   → 3/3 APIs retornaram dados reais (melhor caso)
PARCIAL_FALLBACK       → 1-2/3 APIs em fallback (esperado em horários de manutenção)
COMPLETO_FALLBACK      → 0/3 APIs reais (APIs governamentais offline)
```

---

## Exemplos de Uso

### 1️⃣ Testar Cidade com Dados Reais
```bash
curl -X GET "http://localhost:8000/api/v1/topsis/debug-apis/4106902"
```

**Resposta esperada:**
- IBGE: `API_REAL`
- SICONFI: `API_REAL` ou `FALLBACK_BANCO`
- DataSUS: `FALLBACK_UNIVERSAL` (API frequentemente offline)

---

### 2️⃣ Testar Cidade Fictícia
```bash
curl -X GET "http://localhost:8000/api/v1/topsis/debug-apis/9999999"
```

**Resposta esperada:**
- Todas as APIs: `FALLBACK_UNIVERSAL` (nunca visitada antes)
- Consistência: `COMPLETO_FALLBACK`

---

### 3️⃣ Via Postman
1. Nova requisição GET
2. URL: `http://localhost:8000/api/v1/topsis/debug-apis/4106902`
3. Clique em "Send"
4. Verifique os status de cada API na seção "resumo"

---

## 4-Tier Fallback Hierárquico

O endpoint visualiza o sistema de fallback em 4 tiers implementado:

```
Tier 1: API Real (com Tenacity retry + timeout 10s)
   ↓ if timeout/network error
Tier 2: Banco de Dados (CityManualData - cache persistente local)
   ↓ if not found
Tier 3: Fallback Específico (3 cidades pré-configuradas)
   ↓ if not available
Tier 4: Fallback Universal (média nacional de 5.570 cidades)
   ✅ GARANTIDO nunca retornar zero
```

---

## Fluxo de Persistência Visualizado

```
1. User -> frontend -> /ranking-hibrido
2. Backend chama external_apis.py
3. Tenta Tier 1 (API Real) ← external_apis.py
4. Se falha, chama _get_data_from_db() ← verifica Tier 2
5. Se banco tem, retorna (dados persistidos!)
6. Se não, retorna Tier 3 ou 4
7. TOPSIS processa e salva em CityManualData ← topsis.py
8. Próxima chamada para mesma cidade: vai logo pro Tier 2!
```

---

## Debugging Passo-a-Passo

### Problema: "Recebo FALLBACK_UNIVERSAL para uma cidade que deveria ter dados"

1. Verifique o status com `/debug-apis/{codigo_ibge}`
2. Se `FALLBACK_UNIVERSAL`: os dados nunca foram sincronizados antes
   - Solução: Chamar `/ranking-hibrido` uma vez para sincronizar
3. Se `FALLBACK_BANCO`: dados estão no banco (verifique se está correto)
4. Se `STATUS_DESCONHECIDO`: bug - verifique logs do backend

### Problema: "APIs estão sempre retornando FALLBACK"

1. Verificar se os servidores das APIs estão online:
   - IBGE SIDRA: https://sidra.ibge.gov.br
   - SICONFI: https://apidatalake.tesouro.gov.br
   - DataSUS: https://apidadosabertos.saude.gov.br
2. Verificar logs: `python sync_gov_apis.py --cron`
3. Se persistente, considerar manual update via `/admin/sync-apis`

### Problema: "Tenho dados em Banco mas não aparecem em ranking"

1. Verifique com `/debug-apis/{codigo_ibge}`
2. Se status = `FALLBACK_BANCO`: dados existem localmente
3. Problem: Pode ser que a cidade não foi incluída no request do ranking
4. Solução: Adicione a cidade manualmente ao request `/ranking-hibrido`

---

## Arquitetura da Solução

```python
# app/routers/topsis.py
@topsis_router.get("/debug-apis/{codigo_ibge}")
async def debug_apis(codigo_ibge: str):
    """
    Chama 3 APIs em paralelo com asyncio.gather:
    - get_ibge_population(codigo_ibge)
    - get_siconfi_finances(codigo_ibge)
    - get_datasus_health_infrastructure(codigo_ibge)
    
    Classifica status baseado na chave 'fonte' retornada.
    Retorna JSON estruturado com dados + status + resumo.
    """
    ibge, siconfi, datasus = await asyncio.gather(...)
    # Classifica status
    # Retorna resposta estruturada
```

---

## Integração com Ciclo de Persistência

Este endpoint é ferramenta de visibilidade para o **Ciclo de Persistência Fechado**:

### Antes (sem banco):
```
API fail → FALLBACK_UNIVERSAL sempre
Mesma cidade tomorrow → API fail again → FALLBACK_UNIVERSAL
```

### Depois (com banco):
```
API fail → FALLBACK_UNIVERSAL (salva no banco)
Mesma cidade tomorrow → Checa banco PRIMEIRO → usa dados salvos!
```

Este endpoint mostra exatamente onde cada dado está vindo, validando que o ciclo está funcionando.

---

## Performance

- **Tempo típico**: < 1s (3 APIs em paralelo com timeout 10s)
- **Timeout individual**: 10 segundos por API
- **Cache**: Respostas são cacheadas em memória por 1 hora
- **Banco**: Histórico persistido indefinidamente

---

## Limitações

- ⚠️ Este endpoint ainda tenta as 3 APIs sempre (não há disable total)
- ⚠️ O fallback é automático, não configurável por request
- ⚠️ Não há versionamento de dados (sempre pega a versão mais recente)

---

## Sugestões de Melhorias Futuras

1. Adicionar `?bypass_api=true` para forçar apenas banco
2. Adicionar `?include_history=true` para histórico temporal
3. Dashboard visual com status de todas as 5.570 cidades
4. Alertas quando APIs ficam offline por > 1 hora

---

Generated: 2026-04-01
Last Updated: Session completion
API Version: 2.0.0
