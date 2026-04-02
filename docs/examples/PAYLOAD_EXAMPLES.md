# 📋 Exemplos de Payload - Endpoint /ranking-hibrido

## ✅ Payload Válido (HTTP 200)

Quando **ambas as cidades** têm `codigo_ibge` e `nome_cidade` preenchidos:

```json
[
  {
    "codigo_ibge": "4101408",
    "nome_cidade": "Apucarana",
    "manual_indicators": {
      "pontos_iluminacao_telegestao": 38.5,
      "medidores_inteligentes_energia": 45.0,
      "bombeiros_por_100k": 12.5,
      "area_verde_mapeada": 55.5
    }
  },
  {
    "codigo_ibge": "4113700",
    "nome_cidade": "Londrina",
    "manual_indicators": {
      "pontos_iluminacao_telegestao": 50.0,
      "medidores_inteligentes_energia": 60.0,
      "bombeiros_por_100k": 10.0,
      "area_verde_mapeada": 65.0
    }
  }
]
```

**Resposta:**
```json
{
  "ranking": [
    {
      "nome_cidade": "Londrina",
      "indice_smart": 0.8235
    },
    {
      "nome_cidade": "Apucarana",
      "indice_smart": 0.6843
    }
  ],
  "detalhes_calculo": { /* ... */ }
}
```

---

## ❌ Payload Inválido - Campos Vazios (HTTP 422)

Se `nome_cidade` está vazio:

```json
[
  {
    "codigo_ibge": "4101408",
    "nome_cidade": "",  // ❌ ERRO: Campo vazio
    "manual_indicators": null
  },
  {
    "codigo_ibge": "4113700",
    "nome_cidade": "Londrina",
    "manual_indicators": null
  }
]
```

**Erro Retornado:**
```
❌ Cidade 1: Nome da cidade é obrigatório
HTTP 422 Unprocessable Content
```

---

## ❌ Payload Inválido - Código IBGE Vazio (HTTP 422)

Se `codigo_ibge` está vazio:

```json
[
  {
    "codigo_ibge": "",  // ❌ ERRO: Campo vazio
    "nome_cidade": "Apucarana",
    "manual_indicators": null
  },
  {
    "codigo_ibge": "4113700",
    "nome_cidade": "Londrina",
    "manual_indicators": null
  }
]
```

**Erro Retornado:**
```
❌ Cidade 1: Código IBGE é obrigatório
HTTP 422 Unprocessable Content
```

---

## ❌ Payload Inválido - Apenas 1 Cidade (HTTP 400)

TOPSIS **requer mínimo 2 cidades** para comparação matemática:

```json
[
  {
    "codigo_ibge": "4101408",
    "nome_cidade": "Apucarana",
    "manual_indicators": null
  }
]
```

**Erro Retornado:**
```
❌ TOPSIS requer mínimo 2 cidades... Recebido: 1
HTTP 400 Bad Request
```

---

## 🧪 Teste com cURL

### ✅ Teste Válido (2 cidades)
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

### ❌ Teste Inválido (campo vazio)
```bash
curl -X POST http://localhost:8000/api/v1/topsis/ranking-hibrido \
  -H "Content-Type: application/json" \
  -d '[
    {
      "codigo_ibge": "",
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

### ❌ Teste Inválido (1 cidade)
```bash
curl -X POST http://localhost:8000/api/v1/topsis/ranking-hibrido \
  -H "Content-Type: application/json" \
  -d '[
    {
      "codigo_ibge": "4101408",
      "nome_cidade": "Apucarana",
      "manual_indicators": null
    }
  ]'
```

---

## 🔧 Schema Esperado (Pydantic)

### CityHybridInput
```python
class CityHybridInput(BaseModel):
    codigo_ibge: str              # ✅ Obrigatório - não pode ser vazio
    nome_cidade: str              # ✅ Obrigatório - não pode ser vazio
    manual_indicators: Optional[ManualCityIndicators] = None
```

### ManualCityIndicators
```python
class ManualCityIndicators(BaseModel):
    pontos_iluminacao_telegestao: Optional[float] = 0.0
    medidores_inteligentes_energia: Optional[float] = 0.0
    bombeiros_por_100k: Optional[float] = 0.0
    area_verde_mapeada: Optional[float] = 0.0
```

---

## 📋 Checklist de Debug

Ao receber **HTTP 422**, verificar:

- [ ] Ambas as cidades têm `codigo_ibge` preenchido (não vazio)?
- [ ] Ambas as cidades têm `nome_cidade` preenchido (não vazio)?
- [ ] Está enviando um array com 2 ou mais cidades?
- [ ] Os tipos de dados estão corretos (strings para codigo_ibge/nome_cidade)?
- [ ] Console do navegador mostra o payload exato sendo enviado?

Se ainda receber 422, abrir dev tools (F12 → Network tab) e verificar:
1. **Response Preview** - Ver mensagem de erro exata
2. **Request Payload** - Confirmar que JSON está bem-formado
3. **Backend Logs** - Executar `uvicorn main:app --reload --log-level debug`

