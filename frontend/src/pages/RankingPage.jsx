import React, { useState } from 'react';
import { getHybridRanking } from '../services/api';
import CityInputForm from '../components/CityInputForm';
import RankingTable from '../components/RankingTable';
import IndicatorsComparisonChart from '../components/IndicatorsComparisonChart';
import './RankingPage.css';

function RankingPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState('ranking'); // 'ranking' ou 'indicadores'

  const handleSubmit = async (cities) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // ✅ Validar que todas as cidades têm código IBGE e nome
      const incompleteCities = cities.filter(
        c => !c.codigo_ibge?.trim() || !c.nome_cidade?.trim()
      );
      if (incompleteCities.length > 0) {
        throw new Error(`${incompleteCities.length} cidade(s) sem Código IBGE ou Nome preenchidos`);
      }

      // Formatar payload conforme esperado pelo backend (CityHybridInput)
      const payload = cities.map(city => ({
        codigo_ibge: city.codigo_ibge,
        nome_cidade: city.nome_cidade,  // ✅ Campo obrigatório
        manual_indicators: city.manual_indicators || null,
      }));

      // ✅ Validar mínimo 2 cidades
      if (payload.length < 2) {
        throw new Error(`Mínimo 2 cidades requeridas para TOPSIS. Recebido: ${payload.length}`);
      }

      console.log('📤 Enviando payload:', payload);
      const rankingResult = await getHybridRanking(payload);
      console.log('📥 Resultado recebido:', rankingResult);

      setResult(rankingResult);
      setActiveTab('ranking');
    } catch (err) {
      console.error('❌ Erro ao gerar ranking:', err);
      // Tratar diferentes tipos de erros
      let errorMessage = 'Erro desconhecido ao gerar ranking';
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (err?.detail) {
        errorMessage = err.detail;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else {
        errorMessage = JSON.stringify(err) || 'Erro ao processar resposta do servidor';
      }
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ranking-page container">
      <div className="ranking-header">
        <h1>🏆 Ranking TOPSIS de Cidades Inteligentes</h1>
        <p className="subtitle">
          Análise TOPSIS com dados híbridos (APIs governamentais + indicadores manual da prefeitura)
        </p>
      </div>

      {/* SEÇÃO DE ENTRADA */}
      <div className="input-section">
        <CityInputForm onSubmit={handleSubmit} loading={loading} />
      </div>

      {/* MENSAGENS DE ERRO */}
      {error && (
        <div className="alert alert-error">
          <span>⚠️ {error}</span>
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      {/* LOADING STATE */}
      {loading && (
        <div className="alert alert-loading">
          <div className="spinner"></div>
          <span>Processando cidades e calculando ranking...</span>
        </div>
      )}

      {/* RESULTADOS */}
      {result && (
        <div className="results-section">
          <div className="tabs">
            <button
              className={`tab-btn ${activeTab === 'ranking' ? 'active' : ''}`}
              onClick={() => setActiveTab('ranking')}
            >
              🏅 Ranking Final
            </button>
            <button
              className={`tab-btn ${activeTab === 'indicadores' ? 'active' : ''}`}
              onClick={() => setActiveTab('indicadores')}
            >
              📊 Comparação de Indicadores
            </button>
          </div>

          {activeTab === 'ranking' && (
            <RankingTable ranking={result.ranking} detalhes={result.detalhes_calculo} />
          )}

          {activeTab === 'indicadores' && (
            <IndicatorsComparisonChart
              cidades={result.ranking.map(r => r.nome_cidade)}
              matrizDecisao={result.detalhes_calculo.matriz_normalizada || result.detalhes_calculo.matriz}
              indicadores={result.detalhes_calculo.indicadores_nomes}
            />
          )}
        </div>
      )}

      {/* VAZIO */}
      {!result && !loading && (
        <div className="empty-state">
          <p>Selecione cidades acima e clique em "Gerar Ranking" para começar</p>
        </div>
      )}
    </div>
  );
}

export default RankingPage;
