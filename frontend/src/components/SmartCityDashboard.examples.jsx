// SmartCityDashboard - Exemplos de Uso e Testes

/**
 * EXEMPLO 1: Integração Básica no App.jsx
 * ==========================================
 */
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SmartCityDashboard from './components/SmartCityDashboard';

function AppExample1() {
  return (
    <Router>
      <Routes>
        <Route path="/dashboard" element={<SmartCityDashboard />} />
      </Routes>
    </Router>
  );
}

export default AppExample1;

/**
 * EXEMPLO 2: Integração com Layout Principal
 * ============================================
 */
import React, { useState } from 'react';
import Header from './components/Header';
import NavigationMenu from './components/NavigationMenu';
import SmartCityDashboard from './components/SmartCityDashboard';

function AppExample2() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  return (
    <div className="min-h-screen bg-gray-100">
      <Header />
      <NavigationMenu currentPage={currentPage} onPageChange={setCurrentPage} />
      
      <main className="p-6">
        {currentPage === 'dashboard' && <SmartCityDashboard />}
        {/* outras páginas */}
      </main>
    </div>
  );
}

/**
 * EXEMPLO 3: Integração no AdminPage com Abas
 * =============================================
 */
import React, { useState } from 'react';
import { FileText, Settings, BarChart3 } from 'lucide-react';
import SmartCityDashboard from '../components/SmartCityDashboard';
import ManualDataForm from '../components/ManualDataForm';

