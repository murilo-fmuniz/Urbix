# PARTE 3: Orquestração - Integrar 5 Novas APIs em Paralelo

## 📋 Localização

Procure por onde suas APIs são chamadas em paralelo. Deve estar em:
- **backend/app/routers/topsis.py** (função `processar_cidade_real`)
- **backend/app/main.py** (função que reúne dados de múltiplas APIs)

Procure pela linha com `asyncio.gather()` com as chamadas de:
```python
siconfi_data, ibge_data, datasus_data, inep_data, ...
```

---

## 🔄 Padrão Atual (Exemplo)

```python
# Chamadas ANTIGAS em paralelo
siconfi_data, ibge_data, datasus_data, inep_data, \
transparencia_data, datasus_expanded_data, portal_social_data = await asyncio.gather(
    get_siconfi_finances(codigo_ibge),
    get_ibge_population(codigo_ibge),
    get_datasus_health_infrastructure(codigo_ibge),
    get_inep_education(codigo_ibge),
    get_transparencia_social(codigo_ibge),
    get_datasus_expanded_wrapper(codigo_ibge),
    get_portal_transparencia_expanded_wrapper(codigo_ibge),
    return_exceptions=True
)
```

---

## ✅ Padrão NOVO (Com 5 Novas APIs)

**Substitua o `asyncio.gather()` acima por:**

```python
# Chamadas NOVAS em paralelo (com as 5 novas APIs)
siconfi_data, ibge_data, datasus_data, inep_data, \
transparencia_data, datasus_expanded_data, portal_social_data, \
aneel_data, ministerio_trabalho_data, antp_data, \
defesa_civil_data, cnj_data = await asyncio.gather(
    get_siconfi_finances(codigo_ibge),
    get_ibge_population(codigo_ibge),
    get_datasus_health_infrastructure(codigo_ibge),
    get_inep_education(codigo_ibge),
    get_transparencia_social(codigo_ibge),
    get_datasus_expanded_wrapper(codigo_ibge),
    get_portal_transparencia_expanded_wrapper(codigo_ibge),
    # 🎯 5 NOVAS APIs em paralelo:
    get_aneel_smart_metering(codigo_ibge),
    get_ministerio_trabalho_accidents(codigo_ibge, populacao),
    get_antp_zero_emission_fleet(codigo_ibge),
    get_defesa_civil_disasters(codigo_ibge, populacao),
    get_cnj_corruption_convictions(codigo_ibge, populacao),
    return_exceptions=True
)
```

---

## 🔍 Validação de Dados após `asyncio.gather()`

**Adicione após o `asyncio.gather()`:**

```python
# ✅ VALIDAR TIPO DE RESPOSTA (se houver exceção, retorna dict vazio)

# Dados ANT ELOs (novas)
if isinstance(aneel_data, Exception):
    logger.warning(f"⚠️  ANEEL falhou: {type(aneel_data).__name__}")
    aneel_data = {}

if isinstance(ministerio_trabalho_data, Exception):
    logger.warning(f"⚠️  Min. Trabalho falhou: {type(ministerio_trabalho_data).__name__}")
    ministerio_trabalho_data = {}

if isinstance(antp_data, Exception):
    logger.warning(f"⚠️  ANTP falhou: {type(antp_data).__name__}")
    antp_data = {}

if isinstance(defesa_civil_data, Exception):
    logger.warning(f"⚠️  Defesa Civil falhou: {type(defesa_civil_data).__name__}")
    defesa_civil_data = {}

if isinstance(cnj_data, Exception):
    logger.warning(f"⚠️  CNJ falhou: {type(cnj_data).__name__}")
    cnj_data = {}

# Dados ANTIGOS (manter pattern existente)
if isinstance(siconfi_data, Exception):
    logger.warning(f"⚠️  SICONFI falhou: {type(siconfi_data).__name__}")
    siconfi_data = {}
    
# ... (validar outros como no padrão antigo)
```

---

## 🎯 Como Integrar no Seu TOPSIS

Se você está em **backend/app/routers/topsis.py** na função `processar_cidade_real`:

### Passo 1: Importar as 5 novas funções

```python
from app.services.external_apis import (
    get_siconfi_finances,
    get_ibge_population,
    get_datasus_health_infrastructure,
    get_inep_education,
    get_transparencia_social,
    get_datasus_expanded_wrapper,
    get_portal_transparencia_expanded_wrapper,
    # 🆕 Novas APIs
    get_aneel_smart_metering,
    get_ministerio_trabalho_accidents,
    get_antp_zero_emission_fleet,
    get_defesa_civil_disasters,
    get_cnj_corruption_convictions,
)
```

### Passo 2: Atualizar o `asyncio.gather()` 

Veja instruções acima.

### Passo 3: Injetar dados no TOPSIS

**Dentro da função `inject_api_data_into_flat_list()`**, adicione no final:

