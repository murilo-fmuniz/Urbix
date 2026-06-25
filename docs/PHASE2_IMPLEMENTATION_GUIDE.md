# ROADMAP PHASE 2 - GUIA DE IMPLEMENTAÇÃO

**Status:** Planejamento | **Objetivo:** Atingir 25-30% cobertura (13-16 indicadores reais)  
**Timeline Estimada:** 2-3 semanas | **Responsável:** Próxima etapa

---

## 1. OVERVIEW PHASE 2

### Objetivos
- [ ] Adicionar 5-8 novos indicadores com dados reais
- [ ] Criar Admin Panel CRUD para entrada manual de dados
- [ ] Expandir DataSUS para saúde/infraestrutura
- [ ] Atingir 25-30% de cobertura (13-16/50 indicadores)

### Prioridades
1. **Admin Panel** (Alta) - Sem Admin, não há coleta manual
2. **DataSUS Expansion** (Alta) - Saúde é 16 indicadores (31-46)
3. **Portal Transparência** (Média) - Programas sociais (10-12 indicadores)
4. **Testes** (Média) - Validar todas as rotas

---

## 2. TAREFA 1: CRIAR ADMIN PANEL PARA MANUAL DATA ENTRY

### Objetivo
Formulário CRUD para que prefeituras insiram/atualizem os 50 indicadores manualmente.

### Estrutura de Arquivos a Criar

```
backend/app/routers/manual_data_admin.py (NEW)
  ├─ GET /admin/manual/{codigo_ibge} - Recuperar indicadores atuais
  ├─ POST /admin/manual - Salvar novo conjunto
  ├─ PUT /admin/manual/{codigo_ibge} - Atualizar existente
  └─ DELETE /admin/manual/{codigo_ibge} - Limpar

frontend/src/components/AdminPanel.jsx (NEW)
  ├─ Tabs: ISO37120 | ISO37122 | ISO37123
  ├─ Campos de input para cada indicador
  ├─ Validação de ranges (0-100%, unidades corretas)
  └─ Botões: Save, Cancel, Reset

frontend/src/pages/AdminPage.jsx (NEW)
  ├─ Layout com AdminPanel
  ├─ Autenticação (token de prefeitura)
  └─ Feedback de sucesso/erro
```

### Backend Implementation Checklist

```python
# backend/app/routers/manual_data_admin.py

from fastapi import APIRouter, HTTPException
from app.schemas import ManualCityIndicators
from app.models import CityManualData
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/manual/{codigo_ibge}")
async def get_manual_data(codigo_ibge: str):
    """Recuperar indicadores manuais atuais de uma cidade"""
    city = db.query(CityManualData).filter_by(codigo_ibge=codigo_ibge).first()
    if not city:
        raise HTTPException(404, "Cidade não encontrada")
    return city.indicadores_manuais

@router.post("/manual")
async def create_manual_data(codigo_ibge: str, data: ManualCityIndicators):
    """Criar novo registro de indicadores manuais"""
    # Validar: Nenhum indicador > 100% (exceto orçamento per capita)
    # Salvar com timestamp
    # Retornar confirmação
    pass

@router.put("/manual/{codigo_ibge}")
async def update_manual_data(codigo_ibge: str, data: ManualCityIndicators):
    """Atualizar indicadores manuais existentes"""
    # Validar: Nenhum valor negativo
    # Atualizar data_atualizacao
    # Limpar cache TOPSIS para forçar recálculo
    pass
```

### Frontend Implementation Checklist

```jsx
// frontend/src/components/AdminPanel.jsx

export function AdminPanel({ codigo_ibge }) {
  const [formData, setFormData] = useState({
    iso_37120: {},
    iso_37122: {},
    iso_37123: {}
  });
  const [activeTab, setActiveTab] = useState('iso_37120');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  // 1. Load current data
  useEffect(() => {
    fetch(`/admin/manual/${codigo_ibge}`)
      .then(r => r.json())
      .then(data => setFormData(data));
  }, [codigo_ibge]);

  // 2. Render tabbed form
  return (
    <div className="admin-panel">
      <Tabs activeTab={activeTab} onChange={setActiveTab}>
        <Tab label="ISO 37120" value="iso_37120">
          <IndicatorForm fields={ISO37120_FIELDS} />
        </Tab>
        <Tab label="ISO 37122" value="iso_37122">
          <IndicatorForm fields={ISO37122_FIELDS} />
        </Tab>
        <Tab label="ISO 37123" value="iso_37123">
          <IndicatorForm fields={ISO37123_FIELDS} />
        </Tab>
      </Tabs>
      
      <div className="buttons">
        <button onClick={handleSave} disabled={loading}>
          {loading ? 'Salvando...' : 'Salvar'}
        </button>
        <button onClick={handleReset}>Cancelar</button>
      </div>
    </div>
  );
}
```

