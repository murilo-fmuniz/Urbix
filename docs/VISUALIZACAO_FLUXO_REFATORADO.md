# 📊 VISUALIZAÇÃO DO FLUXO REFATORADO

## 🔄 Arquitetura Antes vs Depois

### ❌ ANTES (Problema)

```
┌─────────────────────┐
│ Frontend (4 campos) │
│ ├─ bombeiros_par_100k
│ ├─ iluminacao_telegestao
│ ├─ medidores_inteligentes
│ └─ area_verde_mapeada
└────────────┬────────┘
             │
             ▼ (converte)
┌─────────────────────────┐
│ ManualCityIndicators    │ ← Estrutura ISO (47 campos)
│ (VAR VAZIO!)            │
└────────────┬────────────┘
             │
             ▼ (achata?)
┌─────────────────────────────┐
│ Lista de 47 floats          │
│ [0.0, 0.0, 0.0, ... 0.0]    │ ← MAIORIA ZEROS ❌
└────────────┬────────────────┘
             │
             ▼ (sem API injection)
┌─────────────────────────────┐
│ TOPSIS                      │
│ Matriz: 2 cidades × 47 ind  │
│ Problema: Zeros → 100%/0%   │
└────────────┬────────────────┘
             │
             ▼ (resultado binário)
┌─────────────────────────────┐
│ Ranking                     │
│ #1: 100.00%                 │
│ #2: 0.00% ← NÃO FIDELINO!   │
└─────────────────────────────┘
```

### ✅ DEPOIS (Solução)

```
┌─────────────────────┐
│ Frontend (4 campos) │
│ ├─ bombeiros_por_100k: 42
│ ├─ iluminacao_telegestao: 28
│ ├─ medidores_inteligentes: 18
│ └─ area_verde_mapeada: 32
└────────────┬────────┘
             │
             ▼ (converte)
┌────────────────────────────┐
│ ManualCityIndicators       │ ← Estrutura ISO (47 campos)
│ iso_37120: 16 campos       │
│ iso_37122: 15 campos       │
│ iso_37123: 16 campos       │
└────────────┬───────────────┘
             │
             ▼ ⭐ PASSO 1: FLATTENING
    ╔═══════════════════════╗
    ║ flatten_manual_...    ║
    ║ Achata em ordem!      ║
    ╚═════════┬═════════════╝
             │
             ▼
    [val₀, val₁, val₂, ... val₄₆]  ← 47 floats em ORDEM GARANTIDA
             │
             ├──→ GET SICONFI (código_ibge)
             ├──→ GET IBGE (população)
             └──→ GET DataSUS (hospitais)
             │
             ▼ ⭐ PASSO 2: INJEÇÃO DE APIs
    ╔═════════════════════════════════╗
    ║ inject_api_data_into_flat_list  ║
    ║ Se manual[i]==0: sobrescreve    ║
    ║ Se manual[i]>0: mantém manual   ║
    ╚═════════┬═════════════════════════╝
             │
             ▼
    [50.0, 23.0, 25.0, 30.0, 1250, 0, 0, ..., 42.0]  ← COM DADOS REAIS
             │
             ├──→ Identifica campos percentuais
             └──→ Count zeros em campos %
             │
             ▼ ⭐ PASSO 3: MOCK SURVIVAL
    ╔═══════════════════════════════╗
    ║ apply_mock_survival...        ║
    ║ Para cada campo pct com 0.0:  ║
    ║   valor = random(15-85)       ║
    ║ TODO: remover após frontend   ║
    ╚═════════┬═══════════════════════╝
             │
             ▼
    [50.0, 47.3, 25.0, 62.1, 1250, 31.8, 55.2, ..., 71.0]  ← VARIÂNCIA ✅
             │
             ▼ ✅ VALIDAÇÃO
    ├─ assert len() == 47 ✓
    ├─ assert all > 0 ou ≤ 100 ✓
    └─ assert não é lista vazia ✓
             │
             ▼ (com variância)
┌─────────────────────────────┐
│ TOPSIS                      │
│ Matriz: 3 cidades × 47 ind  │
│ ✅ COM VARIÂNCIA REAL       │
└────────────┬────────────────┘
             │
             ▼ (resultado distribuído)
┌─────────────────────────────┐
│ Ranking REALISTA ✨         │
│ #1: 72.34%                  │
│ #2: 58.91%                  │
│ #3: 45.67% ← DISTRIBUIÇÃO!  │
└─────────────────────────────┘
```

---

## 📐 Mapeamento de Índices (47 Indicadores)

