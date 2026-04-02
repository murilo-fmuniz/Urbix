# 🔧 FIX: Integração Frontend-Backend TOPSIS

## ✅ Problema Resolvido

O frontend estava enviando indicadores no formato **simples/plano**, mas o backend esperava uma **estrutura ISO hierárquica completa** com 47 campos organizados em 3 normas ISO.

### Antes ❌
```json
{
  "pontos_iluminacao_telegestao": 60,
  "medidores_inteligentes_energia": 50,
  "bombeiros_por_100k": 40,
  "area_verde_mapeada": 35
}
```

### Depois ✅
Backend agora aceita **ambos os formatos** com conversão automática!

---

## 🛠️ Solução Implementada

### 1. **Função de Conversão** (backend/app/routers/topsis.py)

Adicionada função `converter_indicadores_frontend()` que mapeia campos simples para estrutura ISO:

```python
def converter_indicadores_frontend(indicadores_simples: Dict[str, Any]) -> ManualCityIndicators:
    """Converte formato simples → ISO hierárquico"""
    
    # ISO 37120 (Sustentabilidade)
    bombeiros_100k = indicadores_simples.get("bombeiros_por_100k")
    
    # ISO 37122 (Smart Cities)
    iluminacao_telegestao_pct = indicadores_simples.get("pontos_iluminacao_telegestao")
    medidores_energia_pct = indicadores_simples.get("medidores_inteligentes_energia")
    
    # ISO 37123 (Resiliência) - area_verde_mapeada não mapeia (campo adicional)
```

**Mapeamento de Campos:**

| Campo Frontend | ISO Destino | Campo ISO |
|---|---|---|
| `pontos_iluminacao_telegestao` | 37122 | `iluminacao_telegestao_pct` |
| `medidores_inteligentes_energia` | 37122 | `medidores_inteligentes_energia_pct` |
| `bombeiros_por_100k` | 37120 | `bombeiros_100k` |
| `area_verde_mapeada` | ❌ Sem mapa | (ignorado com warning) |

### 2. **Schema Atualizado** (backend/app/schemas.py)

```python
from typing import Union  # ✅ Adicionado

class CityHybridInput(BaseModel):
    codigo_ibge: str
    nome_cidade: str
    manual_indicators: Optional[Union[ManualCityIndicators, Dict[str, Any]]] = None
    # ↑ Aceita AMBOS: estrutura ISO ou Dict simples
```

### 3. **Integração no Endpoint** (backend/app/routers/topsis.py)

```python
# Processa todas as cidades em paralelo
resultados_cidades = await asyncio.gather(
    *[
        processar_cidade_real(
            city.codigo_ibge,
            city.nome_cidade,
            # ✅ Conversão automática se for Dict
            converter_indicadores_frontend(city.manual_indicators) 
            if isinstance(city.manual_indicators, dict) 
            else city.manual_indicators
        ) for city in payload
    ],
    return_exceptions=False
)
```

### 4. **Frontend Corrigido** (frontend/src/components/SmartCityDashboard.jsx)

Removida multiplicação desnecessária por 100:

```javascript
// ❌ Antes (errado)
pontos_iluminacao_telegestao: (value || 0) * 100  // 60 * 100 = 6000 ❌

// ✅ Depois (correto)
pontos_iluminacao_telegestao: parseFloat(value || 0)  // 60 ✅
```

---

## 📊 Teste de Validação

### Comando
```bash
python backend/test_api_local.py
```

### Resultado
```
📥 Status: 200
✅ SUCESSO!

📊 Ranking (2 cidades):
   1. Apucarana: 100.00%
   2. Londrina: 0.00%

✅ Teste PASSOU! Backend aceita corretamente o formato do frontend.
```

---

## 📋 Arquivos Modificados

1. ✅ `backend/app/routers/topsis.py`
   - Adicionada função `converter_indicadores_frontend()`
   - Integrada chamada no endpoint `/ranking-hibrido`

2. ✅ `backend/app/schemas.py`
   - Atualizado import: `Union` adicionado
   - `CityHybridInput.manual_indicators` aceita `Union[ManualCityIndicators, Dict[str, Any]]`

3. ✅ `frontend/src/components/SmartCityDashboard.jsx`
   - Removida multiplicação por 100 dos indicadores

---

## 🔍 Detalhes Técnicos

### Fluxo de Dados

```
Frontend UI (CityInputForm)
    ↓
Inputs 0-100% (pontos_iluminacao_telegestao: 60)
    ↓
SmartCityDashboard.jsx (sem multiplicação)
    ↓
Payload JSON enviado ao backend
    ↓
POST /api/v1/topsis/ranking-hibrido
    ↓
CityHybridInput schema valida
    ↓
converter_indicadores_frontend() mapeia campos
    ↓
ManualCityIndicators estrutura ISO completa
    ↓
processar_cidade_real() calcula TOPSIS c/ 47 indicadores
    ↓
TOPSISResult ranking retornado
    ↓
Frontend exibe resultado
```

### Tratamento de Erros

- ✅ `area_verde_mapeada` é aceito (log warning) mas não mapeado
- ✅ Campos faltantes usar defaults ISO
- ✅ None/empty dict → criado com ManualCityIndicators()

---

## 🚀 Próximos Passos

1. Iniciar servidor backend: `python backend/main.py`
2. Iniciar frontend: `npm run dev` (em `frontend/`)
3. Testar fluxo completo:
   - Inserir cidades no formulário
   - Preencher indicadores manuais
   - Clicar "Gerar Ranking"
   - Verificar resultado

---

## ✨ Beneficios

- ✅ Frontend pode enviar dados simples
- ✅ Backend faz conversão automática
- ✅ 47 indicadores ISO calculados corretamente
- ✅ TOPSIS ranking funciona com dados manuais
- ✅ APIs externas podem estar offline - sistema funciona com dados manuais

---

**Status**: ✅ **PRONTO PARA INTEGRAÇÃO**

Data: 2025
Versão: 1.0