### Validações Obrigatórias
- Nenhum campo pode ser negativo
- % deve estar entre 0-100 (exceto orçamento per capita, população)
- Unidades corretas (R$, habitantes, %)
- Tipos de dados: float, int (nunca string)

### Timeline
- [ ] Backend routes: 1 dia
- [ ] Frontend form: 1 dia
- [ ] Validação + Testes: 1 dia

---

## 3. TAREFA 2: EXPANDIR DataSUS PARA SAÚDE/INFRAESTRUTURA

### Problema Atual
DataSUS está retornando 0 para a maioria das cidades. Precisamos investigar endpoints alternativos.

### Indicadores-Alvo (Indices 28-32)
- [28] hospitais_por_100k (população)
- [29] leitos_uti_pct (leitos UTI / total de leitos)
- [30] cobertura_vacina_covid_pct
- [31] cobertura_atencao_basica_pct
- [32] agentes_comunitarios_saude

### APIs a Investigar

#### Option 1: DataSUS CNES (Estabelecimentos)
```
GET https://apidadosabertos.saude.gov.br/cnes/estabelecimentos?codigo_ibge=XXXX
```
- [ ] Testar com cidades conhecidas (Apucarana 4101408, São Paulo 3550308)
- [ ] Extrair contagem de hospitais, leitos, estabelecimentos

#### Option 2: SINAN (Vigilância Epidemiológica)
```
GET https://apidatalake.tesouro.gov.br/ords/saude/sinan
```
- [ ] Investigar cobertura de doenças/vacinação por município

#### Option 3: TabNet DataSUS
```
GET https://datasus.saude.gov.br/transfer/OpenDataAS/tabnet
```
- [ ] Mais completo, mas menos estruturado
- [ ] Requer parsing HTML/Excel

### Implementation (backend/app/services/datasus_api_expanded.py)

```python
import aiohttp
import logging

async def get_datasus_health(codigo_ibge: str):
    """
    Busca dados de saúde do DataSUS CNES
    Retorna: hospitais, leitos UTI, cobertura de saúde básica
    """
    logger.info(f"📡 DataSUS: Consultando saúde para {codigo_ibge}")
    
    try:
        # 1. Tentar CNES - Estabelecimentos
        async with aiohttp.ClientSession() as session:
            url = f"https://apidadosabertos.saude.gov.br/cnes/estabelecimentos"
            params = {"codigo_ibge": codigo_ibge}
            
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    
                    # Parse response
                    hospitais = data.get('estabelecimentos', [])
                    hospitais_count = len([h for h in hospitais if h['tipo'] == 'HOSPITAL'])
                    
                    populacao = await get_ibge_population(codigo_ibge)
                    hospitais_por_100k = (hospitais_count / populacao) * 100000
                    
                    return {
                        "hospitais_por_100k": hospitais_por_100k,
                        "fonte": "API_REAL",
                        "timestamp": datetime.now()
                    }
    
    except Exception as e:
        logger.error(f"⚠️ DataSUS erro: {e}")
        
        # Fallback: Média nacional (13 hospitais / 100k)
        return {
            "hospitais_por_100k": 13.0,
            "fonte": "FALLBACK_NACIONAL",
            "timestamp": datetime.now()
        }
```

### Injection Points (topsis.py)
```python
# No inject_api_data_into_flat_list:
if "datasus" in external_data:
    flat[28] = external_data["datasus"].get("hospitais_por_100k", 0)
    flat[29] = external_data["datasus"].get("leitos_uti_pct", 0)
    flat[30] = external_data["datasus"].get("cobertura_vacina_covid_pct", 0)
    flat[31] = external_data["datasus"].get("cobertura_atencao_basica_pct", 0)
    flat[32] = external_data["datasus"].get("agentes_comunitarios_saude", 0)
```

