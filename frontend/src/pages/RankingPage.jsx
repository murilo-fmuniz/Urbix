import React, { useState } from 'react';
import { getHybridRanking, getIndicadores } from '../services/api';
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
      // ✅ Validações
      const incompleteCities = cities.filter(
        c => !c.codigo_ibge?.trim() || !c.nome_cidade?.trim()
      );
      if (incompleteCities.length > 0) {
        throw new Error(`${incompleteCities.length} cidade(s) sem Código IBGE ou Nome preenchidos`);
      }

      if (cities.length < 2) {
        throw new Error(`Mínimo 2 cidades requeridas para TOPSIS. Recebido: ${cities.length}`);
      }

      // 1. Extrair IBGEs e montar Simulações
      const cidades_ibge = cities.map(city => city.codigo_ibge.trim());
      const simulacoes = cities.map(city => {
        const raw = city.manual_indicators || {};
        const valores_brutos = {};
        
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

      const payload = {
        cidades_ibge: cidades_ibge,
        simulacoes: simulacoes
      };

      console.log('📤 Enviando payload:', JSON.stringify(payload, null, 2));
      
      // ✅ A MÁGICA ACONTECE AQUI: Dispara as duas consultas ao mesmo tempo (Cálculo + Catálogo)
      const [data, infoIndicadores] = await Promise.all([
        getHybridRanking(payload),
        getIndicadores().catch(() => []) // Fallback de segurança se a rota falhar
      ]);
      
      console.log('📥 Resultado recebido (bruto):', data);

      // ✅ Mapeando os Pesos e Impactos do Backend
      const pesosMap = {};
      const impactosMap = {};
      
      if (infoIndicadores && infoIndicadores.length > 0) {
        infoIndicadores.forEach(ind => {
          pesosMap[ind.id] = ind.peso;
          impactosMap[ind.id] = ind.impacto;
        });
      }

      // Extrai os nomes que o TOPSIS usou no cálculo
      const indicadoresNomes = Object.keys(data[0]?.valores_calculados || {});
      
      // Constrói os arrays de Pesos e Impactos na mesma ordem (com valores de fallback)
      const pesosExtraidos = indicadoresNomes.map(nome => pesosMap[nome] ?? 0.02);
      const impactosExtraidos = indicadoresNomes.map(nome => impactosMap[nome] ?? 1);

      // 4. Traduzir a resposta para a Interface
      const rankingResult = {
        ranking: data.map(item => ({
          ...item,
          indice_smart: item.pontuacao_topsis
        })),
        detalhes_calculo: {
          matriz_normalizada: data.map(item => ({
            cidade: item.nome_cidade,
            ...item.valores_calculados
          })),
          indicadores_nomes: indicadoresNomes,
          pesos: pesosExtraidos,      // 🚀 INJETADO NA TELA!
          impactos: impactosExtraidos // 🚀 INJETADO NA TELA!
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
