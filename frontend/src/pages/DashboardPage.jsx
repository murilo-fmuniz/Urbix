import React, { useState, useEffect } from 'react';
import { getIndicators } from '../services/api';
import IndicatorCard from '../components/IndicatorCard';
import './DashboardPage.css';

function DashboardPage() {
  const [indicators, setIndicators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtroAno, setFiltroAno] = useState('todos');

  useEffect(() => {
    const fetchIndicators = async () => {
      try {
        const data = await getIndicators();
        // Ordenar por NOTA_INTELIGENTE + NOTA_SUSTENTAVEL (média total)
        const sortedData = data.sort((a, b) => 
          (b.NOTA_INTELIGENTE + b.NOTA_SUSTENTAVEL) - (a.NOTA_INTELIGENTE + a.NOTA_SUSTENTAVEL)
        );
        setIndicators(sortedData);
        setLoading(false);
      } catch (err) {
        setError('Erro ao carregar os indicadores');
        setLoading(false);
      }
    };

    fetchIndicators();
  }, []);

  // Obter anos únicos para o filtro
  // Filtrar indicadores válidos (com notas calculadas)
  const indicadoresValidos = indicators.filter(ind => 
    typeof ind.NOTA_INTELIGENTE === 'number' && 
    typeof ind.NOTA_SUSTENTAVEL === 'number' && 
    !isNaN(ind.NOTA_INTELIGENTE) && 
    !isNaN(ind.NOTA_SUSTENTAVEL)
  );

  // Obter anos únicos para o filtro (apenas de indicadores válidos)
  const anos = [...new Set(indicadoresValidos
    .filter(ind => ind.ANO != null)
    .map(ind => ind.ANO))]
    .sort((a, b) => a - b);  // Ordenar numericamente

  // Filtrar indicadores por ano
  const indicadoresFiltrados = filtroAno === 'todos' 
    ? indicadoresValidos 
    : indicadoresValidos.filter(ind => ind.ANO === Number(filtroAno));

  // Calcular médias com segurança
  const calcularMedia = (array, campo) => {
    if (!array.length) return 0;
    const soma = array.reduce((acc, curr) => {
      const valor = curr[campo];
      return acc + (typeof valor === 'number' && !isNaN(valor) ? valor : 0);
    }, 0);
    return (soma / array.length * 100).toFixed(1);
  };

  if (loading) return <div className="loading">Carregando...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard-page container">
      <div className="dashboard-header">
        <h1>Dashboard de Indicadores</h1>
        <div className="filter-section">
          <label htmlFor="ano-filter">Filtrar por ano:</label>
          <select 
            id="ano-filter"
            value={filtroAno}
            onChange={(e) => setFiltroAno(e.target.value)}
          >
            <option value="todos">Todos os anos</option>
            {anos.map(ano => (
              <option key={ano} value={ano}>{ano}</option>
            ))}
          </select>
        </div>
      </div>

      <div className="summary-stats">
        <div className="stat-card">
          <h3>Total de Regiões</h3>
          <p>{indicadoresFiltrados.length}</p>
        </div>
        <div className="stat-card">
          <h3>Média Nota Inteligente</h3>
          <p>{calcularMedia(indicadoresFiltrados, 'NOTA_INTELIGENTE')}%</p>
        </div>
        <div className="stat-card">
          <h3>Média Nota Sustentável</h3>
          <p>{calcularMedia(indicadoresFiltrados, 'NOTA_SUSTENTAVEL')}%</p>
        </div>
      </div>

      <div className="indicators-grid">
        {indicadoresFiltrados.map((indicator) => (
          <IndicatorCard 
            key={`${indicator.CODRM}-${indicator.ANO}`} 
            indicator={indicator} 
          />
        ))}
      </div>
    </div>
  );
}

export default DashboardPage;