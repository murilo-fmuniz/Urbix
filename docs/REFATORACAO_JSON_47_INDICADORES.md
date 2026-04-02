# Refatoração: Suporte a 47 Indicadores com Colunas JSON

**Data**: 31 de março de 2026  
**Status**: ✅ Completo  
**Objetivo**: Preparar o sistema para suportar 47 indicadores ISO dinamicamente via JSON, facilitando migração futura para PostgreSQL

---

## 📋 Resumo Executivo

A refatoração transforma o banco de dados de um modelo com colunas específicas para um modelo **flexible JSON** que suporta 47 indicadores (16 ISO 37120 + 15 ISO 37122 + 16 ISO 37123 + Sendai) de forma dinâmica.

**Benefícios:**
- ✅ Escalabilidade horizontal (fácil adicionar mais indicadores)
- ✅ Flexibilidade de schema (não precisa migração BD a cada mudança)
- ✅ Compatibilidade com PostgreSQL JSONB (melhor performance)
- ✅ Mantém auditoria completa via histórico

---

## 🔄 Arquivos Modificados

### 1. **app/models.py** - Modelo de Dados

#### Antes: Colunas Específicas

```python
class CityManualData(Base):
    __tablename__ = "city_manual_data"
    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(String, unique=True, index=True, nullable=False)
    nome_cidade = Column(String, nullable=True)
    
    # ❌ Apenas 4 indicadores específicos
    pontos_iluminacao_telegestao = Column(Float, default=0.0)
    medidores_inteligentes_energia = Column(Float, default=0.0)
    bombeiros_por_100k = Column(Float, default=0.0)
    area_verde_mapeada = Column(Float, default=0.0)
```

#### Depois: Coluna JSON Dinâmica

```python
class CityManualData(Base):
    __tablename__ = "city_manual_data"
    id = Column(Integer, primary_key=True, index=True)
    codigo_ibge = Column(String, unique=True, index=True, nullable=False)
    nome_cidade = Column(String, nullable=True)
    
    # ✅ 47 indicadores em JSON estruturado
    # Formato: {"iso_37120": {...}, "iso_37122": {...}, "iso_37123": {...}}
    indicadores_manuais = Column(JSON, default=dict)
```

**Mudanças em IndicatorSnapshot:**

```python
# ❌ Antes: 10 colunas específicas
taxa_endividamento = Column(Float)
despesas_capital_percentual = Column(Float)
# ... 8 mais

# ✅ Depois: 1 coluna JSON
valores_indicadores = Column(JSON, nullable=False)
# Lista de 47 floats: [taxa_desemprego, taxa_endividamento, ..., danos_infraestrutura]
```

---

### 2. **app/schemas.py** - Schemas Pydantic

#### Schema de Atualização (CityManualDataUpdate)

```python
# ❌ Antes: 4 campos Float específicos
class CityManualDataUpdate(BaseModel):
    pontos_iluminacao_telegestao: Optional[float] = None
    medidores_inteligentes_energia: Optional[float] = None
    bombeiros_por_100k: Optional[float] = None
    area_verde_mapeada: Optional[float] = None
    usuario_atualizou: Optional[str] = None

# ✅ Depois: Schema estruturado para 47 indicadores
class CityManualDataUpdate(BaseModel):
    dados: Optional[ManualCityIndicators] = None  # 47 indicadores estruturados
    usuario_atualizou: Optional[str] = None
    motivo_atualizacao: Optional[str] = None
```

#### Schema de Response (CityManualDataResponse)

```python
# ❌ Antes
class CityManualDataResponse(BaseModel):
    id: int
    codigo_ibge: str
    nome_cidade: Optional[str]
    pontos_iluminacao_telegestao: float
    medidores_inteligentes_energia: float
    bombeiros_por_100k: float
    area_verde_mapeada: float
    # ...

# ✅ Depois
class CityManualDataResponse(BaseModel):
    id: int
    codigo_ibge: str
    nome_cidade: Optional[str]
    indicadores_manuais: dict  # 47 indicadores estruturados em JSON
    fonte: str
    usuario_atualizou: Optional[str]
    data_criacao: datetime
    data_atualizacao: datetime
```

#### Schema de IndicatorSnapshot

```python
# ❌ Antes: 10 campos de indicadores
class IndicatorSnapshotResponse(BaseModel):
    id: int
    codigo_ibge: str
    taxa_endividamento: float
    despesas_capital_percentual: float
    # ... 8 mais
    data_calculo: datetime

# ✅ Depois: JSON dinâmico
class IndicatorSnapshotResponse(BaseModel):
    id: int
    codigo_ibge: str
    valores_indicadores: dict  # 47 indicadores como lista em JSON
    data_calculo: datetime
    fonte_dados: str
    periodo_referencia: str
```

