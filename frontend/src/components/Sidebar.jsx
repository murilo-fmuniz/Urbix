import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Sparkles,
  History,
  Settings,
  MapPin,
  Database,
  BookOpen,
  ShieldCheck,
  ChevronDown,
  X,
  Menu,
} from 'lucide-react';

/**
 * Componente Sidebar - Menu Principal do Sistema
 *
 * Estrutura:
 * - Visão Geral → HomePage
 * - Nova Avaliação (DESTAQUE) → /nova-avaliacao
 * - Histórico de Rankings → /historico
 * - [Divisor] Configurações
 * - Administração (Dropdown)
 *   - Gestão de Cidades
 *   - Base de Indicadores
 *   - Metodologia TOPSIS
 *   - Auditorias
 *
 * Features:
 * - Active link detection com React Router
 * - Expandable menu para Administração
 * - Mobile responsive (toggle)
 * - Dark/Light mode ready
 * - Tailwind CSS styling
 * - Lucide React icons
 */
function Sidebar() {
  const location = useLocation();
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  // Detecta se a rota atual é ativa
  const isActive = (path) => {
    return location.pathname === path || location.pathname.startsWith(path + '/');
  };

  // Função reutilizável para renderizar itens do menu
  const NavItem = ({ to, icon: Icon, label, className = '', onClick = null }) => (
    <Link
      to={to}
      onClick={onClick}
      className={`
        flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200
        ${
          isActive(to)
            ? 'bg-blue-500 text-white shadow-md'
            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
        }
        ${className}
      `}
    >
      <Icon size={20} className="min-w-[20px]" />
      <span className="text-sm font-medium">{label}</span>
    </Link>
  );

  return (
    <>
      {/* Mobile Menu Toggle */}
      <button
        className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white dark:bg-gray-800 rounded-lg shadow-md"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
      >
        {isMobileOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Overlay Mobile */}
      {isMobileOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`
          fixed md:relative left-0 top-0 h-screen z-40
          w-64 bg-white dark:bg-gray-900
          border-r border-gray-200 dark:border-gray-800
          shadow-lg md:shadow-none
          overflow-y-auto
          transform transition-transform duration-300 md:transform-none
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
        `}
      >
        {/* Logo/Branding */}
        <div className="p-6 border-b border-gray-200 dark:border-gray-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">U</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">Urbix</h1>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
            Análise de Cidades Inteligentes
          </p>
        </div>

        {/* Navigation Container */}
        <nav className="p-4 space-y-2">
          {/* ========================================
              MENU PRINCIPAL
              ======================================== */}

          {/* Visão Geral */}
          <div onClick={() => setIsMobileOpen(false)}>
            <NavItem
              to="/"
              icon={LayoutDashboard}
              label="Visão Geral"
            />
          </div>

          {/* ========================================
              AÇÃO PRINCIPAL - DESTAQUE
              ======================================== */}

          {/* Nova Avaliação Smart (PRIMARY ACTION) */}
          <div className="pt-2" onClick={() => setIsMobileOpen(false)}>
            <div className="relative">
              {/* Background gradient glow effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg opacity-0 group-hover:opacity-20 blur transition-opacity" />
              
              <Link
                to="/nova-avaliacao"
                className={`
                  relative flex items-center gap-3 px-4 py-3 rounded-lg
                  background-gradient-to-r from-blue-500 to-purple-600
                  text-white font-semibold shadow-lg
                  hover:shadow-xl hover:scale-105
                  transition-all duration-200
                  transform
                  ${isActive('/nova-avaliacao') ? 'ring-2 ring-blue-300' : ''}
                `}
              >
                <Sparkles size={20} className="min-w-[20px]" />
                <span>Nova Avaliação</span>
              </Link>
            </div>
          </div>

          {/* Histórico de Rankings */}
          <div onClick={() => setIsMobileOpen(false)}>
            <NavItem
              to="/historico"
              icon={History}
              label="Histórico de Rankings"
            />
          </div>

          {/* ========================================
              DIVISOR - CONFIGURAÇÕES
              ======================================== */}

          <div className="py-4">
            <div className="flex items-center gap-2 px-4">
              <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
              <span className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Configurações
              </span>
              <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700" />
            </div>
          </div>

          {/* ========================================
              ADMINISTRAÇÃO - COLLAPSIBLE
              ======================================== */}

          {/* Admin Menu Header */}
          <div>
            <button
              onClick={() => setIsAdminOpen(!isAdminOpen)}
              className={`
                w-full flex items-center justify-between gap-3 px-4 py-3 rounded-lg
                transition-all duration-200
                ${
                  isAdminOpen || isActive('/admin')
                    ? 'bg-gray-100 dark:bg-gray-800 text-blue-600 dark:text-blue-400'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }
              `}
            >
              <div className="flex items-center gap-3">
                <Settings size={20} className="min-w-[20px]" />
                <span className="text-sm font-medium">Administração</span>
              </div>
              <ChevronDown
                size={18}
                className={`transition-transform duration-300 ${
                  isAdminOpen ? 'rotate-180' : ''
                }`}
              />
            </button>
          </div>

          {/* Admin Submenu - Collapsible */}
          {isAdminOpen && (
            <div className="space-y-2 pl-4 border-l-2 border-gray-200 dark:border-gray-700 ml-2">
              {/* Gestão de Cidades */}
              <div onClick={() => setIsMobileOpen(false)}>
                <NavItem
                  to="/admin/cidades"
                  icon={MapPin}
                  label="Gestão de Cidades"
                  className="pl-6"
                />
              </div>

              {/* Base de Indicadores */}
              <div onClick={() => setIsMobileOpen(false)}>
                <NavItem
                  to="/admin/indicadores"
                  icon={Database}
                  label="Base de Indicadores"
                  className="pl-6"
                />
              </div>

              {/* Metodologia TOPSIS */}
              <div onClick={() => setIsMobileOpen(false)}>
                <NavItem
                  to="/admin/metodologia"
                  icon={BookOpen}
                  label="Metodologia (TOPSIS)"
                  className="pl-6"
                />
              </div>

              {/* Auditorias */}
              <div onClick={() => setIsMobileOpen(false)}>
                <NavItem
                  to="/admin/auditorias"
                  icon={ShieldCheck}
                  label="Auditorias"
                  className="pl-6"
                />
              </div>
            </div>
          )}
        </nav>

        {/* Footer Info */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            v2.0.0 • Sistema de Análise de Cidades Inteligentes
          </p>
        </div>
      </aside>
    </>
  );
}

export default Sidebar;
