import React from 'react';
import './RankingTable.css';

function RankingTable({ ranking, detalhes }) {
  const getMedalEmoji = (position) => {
    const emojis = ['🥇', '🥈', '🥉'];
    return emojis[position] || '•';
  };

  const getScoreColor = (score) => {
    if (score >= 0.7) return '#4CAF50';      // Verde
    if (score >= 0.5) return '#FFC107';      // Amarelo
    if (score >= 0.3) return '#FF9800';      // Laranja
    return '#f44336';                         // Vermelho
  };

  return (
    <div className="ranking-table-container">
      <div className="table-header">
        <h3>🏅 Ranking Final TOPSIS</h3>
        <p className="table-description">
          Cidades ordenadas por Índice Smart (Índice de Similaridade com Ideal Positivo)
        </p>
      </div>

      {ranking && ranking.length > 0 ? (
        <div className="table-responsive">
          <table className="ranking-table">
            <thead>
              <tr>
                <th className="rank-col">Posição</th>
                <th className="city-col">Cidade</th>
                <th className="score-col">Índice Smart</th>
                <th className="status-col">Status</th>
              </tr>
            </thead>
            <tbody>
              {ranking.map((city, index) => (
                <tr key={index} className={`rank-${index}`}>
                  <td className="rank-cell">
                    <span className="medal">{getMedalEmoji(index)}</span>
                    <span className="position">{index + 1}º</span>
                  </td>
                  <td className="city-cell">
                    <strong>{city.nome_cidade}</strong>
                  </td>
                  <td className="score-cell">
                    <div className="score-bar-container">
                      <div
                        className="score-bar"
                        style={{
                          width: `${city.indice_smart * 100}%`,
                          backgroundColor: getScoreColor(city.indice_smart),
                        }}
                      ></div>
                    </div>
                    <span className="score-value">
                      {(city.indice_smart * 100).toFixed(2)}%
                    </span>
                  </td>
                  <td className="status-cell">
                    {city.indice_smart >= 0.7 && <span className="badge badge-excellent">Excelente</span>}
                    {city.indice_smart >= 0.5 && city.indice_smart < 0.7 && <span className="badge badge-good">Bom</span>}
                    {city.indice_smart >= 0.3 && city.indice_smart < 0.5 && <span className="badge badge-fair">Moderado</span>}
                    {city.indice_smart < 0.3 && <span className="badge badge-poor">Baixo</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="no-data">
          <p>Nenhum resultado disponível</p>
        </div>
      )}

      {/* DETALHES DO CÁLCULO */}
      {detalhes && (
        <div className="calculation-details">
          <h4>📋 Detalhes do Cálculo TOPSIS</h4>
          <div className="details-grid">
            <div className="detail-card">
              <h5>Indicadores Utilizados</h5>
              <ul>
                {detalhes.indicadores_nomes && detalhes.indicadores_nomes.map((ind, i) => (
                  <li key={i}>{ind}</li>
                ))}
              </ul>
            </div>

            <div className="detail-card">
              <h5>Pesos</h5>
              <ul>
                {detalhes.pesos && detalhes.pesos.map((peso, i) => (
                  <li key={i}>
                    <strong>{detalhes.indicadores_nomes?.[i] || `Indicador ${i + 1}`}:</strong>{' '}
                    {(peso * 100).toFixed(1)}%
                  </li>
                ))}
              </ul>
            </div>

            <div className="detail-card">
              <h5>Impactos</h5>
              <ul>
                {detalhes.impactos && detalhes.impactos.map((impacto, i) => (
                  <li key={i}>
                    <strong>{detalhes.indicadores_nomes?.[i] || `Indicador ${i + 1}`}:</strong>{' '}
                    {impacto === 1 ? '↑ Benefício' : '↓ Custo'}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default RankingTable;
