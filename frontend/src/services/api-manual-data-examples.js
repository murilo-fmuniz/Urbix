/**
 * Exemplos de como consumir os novos endpoints de Dados Manuais
 * 
 * Adicionar ao frontend/src/services/api.js
 */

// ==========================================
// DADOS MANUAIS - CRUD
// ==========================================

/**
 * Salvar ou atualizar dados manuais de uma cidade
 */
export const salvarDadosManuais = async (codigoIbge, dadosManuals) => {
  try {
    const response = await api.post(`/manual-data/${codigoIbge}`, dadosManuals);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Erro ao salvar dados manuais');
  }
};

/**
 * Obter dados manuais atuais de uma cidade
 */
export const obterDadosManuais = async (codigoIbge) => {
  try {
    const response = await api.get(`/manual-data/${codigoIbge}`);
    return response.data;
  } catch (error) {
    if (error.response?.status === 404) {
      return null; // Nenhum dado manual salvo ainda
    }
    throw new Error(error.response?.data?.detail || 'Erro ao obter dados manuais');
  }
};

/**
 * Atualizar parcialmente dados manuais (PATCH)
 */
export const atualizarDadosManuaisParcial = async (codigoIbge, dadosParaAtualizar) => {
  try {
    const response = await api.patch(`/manual-data/${codigoIbge}`, dadosParaAtualizar);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Erro ao atualizar dados manuais');
  }
};

// ==========================================
// HISTÓRICO E AUDITORIA
// ==========================================

/**
 * Obter histórico completo de alterações
 */