export function AdminPageWithDashboard() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    {
      id: 'dashboard',
      label: 'Smart City Dashboard',
      icon: BarChart3,
      component: SmartCityDashboard,
    },
    {
      id: 'manual-data',
      label: 'Dados Manuais',
      icon: FileText,
      component: ManualDataForm,
    },
    {
      id: 'settings',
      label: 'Configurações',
      icon: Settings,
      component: null, // Substituir com componente de settings
    },
  ];

  return (
    <div className="p-8 bg-gradient-to-br from-slate-50 to-slate-100 min-h-screen">
      {/* TAB NAVIGATION */}
      <div className="flex gap-2 mb-8 border-b border-gray-300">
        {tabs.map((tab) => {
          const TabIcon = tab.icon;
          const isActive = activeTab === tab.id;

          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-6 py-3 font-semibold transition ${
                isActive
                  ? 'border-b-4 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <TabIcon className="w-5 h-5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* TAB CONTENT */}
      <div className="bg-white rounded-2xl shadow-lg p-8">
        {tabs.map((tab) => {
          if (activeTab === tab.id && tab.component) {
            const Component = tab.component;
            return <Component key={tab.id} />;
          }
          return null;
        })}
      </div>
    </div>
  );
}

/**
 * EXEMPLO 4: Usando SmartCityDashboard com Props Customizadas
 * ============================================================
 * 
 * Nota: O componente atual não aceita props. Para torná-lo reutilizável,
 * você pode modificar assim:
 */

// Versão modificada do SmartCityDashboard com props
export function SmartCityDashboardCustom({
  initialCities = null,
  onSubmitSuccess = null,
  apiEndpoint = 'http://localhost:8000/api/v1/topsis/ranking-hibrido',
  disabledCities = [],
}) {
  // Seu código aqui... usar props para customização

  return <SmartCityDashboard />;
}

/**
 * EXEMPLO 5: Testing SmartCityDashboard
 * ====================================== 
 * 
 * Use este arquivo para testes com React Testing Library
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';

describe('SmartCityDashboard', () => {
  // TESTE 1: Renderização Inicial
  test('renderiza com os 3 seletores de cidade', () => {
    render(<SmartCityDashboard />);
    
    expect(screen.getByText('Apucarana')).toBeInTheDocument();
    expect(screen.getByText('Londrina')).toBeInTheDocument();
    expect(screen.getByText('Maringá')).toBeInTheDocument();
  });

  // TESTE 2: Seleção de Aba
  test('alterna entre abas corretamente', async () => {
    render(<SmartCityDashboard />);
    
    const smartCityTab = screen.getByText('Smart City');
    fireEvent.click(smartCityTab);
    
    // Verificar se a aba está ativa
    expect(smartCityTab).toHaveClass('active');
  });

  // TESTE 3: Alteração de Entrada
  test('atualiza valores dos inputs', async () => {
    render(<SmartCityDashboard />);
    
    const inputs = screen.getAllByRole('spinbutton');
    
    await userEvent.clear(inputs[0]);
    await userEvent.type(inputs[0], '5.5');
    
    expect(inputs[0]).toHaveValue(5.5);
  });

  // TESTE 4: Envio de Formulário
  test('envia dados para API ao clicar em Calcular Ranking', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            ranking: [
              { codigo_ibge: '4113700', nome: 'Londrina', score: 0.75 },
            ],
            indicadores: { indice_smart: 0.65 },
          }),
      })
    );

    render(<SmartCityDashboard />);
    
    const submitButton = screen.getByRole('button', {
      name: /Calcular Ranking/i,
    });
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/topsis/ranking-hibrido',
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
        })
      );
    });
  });

  // TESTE 5: Exibição de Resultados
  test('exibe resultados após submit bem-sucedido', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            ranking: [
              { codigo_ibge: '4113700', nome: 'Londrina', score: 0.75 },
            ],
            indicadores: { indice_smart: 0.65 },
          }),
      })
    );

    render(<SmartCityDashboard />);
    
    const submitButton = screen.getByRole('button', {
      name: /Calcular Ranking/i,
    });
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Resultados do Ranking/i)).toBeInTheDocument();
      expect(screen.getByText('Londrina')).toBeInTheDocument();
    });
  });

  // TESTE 6: Tratamento de Erro
  test('exibe mensagem de erro quando API falha', async () => {
    global.fetch = jest.fn(() =>
      Promise.resolve({
        ok: false,
        json: () =>
          Promise.resolve({
            detail: 'Erro no servidor',
          }),
      })
    );

    render(<SmartCityDashboard />);
    
    const submitButton = screen.getByRole('button', {
      name: /Calcular Ranking/i,
    });
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(
        screen.getByText(/Erro ao enviar dados/i)
      ).toBeInTheDocument();
    });
  });

  // TESTE 7: Limpeza de Dados
  test('limpa dados ao clicar em Limpar Dados', () => {
    render(<SmartCityDashboard />);
    
    // Preencher um input
    const inputs = screen.getAllByRole('spinbutton');
    fireEvent.change(inputs[0], { target: { value: '5.5' } });
    expect(inputs[0]).toHaveValue(5.5);

    // Clicar em reset
    const resetButton = screen.getByRole('button', {
      name: /Limpar Dados/i,
    });
    fireEvent.click(resetButton);

    // Verificar se voltou a 0
    expect(inputs[0]).toHaveValue(0);
  });
});

/**
 * EXEMPLO 6: Dados Mock para Testes Manual
 * ========================================= 
 * 
 * ⚠️ REMOVIDOS: MockData antigo removido.
 * Agora use o backend real em /api/v1/topsis/ranking-hibrido
 * 
 * O sistema funciona apenas com 2+ cidades (validação TOPSIS)
 */

// Para testes locais, configure um backend local ou use dados reais das APIs

/**
 * EXEMPLO 7: Customização Avançada
 * ================================ 
 * 
 * Para usar um Provider global com dados compartilhados:
 */

import React, { createContext, useContext, useState } from 'react';

const SmartCityContext = createContext();

export function SmartCityProvider({ children }) {
  const [globalCitiesData, setGlobalCitiesData] = useState(MOCK_CITY_DATA);
  const [globalResults, setGlobalResults] = useState(null);

  return (
    <SmartCityContext.Provider
      value={{
        citiesData: globalCitiesData,
        setCitiesData: setGlobalCitiesData,
        results: globalResults,
        setResults: setGlobalResults,
      }}
    >
      {children}
    </SmartCityContext.Provider>
  );
}

export function useSmartCity() {
  return useContext(SmartCityContext);
}

// Uso:
/*
<SmartCityProvider>
  <App />
</SmartCityProvider>
*/

/**
 * EXEMPLO 8: Validação Customizada
 * ================================
 */

export function validateCityData(cityData) {
  const errors = [];

  // ISO 37120
  if (
    cityData.iso_37120.taxa_desemprego_pct < 0 ||
    cityData.iso_37120.taxa_desemprego_pct > 100
  ) {
    errors.push('Taxa de desemprego deve estar entre 0 e 100%');
  }

  if (cityData.iso_37120.expectativa_vida_anos < 30 ||
    cityData.iso_37120.expectativa_vida_anos > 150) {
    errors.push('Expectativa de vida deve estar entre 30 e 150 anos');
  }

  // ISO 37122
  if (
    cityData.iso_37122.servicos_urbanos_online_pct < 0 ||
    cityData.iso_37122.servicos_urbanos_online_pct > 100
  ) {
    errors.push('Serviços urbanos online deve estar entre 0 e 100%');
  }

  // ISO 37123
  if (cityData.iso_37123.populacao_treinada_emergencia_pct < 0 ||
    cityData.iso_37123.populacao_treinada_emergencia_pct > 100) {
    errors.push('População treinada deve estar entre 0 e 100%');
  }

  return {
    isValid: errors.length === 0,
    errors,
  };
}

/**
 * EXEMPLO 9: Executar Localmente com Mock
 * ======================================== 
 */

export function SmartCityDashboardDemo() {
  const [apiResponse, setApiResponse] = useState(null);

  const handleMockSubmit = () => {
    // Simular delay de API
    setTimeout(() => {
      setApiResponse(MOCK_API_RESPONSE);
    }, 2000);
  };

  return (
    <div>
      <SmartCityDashboard />
      <button
        onClick={handleMockSubmit}
        className="mt-4 px-4 py-2 bg-green-600 text-white rounded"
      >
        Usar Mock API
      </button>
      {apiResponse && (
        <pre className="mt-4 p-4 bg-gray-100 rounded">
          {JSON.stringify(apiResponse, null, 2)}
        </pre>
      )}
    </div>
  );
}

/**
 * EXEMPLO 10: Environment Variables
 * =================================
 * 
 * .env.example:
 */

// VITE_API_BASE_URL=http://localhost:8000
// VITE_API_VERSION=v1
// VITE_ENDPOINT_RANKING=/topsis/ranking-hibrido

// Uso no componente:
const API_ENDPOINT = `${import.meta.env.VITE_API_BASE_URL}/api/${import.meta.env.VITE_API_VERSION}${import.meta.env.VITE_ENDPOINT_RANKING}`;

export default {
  AppExample1,
  AppExample2,
  AdminPageWithDashboard,
  SmartCityDashboardCustom,
  SmartCityDashboardDemo,
  MOCK_API_RESPONSE,
  MOCK_CITY_DATA,
  validateCityData,
};
