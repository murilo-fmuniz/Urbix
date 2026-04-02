# 🧪 Teste de Integração: DadosColeta → TOPSIS

## ✅ Objetivos

Validar que o TOPSIS agora consulta o banco de dados (DadosColeta) antes de usar APIs.

---

## 📋 Pré-requisitos

1. Backend rodando: `uvicorn main:app --reload`
2. Se possível, AdminPage com dados salvos, ou use curl para inserir manualmente
3. Frontend rodando (para testes de UI)

---

## 🧫 Passo 1: Inserir Dados via AdminPage

### Opção A: Via Frontend (AdminPage)

1. Acesse: http://localhost:5173/admin
2. Preencha formulário com dados para **Apucarana**
3. Clique em submeter
4. Verifique sucesso ✅

### Opção B: Via cURL (Inserir coleta manualmente)

```bash
# Inserir coleta para Apucarana (ECO.1 - Taxa de desemprego)
curl -X POST http://localhost:8000/api/v1/indicadores/ECO.1/coletas \
  -H "Content-Type: application/json" \
  -d '{
    "cidade": "Apucarana",
    "estado": "PR",
    "ano_referencia": 2025,
    "valor_numerador": 1250,
    "valor_denominador": 25000,
    "valor_final": 5.0,
    "dado_disponivel": true
  }'
```

**Esperado:** HTTP 201 com dados criados

---

## 🧪 Passo 2: Verificar Dados no Banco

```bash
# Listar coletas de Apucarana
curl -X GET "http://localhost:8000/api/v1/indicadores?cidade=Apucarana" \
  -H "Content-Type: application/json"
```

**Esperado:** JSON retornando `DadosColeta` com dados de Apucarana

---

## 🎯 Passo 3: Teste TOPSIS com 2 Cidades

### Via Frontend (RankingPage/SmartCityDashboard)

1. Acesse: http://localhost:5173/ranking ou /dashboard
2. Selecione 2 cidades (ex: Apucarana, Londrina)
3. Clique "Calcular Ranking"
4. **VERIFICAR LOGS** (próximo passo)

### Via cURL

```bash
curl -X POST http://localhost:8000/api/v1/topsis/ranking-hibrido \
  -H "Content-Type: application/json" \
  -d '[
    {
      "codigo_ibge": "4101408",
      "nome_cidade": "Apucarana",
      "manual_indicators": null
    },
    {
      "codigo_ibge": "4113700",
      "nome_cidade": "Londrina",
      "manual_indicators": null
    }
  ]'
```

---

## 📊 Passo 4: Validar no Console / Logs

Abra o terminal onde rodou `uvicorn` e procure por:

### ✅ Se dados estão no BANCO:

```
========== PROCESSANDO CIDADE: Apucarana (IBGE: 4101408) ==========
✅ Dados encontrados no BANCO para Apucarana (Ano: 2025)
   Ano de Referência: 2025
   Data da Coleta: 2026-03-28T...
   Valor Final: 5.0
🏛️ Usando dados do BANCO DE DADOS para Apucarana
✅ Apucarana processada com sucesso (Fonte: BANCO)
```

### ❌ Se dados NÃO estão no banco (usa API):

```
========== PROCESSANDO CIDADE: Londrina (IBGE: 4113700) ==========
⚠️ Dados não encontrados no banco para Londrina, usando APIs
🌐 Consultando APIs EXTERNAS para Londrina
[DEBUG] Londrina - População IBGE: 575096
[DEBUG] Londrina - Dados SICONFI: {...}
[DEBUG] Londrina - Hospitais DataSUS: 12
✅ Londrina processada com sucesso (Fonte: API)
```

---

## ✨ Passo 5: Validação Completa

### Cenário 1: Apenas Banco ✅
- Inserir dados para Apucarana no banco
- TOPSIS usa dados do banco
- ✅ Logs mostram: **(Fonte: BANCO)**

### Cenário 2: Apenas APIs ✅
- NÃO inserir dados no banco
- TOPSIS usa APIs
- ✅ Logs mostram: **(Fonte: API)**

### Cenário 3: Uma Cidade com Banco, Outra com API ✅
- Inserir dados só de Apucarana
- TOPSIS calcula ranking com:
  - Apucarana: Dados do BANCO
  - Londrina: Dados da API
- ✅ Logs mostram ambas fontes

### Cenário 4: Fallback (Banco + API falha) ✅
- Inserir dados tópicos no banco (faltam alguns)
- APIs externas falham
- ✅ TOPSIS ainda calcula (usa valores padrão + banco)

---

## 🔑 Verificação de Sucesso

A integração funciona se:

- [ ] Logs mostram "✅ Dados encontrados no BANCO" quando dados estão lá
- [ ] Logs mostram "⚠️ Dados não encontrados no banco" quando banco vazio
- [ ] TOPSIS calcula normalmente em ambos casos
- [ ] Retorna ranking JSON válido (HTTP 200)
- [ ] Indicadores fazem sentido (valores não absurdos)

---

## 🐛 Debug / Troubleshooting

### Logs não mostram BANCO?

1. Verificar se dados foram realmente inseridos:
   ```bash
   curl http://localhost:8000/api/v1/indicadores?cidade=Apucarana
   ```

2. Verificar se nome_cidade do JSON é exatamente igual ao nome no banco:
   ```python
   # Não importa maiúsc/minúsc (usa ilike), mas:
   # "Apucarana" ✅
   # "apucarana" ✅
   # "APUCARANA" ✅
   # "Apucirana" ❌ (typo)
   ```

3. Verificar ano_referencia:
   ```python
   # Busca qualquer ano encontrado, mas loga:
   # "Ano de Referência: 2025" ✅
   ```

### Erro de conexão com banco?

```
Erro ao buscar dados do banco para Apucarana: ...
```

1. Verificar se `SessionLocal()` está funcionando
2. Verificar permissões do arquivo `urbix.db`
3. Verificar se tabela `dados_coleta` existe

---

## 📈 Esperado vs. Atual

| O Quê | Antes | Depois |
|-------|-------|--------|
| TOPSIS consulta banco? | ❌ Nunca | ✅ Primeiro |
| TOPSIS usa APIs | ✅ Sempre | ✅ Se banco empty |
| AdminPage útil? | ❌ Não | ✅ Sim! |
| Rastreabilidade | ❌ Não | ✅ Sim (logs) |
| Dados offline | ❌ Não | ✅ Sim |

---

## 🎯 Conclusão

Se todos os testes passarem:
- ✅ AdminPage agora alimenta TOPSIS
- ✅ TOPSIS usa dados curados manualmente
- ✅ Fallback automático para APIs
- ✅ Sistema é mais robusto e flexível

