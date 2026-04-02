import React, { useState } from 'react';
import { Link } from 'react-router-dom';

/**
 * Navbar Component - Menu Superior Fixo
 * 
 * Design:
 * - Sticky top-0 (fixo no topo)
 * - Cores claras: branco, azul, cinza
 * - Logo à esquerda
 * - Navegação à direita com dropdown admin
 * - Shadow leve (sombra sutil)
 */
function Navbar() {
  const [isAdminDropdownOpen, setIsAdminDropdownOpen] = useState(false);

  const toggleAdminDropdown = () => {
    setIsAdminDropdownOpen(!isAdminDropdownOpen);
  };

  const closeAdminDropdown = () => {
    setIsAdminDropdownOpen(false);
  };

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Logo/Marca */}
          <div className="flex-shrink-0">
            <Link to="/" className="flex items-center gap-2">
              <span className="text-2xl font-bold text-orange-600">Urbix</span>
              <span className="text-xs text-gray-500 font-medium hidden sm:inline">
                Cidades Inteligentes
              </span>
            </Link>
          </div>

          {/* Navigation Links - Centro/Direita */}
          <div className="flex items-center space-x-1">
            
            {/* Visão Geral */}
            <Link
              to="/"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-orange-600 hover:bg-orange-50 transition-colors"
            >
              📊 Visão Geral
            </Link>

            {/* Nova Avaliação */}
            <Link
              to="/nova-avaliacao"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-orange-600 hover:bg-orange-50 transition-colors"
            >
              ➕ Nova Avaliação
            </Link>

            {/* Histórico */}
            <Link
              to="/historico"
              className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-orange-600 hover:bg-orange-50 transition-colors"
            >
              📜 Histórico
            </Link>

            {/* Dropdown Administração */}
            <div className="relative group">
              <button
                onClick={toggleAdminDropdown}
                className="px-3 py-2 rounded-md text-sm font-medium text-gray-700 hover:text-orange-600 hover:bg-orange-50 transition-colors flex items-center gap-1"
              >
                ⚙️ Administração
                <span
                  className={`transform transition-transform ${
                    isAdminDropdownOpen ? 'rotate-180' : ''
                  }`}
                >
                  ▼
                </span>
              </button>

              {/* Dropdown Menu */}
              <div
                className={`absolute right-0 mt-0 w-48 bg-white border border-gray-200 rounded-md shadow-lg py-1 transition-all duration-200 ${
                  isAdminDropdownOpen
                    ? 'opacity-100 visible'
                    : 'opacity-0 invisible'
                }`}
              >
                <Link
                  to="/admin/cidades"
                  onClick={closeAdminDropdown}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-600 transition-colors"
                >
                  🏙️ Gestão de Cidades
                </Link>
                <Link
                  to="/admin/indicadores"
                  onClick={closeAdminDropdown}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-600 transition-colors"
                >
                  📈 Base de Indicadores
                </Link>
                <Link
                  to="/admin/metodologia"
                  onClick={closeAdminDropdown}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-600 transition-colors"
                >
                  🔬 Metodologia TOPSIS
                </Link>
                <Link
                  to="/admin/auditorias"
                  onClick={closeAdminDropdown}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-orange-50 hover:text-orange-600 transition-colors border-t border-gray-100"
                >
                  🔍 Auditorias
                </Link>
              </div>

              {/* Overlay para fechar dropdown */}
              {isAdminDropdownOpen && (
                <div
                  className="fixed inset-0"
                  onClick={closeAdminDropdown}
                />
              )}
            </div>
          </div>

          {/* Right Side Actions (opcional para versão futura) */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Aqui pode ir ícone de user, notificações, etc */}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
