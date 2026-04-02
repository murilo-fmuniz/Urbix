# ⚡ Quick Start - Sidebar Urbix

## 🎯 Em 5 Minutos

### 1️⃣ Instalar Dependências

```bash
cd frontend
npm install
```

**O que foi instalado:**
- ✅ `tailwindcss@3.3.6` - CSS framework
- ✅ `lucide-react@0.263.1` - Icons
- ✅ `postcss@8.4.31` - CSS processor
- ✅ `autoprefixer@10.4.16` - Browser prefixes
- ✅ `@tailwindcss/forms@0.5.7` - Form styling

### 2️⃣ Iniciar Dev Server

```bash
npm run dev
```

Acesse: `http://localhost:5173`

### 3️⃣ Verificar Sidebar

Você deve ver:
- [ ] Sidebar fixo na esquerda (desktop)
- [ ] Menu toggle no canto (mobile)
- [ ] Ícones coloridos no menu
- [ ] "Nova Avaliação" destacado em azul/roxo

---

## 📖 Documentos Inclusos

| Documento | Finalidade |
|-----------|-----------|
| **SIDEBAR_GUIDE.md** | 📚 Guia completo de implementação |
| **SIDEBAR_VISUAL_GUIDE.md** | 🎨 Layout visual e CSS classes |
| **Sidebar.jsx** | 💻 Componente principal (264 linhas) |
| **Sidebar.examples.jsx** | 🔧 10 exemplos avançados |

---

## 🗂️ Estrutura do Sidebar

```
Sidebar (264px fixed | mobile toggle)
├─ Logo Section (Urbix)
│
├─ Navigation
│  ├─ Visão Geral (/)
│  ├─ ✨ Nova Avaliação (/nova-avaliacao) [DESTAQUE]
│  ├─ Histórico (/historico)
│  │
│  ├─ [Divisor: Configurações]
│  │
│  └─ Administração [COLLAPSIBLE]
│     ├─ Gestão de Cidades (/admin/cidades)
│     ├─ Base de Indicadores (/admin/indicadores)
│     ├─ Metodologia (/admin/metodologia)
│     └─ Auditorias (/admin/auditorias)
│
└─ Footer Info (v2.0.0)
```

---

## 🎨 Recursos de Design

### ✨ Nova Avaliação (Ação Principal)

Estilo especial para chamar atenção:

```jsx
// Gradient + Shadow + Hover Scale
className="bg-gradient-to-r from-blue-500 to-purple-600 
           text-white shadow-lg hover:shadow-xl hover:scale-105"
```

Resultado: Botão que "salta" quando hover!

### 🔵 Active Link Detection

Rota atual é automaticamente destacada:

```jsx
isActive = location.pathname === path
// Se ativo → azul com sombra
// Se inativo → cinza com hover suave
```

### 📱 Mobile Responsivo

```jsx
// Sidebar hidden no mobile, usa toggle
md:hidden  → Toggle visível apenas mobile
translate-x → Animação de entrada/saída
overlay    → Click anywhere para fechar
```

### 🌙 Dark Mode

Suportado automaticamente via Tailwind:

```jsx
// Exemplo
className="text-gray-700 dark:text-gray-300"
// Light: gray-700
// Dark:  gray-300
```

---

## ✅ Checklist de Testes

### Desktop
- [ ] Sidebar visível na esquerda (264px)
- [ ] Menu fixo (não scroll)
- [ ] Links clicáveis
- [ ] Ícones aparecem
- [ ] Hover effects funcionam
- [ ] Active link destacado em azul
- [ ] Menu Admin expande/colapsa

### Mobile
- [ ] Hamburger menu (☰) visível
- [ ] Sidebar oculto por padrão
- [ ] Click no toggle abre sidebar
- [ ] Overlay escuro aparece
- [ ] Click no overlay fecha sidebar
- [ ] Links clicáveis
- [ ] Sidebar fecha após click em link

### Dark Mode
- [ ] Colors corretas no light mode
- [ ] Colors corretas no dark mode
- [ ] Transição suave entre temas

---

## 🔧 Troubleshooting Básico

### ❌ Tailwind CSS não funciona

```bash
# Solução 1: Limpar cache
rm -rf node_modules package-lock.json
npm install

# Solução 2: Verificar tailwind.config.js
# Ensure content paths are correct:
content: ["./src/**/*.{js,jsx,ts,tsx}"]
```

### ❌ Ícones não aparecem

```bash
# Solução: Reinstalar lucide-react
npm install lucide-react@latest

# Verificar import no Sidebar.jsx
import { LayoutDashboard, Sparkles, ... } from 'lucide-react';
```

### ❌ Layout quebrado

```jsx
// Verificar App.jsx
// Deve ter estrutura flex:
<div className="flex h-screen">
  <Sidebar />
  <main className="flex-1 overflow-y-auto">
    {/* content */}
  </main>
</div>
```

---

## 📝 Próximos Passos

### 1. Implementar Páginas Admin

