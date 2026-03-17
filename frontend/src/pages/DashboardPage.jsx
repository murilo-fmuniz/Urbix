import React, { useState, useEffect } from 'react';
import { getIndicadores } from '../services/api';
import IndicatorCard from '../components/IndicatorCard';
import IndicatorsChart from '../components/IndicatorsChart';
import './DashboardPage.css';

function DashboardPage() {
  const [indicadores, setIndicadores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // View mode: 'chart' (gráfico de médias) ou 'detail' (indicadores detalhados)
  const [viewMode, setViewMode] = useState('chart');
  
  // Controlar visibilidade dos filtros
  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  
  // Filtros
  const [filtroCidade, setFiltroCidade] = useState('');
  const [filtroNorma, setFiltroNorma] = useState('');
  const [filtroGrandeArea, setFiltroGrandeArea] = useState('');

  // Valores únicos para os dropdowns
  const [cidades, setCidades] = useState([]);
  const [normas, setNormas] = useState([]);
  const [grandesAreas, setGrandesAreas] = useState([]);

  // Carregar indicadores
  useEffect(() => {
    const fetchIndicadores = async () => {
      try {
        setLoading(true);
        const data = await getIndicadores({
          cidade: filtroCidade || undefined,
          norma: filtroNorma || undefined,
          grande_area: filtroGrandeArea || undefined,
        });
        
        setIndicadores(data);
        
        // Extrair valores únicos para os filtros (apenas na primeira carga)
        if (!filtroCidade && !filtroNorma && !filtroGrandeArea) {
          const uniqueCidades = [...new Set(
            data.flatMap(ind => 
              ind.dados_coleta?.map(col => col.cidade) || []
            ).filter(Boolean)
          )].sort();
          
          const uniqueNormas = [...new Set(
            data.map(ind => ind.norma).filter(Boolean)
          )].sort();
          
          const uniqueAreas = [...new Set(
            data.map(ind => ind.grande_area).filter(Boolean)
          )].sort();
          
          setCidades(uniqueCidades);
          setNormas(uniqueNormas);
          setGrandesAreas(uniqueAreas);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Erro ao carregar os indicadores');
        console.error(err);
        setLoading(false);
      }
    };

    fetchIndicadores();
  }, [filtroCidade, filtroNorma, filtroGrandeArea]);

  // Limpar filtros e voltar ao modo gráfico
  const handleLimparFiltros = () => {
    setFiltroCidade('');
    setFiltroNorma('');
    setFiltroGrandeArea('');
    setViewMode('chart');
    setMostrarFiltros(false);
  };

  // Quando seleciona uma cidade, entra em modo detail
  const handleSelectCity = (cidade) => {
    setFiltroCidade(cidade);
    setViewMode('detail');
    setMostrarFiltros(true);
  };

  if (loading) return <div className="loading">Carregando indicadores...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div className="dashboard-page container">
      <div className="dashboard-header">
        <h1>Dashboard de Indicadores</h1>
        <p className="subtitle">ISO 37122 - Indicadores para Cidades Inteligentes</p>
      </div>
      {/* RESUMO E GRID - Mostrados apenas em modo detail */}
      {viewMode === 'detail' && (
        <>
          <div className="summary-stats">
            <div className="stat-card">
              <h3>Total de Indicadores</h3>
              <p>{indicadores.length}</p>
            </div>
            <div className="stat-card">
              <h3>Dados Disponíveis</h3>
              <p>
                {indicadores.flatMap(ind => ind.dados_coleta || [])
                  .filter(col => col.dado_disponivel).length}
              </p>
            </div>
            <div className="stat-card">
              <h3>Cidades Cobertas</h3>
              <p>
                {[...new Set(
                  indicadores.flatMap(ind => 
                    ind.dados_coleta?.map(col => col.cidade) || []
                  )
                )].length}
              </p>
            </div>
          </div>

          <div className="indicators-grid">
            {indicadores.length > 0 ? (
              indicadores.map((indicador) => (
                <IndicatorCard 
                  key={indicador.id} 
                  indicador={indicador}
                />
              ))
            ) : (
              <div className="no-results">
                <p>Nenhum indicador encontrado com os filtros selecionados</p>
              </div>
            )}
          </div>
        </>
      )}
      
      {/* MODO GRÁFICO - Mostra visão geral dos indicadores */}
      {viewMode === 'chart' && (
        <div className="chart-view">
          <IndicatorsChart 
            indicadores={indicadores}
            onSelectCity={handleSelectCity}
          />
          <div className="chart-actions">
            <button 
              className="btn-expandir"
              onClick={() => setMostrarFiltros(!mostrarFiltros)}
            >
              {mostrarFiltros ? '▼ Recolher Filtros' : '▲ Expandir Filtros'}
            </button>
          </div>
        </div>
      )}

      {/* MODO DETALHE - Mostra indicadores com filtros */}
      {viewMode === 'detail' && (
        <div className="detail-view">
          <button className="btn-voltar" onClick={handleLimparFiltros}>
            ↶ Voltar ao Gráfico
          </button>
        </div>
      )}

      {/* FILTROS - Mostrados em modo detail ou se expandidos em chart mode */}
      {(mostrarFiltros || viewMode === 'detail') && (
        <div className="filter-section">
          <div className="filters-container">
            <div className="filter-group">
              <label htmlFor="filter-cidade">Cidade:</label>
              <select 
                id="filter-cidade"
                value={filtroCidade}
                onChange={(e) => {
                  setFiltroCidade(e.target.value);
                  setViewMode('detail');
                }}
                className="filter-select"
              >
                <option value="">Todas as cidades</option>
                {cidades.map(cidade => (
                  <option key={cidade} value={cidade}>{cidade}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="filter-norma">Norma:</label>
              <select 
                id="filter-norma"
                value={filtroNorma}
                onChange={(e) => {
                  setFiltroNorma(e.target.value);
                  setViewMode('detail');
                }}
                className="filter-select"
              >
                <option value="">Todas as normas</option>
                {normas.map(norma => (
                  <option key={norma} value={norma}>{norma}</option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label htmlFor="filter-area">Grande Área:</label>
              <select 
                id="filter-area"
                value={filtroGrandeArea}
                onChange={(e) => {
                  setFiltroGrandeArea(e.target.value);
                  setViewMode('detail');
                }}
                className="filter-select"
              >
                <option value="">Todas as áreas</option>
                {grandesAreas.map(area => (
                  <option key={area} value={area}>{area}</option>
                ))}
              </select>
            </div>

            <button className="btn-limpar" onClick={handleLimparFiltros}>
              Limpar Filtros
            </button>
          </div>
        </div>
      )}

      
    </div>
  );
}

export default DashboardPage;