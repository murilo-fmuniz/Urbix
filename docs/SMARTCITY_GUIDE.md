# SmartCityDashboard - Guia de Integração

## 📋 Visão Geral

O componente **SmartCityDashboard.jsx** é um painel administrativo senior-level que gerencia dados de 3 cidades (Apucarana, Londrina, Maringá) estruturados segundo as normas ISO 37120, 37122 e 37123.

### ✨ Funcionalidades Principais

- ✅ **Seleção Dupla de Contexto**: Barra lateral para alternar cidades + abas internas por norma ISO
- ✅ **Validação em Tempo Real**: Inputs com mascaração de números decimais
- ✅ **Integração REST**: POST para `http://localhost:8000/api/v1/topsis/ranking-hibrido`
- ✅ **Visualization de Resultados**: Tabela ranking com badges de performance
- ✅ **Responsividade**: Desktop, tablet e mobile (Tailwind CSS + Media Queries)
- ✅ **Acessibilidade**: Ícones lucide-react, descrições de campos, estados ARIA

---

## 🚀 Pré-requisitos

### Dependências npm Obrigatórias

```bash
npm install lucide-react
npm install -D tailwindcss postcss autoprefixer
```

Se ainda não tem Tailwind configurado:

```bash
npx tailwindcss init -p
```

### Verificar package.json

```json
{
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0",
    "lucide-react": "^0.400.0"
  },
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
```

---

## 📁 Estrutura de Arquivos

```
frontend/
├── src/
│   ├── components/
│   │   ├── SmartCityDashboard.jsx          ✨ NOVO
│   │   ├── SmartCityDashboard.css          ✨ NOVO
│   │   ├── Header.jsx
│   │   └── ...outros componentes
│   ├── pages/
│   │   ├── AdminPage.jsx                   📝 MODIFICAR
│   │   └── ...
│   ├── App.jsx                            📝 MODIFICAR
│   ├── main.jsx
│   └── styles/
│       └── global.css
├── tailwind.config.js
├── postcss.config.js
└── package.json
```

---

## 🔧 Passo 1: Importar no App.jsx

Edite [src/App.jsx](../App.jsx) e adicione a rota:

```jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SmartCityDashboard from './components/SmartCityDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<SmartCityDashboard />} />
        {/* outras rotas */}
      </Routes>
    </Router>
  );
}

export default App;
```

---

## 🔧 Passo 2: Importar no AdminPage.jsx (Alternativa)

Se preferir como uma aba dentro da AdminPage:

```jsx
import SmartCityDashboard from '../components/SmartCityDashboard';
import SmartCityDashboard from '../components/SmartCityDashboard.css';

export default function AdminPage() {
  const [tabActive, setTabActive] = useState('dashboard');

  return (
    <div>
      {/* Tabs */}
      <div className="flex gap-4 border-b">
        <button
          onClick={() => setTabActive('dashboard')}
          className={tabActive === 'dashboard' ? 'font-bold border-b-2 border-blue-600' : ''}
        >
          Dashboard Smart City
        </button>
      </div>

      {/* Content */}
      <div className="mt-6">
        {tabActive === 'dashboard' && <SmartCityDashboard />}
      </div>
    </div>
  );
}
```

---

## 🎨 Passo 3: Configurar Tailwind CSS

### tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'in': 'slideUpIn 0.5s ease-out',
      },
      keyframes: {
        slideUpIn: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
```

### postcss.config.js

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

---

## 🌐 Passo 4: Verificar Backend

### Endpoint Esperado

```
POST http://localhost:8000/api/v1/topsis/ranking-hibrido
```

### Payload Esperado

```json
{
  "cidades": [
    {
      "codigo_ibge": "4101408",
      "nome": "Apucarana",
      "iso_37120": {
        "taxa_desemprego_pct": 5.2,
        "homicidios_por_100k": 12.5,
        "populacao_moradia_inadequada_pct": 8.3,
        "expectativa_vida_anos": 76.5,
        "taxa_mortalidade_infantil_por_1000": 15.2
      },
      "iso_37122": {
        "servicos_urbanos_online_pct": 65.0,
        "semaforos_inteligentes_pct": 45.0,
        "iluminacao_publica_led_pct": 72.0,
        "coleta_dados_sensores_pct": 38.5
      },
      "iso_37123": {
        "mortalidade_desastres_por_100k": 2.1,
        "populacao_treinada_emergencia_pct": 22.0,
        "planos_reducao_risco_desastres": 3,
        "infraestrutura_resiliente_pct": 55.5
      }
    },
    // ... Londrina e Maringá
  ]
}
```

### Response Esperado

```json
{
  "ranking": [
    {
      "codigo_ibge": "4113700",
      "nome": "Londrina",
      "score": 0.7845
    },
    {
      "codigo_ibge": "4115200",
      "nome": "Maringá",
      "score": 0.6532
    },
    {
      "codigo_ibge": "4101408",
      "nome": "Apucarana",
      "score": 0.5123
    }
  ],
  "indicadores": {
    "indice_smart": 0.6500
  }
}
```

---

## ▶️ Passo 5: Testar

### 1. Iniciar Backend

```bash
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

### 2. Iniciar Frontend

```bash
cd frontend
npm run dev
```

### 3. Acessar Dashboard

```
http://localhost:5173/dashboard
```

---

## 🎯 Fluxo do Usuário

```
┌─────────────────────────────────────────────┐
│  1. SELECIONAR CIDADE (Sidebar)             │
│     └─> Apucarana / Londrina / Maringá     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. SELECIONAR ABA (Tabs)                   │
│     └─> ISO 37120 / 37122 / 37123          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. PREENCHER INPUTS                        │
│     └─> Números decimais com validação     │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. CLICAR "CALCULAR RANKING"               │
│     └─> POST para /ranking-hibrido         │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  5. VISUALIZAR RESULTADOS                   │
│     └─> Tabela com Scores TOPSIS            │
│     └─> Índice Smart City (4 decimais)      │
└─────────────────────────────────────────────┘
```

---

## 📊 Estados do Componente

### State Management

| Estado | Tipo | Descrição |
|--------|------|-----------|
| `citiesData` | Array | Array de 3 cidades com dados ISO |
| `selectedCityIndex` | Number | Índice da cidade selecionada (0-2) |
| `selectedTabId` | String | ID da aba: 'iso_37120' \| 'iso_37122' \| 'iso_37123' |
| `loading` | Boolean | Status de envio para API |
| `error` | String \| null | Mensagem de erro |
| `results` | Object \| null | Response do backend (ranking + índices) |
| `submitSuccess` | Boolean | Flag para exibir alert de sucesso |

### Estrutura de City Data

```javascript
{
  codigo_ibge: String,      // IBGE code único
  nome: String,             // Nome da cidade
  estado: String,           // UF (PR, SP, etc)
  iso_37120: Object,        // Qualidade de Vida
  iso_37122: Object,        // Smart City
  iso_37123: Object,        // Resiliência
}
```

---

## 🛠️ Customização

### Adicionar Mais Cidades

Edit `INITIAL_CITIES` no componente:

```jsx
const INITIAL_CITIES = [
  // ... cidades existentes
  {
    codigo_ibge: '3301702', // Rio de Janeiro
    nome: 'Rio de Janeiro',
    estado: 'RJ',
    iso_37120: { /* ... */ },
    iso_37122: { /* ... */ },
    iso_37123: { /* ... */ },
  },
];
```

### Alterar Cores

As cores estão nos arrays `TABS`:

```jsx
const TABS = [
  {
    id: 'iso_37120',
    color: 'from-red-500 to-red-600', // Mudar aqui
    // ...
  },
];
```

### Modificar Campos de Uma Norma

Edit `FIELD_DESCRIPTIONS`:

```jsx
const FIELD_DESCRIPTIONS = {
  iso_37120: {
    novo_campo: {
      label: 'Novo Campo',
      unit: '%',
      placeholder: 'Ex: 10',
      help: 'Descrição do novo campo',
    },
  },
};
```

---

## 🐛 Troubleshooting

### Erro: "lucide-react not found"

```bash
npm install lucide-react@latest
```

### Erro: "Tailwind classes not applied"

1. Verifique se `tailwind.config.js` está correto
2. Certifique-se de que `node_modules/.vite` está limpo: `rm -rf node_modules && npm install`
3. Restart dev server

### Erro: "POST http://localhost:8000 CORS"

Adicione CORS no backend (`main.py`):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Erro: "Cannot read property 'map' of undefined"

Verifique se o backend retorna `results.ranking` como array:

```jsx
console.log('Response:', results);
// Deve ter: { ranking: [...], indicadores: {...} }
```

---

## 📱 Responsividade

| Breakpoint | Comportamento |
|------------|---------------|
| **Desktop** (≥1024px) | 4-col layout: Sidebar + 3-col content |
| **Tablet** (768px-1023px) | 2-col layout com sidebar ajustada |
| **Mobile** (<768px) | 1-col layout, tabs com scroll horizontal |

---

## ♿ Acessibilidade

- ✅ Ícones com labels textuais
- ✅ Inputs com `htmlFor` nas labels
- ✅ Estados disabled explícitos
- ✅ Cores WCAG AA compliant
- ✅ Texto descritivo para cada campo
- ✅ Animações respeitam `prefers-reduced-motion`

---

## 📦 Performance

- **Bundle Size**: ~45KB gzipped (React + Lucide + Tailwind)
- **API Calls**: 1 POST por submit
- **Render Optimization**: useMemo + useCallback para evitar re-renders desnecessários
- **CSS**: Tailwind purge remove classes não utilizadas

---

## 🔐 Validações

| Campo | Min | Max | Validação |
|-------|-----|-----|-----------|
| `taxa_desemprego_pct` | 0 | 100 | Valor decimal |
| `homicidios_por_100k` | 0 | ∞ | Valor decimal |
| `expectativa_vida_anos` | 0 | 150 | Valor decimal |
| Todos os campos | - | - | `step="0.1"` (1 decimal mín) |

---

## 🔄 Próximos Passos (Roadmap)

- [ ] Adicionar persistência local (localStorage)
- [ ] Implementar export para CSV/PDF
- [ ] Adicionar gráficos com Chart.js
- [ ] Suporte para múltiplos períodos históricos
- [ ] Dark mode toggle
- [ ] Undo/redo para edições
- [ ] Comparação lado-a-lado de cidades

---

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique o console do navegador (F12 → Console)
2. Verifique o terminal backend (erros de validação)
3. Valide o payload com Postman antes de integrar

---

**Criado com ❤️ por GitHub Copilot - Senior Frontend Engineer**