---

### 3. **app/routers/manual_data.py** - Endpoints

#### POST - Criar/Atualizar Dados Manuais

**Antes:**
```python
# Extrair 4 valores específicos
novo_iluminacao = dados_dict.get("pontos_iluminacao_telegestao", 0.0)
novo_medidores = dados_dict.get("medidores_inteligentes_energia", 0.0)
novo_bombeiros = dados_dict.get("bombeiros_por_100k", 0.0)
novo_verde = dados_dict.get("area_verde_mapeada", 0.0)

# Criar registro com 4 colunas
novo = CityManualData(
    codigo_ibge=codigo_ibge,
    pontos_iluminacao_telegestao=novo_iluminacao,
    medidores_inteligentes_energia=novo_medidores,
    bombeiros_por_100k=novo_bombeiros,
    area_verde_mapeada=novo_verde,
)
```

**Depois:**
```python
# Converter ManualCityIndicators (47 indicadores) para dict
indicadores_dict = data.dados.model_dump() if data.dados else {}

# Criar registro com JSON (suporta 47 indicadores)
novo = CityManualData(
    codigo_ibge=codigo_ibge,
    indicadores_manuais=indicadores_dict,  # 47 indicadores em JSON
    usuario_atualizou=data.usuario_atualizou,
    fonte="prefeitura",
)
```

#### PATCH - Atualização Parcial

**Antes:**
```python
# Atualizar apenas colunas específicas
existing.pontos_iluminacao_telegestao = novo_iluminacao
existing.medidores_inteligentes_energia = novo_medidores
existing.bombeiros_por_100k = novo_bombeiros
existing.area_verde_mapeada = novo_verde
```

**Depois:**
```python
# Fazer merge dinâmico no JSON
if data.dados:
    novos_indicadores = data.dados.model_dump()
    dados_novos = {**dados_antigos, **novos_indicadores}
    dados.indicadores_manuais = dados_novos
```

---

## 🏗️ Estrutura de Dados JSON

### Exemplo: Indicadores Manuais de Uma Cidade

```json
{
  "iso_37120": {
    "taxa_desemprego_pct": 5.2,
    "taxa_endividamento_pct": 15.3,
    "despesas_capital_pct": 22.1,
    "receita_propria_pct": 45.8,
    "orcamento_per_capita": 1250.50,
    "mulheres_eleitas_pct": 30.0,
    "condenacoes_corrupcao_100k": 2.1,
    "participacao_eleitoral_pct": 78.5,
    "moradias_inadequadas_pct": 12.3,
    "sem_teto_100k": 8.5,
    "bombeiros_100k": 25.3,
    "mortes_incendio_100k": 1.2,
    "agentes_policia_100k": 150.0,
    "homicidios_100k": 18.5,
    "acidentes_industriais_100k": 0.8
  },
  "iso_37122": {
    "sobrevivencia_novos_negocios_100k": 45.2,
    "empregos_tic_pct": 8.5,
    "graduados_stem_100k": 120.3,
    "energia_residuos_pct": 5.1,
    "iluminacao_telegestao_pct": 35.0,
    "medidores_inteligentes_energia_pct": 42.0,
    "edificios_verdes_pct": 18.5,
    "monitoramento_ar_tempo_real_pct": 65.0,
    "servicos_urbanos_online_pct": 75.0,
    "prontuario_eletronico_pct": 55.2,
    "consultas_remotas_100k": 280.5,
    "medidores_inteligentes_agua_pct": 38.5,
    "areas_cobertas_cameras_pct": 45.0,
    "lixeiras_sensores_pct": 12.0,
    "semaforos_inteligentes_pct": 28.5,
    "frota_onibus_limpos_pct": 5.0
  },
  "iso_37123": {
    "seguro_ameacas_pct": 32.0,
    "empregos_informais_pct": 35.2,
    "escolas_preparacao_emergencia_pct": 68.0,
    "populacao_treinada_emergencia_pct": 42.5,
    "hospitais_geradores_backup_pct": 85.0,
    "seguro_saude_basico_pct": 78.5,
    "imunizacao_pct": 92.3,
    "abrigos_emergencia_100k": 15.2,
    "edificios_vulneraveis_pct": 8.5,
    "rotas_evacuacao_100k": 22.3,
    "reservas_alimentos_72h_pct": 45.0,
    "mapas_ameacas_publicos_pct": 65.0,
    "mortalidade_desastres_100k": 0.5,
    "pessoas_afetadas_desastres_100k": 12.3,
    "perdas_desastres_pct_pib": 0.25,
    "danos_infraestrutura_basica_pct": 5.0
  }
}
```

