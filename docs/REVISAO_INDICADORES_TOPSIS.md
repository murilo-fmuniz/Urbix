# 📋 Revisão: Integração de indicadores.py com Cálculos TOPSIS

## ⚠️ Problema Identificado

### Arquitetura Atual (Desconectada)

```
┌─────────────────────────────────────────────────────────┐
│              Fluxo 1: AdminPage (Frontend)              │
├─────────────────────────────────────────────────────────┤
AdminPage.jsx
    │
    ├─→ criarColeta()  (API call)
    │
    ├─→ POST /api/v1/indicadores/{codigo}/coletas
    │
    ├─→ indicadores.py (Router)
    │
    └─→ Database: DadosColeta (Armazenado)
    
    ❌ PORÉM: Não é usando em TOPSIS
```

```
┌─────────────────────────────────────────────────────────┐
│         Fluxo 2: RankingPage/SmartCityDashboard        │
├─────────────────────────────────────────────────────────┤
Frontend (RankingPage)
    │
    ├─→ POST /api/v1/topsis/ranking-hibrido
    │
    ├─→ topsis.py (Router)
    │
    ├─→ processar_cidade_real()
    │
    ├─→ Chamadas em paralelo:
    │   ├─ get_ibge_population()      ✅ API externa
    │   ├─ get_siconfi_finances()     ✅ API externa
    │   └─ get_datasus_health_infrastructure() ✅ API externa
    │
    ├─→ calculate_all_indicators()
    │
    └─✅ Retorna Ranking TOPSIS
    
    ❌ PORÉM: Nunca consulta DadosColeta (banco de dados)
```

---

## 🔍 Análise Do Problema

### O Que É indicadores.py?

**Router CRUD para gerenciar indicadores estratégicos:**

```python
# Endpoints Disponíveis:

# 1. Listar indicadores (com filtros)
GET /api/v1/indicadores?cidade=Apucarana&norma=ISO 37122

# 2. Obter detalhes de um indicador específico
GET /api/v1/indicadores/ECO.1

# 3. Criar novo indicador mestre
POST /api/v1/indicadores
{ "codigo_indicador": "ECO.1", "nome": "Taxa de desemprego", ... }

# 4. Inserir coleta de dados para um indicador
POST /api/v1/indicadores/ECO.1/coletas
{ "cidade": "Apucarana", "estado": "PR", "valor_final": 5.2, ... }

# 5. Atualizar coleta existente
PUT /api/v1/indicadores/coletas/{coleta_id}
{ "valor_final": 5.1, ... }
```

**Propósito:** Armazenar dados históricos coletados de políticas públicas (governança, finanças, infraestrutura, etc.)

### O Que É topsis.py?

**Router de cálculo TOPSIS (análise de decisão multicritério):**

```python
# Endpoints Disponíveis:

# 1. Cálculo híbrido com APIs + dados manuais
POST /api/v1/topsis/ranking-hibrido
[
  { "codigo_ibge": "4101408", "nome_cidade": "Apucarana", "manual_indicators": {...} },
  { "codigo_ibge": "4113700", "nome_cidade": "Londrina", "manual_indicators": null }
]
```

**Propósito:** Análise TOPSIS usando dados em tempo real (APIs governamentais + indicadores manuais da prefeitura)

---

## 🚨 O Problema Real

### Fluxo AdminPage → Dados Coletados Mas Não Usados

```
AdminPage coleta dados:
├─ ECO.1 Taxa de desemprego
├─ ECO.2 Despesas de capital
├─ GOV.2 Serviços urbanos online
└─ SAU.1 Mortalidade infantil
    │
    ├─→ POST /indicadores/ECO.1/coletas
    │
    └─→ Armazenado em DadosColeta table ✅
    
PORÉM: Esses dados NUNCA são consultados no cálculo de TOPSIS ❌
```

### Por Que Não Funciona Hoje?

**topsis.py NÃO consulta o banco de dados:**

```python
# topsis.py faz APENAS chamadas a APIs externas:
async def processar_cidade_real(codigo_ibge, nome_cidade, manual):
    # ❌ Nunca faz: db.query(DadosColeta).filter(...)
    
    populacao, finances, hospitais = await asyncio.gather(
        get_ibge_population(codigo_ibge),        # 🌐 API IBGE
        get_siconfi_finances(codigo_ibge),       # 🌐 API SICONFI
        get_datasus_health_infrastructure(...),  # 🌐 API DataSUS
    )
    
    # Usa apenas dados da API + manual_indicators (do frontend)
    # ❌ Nunca consulta: dados_coleta table
```

---

## ✅ Solução Recomendada

### Opção A: Integração Completa (Recomendada)

**Fluxar topsis.py para consultar banco de dados como fallback:**

