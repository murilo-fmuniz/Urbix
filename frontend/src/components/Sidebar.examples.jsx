/**
 * Sidebar.jsx - Complemento - Exemplos Avançados
 * 
 * Este arquivo contém exemplos de como estender e personalizar o Sidebar
 * para diferentes casos de uso.
 */

// ==========================================
// EXEMPLO 1: Adicionar Notificações ao Sidebar
// ==========================================

/*
import { Bell } from 'lucide-react';

function SidebarWithNotifications() {
  const [notifications, setNotifications] = useState(0);

  return (
    <>
      {/* Existing Sidebar */}
      {/* ... */}

      {/* Notification Badge */}
      <div className="absolute top-6 right-6">
        {notifications > 0 && (
          <div className="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold">
            {notifications}
          </div>
        )}
      </div>
    </>
  );
}
*/

// ==========================================
// EXEMPLO 2: Adicionar User Profile Section
// ==========================================

/*
import { LogOut, User } from 'lucide-react';

function SidebarWithUserProfile() {
  const user = {
    name: "João Silva",
    role: "Administrador",
    avatar: "https://i.pravatar.cc/150?img=1"
  };

  return (
    <aside className="...">
      {/* Logo Section */}
      {/* ... */}

      {/* Navigation */}
      {/* ... */}

      {/* User Profile Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-800">
        <div className="flex items-center gap-3">
          <img 
            src={user.avatar} 
            alt={user.name}
            className="w-10 h-10 rounded-full object-cover"
          />
          <div className="flex-1">
            <p className="text-sm font-semibold text-gray-900 dark:text-white">
              {user.name}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              {user.role}
            </p>
          </div>
          <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </aside>
  );
}
*/

// ==========================================
// EXEMPLO 3: Breadcrumb com Sidebar
// ==========================================

/*
import { ChevronRight } from 'lucide-react';

function Breadcrumb() {
  const location = useLocation();
  const paths = location.pathname.split('/').filter(Boolean);

  return (
    <div className="flex items-center gap-2 px-4 py-3 bg-gray-50 dark:bg-gray-800">
      <Link to="/" className="hover:text-blue-500">Home</Link>
      {paths.map((path, index) => (
        <div key={index} className="flex items-center gap-2">
          <ChevronRight size={16} className="text-gray-400" />
          <span className="capitalize text-sm">{path.replace(/-/g, ' ')}</span>
        </div>
      ))}
    </div>
  );
}
*/

// ==========================================
// EXEMPLO 4: Search Box no Sidebar
// ==========================================

/*
import { Search } from 'lucide-react';

function SidebarWithSearch() {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredItems = [
    { name: 'Visão Geral', path: '/' },
    { name: 'Nova Avaliação', path: '/nova-avaliacao' },
    { name: 'Histórico', path: '/historico' },
    { name: 'Cidades', path: '/admin/cidades' },
    // ... mais itens
  ].filter(item => 
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="p-4 border-b border-gray-200 dark:border-gray-800">
      <div className="relative">
        <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
        <input
          type="text"
          placeholder="Buscar..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>
    </div>
  );
}
*/

// ==========================================
// EXEMPLO 5: Recent Pages Indicator
// ==========================================

/*
function SidebarWithRecentPages() {
  const [recentPages, setRecentPages] = useState([]);

  useEffect(() => {
    // Salvar página atual no localStorage
    const currentPage = location.pathname;
    const recent = JSON.parse(localStorage.getItem('recentPages') || '[]');
    
    if (!recent.includes(currentPage)) {
      recent.unshift(currentPage);
      recent.splice(5); // Manter apenas últimas 5
      localStorage.setItem('recentPages', JSON.stringify(recent));
      setRecentPages(recent);
    }
  }, [location.pathname]);

  return (
    // ... mostrar recent pages no footer
  );
}
*/

// ==========================================
// EXEMPLO 6: Custom Theme Colors
// ==========================================

/*
// Tailwind CSS Classes Customizados

// Tema Claro (padrão)
.sidebar-light {
  @apply bg-white text-gray-900 border-gray-200;
}

.nav-item-light-active {
  @apply bg-blue-500 text-white;
}

.nav-item-light-hover {
  @apply hover:bg-gray-100;
}

// Tema Escuro
.sidebar-dark {
  @apply bg-gray-900 text-gray-100 border-gray-800;
}

.nav-item-dark-active {
  @apply bg-blue-600 text-white;
}

.nav-item-dark-hover {
  @apply hover:bg-gray-800;
}

// Tema Corporativo (Premium)
.sidebar-corporate {
  @apply bg-gradient-to-b from-gray-900 to-gray-800 text-white;
}

.nav-item-corporate-active {
  @apply bg-gradient-to-r from-blue-600 to-purple-600 shadow-lg;
}

.nav-item-corporate-hover {
  @apply hover:translate-x-1 transition-transform;
}
*/

// ==========================================
// EXEMPLO 7: Submenu Avançado(Nested)
// ==========================================

/*
{/* Exemplo de submenu aninhado */}
/*

<div className="space-y-2">
  <button className="w-full flex items-center justify-between...">
    Administração
    <ChevronDown size={18} className={`transition-transform ${isAdminOpen ? 'rotate-180' : ''}`} />
  </button>

  {isAdminOpen && (
    <div className="space-y-1 pl-4 border-l-2 border-gray-200">
      {/* Level 2 */}
      <button className="w-full flex items-center justify-between...">
        Gestão
        <ChevronDown size={14} className={`transition-transform ${isGestaoOpen ? 'rotate-180' : ''}`} />
      </button>

      {isGestaoOpen && (
        <div className="space-y-1 pl-4">
          {/* Level 3 */}
          <NavItem to="/admin/gestao/cidades" icon={MapPin} label="Cidades" className="text-xs" />
          <NavItem to="/admin/gestao/usuarios" icon={Users} label="Usuários" className="text-xs" />
        </div>
      )}
    </div>
  )}