### Exemplo: Snapshot de Indicadores (Lista de 47 Floats)

```json
{
  "valores_indicadores": [
    5.2, 15.3, 22.1, 45.8, 1250.50,       // ISO 37120: 5
    30.0, 2.1, 78.5, 12.3, 8.5,           // ISO 37120: +5 = 10
    25.3, 1.2, 150.0, 18.5, 0.8,          // ISO 37120: +5 = 15
    0.0,                                   // ISO 37120: +1 = 16
    45.2, 8.5, 120.3, 5.1, 35.0,          // ISO 37122: 5
    42.0, 18.5, 65.0, 75.0, 55.2,         // ISO 37122: +5 = 10
    280.5, 38.5, 45.0, 12.0, 28.5,        // ISO 37122: +5 = 15
    5.0,                                   // ISO 37122: +1 = 16
    32.0, 35.2, 68.0, 42.5, 85.0,         // ISO 37123: 5
    78.5, 92.3, 15.2, 8.5, 22.3,          // ISO 37123: +5 = 10
    45.0, 65.0, 0.5, 12.3, 0.25, 5.0      // ISO 37123: +6 = 16
  ]
}
```

---

## 📡 Exemplos de Requisições da API

### POST - Criar com 47 Indicadores

```bash
POST /api/manual-data/3509502

{
  "nome_cidade": "Apucarana",
  "usuario_atualizou": "admin@example.com",
  "dados": {
    "iso_37120": {
      "taxa_desemprego_pct": 5.2,
      "taxa_endividamento_pct": 15.3,
      // ... 14 mais
    },
    "iso_37122": {
      "sobrevivencia_novos_negocios_100k": 45.2,
      // ... 14 mais
    },
    "iso_37123": {
      "seguro_ameacas_pct": 32.0,
      // ... 15 mais
    }
  }
}
```

**Response:**
```json
{
  "id": 1,
  "codigo_ibge": "3509502",
  "nome_cidade": "Apucarana",
  "indicadores_manuais": {
    "iso_37120": { ... },
    "iso_37122": { ... },
    "iso_37123": { ... }
  },
  "fonte": "prefeitura",
  "usuario_atualizou": "admin@example.com",
  "data_criacao": "2026-03-31T10:30:00",
  "data_atualizacao": "2026-03-31T10:30:00"
}
```

### PATCH - Atualizzar Alguns Indicadores

```bash
PATCH /api/manual-data/3509502

{
  "dados": {
    "iso_37120": {
      "taxa_desemprego_pct": 4.8  // Apenas este será atualizado
    }
  },
  "usuario_atualizou": "admin@example.com",
  "motivo_atualizacao": "Correção de dado"
}
```

---

## 🔐 Auditoria e Histórico

### CityManualDataHistory - Mudanças Rastreadas

```python
class CityManualDataHistory(Base):
    id: int
    codigo_ibge: str
    dados_antigos: dict  # Snapshot anterior completo
    dados_novos: dict    # Snapshot novo completo
    alteracoes_resumo: str  # "taxa_desemprego: 5.2 → 4.8 | ..."
    usuario_atualizou: str
    motivo_atualizacao: str
    data_alteracao: datetime
```

**Exemplo de Histórico:**
```json
{
  "id": 1,
  "codigo_ibge": "3509502",
  "dados_antigos": {
    "iso_37120": {
      "taxa_desemprego_pct": 5.2,
      "taxa_endividamento_pct": 15.3
    }
  },
  "dados_novos": {
    "iso_37120": {
      "taxa_desemprego_pct": 4.8,
      "taxa_endividamento_pct": 15.3
    }
  },
  "alteracoes_resumo": "taxa_desemprego_pct: 5.2 → 4.8",
  "usuario_atualizou": "admin@example.com",
  "motivo_atualizacao": "Correção de dado",
  "data_alteracao": "2026-03-31T11:00:00"
}
```

---

## ✅ Checklist de Migração

### Fase 1: Refatoração Completa (✅ FEITO)

- [x] Atualizar models.py com colunas JSON
- [x] Atualizar schemas.py com ManualCityIndicators
- [x] Refatorar rotas POST e PATCH
- [x] Manter auditoria de histórico
- [x] Documentação técnica

### Fase 2: Testes (PRÓXIMO)

