import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import RankingPage from './pages/RankingPage';
import AboutPage from './pages/AboutPage';

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-white">
        {/* Top Navbar - Sticky */}
        <Navbar />

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/ranking" element={<RankingPage />} />
              <Route path="/about" element={<AboutPage />} />
              
              {/* Placeholder routes for Admin pages */}
              <Route path="/nova-avaliacao" element={<NovaAvaliacaoPage />} />
              <Route path="/historico" element={<HistoricoPage />} />
              <Route path="/admin/cidades" element={<AdminCidadesPage />} />
              <Route path="/admin/indicadores" element={<AdminIndicadoresPage />} />
              <Route path="/admin/metodologia" element={<AdminMetodologiaPage />} />
              <Route path="/admin/auditorias" element={<AdminAuditoriaPage />} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

// Placeholder pages (substituir com componentes reais)
const NovaAvaliacaoPage = () => (
  <div>
    <h1 className="text-3xl font-bold text-gray-900">Nova Avaliação Smart</h1>
    <p className="text-gray-600 mt-2">Crie uma nova avaliação para analisar cidades</p>
  </div>
);

const HistoricoPage = () => (
  <div>
    <h1 className="text-3xl font-bold text-gray-900">Histórico de Rankings</h1>
    <p className="text-gray-600 mt-2">Visualize todos os rankings gerados</p>
  </div>
);

const AdminCidadesPage = () => (
  <div>
    <h1 className="text-3xl font-bold text-gray-900">Gestão de Cidades</h1>
    <p className="text-gray-600 mt-2">Gerencie as cidades cadastradas no sistema</p>
  </div>
);

const AdminIndicadoresPage = () => (
  <div>
    <h1 className="text-3xl font-bold text-gray-900">Base de Indicadores</h1>
    <p className="text-gray-600 mt-2">Visualize e gerencie os 47 indicadores ISO</p>
  </div>
);

const AdminMetodologiaPage = () => (
  <div>
    <h1 className="text-3xl font-bold text-gray-900">Metodologia TOPSIS</h1>
    <p className="text-gray-600 mt-2">Compreenda a metodologia de ranking utilizada</p>
  </div>
);

const AdminAuditoriaPage = () => (
  <div>
    <h1 className="text-3xl font-bold text-gray-900">Auditorias</h1>
    <p className="text-gray-600 mt-2">Visualize logs e auditorias do sistema</p>
  </div>
);

export default App;