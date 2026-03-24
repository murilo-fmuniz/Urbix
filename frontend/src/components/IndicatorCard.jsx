import React from 'react';
import './IndicatorCard.css';

function IndicatorCard({ indicador }) {
  const { codigo_indicador, nome, grande_area, dados_coleta } = indicador;
  
  // Pegar a coleta mais recente
  const coletaAtual = dados_coleta && dados_coleta.length > 0 
    ? dados_coleta[dados_coleta.length - 1]
    : null;

  const formatValue = (value, decimals = 2) => {
    if (value === null || value === undefined || isNaN(value)) {
      return 'N/A';
    }
    return Number(value).toLocaleString('pt-BR', { 
      minimumFractionDigits: decimals, 
      maximumFractionDigits: decimals 
    });
  };

  const getStatusColor = (disponivel) => {
    return disponivel ? '#4CAF50' : '#f44336';
  };

  return (
    <div className="indicator-card card">
      <div className="card-header">
        <h3>{codigo_indicador}</h3>
        <span className={`badge ${grande_area?.toLowerCase().replace(/\s+/g, '-') || ''}`}>
          {grande_area || 'Sem categoria'}
        </span>
      </div>

      <p className="card-title">{nome}</p>

      {coletaAtual ? (
        <div className="card-content">
          <div className="data-item">
            <span className="label">Cidade:</span>
            <span className="value">{coletaAtual.cidade || 'N/A'}</span>
          </div>

          <div className="data-item">
            <span className="label">Ano:</span>
            <span className="value">{coletaAtual.ano_referencia || 'N/A'}</span>
          </div>

          <div className="data-item">
            <span className="label">Valor Final:</span>
            <span className="value">{formatValue(coletaAtual.valor_final)}</span>
          </div>

          <div className="data-item">
            <span className="label">Numerador:</span>
            <span className="value">{formatValue(coletaAtual.valor_numerador)}</span>
          </div>

          <div className="data-item">
            <span className="label">Denominador:</span>
            <span className="value">{formatValue(coletaAtual.valor_denominador)}</span>
          </div>

          <div className="data-item status">
            <span className="label">Status:</span>
            <span 
              className={`status-badge ${coletaAtual.dado_disponivel ? 'disponivel' : 'indisponivel'}`}
              style={{ backgroundColor: getStatusColor(coletaAtual.dado_disponivel) }}
            >
              {coletaAtual.dado_disponivel ? '✓ Disponível' : '✗ Indisponível'}
            </span>
          </div>

          {coletaAtual.auditoria && (
            <div className="auditoria-section">
              <h4>Auditoria</h4>
              <p><strong>Fonte:</strong> {coletaAtual.auditoria.fonte_nome}</p>
              {coletaAtual.auditoria.fonte_url && (
                <p><strong>URL:</strong> <a href={coletaAtual.auditoria.fonte_url} target="_blank" rel="noopener noreferrer">{coletaAtual.auditoria.fonte_url}</a></p>
              )}
              <p><strong>Data Extração:</strong> {coletaAtual.auditoria.data_extracao || 'N/A'}</p>
              {coletaAtual.auditoria.observacoes && (
                <p><strong>Observações:</strong> {coletaAtual.auditoria.observacoes}</p>
              )}
            </div>
          )}
        </div>
      ) : (
        <div className="no-data">
          <p>Sem dados de coleta</p>
        </div>
      )}
    </div>
  );
}

export default IndicatorCard;