- [ ] Testar POST com 47 indicadores
- [ ] Testar PATCH com atualização parcial
- [ ] Testar GET histórico
- [ ] Testar serialização/deserialização JSON
- [ ] Testes unitários completos

### Fase 3: Migração de Dados (FUTURO)

- [ ] Backup do banco SQLite
- [ ] Script de migração: SQLite → JSON format
- [ ] Validação de dados após migração
- [ ] Testes de integração
- [ ] Rollback plan (se necessário)

### Fase 4: PostgreSQL (FUTURO)

- [ ] Criar schema no PostgreSQL com JSONB
- [ ] Testar performance JSONB vs JSON (SQLite)
- [ ] Atualizar driver de banco de dados
- [ ] Testes de carga
- [ ] Migração em produção

---

## 📊 Comparação: Antes vs Depois

| Aspecto | Antes | Depois |
|---------|-------|--------|
| **Indicadores Suportados** | 4 (hardcoded) | 47 (dinâmico) |
| **Colunas do Banco** | 7 específicas | 1 JSON |
| **Flexibilidade** | Baixa (requer ALTER TABLE) | Alta (apenas dados) |
| **PostgreSQL Optimization** | ❌ Não | ✅ JSONB-ready |
| **Escalabilidade** | Limitada | Ilimitada |
| **Migração BD** | Complexa | Transparente |
| **Size (bytes/registro)** | ~60 bytes | ~2KB (mas flexível) |

---

## 🔧 Comandos Úteis

### Validar JSON após migração

```python
from app.models import CityManualData
from app.database import SessionLocal

db = SessionLocal()
city = db.query(CityManualData).filter_by(codigo_ibge="3509502").first()

# Verificar estrutura
print(city.indicadores_manuais)
print(len(city.indicadores_manuais.get("iso_37120", {})))  # Deve ser 16

# Verificar valor específico
valor = city.indicadores_manuais["iso_37120"]["taxa_desemprego_pct"]
print(f"Taxa Desemprego: {valor}%")
```

### Query histórico via SQL (SQLite)

```sql
SELECT 
    codigo_ibge,
    alteracoes_resumo,
    usuario_atualizou,
    data_alteracao
FROM city_manual_data_history
WHERE codigo_ibge = '3509502'
ORDER BY data_alteracao DESC
LIMIT 10;
```

### Query com JSONB (PostgreSQL - futuro)

```sql
SELECT 
    codigo_ibge,
    indicadores_manuais -> 'iso_37120' ->> 'taxa_desemprego_pct' as taxa_desemprego,
    data_atualizacao
FROM city_manual_data
WHERE (indicadores_manuais -> 'iso_37120' ->> 'taxa_desemprego_pct')::float < 5.0;
```

---

## ⚠️ Breaking Changes

### Para Clientes da API

**Antes:**
```json
{
  "pontos_iluminacao_telegestao": 35.0,
  "medidores_inteligentes_energia": 42.0,
  "bombeiros_por_100k": 25.3,
  "area_verde_mapeada": 18.5
}
```

**Depois:**
```json
{
  "indicadores_manuais": {
    "iso_37120": { ... },
    "iso_37122": { ... },
    "iso_37123": { ... }
  }
}
```

### Mitigação

- ✅ Versão API antiga em `/api/v1/manual-data` (deprecated)
- ✅ Versão nova em `/api/v2/manual-data` (current)
- ✅ Período de transição: 3 meses (recomendado)

---

## 📚 Referências

- [ISO 37120 - Sustainable Cities and Communities](https://www.iso.org/standard/68498.html)
- [ISO 37122 - Smart Communities](https://www.iso.org/standard/69050.html)
- [ISO 37123 - Linked Data and Governance](https://www.iso.org/standard/71014.html)
- [PostgreSQL JSONB Performance](https://www.postgresql.org/docs/current/datatype-json.html)
- [SQLAlchemy JSON Column](https://docs.sqlalchemy.org/en/14/core/types.html#sqlalchemy.JSON)

---

## 🎯 Conclusão

A refatoração transforma o sistema de um modelo rígido para um modelo flexível baseado em JSON, preparando o Urbix para:

1. **Escalabilidade**: Suportar novos indicadores sem alterar schema
2. **Produção PostgreSQL**: Pronto para migração com otimização JSONB
3. **Auditoria Completa**: Histórico total de mudanças mantido
4. **Flexibilidade**: Permite campos opcionais e estrutura dinâmica

**Status**: ✅ **Refatoração Completa e Testável**

---

**Versão**: 1.0  
**Data**: 31/03/2026  
**Autor**: DevOps Engineer (Senior)