```python
# 🎯 PARTE 3: Injetar dados das 5 NOVAS APIs

# [X] ANEEL: Medidores Inteligentes
if indicadores_flat[X] == 0.0 and aneel_data.get("medidores_inteligentes_pct", 0) > 0:
    indicadores_flat[X] = aneel_data["medidores_inteligentes_pct"]
    logger.info(f"   ✅ [Índice X] Medidores Inteligentes: {aneel_data['medidores_inteligentes_pct']:.1f}% (ANEEL)")

# [Y] Min. Trabalho: Acidentes Industriais
if indicadores_flat[Y] == 0.0 and ministerio_trabalho_data.get("acidentes_industriais_100k", 0) > 0:
    indicadores_flat[Y] = ministerio_trabalho_data["acidentes_industriais_100k"]
    logger.info(f"   ✅ [Índice Y] Acidentes Industriais: {ministerio_trabalho_data['acidentes_industriais_100k']:.2f}/100k (Min. Trabalho)")

# [Z] ANTP: Frota Zero Emissão
if indicadores_flat[Z] == 0.0 and antp_data.get("frota_onibus_zero_emissao_pct", 0) > 0:
    indicadores_flat[Z] = antp_data["frota_onibus_zero_emissao_pct"]
    logger.info(f"   ✅ [Índice Z] Frota Zero Emissão: {antp_data['frota_onibus_zero_emissao_pct']:.1f}% (ANTP)")

# [A] Defesa Civil: Mortalidade por Desastres
if indicadores_flat[A] == 0.0 and defesa_civil_data.get("mortalidade_desastres_100k", 0) > 0:
    indicadores_flat[A] = defesa_civil_data["mortalidade_desastres_100k"]
    logger.info(f"   ✅ [Índice A] Mortalidade Desastres: {defesa_civil_data['mortalidade_desastres_100k']:.2f}/100k (Defesa Civil)")

# [B] CNJ: Condenações por Corrupção
if indicadores_flat[B] == 0.0 and cnj_data.get("condenacoes_corrupcao_100k", 0) > 0:
    indicadores_flat[B] = cnj_data["condenacoes_corrupcao_100k"]
    logger.info(f"   ✅ [Índice B] Condenações Corrupção: {cnj_data['condenacoes_corrupcao_100k']:.2f}/100k (CNJ)")
```

---

## 📊 Índices Sugeridos (ajuste conforme necessário)

Se você está expandindo para 50+ indicadores, sugiro usar:

| API | Indicador | Índice Sugerido |
|-----|-----------|-----------------|
| ANEEL | Medidores Inteligentes (%) | 45 |
| Min. Trabalho | Acidentes Industriais/100k | 46 |
| ANTP | Frota Zero Emissão (%) | 47 |
| Defesa Civil | Mortalidade Desastres/100k | 48 |
| CNJ | Condenações Corrupção/100k | 49 |

---

## ✅ Checklist de Integração

- [ ] Importar as 5 novas funções em `topsis.py`
- [ ] Atualizar `asyncio.gather()` com as 5 novas chamadas
- [ ] Adicionar validação de Exception para cada novo dado
- [ ] Injetar dados das 5 novas APIs em `inject_api_data_into_flat_list()`
- [ ] Testar com `POST /api/v1/topsis/ranking-hibrido`
- [ ] Validar que as 5 novas APIs retornam dados (logs devem mostrar ✅)
- [ ] Verificar que o ranking reflete os dados (não deve ser 100% igual para todas as cidades)

---

## 🚀 Teste Rápido

```bash
# 1. Executar TOPSIS
curl -X POST "http://localhost:8000/api/v1/topsis/ranking-hibrido" \
  -H "Content-Type: application/json" \
  -d '{
    "municipios": [
      {"codigo_ibge": "4101408", "nome": "Apucarana"},
      {"codigo_ibge": "4113700", "nome": "Londrina"}
    ]
  }'

# 2. Verificar nos LOGS se as 5 novas APIs aparecem com ✅
# Procure por:
#   ✅ [Índice 45] Medidores Inteligentes
#   ✅ [Índice 46] Acidentes Industriais
#   ✅ [Índice 47] Frota Zero Emissão
#   ✅ [Índice 48] Mortalidade Desastres
#   ✅ [Índice 49] Condenações Corrupção
```

---

## 🔧 Troubleshooting

**Problema:** "Função `get_aneel_smart_metering` não encontrada"
- **Solução:** Importar em `topsis.py` com: `from app.services.external_apis import get_aneel_smart_metering`

**Problema:** "TypeError: expected float, got None"
- **Solução:** As 5 funções retornam dict com `{"campo": valor, "fonte": "str"}`. Acessar com `.get("campo", 0)`

**Problema:** "Timeout ao chamar 5 APIs"
- **Solução:** Normal em ambiente de desenvolvimento. As APIs têm timeout de 20s cada. Em paralelo com `asyncio.gather()`, máximo total é ~20s (não 100s).

---

## 📚 Referências

- **Função novo padrão:** `backend/app/services/external_apis.py` (linhas ~1300-1800)
- **TOPSIS principal:** `backend/app/routers/topsis.py` (função `inject_api_data_into_flat_list`)
- **Orquestração:** Procure por `asyncio.gather()` em `topsis.py` ou `main.py`