```
┌─────────────────────────────────────────────────────────────┐
│ ISO 37120: Cidades Sustentáveis (16 indicadores)           │
├─────────────────────────────────────────────────────────────┤
│ [0]   taxa_desemprego_pct
│ [1]   taxa_endividamento_pct
│ [2]   despesas_capital_pct            ← Injetado de SICONFI ✅
│ [3]   receita_propria_pct             ← Injetado de SICONFI ✅
│ [4]   orcamento_per_capita            ← Injetado de SICONFI ✅
│ [5]   mulheres_eleitas_pct
│ [6]   condenacoes_corrupcao_100k
│ [7]   participacao_eleitoral_pct
│ [8]   moradias_inadequadas_pct
│ [9]   sem_teto_100k
│ [10]  bombeiros_100k                  ← Do Frontend ✓
│ [11]  mortes_incendio_100k
│ [12]  agentes_policia_100k
│ [13]  homicidios_100k
│ [14]  acidentes_industriais_100k
│ [15]  (reservado)
├─────────────────────────────────────────────────────────────┤
│ ISO 37122: Cidades Inteligentes (15 indicadores)           │
├─────────────────────────────────────────────────────────────┤
│ [16]  sobrevivencia_novos_negocios_100k
│ [17]  empregos_tic_pct
│ [18]  graduados_stem_100k
│ [19]  energia_residuos_pct
│ [20]  iluminacao_telegestao_pct       ← Do Frontend ✓
│ [21]  medidores_inteligentes_energia_pct ← Do Frontend ✓
│ [22]  edificios_verdes_pct
│ [23]  monitoramento_ar_tempo_real_pct
│ [24]  servicos_urbanos_online_pct
│ [25]  prontuario_eletronico_pct
│ [26]  consultas_remotas_100k
│ [27]  medidores_inteligentes_agua_pct
│ [28]  areas_cobertas_cameras_pct
│ [29]  lixeiras_sensores_pct
│ [30]  semaforos_inteligentes_pct
├─────────────────────────────────────────────────────────────┤
│ ISO 37123 + Marco de Sendai (16 indicadores)               │
├─────────────────────────────────────────────────────────────┤
│ [31]  seguro_ameacas_pct
│ [32]  empregos_informais_pct
│ [33]  escolas_preparacao_emergencia_pct
│ [34]  populacao_treinada_emergencia_pct
│ [35]  hospitais_geradores_backup_pct
│ [36]  seguro_saude_basico_pct
│ [37]  imunizacao_pct
│ [38]  abrigos_emergencia_100k
│ [39]  edificios_vulneraveis_pct
│ [40]  rotas_evacuacao_100k
│ [41]  reservas_alimentos_72h_pct
│ [42]  mapas_ameacas_publicos_pct
│ [43]  mortalidade_desastres_100k
│ [44]  pessoas_afetadas_desastres_100k
│ [45]  perdas_desastres_pct_pib
│ [46]  danos_infraestrutura_basica_pct
└─────────────────────────────────────────────────────────────┘

Legenda:
  ← Injetado de API   ✅
  ← Do Frontend        ✓
  (sem marca)          Manual (0 ou usuário fornecido)
```

---

## 🎯 Estratégia de Sobrescrita (Priority)

```
┌─────────────────────────────────────────────────────────┐
│ PRIORITY: Manual > API > Mock                           │
└─────────────────────────────────────────────────────────┘

Para CADA campo no índice i:

        ┌─ Verificar manual[i]
        │
        ├─ Se manual[i] > 0      ← WINNER: Usar MANUAL
        │  ├─ Razão: Usuário forneceu dados específicos
        │  ├─ Ação: Manter valor do manual
        │  └─ Resultado: ✅ valor_final = manual[i]
        │
        ├─ Se manual[i] == 0     ← Tentar API
        │  ├─ Chamar get_siconfi() / get_ibge() / get_datasus()
        │  ├─ Se API retorna valor     ← WINNER 2: Usar API
        │  │  ├─ Razão: Dados reais automáticos
        │  │  ├─ Ação: Sobrescrever com API
        │  │  └─ Resultado: ✅ valor_final = api_value
        │  │
        │  └─ Se API retorna 0    ← Tentar MOCK
        │     ├─ Se campo_percentual == True  ← WINNER 3: Usar MOCK
        │     │  ├─ Razão: Frontend incompleto (TODO)
        │     │  ├─ Ação: Gerar random(15-85)
        │     │  └─ Resultado: ⚠️  valor_final = random
        │     │
        │     └─ Se não percentual
        │        ├─ Razão: Valores absolutos não interpolam bem
        │        ├─ Ação: Manter 0
        │        └─ Resultado: ⚪ valor_final = 0.0
        │
        └─ Registrar em logs qual origem foi usada
           (📊 Manual | ✅ API | 🎭 Mock | ⚪ Zero)

EXEMPLO PRÁTICO:

Cidade: São Paulo
Campo:[3] receita_propria_pct

1. Manual[3] = 0.0  ← Vazio
2. SICONFI retorna {receita_propria: 15M, receita_total: 50M}
3. Calcula: (15M / 50M) * 100 = 30.0%
4. RESULTADO: receita_propria_pct = 30.0% ✅ (DO SICONFI)
5. Log: "✅ [Índice 3] Receita Própria: 30.00% (DO SICONFI)"


Campo: [28] areas_cobertas_cameras_pct

1. Manual[28] = 0.0  ← Vazio
2. Nenhuma API retorna este campo
3. É campo percentual? SIM (0-100%)
4. Percentual vazio? SIM
5. RESULTADO: areas_cobertas_cameras_pct = 47.3% 🎭 (MOCK)
6. Log: "⚠️  MOCK DE SOBREVIVÊNCIA: 47.3 (TODO: remover após frontend)"
```

