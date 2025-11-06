import React from 'react';
import './IndicatorCard.css';

function IndicatorCard({ indicator }) {
  // Garantir que as notas são números e estão entre 0 e 1
  const notaInteligente = (
    typeof indicator.NOTA_INTELIGENTE === 'number' && 
    !isNaN(indicator.NOTA_INTELIGENTE) ? 
    Math.min(Math.max(indicator.NOTA_INTELIGENTE, 0), 1) * 100 : 0
  ).toFixed(1);

  const notaSustentavel = (
    typeof indicator.NOTA_SUSTENTAVEL === 'number' && 
    !isNaN(indicator.NOTA_SUSTENTAVEL) ? 
    Math.min(Math.max(indicator.NOTA_SUSTENTAVEL, 0), 1) * 100 : 0
  ).toFixed(1);
  
  const formatValue = (value, decimals = 3) => {
    if (value === null || value === undefined || isNaN(value)) {
      return 'N/A';
    }
    return Number(value).toFixed(decimals);
  };

  return (
    <div className="indicator-card card">
      <h3>{indicator.NOME_RM || 'Região Metropolitana'}</h3>
      <p className="category">Ano: {indicator.ANO || 'N/A'}</p>
      
      <div className="scores">
        <div className="score-section">
          <h4>Nota Inteligente</h4>
          <div className="progress-container">
            <div 
              className="progress-bar" 
              style={{ width: `${notaInteligente}%` }}
            />
          </div>
          <div className="values">
            <span>{notaInteligente}%</span>
          </div>
        </div>

        <div className="score-section">
          <h4>Nota Sustentável</h4>
          <div className="progress-container">
            <div 
              className="progress-bar sustainable" 
              style={{ width: `${notaSustentavel}%` }}
            />
          </div>
          <div className="values">
            <span>{notaSustentavel}%</span>
          </div>
        </div>
      </div>

      <div className="indicators-detail">
        <div className="detail-item">
          <span className="label">IDHM:</span>
          <span className="value">{formatValue(indicator.IDHM)}</span>
        </div>
        <div className="detail-item">
          <span className="label">Expectativa de Vida:</span>
          <span className="value">{formatValue(indicator.ESPVIDA, 1)}</span>
        </div>
        <div className="detail-item">
          <span className="label">IDHM Renda:</span>
          <span className="value">{formatValue(indicator.IDHM_R)}</span>
        </div>
      </div>
    </div>
  );
}

export default IndicatorCard;