</div>
*/

// ==========================================
// EXEMPLO 8: Context para Sidebar State
// ==========================================

/*
import { createContext, useState } from 'react';

const SidebarContext = createContext();

export function SidebarProvider({ children }) {
  const [isOpen, setIsOpen] = useState(true);
  const [activeMenu, setActiveMenu] = useState(null);

  return (
    <SidebarContext.Provider value={{ isOpen, setIsOpen, activeMenu, setActiveMenu }}>
      {children}
    </SidebarContext.Provider>
  );
}

// Usar no App.jsx
function App() {
  return (
    <SidebarProvider>
      <Router>
        <div className="flex">
          <Sidebar />
          <main className="flex-1">
            <Routes>
              {/* rotas */}
            </Routes>
          </main>
        </div>
      </Router>
    </SidebarProvider>
  );
}
*/

// ==========================================
// EXEMPLO 9: Keyboard Shortcuts
// ==========================================

/*
function SidebarWithKeyboardShortcuts() {
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Ctrl + K = Busca
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        // Focar no input de busca
      }

      // G + H = Go Home
      if (e.key === 'g' && e.shiftKey === false) {
        navigate('/');
      }

      // G + A = Go to Admin
      if (e.key === 'a' && e.shiftKey === false) {
        navigate('/admin/cidades');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    // ... Sidebar com hints de atalhos
  );
}
*/

// ==========================================
// EXEMPLO 10: Testing Sidebar
// ==========================================

/*
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import Sidebar from './Sidebar';

describe('Sidebar Component', () => {
  test('renders navigation items', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    expect(screen.getByText('Visão Geral')).toBeInTheDocument();
    expect(screen.getByText('Nova Avaliação')).toBeInTheDocument();
    expect(screen.getByText('Histórico de Rankings')).toBeInTheDocument();
  });

  test('expands admin menu when clicked', async () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    const adminButton = screen.getByText('Administração');
    await userEvent.click(adminButton);

    expect(screen.getByText('Gestão de Cidades')).toBeInTheDocument();
  });

  test('highlights active link', () => {
    render(
      <BrowserRouter>
        <Sidebar />
      </BrowserRouter>
    );

    const homeLink = screen.getByText('Visão Geral').closest('a');
    expect(homeLink).toHaveClass('bg-blue-500');
  });
});
*/

export const SIDEBAR_EXAMPLES = 'Veja exemplos acima para estender o Sidebar';