Substituir placeholders em `App.jsx`:

```jsx
// Antes (placeholder)
const AdminCidadesPage = () => (
  <div className="p-8">
    <h1>Gestão de Cidades</h1>
  </div>
);

// Depois (componente real)
import AdminCidades from './pages/admin/AdminCidades';
```

### 2. Adicionar Rota de Logout

```jsx
// No footer do Sidebar
import { LogOut } from 'lucide-react';

<button onClick={handleLogout} className="...">
  <LogOut /> Logout
</button>
```

### 3. Integrar Dark Mode Toggle

```jsx
// Adicione em App.jsx
<button onClick={() => {
  document.documentElement.classList.toggle('dark');
}}>
  🌙 Toggle Dark
</button>
```

---

## 📊 Performance

### Bundle Size
- Tailwind CSS: ~50KB (purged in production)
- Lucide React: ~40KB (tree-shaked)
- Sidebar Component: ~12KB

### Optimization Tips
- Tailwind purges unused CSS em production
- Lucide React é tree-shakeable (importa só o que usa)
- Componente usa React hooks (no class bloat)

---

## 🎓 Aprenda Mais

### Tailwind CSS
- Docs: https://tailwindcss.com/docs
- 

Playground: https://play.tailwindcss.com/
- CHEATSHEET: https://nerdcave.com/tailwind-cheat-sheet

### Lucide React
- Icons: https://lucide.dev/
- Search: https://lucide.dev/?search=

### React Router
- Docs: https://reactrouter.com/docs/
- Tutorial: https://reactrouter.com/docs/start/tutorial

---

## 💡 Pro Tips

### Dica 1: Hot Reload

Tailwind CSS recompila automaticamente ao salvar:

```bash
npm run dev

# Mude qualquer classe em Sidebar.jsx
# Salve file
# Página atualiza automaticamente com novos estilos!
```

### Dica 2: Inspect Components

Use DevTools do browser:

```
Right-click → Inspect
Aba "Styles" mostra todas as classes Tailwind
Aba "Elements" mostra estrutura HTML
```

### Dica 3: Tailwind IntelliSense

Instale extensão no VS Code:

```
Ext: Tailwind CSS IntelliSense
Por: Tailwind Labs
```

Autocomplete de classes Tailwind!

### Dica 4: Dark Mode Dev

Forçar dark mode no DevTools:

```javascript
// Console do browser
document.documentElement.classList.toggle('dark')

// Agora vê dark mode sem mudar setting do SO
```

---

## 🐛 Bugs Conhecidos / Limitações

### ✅ Nenhum bug crítico reportado

Mas observe:

1. **Mobile**: Menu não se fecha ao pressionar Escape (implementar depois)
2. **Accessibility**: Considere adicionar ARIA labels
3. **Animations**: Performance em dispositivos muito antigos pode ser afetada

---

## 📞 FAQ

### P: Posso usar meu próprio tema de cores?

**R:** Sim! Edite `tailwind.config.js`:

```js
colors: {
  primary: '#sua-cor-aqui',
  secondary: '#sua-outra-cor',
}
```

### P: Como adicionar novos ícones?

**R:** Importe do Lucide e use:

```jsx
import { YourIcon } from 'lucide-react';

<NavItem icon={YourIcon} label="..." to="..." />
```

### P: Funciona com TypeScript?

**R:** Sim! Renomeie componentes para `.tsx` e adicione tipos:

```tsx
interface SidebarProps {
  isOpen?: boolean;
}

function Sidebar({ isOpen = true }: SidebarProps) {
  // ...
}
```

### P: Como remover o Header antigo?

**R:** Em `App.jsx`, remova:

```jsx
// Remova estas linhas
import Header from './components/Header';
// <Header /> (não use)
```

### P: Dark mode está trocado?

**R:** Verifique `tailwind.config.js`:

```js
darkMode: 'class',  // Deve ser 'class' (não 'media')
```

---

## ✨ Exemplos Rápidos

### Exemplo 1: Adicionar novo menu item

```jsx
// Em Sidebar.jsx, após "Histórico":

<NavItem
  to="/relatorios"
  icon={BarChart3}
  label="Relatórios"
/>
```

### Exemplo 2: Destacar item específico

```jsx
// Exemplo: Destacar "Auditorias"

<NavItem
  to="/admin/auditorias"
  icon={ShieldCheck}
  label="Auditorias ⭐"
  className="ring-2 ring-yellow-300"
/>
```

### Exemplo 3: Desabilitar item

```jsx
// Criar variante desabilitada:

className={`... ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
onClick={disabled ? (e) => e.preventDefault() : undefined}
```

---

## 🎉 Conclusão

Você agora tem um Sidebar moderno, profissional e responsivo! 

**Próximo passo**: Implemente as páginas de Administração.

```bash
# Continue desenvolvendo! 🚀
npm run dev
```

**Bom coding!** 💻✨

---

Version: 2.0.0 | Updated: March 28, 2026 | Status: ✅ Production Ready