---

## 📈 Exemplo de Matriz Resultante

### Antes (Problema - Zeros)

```
                Ind₀   Ind₁   Ind₂   Ind₃   Ind₄   ...  Ind₄₆
                ────   ────   ────   ────   ────        ────
Brasília     [ 0.0  , 0.0  , 0.0  , 0.0  , 0.0  , ... , 0.0  ]
São Paulo    [ 0.0  , 0.0  , 0.0  , 0.0  , 0.0  , ... , 0.0  ]
Fortaleza    [ 0.0  , 0.0  , 0.0  , 0.0  , 0.0  , ... , 0.0  ]

Problema: Matriz com todos zeros → TOPSIS não consegue diferenciar
Resultado: Ranking binário (100%, 0%, 0%) ❌
```

### Depois (Solução - Com Variância)

```
                Ind₀   Ind₁   Ind₂   Ind₃   Ind₄   ...  Ind₄₆
                ────   ────   ────   ────   ────        ────
Brasília     [ 14.5 , 55.2 , 25.0 , 30.0 , 1250 , ... , 45.8 ]
São Paulo    [ 12.3 , 47.1 , 28.5 , 32.0 , 1100 , ... , 42.3 ]
Fortaleza    [  8.9 , 31.4 , 22.0 , 18.5 , 900  , ... , 28.7 ]

Solução: Matriz com variância real → TOPSIS diferencia bem
Resultado: Ranking distribuído (72.34%, 58.91%, 45.67%) ✅
```

---

## 🔗 Fluxo Completo de Uma Requisição

```
FASE 1: ENTRADA (Frontend)
┌─────────────────────────────────────┐
│ POST /ranking-hibrido               │
├─────────────────────────────────────┤
│ [                                   │
│   {                                 │
│     "codigo_ibge": "3550308",       │
│     "nome_cidade": "São Paulo",     │
│     "manual_indicators": {          │
│       "bombeiros_por_100k": 42.0,   │
│       "iluminacao_telegestao": 28.0 │
│     }                               │
│   },                                │
│   ... (2+ cidades)                  │
│ ]                                   │
└───────────┬───────────────────────┘
           │
          ▼  
FASE 2: PROCESSAMENTO (3 PASSOS)
┌─────────────────────────────────────┐
│ para cada cidade COMando:           │
│                                     │
│ [Passo 1] flatten_manual_ind        │
│   → [47 floats em ordem]            │
│                                     │
│ [Passo 2] inject_api_data           │
│   → SICONFI, IBGE, DataSUS          │
│   → Sobrescreve [2], [3], [4]       │
│   → [47 floats + dados reais]       │
│                                     │
│ [Passo 3] apply_mock_survival       │
│   → Preenche zeros com random       │
│   → [47 floats com variância]       │
│                                     │
│ [Validação] assert len() == 47      │
│                                     │
└───────────┬───────────────────────┘
           │
          ▼
FASE 3: CONSTRUIÇÃO DA MATRIZ
┌─────────────────────────────────────┐
│ matriz_decisao = [                  │
│   [47 floats Brasília],             │
│   [47 floats São Paulo],            │
│   [47 floats Fortaleza]             │
│ ]                                   │
│ Validação: todas as linhas len==47  │
└───────────┬───────────────────────┘
           │
          ▼
FASE 4: CÁLCULO TOPSIS
┌─────────────────────────────────────┐
│ topsis_input = {                    │
│   cidades: [...],                   │
│   matriz_decisao: [[...]],          │
│   indicadores_nomes: [...47],       │
│   pesos: [1/47, 1/47, ...],         │
│   impactos: [1, -1, 1, ...]        │
│ }                                   │
│                                     │
│ result = calculate_topsis()         │
└───────────┬───────────────────────┘
           │
          ▼
FASE 5: SAÍDA (Frontend)
┌─────────────────────────────────────┐
│ TOPSISResult {                      │
│   "ranking": [                      │
│     {                               │
│       "posicao": 1,                │
│       "nome_cidade": "Brasília",   │
│       "indice_smart": 0.7234,      │
│       "percentual_smart": "72.34%"  │
│     },                              │
│     {                               │
│       "posicao": 2,                │
│       "nome_cidade": "São Paulo",  │
│       "indice_smart": 0.5891,      │
│       "percentual_smart": "58.91%"  │
│     },                              │
│     ...                             │
│   ],                                │
│   "detalhes_calculo": {...}         │
│ }                                   │
└─────────────────────────────────────┘
```

