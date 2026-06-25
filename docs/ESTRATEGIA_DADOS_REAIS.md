# 🎯 ESTRATÉGIA: Integração de Dados Reais por Indicador

## Situação Atual
- ❌ Apenas 3-12 indicadores com dados reais por cidade
- ❌ 38-47 indicadores em 0.0 ou usando médias nacionais (0.7071)
- ❌ Fallbacks genéricos distorcem o ranking
- ✅ 31 cidades com dados parciais no banco

## Objetivo
**Implementar coleta de dados REAIS de fontes oficiais para TODOS os 50 indicadores**

---

## 📊 MAPEAMENTO: 50 Indicadores → Fontes de Dados

### ISO 37120 - Cidades Sustentáveis (18 indicadores)

| # | Indicador | Fonte Atual | Fonte Ideal | Status |
|---|-----------|------------|------------|--------|
| 0 | Taxa Desemprego (%) | ❌ Média nacional | **CAGED (MTE)** ou **PED/DIEESE** | 🔴 |
| 1 | Taxa Endividamento (%) | ⚠️ SICONFI (0) | **SICONFI + Análise Manual** | 🟡 |
| 2 | Despesas Capital (% orç) | ✅ SICONFI | **SICONFI** (mantém) | 🟢 |
| 3 | Receita Própria (%) | ✅ SICONFI | **SICONFI** (mantém) | 🟢 |
| 4 | Orçamento per capita | ✅ SICONFI | **SICONFI** (mantém) | 🟢 |
| 5 | Mulheres Eleitas (%) | ❌ Média nacional | **TSE + API Transparência** | 🔴 |
| 6 | Condenações Corrupção | ❌ Média nacional | **CNJ + MPF** | 🔴 |
| 7 | Participação Eleitoral (%) | ❌ Média nacional | **TSE (eleições locais)** | 🔴 |
| 8 | Moradias Inadequadas (%) | ❌ Média nacional | **IBGE + DataSUS** ou **Levantamento municipal** | 🔴 |
| 9 | Sem-teto (100k hab) | ❌ Média nacional | **Censo SUAS** ou **Secretaria de Assistência Social** | 🔴 |
| 10 | Bombeiros (100k hab) | ❌ Média nacional | **SSP estadual + PM local** | 🔴 |
| 11 | Mortes por Incêndio | ❌ Média nacional | **DataSUS + Corpo de Bombeiros** | 🔴 |
| 12 | Agentes Polícia (100k) | ❌ Média nacional | **SSP estadual** | 🔴 |
| 13 | Homicídios (100k hab) | ❌ Média nacional | **DataSUS + SSP** | 🔴 |
| 14 | Acidentes Industriais | ❌ Média nacional | **CEREST + Ministério do Trabalho** | 🔴 |
| 15 | Relação Estudante/Prof | ⚠️ INEP Fallback | **INEP (CENSO ESCOLAR)** | 🟡 |
| 16 | IDEB Anos Iniciais | ⚠️ INEP Fallback | **INEP (SAEB)** | 🟡 |
| 17 | Relação Est/Prof (repet) | ⚠️ Duplicado | **REMOVER ou usar INEP** | 🔴 |

### ISO 37122 - Cidades Inteligentes (17 indicadores)

| # | Indicador | Fonte Atual | Fonte Ideal | Status |
|---|-----------|------------|------------|--------|
| 18 | Novos Negócios (100k) | ❌ Média nacional | **JUCESP/JUCERGS/Portal CNPJ** | 🔴 |
| 19 | Empregos em TIC (%) | ❌ Média nacional | **CAGED + Pesquisa municipal** | 🔴 |
| 20 | Graduados STEM (100k) | ❌ Média nacional | **INEP + Universidades locais** | 🔴 |
| 21 | Energia de Resíduos (%) | ❌ Média nacional | **ANEEL + Prefeitura (ETAs)** | 🔴 |
| 22 | Iluminação Telegestão (%) | ❌ Média nacional | **Prefeitura (Secretaria Obras)** | 🔴 |
| 23 | Medidores Inteligentes (%) | ❌ Média nacional | **Concessionária de energia local** | 🔴 |
| 24 | Edifícios Verdes (%) | ❌ Média nacional | **Prefeitura + Selos certificação** | 🔴 |
| 25 | Monitoramento Ar (%) | ❌ Média nacional | **CETESB + Estações de monitoramento** | 🔴 |
| 26 | Serviços Urbanos Online (%) | ❌ Média nacional | **Plataforma Gov.br + Portal Prefeitura** | 🔴 |
| 27 | Prontuário Eletrônico (%) | ❌ Média nacional | **DataSUS + Secretaria Saúde** | 🔴 |
| 28 | Consultas Remotas (100k) | ❌ Média nacional | **DataSUS (SIA-SUS)** | 🔴 |
| 29 | Medidores Água (%) | ❌ Média nacional | **Concessionária água local** | 🔴 |
| 30 | Áreas com Câmeras (%) | ❌ Média nacional | **Prefeitura + SSP** | 🔴 |
| 31 | Lixeiras com Sensores (%) | ❌ Média nacional | **Prefeitura (Limpeza Urbana)** | 🔴 |
| 32 | Semáforos Inteligentes (%) | ❌ Média nacional | **Prefeitura (Mobilidade)** | 🔴 |
| 33 | Frota Ônibus Limpo (%) | ❌ Média nacional | **Concessionária de transporte** | 🔴 |
| 34 | Escolas Conectadas (%) | ⚠️ Fallback INEP | **INEP (Censo Escolar)** | 🟡 |

### ISO 37123 + Sendai - Resiliência (16 indicadores)

