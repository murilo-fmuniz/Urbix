# 🔧 FIX PARA TOPSIS - PROBLEMAS IDENTIFICADOS E SOLUÇÃO

## 🚨 PROBLEMA RAIZ

O frontend está enviando **4 indicadores** quando deveria enviar **47**.

```
❌ ANTES (Errado):
{
  "pontos_iluminacao_telegestao": 0,
  "medidores_inteligentes_energia": 0,
  "bombeiros_por_100k": 0,
  "area_verde_mapeada": 0
}

✅ DEPOIS (Correto):
{
  "iso_37120": { 16 campos },
  "iso_37122": { 15 campos },
  "iso_37123": { 16 campos }
}
```

---

## 📋 MUDANÇAS NECESSÁRIAS

### **1. SmartCityDashboard.jsx - Linhas 1-70: Imports e Estrutura Inicial**

**Substitua por:**

```javascript
import React, { useState, useCallback, useMemo } from 'react';
import {
  BarChart3, TrendingUp, AlertCircle, CheckCircle,
  Loader, ChevronDown, Home, Zap, Shield,
} from 'lucide-react';
import IndicatorsComparisonChart from './IndicatorsComparisonChart';
import { EMPTY_INDICATORS, FIELD_DESCRIPTIONS } from '../constants/indicadores';

// ✅ DADOS INICIAIS COM ESTRUTURA CORRETA (47 indicadores)
const INITIAL_CITIES = [
  {
    codigo_ibge: '4101408',
    nome: 'Apucarana',
    estado: 'PR',
    manual_indicators: JSON.parse(JSON.stringify(EMPTY_INDICATORS)),
  },
  {
    codigo_ibge: '4113700',
    nome: 'Londrina',
    estado: 'PR',
    manual_indicators: JSON.parse(JSON.stringify(EMPTY_INDICATORS)),
  },
];

// DEFINIÇÃO DAS ABAS
const TABS = [
  {
    id: 'iso_37120',
    label: 'Boas Práticas Urbanas (ISO 37120)',
    icon: Home,
    color: 'from-blue-500 to-blue-600',
    description: '16 indicadores de qualidade de vida',
  },
  {
    id: 'iso_37122',
    label: 'Cidades Inteligentes (ISO 37122)',
    icon: Zap,
    color: 'from-amber-500 to-orange-600',
    description: '15 indicadores de smart cities',
  },
  {
    id: 'iso_37123',
    label: 'Resiliência e Desastres (ISO+Sendai)',
    icon: Shield,
    color: 'from-red-500 to-rose-600',
    description: '16 indicadores de resiliência',
  },
];
```

### **2. SmartCityDashboard.jsx - Linhas 280-310: Construir Payload Correto**

**Encontre a seção `const payload = citiesData.filter...`**

**Substitua por:**

```javascript
// ✅ PAYLOAD CORRETO - COM 47 INDICADORES ESTRUTURADOS
const payload = citiesData
  .filter((city) => city.codigo_ibge && city.nome)
  .map((city) => ({
    codigo_ibge: city.codigo_ibge,
    nome_cidade: city.nome,
    manual_indicators: city.manual_indicators || EMPTY_INDICATORS,
  }));
```

### **3. SmartCityDashboard.jsx - Linha 250: Atualizar handleInputChange**

**Encontre:**
```javascript
const handleInputChange = useCallback((fieldKey, value) => {
  setCitiesData((prev) => {
    const updated = [...prev];
    const city = updated[selectedCityIndex];
    
    if (city && city[selectedTabId]) {
      city[selectedTabId][fieldKey] = ...
```

**Substitua por:**
```javascript
const handleInputChange = useCallback((fieldKey, value) => {
  setCitiesData((prev) => {
    const updated = [...prev];
    const city = updated[selectedCityIndex];
    
    // ✅ Acessa manual_indicators[iso_xxxxx][field]
    if (city?.manual_indicators?.[selectedTabId]) {
      city.manual_indicators[selectedTabId][fieldKey] = 
        value === '' ? 0 : parseFloat(value) || 0;
    }
    return updated;
  });
}, [selectedCityIndex, selectedTabId]);
```

