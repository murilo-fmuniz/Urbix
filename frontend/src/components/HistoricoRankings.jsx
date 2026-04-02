import React, { useState, useEffect } from 'react';
import { obterHistoricoRankings } from '../services/api';
import './HistoricoRankings.css';

/**
 * HistoricoRankings - Visualiza série histórica dos rankings
 * Mostra posição relativa das cidades e evolução ao longo do tempo
 */
function HistoricoRankings() {
  const [historico, setHistorico] = useState([]);
  const [periodos, setPeriodos] = useState([]);
  const [selectedPeriodo, setSelectedPeriodo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filtroNomeCidade, setFiltroNomeCidade] = useState('');

  const carregarHistoricoRankings = async () => {
    setLoading(true);
    setError('');
    setHistorico([]);
    setPeriodos([]);

    try {
      const dados = await obterHistoricoRankings(24); // Últimos 24 períodos
      if (dados && dados.length > 0) {
        setHistorico(dados);
        
        // Extrair períodos únicos e ordenar em ordem decrescente
        const periodosUnicos = [...new Set(dados.map(r => r.periodo_referencia))].sort().reverse();
        setPeriodos(periodosUnicos);
        
        if (periodosUnicos.length > 0) {
          setSelectedPeriodo(periodosUnicos[0]); // Seleciona período mais recente
        }
      } else {
        setError('Nenhum dado de ranking encontrado');
      }
    } catch (err) {
      setError(`Erro ao carregar rankings: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Carregar ao montar
  useEffect(() => {
    carregarHistoricoRankings();
  }, []);

  // Dados do período selecionado
  const rankingAtual = historico
    .filter(r => r.periodo_referencia === selectedPeriodo)
    .sort((a, b) => (a.posicao || 999) - (b.posicao || 999));

  // Filtrar pelo nome da cidade
  const rankingFiltrado = rankingAtual.filter(r => 
    r.nome_cidade?.toLowerCase().includes(filtroNomeCidade.toLowerCase())
  );

  // Série histórica de uma cidade específica
  const obterSerieTemporalCidade = (codigoIBGE) => {
    return historico
      .filter(r => r.codigo_ibge === codigoIBGE)
      .sort((a, b) => a.periodo_referencia.localeCompare(b.periodo_referencia));
  };

  const renderRankingTable = () => {
    if (rankingFiltrado.length === 0) {
      return (
        <div className="no-results">
          Nenhuma cidade encontrada para o período {selectedPeriodo}
        </div>
      );
    }

    return (
      <table className="ranking-tabela">
        <thead>
          <tr>
            <th className="rank-pos">Posição</th>
            <th className="rank-nome">Cidade</th>
            <th className="rank-score">Score TOPSIS</th>
            <th className="rank-eco">Économico</th>
            <th className="rank-soc">Social</th>
            <th className="rank-amb">Ambiental</th>
          </tr>
        </thead>
        <tbody>
          {rankingFiltrado.map((cidade, idx) => {
            const scoreNorm = parseFloat(cidade.score_topsis || 0);
            let badgeClass = 'badge-neutral';
            
            if (scoreNorm >= 0.7) badgeClass = 'badge-alto';
            else if (scoreNorm >= 0.4) badgeClass = 'badge-medio';
            else badgeClass = 'badge-baixo';

            return (
              <tr key={idx} className="ranking-row">
                <td className="rank-pos">
                  <div className={`posicao-badge ${idx < 3 ? 'top3' : ''}`}>
                    {idx === 0 && '🥇'}
                    {idx === 1 && '🥈'}
                    {idx === 2 && '🥉'}
                    {idx > 2 && `${idx + 1}º`}
                  </div>
                </td>
                <td className="rank-nome">
                  <strong>{cidade.nome_cidade || 'N/A'}</strong>
                  <small>{cidade.codigo_ibge}</small>
                </td>
                <td className="rank-score">
                  <div className={`score-box ${badgeClass}`}>
                    {scoreNorm.toFixed(3)}
                  </div>
                </td>
                <td className="rank-eco">
                  {cidade.dimensao_economica?.toFixed(2) || '-'}
                </td>
                <td className="rank-soc">
                  {cidade.dimensao_social?.toFixed(2) || '-'}
                </td>
                <td className="rank-amb">
                  {cidade.dimensao_ambiental?.toFixed(2) || '-'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    );
  };

  return (
    <div className="historico-rankings-container">
      <div className="rankings-header">
        <h2>📊 Histórico de Rankings</h2>
        <p>Acompanhe a evolução das posições das cidades nos rankings TOPSIS</p>
      </div>

      {historico.length === 0 && !loading && (
        <button onClick={carregarHistoricoRankings} className="btn btn-primary btn-load">
          🔄 Carregar Histórico de Rankings
        </button>
      )}

      {loading && (
        <div className="loading-state">
          ⏳ Carregando histórico de rankings...
        </div>
      )}

      {error && (
        <div className="alert alert-error">{error}</div>
      )}

      {historico.length > 0 && (
        <>
          {/* Seletor de Período */}
          <div className="periodo-selector">
            <label htmlFor="periodoSelect">Selecionar Período:</label>
            <select
              id="periodoSelect"
              value={selectedPeriodo}
              onChange={(e) => setSelectedPeriodo(e.target.value)}
              className="select-field"
            >
              {periodos.map(periodo => (
                <option key={periodo} value={periodo}>
                  {periodo}
                </option>
              ))}
            </select>
          </div>

          {/* Filtro de Cidade */}
          <div className="filtro-cidade">
            <input
              type="text"
              placeholder="🔍 Filtrar por nome da cidade..."
              value={filtroNomeCidade}
              onChange={(e) => setFiltroNomeCidade(e.target.value)}
              className="input-filtro"
            />
            {filtroNomeCidade && (
              <button
                onClick={() => setFiltroNomeCidade('')}
                className="btn-clear-filtro"
              >
                ✕
              </button>
            )}
          </div>

          {/* Tabela de Rankings */}
          <div className="ranking-table-container">
            {renderRankingTable()}
          </div>

          {/* Estatísticas do Período */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-label">Cidades Analisadas</div>
              <div className="stat-value">{rankingAtual.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Períodos Disponíveis</div>
              <div className="stat-value">{periodos.length}</div>
            </div>
            <div className="stat-card">
              <div className="stat-label">Período Atual</div>
              <div className="stat-value">{selectedPeriodo}</div>
            </div>
          </div>

          {/* Timeline Visual */}
          <div className="timeline-section">
            <h3>📅 Timeline de Períodos</h3>
            <div className="timeline">
              {periodos.map((periodo, idx) => (
                <button
                  key={periodo}
                  onClick={() => setSelectedPeriodo(periodo)}
                  className={`timeline-item ${selectedPeriodo === periodo ? 'active' : ''}`}
                  title={periodo}
                >
                  {periodo}
                </button>
              ))}
            </div>
          </div>

          {/* Info Box */}
          <div className="info-box">
            ℹ️ <strong>Dicas:</strong> Clique em um período da timeline para visualizar o ranking daquele mês. 
            Use o filtro de cidade para buscar uma municipalidade específica.
          </div>
        </>
      )}
    </div>
  );
}

export default HistoricoRankings;
