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

      // ✅ Validar mínimo 2 cidades
      if (cities.length < 2) {
        throw new Error(`Mínimo 2 cidades requeridas para TOPSIS. Recebido: ${cities.length}`);
      }

      // 1. Extrair a lista de IBGEs para o schema do backend
      const cidades_ibge = cities.map(city => city.codigo_ibge.trim());

      // 2. Montar as simulações no formato flat (valores_brutos)
      const simulacoes = cities.map(city => {
        const raw = city.manual_indicators || {};
        const valores_brutos = {};
        
        // Garante que só mandamos números válidos para o Pydantic
        Object.entries(raw).forEach(([k, v]) => {
          if (v !== '' && v !== null && !isNaN(v)) {
            valores_brutos[k] = Number(v);
          }
        });

        return {
          codigo_ibge: city.codigo_ibge.trim(),
          valores_brutos: valores_brutos
        };
      });

      // 3. Montar o payload no padrão exato do TopsisSimulationRequest
      const payload = {
        cidades_ibge: cidades_ibge,
        simulacoes: simulacoes
      };

      console.log('📤 Enviando payload:', JSON.stringify(payload, null, 2));
      const data = await getHybridRanking(payload);
      console.log('📥 Resultado recebido (bruto):', data);

      // 4. Traduzir a resposta (Array) para o formato que a UI da RankingPage espera (Objeto)
      const rankingResult = {
        ranking: data.map(item => ({
          ...item,
          indice_smart: item.pontuacao_topsis // Ajuste do nome da variável
        })),
        detalhes_calculo: {
          matriz_normalizada: data.map(item => ({
            cidade: item.nome_cidade,
            ...item.valores_calculados
          })),
          indicadores_nomes: Object.keys(data[0]?.valores_calculados || {})
        }
      };

      setResult(rankingResult);
      setActiveTab('ranking');
    } catch (err) {
      console.error('❌ Erro ao gerar ranking:', err);
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
