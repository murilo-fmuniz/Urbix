import React, { useState, useEffect } from 'react';
import { obterHistoricoIndicadores } from '../services/api';
import './HistoricoIndicadores.css';

/**
 * HistoricoIndicadores - Visualiza série histórica de indicadores de uma cidade
 * Mostra evolução dos 10 indicadores calculados ao longo do tempo
 */
function HistoricoIndicadores() {
  const [codigoIBGE, setCodigoIBGE] = useState('');
  const [nomeCidade, setNomeCidade] = useState('');
  const [historico, setHistorico] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selecionadosIndicadores, setSelecionadosIndicadores] = useState(new Set([
    'ECO_COMPETITIVIDADE',
    'EDU_ACESSO_QUALIDADE',
    'SAU_COBERTURA_QUALIDADE'
  ]));

  const indicadores = [
    { id: 'ECO_COMPETITIVIDADE', nome: '💰 Competitividade Econômica' },
    { id: 'EDU_ACESSO_QUALIDADE', nome: '📚 Educação - Acesso e Qualidade' },
    { id: 'SAU_COBERTURA_QUALIDADE', nome: '🏥 Saúde - Cobertura e Qualidade' },
    { id: 'HAB_HABITACAO_ADEQUADA', nome: '🏠 Habitação Adequada' },
    { id: 'AMB_QUALIDADE_AMBIENTAL', nome: '🌍 Qualidade Ambiental' },
    { id: 'GOV_TRANSPARENCIA_EFICIENCIA', nome: '📋 Governança - Transparência e Eficiência' },
    { id: 'SEG_PUBLICA', nome: '🛡️ Segurança Pública' },
    { id: 'RES_CIDADE', nome: '🏗️ Resiliência da Cidade' },
    { id: 'TECNOLOGIA_INOVACAO', nome: '🤖 Tecnologia e Inovação' },
    { id: 'PARTICIPACAO_SOCIAL', nome: '👥 Participação Social' }
  ];

  const carregarHistorico = async () => {
    if (!codigoIBGE || codigoIBGE.length !== 7) {
      setError('Código IBGE inválido (deve ter 7 dígitos)');
      return;
    }

    setLoading(true);
    setError('');
    setHistorico([]);

    try {
      const dados = await obterHistoricoIndicadores(codigoIBGE, 24);
      setHistorico(dados);
      if (dados.length > 0 && dados[0].nome_cidade) {
        setNomeCidade(dados[0].nome_cidade);
      }
    } catch (err) {
      setError(`Erro ao carregar histórico: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleIndicador = (indicadorId) => {
    const novo = new Set(selecionadosIndicadores);
    if (novo.has(indicadorId)) {
      novo.delete(indicadorId);
    } else {
      novo.add(indicadorId);
    }
    setSelecionadosIndicadores(novo);
  };

  const selecionarTodos = () => {
    setSelecionadosIndicadores(new Set(indicadores.map(ind => ind.id)));
  };

  const desmarcarTodos = () => {
    setSelecionadosIndicadores(new Set());
  };

  // Dados para o gráfico simplificado
  const renderGraficoSimples = () => {
    if (historico.length === 0) return null;

    const indicadoresSelecionados = Array.from(selecionadosIndicadores);
    
    return (
      <div className="grafico-container">
        <table className="grafico-tabela">
          <thead>
            <tr>
              <th>Período</th>
              {indicadoresSelecionados.map(ind => {
                const nome = indicadores.find(i => i.id === ind)?.nome || ind;
                return <th key={ind}>{nome}</th>;
              })}
            </tr>
          </thead>
          <tbody>
            {historico.slice().reverse().map((snapshot, idx) => (
              <tr key={idx} className="dados-row">
                <td className="periodo-cell">{snapshot.periodo_referencia}</td>
                {indicadoresSelecionados.map(ind => {
                  const valor = snapshot.indicadores?.[ind];
                  let cor = 'neutral';
                  if (valor !== undefined && valor !== null) {
                    const num = parseFloat(valor);
                    if (num >= 0.7) cor = 'alto';
                    else if (num >= 0.4) cor = 'medio';
                    else cor = 'baixo';
                  }
                  return (
                    <td key={ind} className={`valor-cell ${cor}`}>
                      {valor !== undefined && valor !== null 
                        ? typeof valor === 'number'
                          ? valor.toFixed(2)
                          : valor
                        : '-'
                      }
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="historico-indicadores-container">
      <div className="historico-header">
        <h2>📈 Histórico de Indicadores</h2>
        <p>Acompanhe a evolução dos indicadores calculados ao longo do tempo</p>
      </div>

      <div className="input-section">
        <div className="input-group">
          <label htmlFor="codigoIBGE">Código IBGE da Cidade:</label>
          <input
            type="text"
            id="codigoIBGE"
            value={codigoIBGE}
            onChange={(e) => setCodigoIBGE(e.target.value.replace(/\D/g, '').slice(0, 7))}
            placeholder="Ex: 4101408"
            maxLength="7"
            className="input-field"
          />
        </div>
        <button onClick={carregarHistorico} disabled={loading} className="btn btn-primary">
          {loading ? '⏳ Carregando...' : '🔍 Carregar Histórico'}
        </button>
      </div>

      {nomeCidade && (
        <div className="cidade-info">
          📍 <strong>{nomeCidade}</strong> - {codigoIBGE}
        </div>
      )}

      {error && <div className="alert alert-error">{error}</div>}

      {historico.length > 0 && (
        <div className="indicadores-selection">
          <h3>Selecione indicadores para visualizar:</h3>
          <div className="selection-buttons">
            <button 
              onClick={selecionarTodos} 
              className="btn btn-small"
              type="button"
            >
              ✓ Todos
            </button>
            <button 
              onClick={desmarcarTodos} 
              className="btn btn-small"
              type="button"
            >
              ✗ Nenhum
            </button>
          </div>
          <div className="indicadores-checkboxes">
            {indicadores.map(ind => (
              <label key={ind.id} className="checkbox-label">
                <input
                  type="checkbox"
                  checked={selecionadosIndicadores.has(ind.id)}
                  onChange={() => toggleIndicador(ind.id)}
                />
                <span>{ind.nome}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {historico.length > 0 && selecionadosIndicadores.size > 0 && (
        <div className="dados-section">
          {renderGraficoSimples()}
          <div className="legenda">
            <div className="legenda-item">
              <span className="legenda-cor alto"></span> Valores altos (≥ 0.70)
            </div>
            <div className="legenda-item">
              <span className="legenda-cor medio"></span> Valores médios (0.40 - 0.69)
            </div>
            <div className="legenda-item">
              <span className="legenda-cor baixo"></span> Valores baixos (< 0.40)
            </div>
          </div>
        </div>
      )}

      {!loading && historico.length === 0 && !error && (
        <div className="empty-state">
          📊 Insira um código IBGE e clique em "Carregar Histórico" para visualizar a série temporal dos indicadores
        </div>
      )}
    </div>
  );
}

export default HistoricoIndicadores;