### **4. SmartCityDashboard.jsx - Linha 270: Atualizar selectedTabData**

**Encontre:**
```javascript
const selectedTabData = useMemo(() => {
  const city = citiesData[selectedCityIndex];
  if (!city || !city[selectedTabId]) return {};
  return city[selectedTabId];
}, [citiesData, selectedCityIndex, selectedTabId]);
```

**Substitua por:**
```javascript
const selectedTabData = useMemo(() => {
  const city = citiesData[selectedCityIndex];
  if (!city?.manual_indicators?.[selectedTabId]) return {};
  return city.manual_indicators[selectedTabId];
}, [citiesData, selectedCityIndex, selectedTabId]);
```

### **5. SmartCityDashboard.jsx - Linha 340: Atualizar handleAddCity**

**Encontre a função completa `handleAddCity`**

**Substitua por:**
```javascript
const handleAddCity = useCallback(() => {
  const newCity = {
    codigo_ibge: '',
    nome: '',
    estado: 'PR',
    manual_indicators: JSON.parse(JSON.stringify(EMPTY_INDICATORS)),
  };
  setCitiesData((prev) => [...prev, newCity]);
  setSelectedCityIndex(citiesData.length);
  setResults(null);
  setSelectedResultsTab('ranking');
}, [citiesData.length]);
```

### **6. SmartCityDashboard.jsx - Linha 395: Remover FIELD_DESCRIPTIONS Local**

**Encontre a definição gigante de `const FIELD_DESCRIPTIONS = { ... }`**

**Substitua simplesmente por:**
```javascript
// ✅ FIELD_DESCRIPTIONS agora vem do arquivo de constantes importado
// Remova toda a definição local - ela já está em ../constants/indicadores.js
```

---

## 🧪 TESTE APÓS MUDANÇAS

1. **Abra o navegador e navegue para AdminPage/SmartCityDashboard**
2. **Preencha alguns indicadores** (mínimo 1-2 valores por aba par cidade)
3. **Click "Calcular Ranking TOPSIS"**
4. **Verifique no console:**
   - `📤 Enviando payload:` deve mostrar 47 indicadores estruturados
   ```json
   {
     "iso_37120": { 
       "taxa_desemprego_pct": 5.2,
       "taxa_endividamento_pct": 15.0,
       // ... 14 mais
     },
     "iso_37122": { ... 15 campos ... },
     "iso_37123": { ... 16 campos ... }
   }
   ```
5. **Resultado esperado:** Índices Smart devem ser **> 0** e diferentes entre cidades

---

## ✅ CHECKLIST DE VALIDAÇÃO

- [ ] `EMPTY_INDICATORS` importado de `../constants/indicadores`
- [ ] `FIELD_DESCRIPTIONS` importado de `../constants/indicadores`
- [ ] `INITIAL_CITIES` usa `manual_indicators` com estrutura ISO
- [ ] `handleInputChange` acessa `city.manual_indicators[selectedTabId]`
- [ ] `selectedTabData` retorna `city.manual_indicators[selectedTabId]`
- [ ] `handleAddCity` cria `manual_indicators` estruturado
- [ ] `payload` envia estrutura completa com `manual_indicators`
- [ ] Console mostra 47 campos no payload enviado
- [ ] Índice Smart retorna valores > 0

---

## 📊 ESPERADO PÓS-FIX

**Antes:**
```
API Response: 
  Apucarana: 0.00
  Londrina: 0.00
❌ Ambos zerados = indicadores não enviados
```

**Depois:**
```
API Response:
  Apucarana: 0.6234
  Londrina: 0.7891
✅ Valores distintos = TOPSIS funcionando
```