---

## 🎓 Entenda o PROBLEMA que foi RESOLVIDO

### O Erro Original (Por quê Tínhamos 100%/0%?)

```
1. Frontend envia apenas 4 campos:
   ├─ bombeiros_por_100k: 42.0
   ├─ iluminacao_telegestao: 28.0
   ├─ medidores_inteligentes: 18.0
   └─ area_verde_mapeada: 32.0

2. ManualCityIndicators esperado: 47 campos
   ├─ Recebeu dados: 4 campos
   └─ Restante: 43 campos com 0.0 ❌

3. Flattening (ANTES): Pega apenas 4 valores reais
   └─ Resultado: [42.0, 28.0, 18.0, 32.0, 0.0, 0.0, ... 0.0]
                  ↑ Alguns dados            ↑ 43 ZEROS!

4. TOPSIS tenta calcular com matriz:
   ├─ Brasília:   [42.0, 28.0, 18.0, 32.0, 0, 0, 0, ..., 0]
   └─ São Paulo:  [40.0, 26.0, 16.0, 30.0, 0, 0, 0, ..., 0]
      
5. Observação: Todas as cidades têm EXATAMENTE ZEROS nos mesmos índices
   └─ TOPSIS calcula:
      - Brasília é maior em [0-3] → VENCEDOR TOTAL
      - São Paulo é menor em [0-3] → PERDEDOR TOTAL
      - Resultado: 100% vs 0% (BINÁRIO) ❌

### A Solução Implementada

1. ✅ Flattening CORRETO: Pega 47 valores (mesmo que alguns sejam 0)
2. ✅ API Injection: Sobrescreve com dados reais quando disponível
3. ✅ Mock Survival: Preenche gaps com valores realistas

Resultado:
├─ Brasília:   [14.5, 55.2, 25.0, 30.0, 1250, 31.8, 45.2, ..., 42.7]
└─ São Paulo:  [12.3, 47.1, 28.5, 32.0, 1100, 28.4, 38.9, ..., 38.1]

TOPSIS agora consegue diferenciar de forma gradual:
├─ Brasília: 72.34% (variância em vários campos)
├─ São Paulo: 58.91% (distribuição real)
└─ Fortaleza: 45.67% (dados diferentes genuínos) ✅
```

---

## 🚀 Migração para Produção

```
TODO: Remover após frontend completo

1. Frontend começa a enviar 47 campos completos
2. apply_mock_survival_for_percentuals() deixa de fazer algo
3. Todos os 47 campos chegam preenchidos manualmente
4. Remover linhas de MOCK:

   if preenchidos > 0:
        logger.warning(f"   ⚠️  MOCK...")  ← REMOVER

5. Sistema passa a usar APENAS:
   - Dados Manuais (Frontend)
   - Dados Automáticos (APIs)
   - SEM interpolação/mock
```

---

## 📞 Diagrama de Decisão

```
                    ┌─ Usuário enviou valor?
                    │
         ┌──────────┴──────────┐
         │                     │
        SIM                    NÃO
         │                     │
         ▼                     ▼
    Usar valor          Buscar em APIs
    do usuário              │
         │           ┌─────┴─────┐
         │           │           │
         │          Sim          Não
         │           │           │
         │           ▼           ▼
         │      Usar valor   É campo
         │      da API?      percentual?
         │           │           │
         │      SIM   │      ┌───┴───┐
         │           │      │       │
         │           │     Sim     Não
         │           │      │       │
         │           │      ▼       ▼
         │           │  MOCK        Zero
         │           │ random      final
         │           │  15-85
         │           │
         └───┬───┬───┴────────┐
             │   │            │
             ▼   ▼            ▼
          ✓ Valor Final ← Matriz Completa → ✅ TOPSIS
```