### Timeline
- [ ] Investigar endpoints DataSUS: 1 dia
- [ ] Implementar módulo: 1 dia
- [ ] Testar + fallbacks: 0.5 dias

---

## 4. TAREFA 3: EXPANDIR PORTAL TRANSPARÊNCIA PARA PROGRAMAS SOCIAIS

### Objetivo
Integrar Portal da Transparência para indicadores de programas sociais (Bolsa Família, etc).

### Indicadores-Alvo (Indices 9-14)
- [9] bolsa_familia_beneficiarios_pct
- [10] seguro_desemprego_beneficiarios_pct
- [11] abono_salarial_beneficiarios_pct
- [12] gastos_sociais_per_capita
- [13] pessoas_atendidas_programas_pct
- [14] taxa_participacao_programas_pct

### API: Portal da Transparência
```
GET https://api.portaldatransparencia.gov.br/api-de-dados/beneficiarios/v1
  ?municipio={codigo_ibge}&programa=BOLSA_FAMILIA
```

### Implementation (backend/app/services/transparencia_api_expanded.py)

```python
async def get_transparencia_social(codigo_ibge: str):
    """Dados de programas sociais do Portal da Transparência"""
    
    # Buscar beneficiários de Bolsa Família
    bf_response = await fetch_portal_api(
        endpoint="beneficiarios",
        municipio=codigo_ibge,
        programa="BOLSA_FAMILIA"
    )
    
    populacao = await get_ibge_population(codigo_ibge)
    
    if bf_response:
        bf_count = bf_response['total_beneficiarios']
        bf_pct = (bf_count / populacao) * 100
        
        return {
            "bolsa_familia_pct": bf_pct,
            "fonte": "API_REAL",
            ...
        }
    else:
        return {
            "bolsa_familia_pct": 3.2,  # Fallback nacional ~3.2%
            "fonte": "FALLBACK_NACIONAL",
            ...
        }
```

### Timeline
- [ ] Testar Portal API: 1 dia
- [ ] Implementar módulo: 1 dia

---

## 5. TAREFA 4: TESTES + VALIDAÇÃO

### Test Plan
```python
# tests/test_phase2.py

def test_admin_panel_crud():
    """Validar criação/edição/exclusão de dados manuais"""
    pass

def test_datasus_health_expansion():
    """Validar injeção de dados de saúde"""
    pass

def test_transparencia_social():
    """Validar injeção de programas sociais"""
    pass

def test_total_coverage():
    """Validar cobertura pós-Phase 2 (target 25-30%)"""
    pass
```

### Validation Checklist
- [ ] Todas cidades recebem 13-16 indicadores (vs 8 atualmente)
- [ ] Não há erros 502
- [ ] Fallbacks acionam corretamente quando API falha
- [ ] Cache-inteligente persiste dados
- [ ] Admin Panel salva corretamente

---

## 6. DEPENDENCIES E IMPORTS A ADICIONAR

```python
# backend/app/services/external_apis.py

from app.services.datasus_api_expanded import get_datasus_health
from app.services.transparencia_api_expanded import get_transparencia_social_expanded

# Atualizar get_all_external_data():
datasus = await get_datasus_health(codigo_ibge)
social = await get_transparencia_social_expanded(codigo_ibge)
```

---

## 7. MÉTRICAS DE SUCESSO

| Métrica | Atual | Target Phase 2 |
|---------|-------|-----------------|
| Indicadores Reais | 8/50 (16%) | 13-16/50 (26-32%) |
| APIs Operacionais | 3 (SICONFI, TSE, INEP) | 5+ (+ DataSUS, Transparência) |
| Admin Panel | ❌ Não existe | ✅ Completo |
| Testes | 52 (100% PASS) | 60+ (100% PASS) |
| Error Rate 502 | 0% | 0% |

---

## 8. PRÓXIMAS ETAPAS APÓS PHASE 2

### Phase 3: SSP + Complementos
- SSP/Polícia (criminalidade)
- Painel Admin avançado (auditoria)
- Dashboard (rankings visualizados)

### Phase 4: Finalizações
- Web scraping (infraestrutura)
- Protocolos municipais
- Deploy produção

---

**Documento criado:** 30/04/2026  
**Status:** Pronto para implementação  
**Responsável:** Próxima iteração