export const obterHistoricoAlteracoes = async (codigoIbge, limite = 50) => {
  try {
    const response = await api.get(`/manual-data/${codigoIbge}/history?limit=${limite}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Erro ao obter histórico');
  }
};

// ==========================================
// SÉRIE HISTÓRICA - INDICADORES
// ==========================================

/**
 * Obter série histórica de indicadores (últimos 52 períodos = ~1 ano)
 */
export const obterHistoricoIndicadores = async (codigoIbge, limite = 52) => {
  try {
    const response = await api.get(
      `/manual-data/${codigoIbge}/indicadores/historico?limit=${limite}`
    );
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Erro ao obter histórico de indicadores');
  }
};

// ==========================================
// SÉRIE HISTÓRICA - RANKINGS
// ==========================================

/**
 * Obter histórico de rankings (últimos 24 períodos = ~2 anos)
 */
export const obterHistoricoRankings = async (limite = 24) => {
  try {
    const response = await api.get(`/manual-data/rankings/historico?limit=${limite}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Erro ao obter histórico de rankings');
  }
};

/**
 * Obter ranking de um período específico (ex: "2025-03")
 */
export const obterRankingPorPeriodo = async (periodoReferencia) => {
  try {
    const response = await api.get(`/manual-data/rankings/periodo/${periodoReferencia}`);
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Erro ao obter ranking do período');
  }
};

// ==========================================
// EXEMPLO DE USO EM COMPONENTES REACT
// ==========================================

import React, { useState, useEffect } from 'react';
import {
  salvarDadosManuais,
  obterDadosManuais,
  obterHistoricoAlteracoes,
  obterHistoricoIndicadores,
  obterHistoricoRankings,
} from '../services/api';

/**
 * EXEMPLO 1: Formulário para Atualizar Dados Manuais
 */
function ManualDataForm({ codigoIbge }) {
  const [formData, setFormData] = useState({
    pontos_iluminacao_telegestao: 0,
    medidores_inteligentes_energia: 0,
    bombeiros_por_100k: 0,
    area_verde_mapeada: 0,
    usuario_atualizou: '',
    motivo_atualizacao: '',
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSalvar = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const resultado = await salvarDadosManuais(codigoIbge, formData);
      setMessage(`✅ Dados salvos com sucesso! Atualizado em ${resultado.data_atualizacao}`);
    } catch (error) {
      setMessage(`❌ Erro: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSalvar}>
      <input
        type="number"
        placeholder="Iluminação com Telegestão (%)"
        value={formData.pontos_iluminacao_telegestao}
        onChange={(e) =>
          setFormData({ ...formData, pontos_iluminacao_telegestao: Number(e.target.value) })
        }
      />
      {/* Outros campos... */}
      <button type="submit" disabled={loading}>
        {loading ? 'Salvando...' : 'Salvar Dados'}
      </button>
      {message && <p>{message}</p>}
    </form>
  );
}

/**
 * EXEMPLO 2: Visualizar Histórico de Alterações
 */
function HistoricoAlteracoes({ codigoIbge }) {
  const [historico, setHistorico] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregarHistorico = async () => {
      try {
        const dados = await obterHistoricoAlteracoes(codigoIbge, 20);
        setHistorico(dados);
      } catch (error) {
        console.error('Erro:', error);
      } finally {
        setLoading(false);
      }
    };

    carregarHistorico();
  }, [codigoIbge]);

  if (loading) return <div>Carregando histórico...</div>;

  return (
    <div className="historico">
      <h3>📋 Histórico de Alterações</h3>
      {historico.length === 0 ? (
        <p>Nenhuma alteração registrada</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Data</th>
              <th>Usuário</th>
              <th>Alterações</th>
              <th>Motivo</th>
            </tr>
          </thead>
          <tbody>
            {historico.map((item, idx) => (
              <tr key={idx}>
                <td>{new Date(item.data_alteracao).toLocaleDateString('pt-BR')}</td>
                <td>{item.usuario_atualizou || 'Sistema'}</td>
                <td>{item.alteracoes_resumo}</td>
                <td>{item.motivo_atualizacao || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

/**
 * EXEMPLO 3: Gráfico de Evolução de Indicadores
 */
function GraficoEvolucaoIndicadores({ codigoIbge }) {
  const [dados, setDados] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregarDados = async () => {
      try {
        const historico = await obterHistoricoIndicadores(codigoIbge, 52);
        setDados(historico);
      } catch (error) {
        console.error('Erro:', error);
      } finally {
        setLoading(false);
      }
    };

    carregarDados();
  }, [codigoIbge]);

  if (loading) return <div>Carregando gráfico...</div>;

  // Preparar dados para gráfico (crescente por tempo)
  const dadosOrdenados = dados.reverse();
  
  return (
    <div className="grafico-evolucao">
      <h3>📈 Evolução de Indicadores (Últimos 12 meses)</h3>
      {/* Usar Chart.js ou similar para visualizar dados */}
      <pre>{JSON.stringify(dadosOrdenados.slice(0, 3), null, 2)}</pre>
    </div>
  );
}

/**
 * EXEMPLO 4: Comparação de Rankings Temporais
 */
function ComparativoRankings() {
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const carregarRankings = async () => {
      try {
        // Obter últimos 6 rankings (últimos 6 meses)
        const historico = await obterHistoricoRankings(6);
        setRankings(historico);
      } catch (error) {
        console.error('Erro:', error);
      } finally {
        setLoading(false);
      }
    };

    carregarRankings();
  }, []);

  if (loading) return <div>Carregando rankings...</div>;

  return (
    <div className="comparativo-rankings">
      <h3>🏆 Evolução dos Rankings</h3>
      <table>
        <thead>
          <tr>
            <th>Período</th>
            <th>1º Lugar</th>
            <th>2º Lugar</th>
            <th>3º Lugar</th>
          </tr>
        </thead>
        <tbody>
          {rankings.map((ranking, idx) => (
            <tr key={idx}>
              <td><strong>{ranking.periodo_referencia}</strong></td>
              {ranking.ranking_data.slice(0, 3).map((city) => (
                <td key={city.nome_cidade}>
                  {city.nome_cidade} ({(city.indice_smart * 100).toFixed(2)}%)
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export {
  ManualDataForm,
  HistoricoAlteracoes,
  GraficoEvolucaoIndicadores,
  ComparativoRankings,
};