```python
async def get_indicators_from_db_or_api(codigo_ibge, nome_cidade):
    """
    Buscar indicadores com prioridade:
    1. Banco de dados (DadosColeta) se disponível
    2. Caso contrário, APIs externas (fallback)
    3. Se ambos falharem, usar valores padrão
    """
    db = SessionLocal()
    
    # Buscar coletas recentes no banco
    coleta_recente = db.query(DadosColeta).filter(
        DadosColeta.cidade == nome_cidade,
        DadosColeta.ano_referencia >= 2024  # Últimos 2 anos
    ).order_by(DadosColeta.data_criacao.desc()).first()
    
    if coleta_recente:
        # ✅ Usar dados do banco (mais confiáveis, curados manualmente)
        logger.info(f"✅ Usando dados do banco para {nome_cidade}")
        return {
            "fonte": "banco_de_dados",
            "data": coleta_recente.data_criacao,
            "...dados...": coleta_recente.to_dict()
        }
    else:
        # ❌ Fallback para APIs externas
        logger.info(f"⚠️ Dados não encontrados no banco, consultando APIs para {nome_cidade}")
        return await get_from_apis(codigo_ibge)

# Em processar_cidade_real():
indicator_data = await get_indicators_from_db_or_api(codigo_ibge, nome_cidade)
```

**Vantagens:**
- ✅ Usa dados curados manualmente (AdminPage)
- ✅ Fallback automático para APIs se banco vazio
- ✅ Compatível com fluxo atual
- ✅ Permite offline (com dados históricos)

---

### Opção B: API Híbrida (Alternativa)

**Criar novo endpoint que permite explicitar fonte de dados:**

```python
POST /api/v1/topsis/ranking-hibrido-v2
[
  {
    "codigo_ibge": "4101408",
    "nome_cidade": "Apucarana",
    "fonte_dados": "banco",  # ← Novo: "banco" ou "api"
    "ano_referencia": 2025,  # ← Novo: qual ano do banco usar
    "manual_indicators": {...}
  },
  {
    "codigo_ibge": "4113700",
    "nome_cidade": "Londrina",
    "fonte_dados": "api",    # ← Usar APIs para esta cidade
    "manual_indicators": null
  }
]
```

**Vantagens:**
- ✅ Controle explícito do usuário sobre fonte
- ✅ Permite comparar banco vs. API
- ✅ Transparência total

---

## 📊 Recomendação Final

### Implementar **Opção A** (Integração Completa)

**Passos:**

1. **Modificar `processar_cidade_real()` em topsis.py:**
   ```python
   async def processar_cidade_real(codigo_ibge: str, nome_cidade: str, manual: ManualCityIndicators = None) -> dict:
       # 1. Tentar banco primeiro
       coleta = await get_coleta_from_db(nome_cidade)
       
       if coleta_data:
           # Usar dados do banco
           return process_db_data(coleta_data)
       else:
           # Fallback para APIs (código atual)
           return await process_from_apis(codigo_ibge, nome_cidade)
   ```

2. **Criar função auxiliar:**
   ```python
   async def get_coleta_from_db(nome_cidade: str) -> Optional[dict]:
       """Busca coleta mais recente no banco para uma cidade"""
       db = SessionLocal()
       coleta = db.query(DadosColeta)\
           .filter(DadosColeta.cidade == nome_cidade)\
           .order_by(DadosColeta.data_criacao.desc())\
           .first()
       db.close()
       return coleta.to_dict() if coleta else None
   ```

3. **Adicionar logging:**
   ```python
   logger.info(f"Fonte de dados: {'BANCO' if from_db else 'API'}")
   ```

4. **Testar integração:**
   - Inserir dados via AdminPage
   - Verificar que TOPSIS os encontra e usa

---

## 🧪 Teste de Validação

### Teste 1: Dados no Banco
```bash
# 1. Inserir via AdminPage
# POST /api/v1/indicadores/ECO.1/coletas
# Inserir valores para Apucarana, 2025

# 2. Calcular TOPSIS
# POST /api/v1/topsis/ranking-hibrido
# Deve usar dados do banco (presente nos logs)
```

### Teste 2: Dados Não Encontrados
```bash
# Tentar TOPSIS com cidade que não tem dados no banco
# Deve fazer fallback automático para APIs
```

### Teste 3: Priorização
```bash
# Inserir dados do banco
# Comparar resultado TOPSIS com/sem dados do banco
# Deve usar dados do banco quando disponíveis
```

---

## 📋 Status Atual vs. Proposto

| Aspecto | Atual | Proposto |
|---------|-------|----------|
| Fluxo AdminPage → indicadores.py | ✅ Funciona | ✅ Continua |
| Armazenamento DadosColeta | ✅ Funciona | ✅ Continua |
| Consulta banco em TOPSIS | ❌ Não faz | ✅ Adicionar |
| APIs externas | ✅ Funciona | ✅ Como fallback |
| Indicadores manuais (frontend) | ✅ Funciona | ✅ Continua |
| Transparência de fonte | ❌ Não | ✅ Adicionar logs |

---

## ⚡ Próximos Passos

1. **Decidir:** Implementar Opção A (recomendado)?
2. **Desenvolvimento:** Modificar `processar_cidade_real()` 
3. **Testes:** Validar com dados AdminPage
4. **Documentação:** Atualizar README com novo fluxo

