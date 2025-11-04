import React, { useState, useEffect } from 'react';
import { getIndicators } from '../services/api';
import IndicatorCard from '../components/IndicatorCard';
import './DashboardPage.css';

function DashboardPage() {
  const [indicators, setIndicators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchIndicators = async () => {
      try {
        const data = await getIndicators();
        setIndicators(data);
        setLoading(false);
      } catch (err) {
        setError('Erro ao carregar os indicadores');
        setLoading(false);
      }
    };

    fetchIndicators();
  }, []);

  if (loading) return <div className="loading">Carregando...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard-page container">
      <h1>Dashboard de Indicadores</h1>
      <div className="indicators-grid">
        {indicators.map((indicator) => (
          <IndicatorCard key={indicator.id} indicator={indicator} />
        ))}
      </div>
    </div>
  );
}

export default DashboardPage;