| # | Indicador | Fonte Atual | Fonte Ideal | Status |
|---|-----------|------------|------------|--------|
| 35 | Seguro contra Ameaças (%) | ❌ Média nacional | **Susep + Seguradoras** | 🔴 |
| 36 | Empregos Informais (%) | ❌ Média nacional | **IBGE (PME/PNAD)** | 🔴 |
| 37 | Escolas Prep. Emergência (%) | ❌ Média nacional | **INEP + Bombeiros** | 🔴 |
| 38 | População Treinada (%) | ❌ Média nacional | **Prefeitura + Defesa Civil** | 🔴 |
| 39 | Hospitais Gerador Backup (%) | ❌ Média nacional | **DataSUS + Secretaria Saúde** | 🔴 |
| 40 | Seguro Saúde Básico (%) | ❌ Média nacional | **ANS + Pesquisa municipal** | 🔴 |
| 41 | Taxa Imunização (%) | ❌ Média nacional | **DataSUS (PNI)** | 🟡 |
| 42 | Abrigos Emergência (100k) | ❌ Média nacional | **SUAS + Defesa Civil** | 🔴 |
| 43 | Edifícios Vulneráveis (%) | ❌ Média nacional | **Prefeitura + Defesa Civil** | 🔴 |
| 44 | Rotas Evacuação (100k) | ❌ Média nacional | **Prefeitura + Defesa Civil** | 🔴 |
| 45 | Reservas Alimentos 72h (%) | ❌ Média nacional | **Prefeitura + CONAB** | 🔴 |
| 46 | Mapas Ameaças Públicos (%) | ❌ Média nacional | **Prefeitura + Defesa Civil** | 🔴 |
| 47 | Mortalidade Desastres | ❌ Média nacional | **DataSUS + Defesa Civil** | 🔴 |
| 48 | Pessoas Afetadas Desastres | ❌ Média nacional | **Defesa Civil + Proteção Civil** | 🔴 |
| 49 | Perdas % PIB | ❌ Média nacional | **ABNT + Mapeamento municipal** | 🔴 |

---

## 🔌 PLANO DE IMPLEMENTAÇÃO (Prioridade)

### FASE 1: Fontes Imediatas (Próximas 2 semanas)
**Indicadores que podem ser implementados AGORA:**

1. ✅ **SICONFI** - Já implementado (manter)
   - Taxa Endividamento (campo: divida_consolidada)
   - Despesas Capital
   - Receita Própria
   - Orçamento per capita

2. 🔴 **INEP (Censo Escolar)**
   - Relação Estudante/Professor → API INEP
   - IDEB → API INEP
   - Escolas Conectadas → API INEP

3. 🔴 **DataSUS (Tabulação)**
   - Taxa Imunização → SIA-SUS
   - Hospitais com Gerador → CNES
   - Prontuário Eletrônico → e-Gestor
   - Consultas Remotas → SIA-SUS

4. 🔴 **TSE (Eleições)**
   - Participação Eleitoral → API TSE
   - Mulheres Eleitas → API TSE

### FASE 2: APIs Estaduais (3-4 semanas)
5. SSP (Segurança Pública)
   - Policiais por 100k
   - Homicídios
   - Acidentes industriais

6. CETESB (Meio Ambiente - SP)
   - Monitoramento de Ar

### FASE 3: Painel Administrativo (4-6 semanas)
**Para indicadores sem fonte oficial confiável:**
- Criar formulário web para gestores municipais preencherem dados
- Incluir: bombeiros, moradias inadequadas, energia renovável, etc.
- Validação e auditoria de mudanças

### FASE 4: Integração Manual Web Scraping (6-8 semanas)
- Web scraping de portais municipais
- OCR para documentos PDF
- Importação de Excel/CSV

---

## 🛠️ IMPLEMENTAÇÃO TÉCNICA

### Option A: Usar Este Semestre (Rápido)
```python
# backend/app/services/data_sources.py

# 1. INEP - Já tem api
get_inep_education(municipio_code)  # ✅ IMPLEMENTAR COM AUTENTICAÇÃO

# 2. TSE - API pública
get_tse_elections(municipio_code)  # 🔴 NOVO

# 3. DataSUS - Tabulação
get_datasus_immunization(municipio_code)  # 🔴 NOVO

# 4. Painel Admin para dados manuais
POST /api/v1/admin/indicadores/{cidade}
{
    "bombeiros_100k": 25.5,
    "moradias_inadequadas_pct": 12.3,
    ...
}
```

### Option B: Usar Próximo Ano (Completo)
- Integração com CAGED, JUCESP, Concessionárias
- Web scraping automatizado
- Machine learning para estimar dados faltantes

---

## ✅ RECOMENDAÇÃO

**Comecar AGORA com:**

1. **INEP (API)**
   - Relação Estudante/Professor ✅
   - IDEB ✅
   - Escolas Conectadas ✅

2. **TSE (API)**
   - Participação Eleitoral
   - Mulheres Eleitas

3. **DataSUS (Tabulação)**
   - Taxa Imunização
   - Hospitais gerador

4. **Painel Admin Web**
   - Bombeiros, Polícia, Moradias, Energia
   - ~15 campos críticos

**Isso vai de 12/50 → 25-30/50 indicadores com dados REAIS em 1 mês!**

---

## 📝 Próximos Passos

Qual desses você quer que eu implemente PRIMEIRO?

1. 🔵 INEP + TSE (APIs públicas - fácil)
2. 🔵 Painel Admin (web form - moderado)
3. 🔵 DataSUS completo (API complexa - difícil)
4. 🔵 Tudo ao mesmo tempo (paralelo)
