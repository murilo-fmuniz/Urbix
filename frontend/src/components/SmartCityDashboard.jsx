import React, { useState, useCallback, useMemo } from 'react';
import {
  BarChart3,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Loader,
  ChevronDown,
  Home,
  Zap,
  Shield,
} from 'lucide-react';
import IndicatorsComparisonChart from './IndicatorsComparisonChart';
import { INDICADORES_CONFIG, INDICADORES_INICIAL } from './ManualDataForm';

// ✅ GERAR TABS DINAMICAMENTE A PARTIR DE INDICADORES_CONFIG
const TABS = Object.entries(INDICADORES_CONFIG).map(([isoKey, config]) => ({
  id: isoKey,
  label: config.label,
  icon: isoKey === 'iso_37120' ? Home : isoKey === 'iso_37122' ? Zap : Shield,
  color:
    isoKey === 'iso_37120'
      ? 'from-orange-500 to-orange-600'
      : isoKey === 'iso_37122'
        ? 'from-purple-500 to-purple-600'
        : 'from-blue-500 to-blue-600',
  description: config.description,
}));

// ✅ DADOS INICIAIS: 3 cidades com TODOS os 47 indicadores (via INDICADORES_INICIAL)
const INITIAL_CITIES = [
  {
    codigo_ibge: '4101408',
    nome: 'Apucarana',
    estado: 'PR',
    ...INDICADORES_INICIAL,
  },
  {
    codigo_ibge: '4113700',
    nome: 'Londrina',
    estado: 'PR',
    ...INDICADORES_INICIAL,
  },
  {
    codigo_ibge: '4115200',
    nome: 'Maringá',
    estado: 'PR',
    ...INDICADORES_INICIAL,
  },
];

export default function SmartCityDashboard() {
  // ESTADO PRINCIPAL
  const [citiesData, setCitiesData] = useState(INITIAL_CITIES);
  const [selectedCityIndex, setSelectedCityIndex] = useState(0);
  const [selectedTabId, setSelectedTabId] = useState('iso_37120');
  const [selectedResultsTab, setSelectedResultsTab] = useState('ranking'); // 'ranking', 'comparacao', 'detalhes'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // ✅ CALCULAR CIDADE SELECIONADA
  const selectedCity = useMemo(
    () => citiesData[selectedCityIndex] || citiesData[0],
    [citiesData, selectedCityIndex]
  );

  // VALIDAR SE CIDADES ESTÃO COMPLETAS
  const validateCitiesComplete = useMemo(() => {
    return citiesData.every(
      (city) =>
        city.codigo_ibge?.trim() && // Não vazio
        city.nome?.trim() // Não vazio
    );
  }, [citiesData]);

  // CONTAR CIDADES INCOMPLETAS (PARA MENSAGEM DE ERRO)
  const incompleteCities = useMemo(() => {
    return citiesData.filter(
      (city) => !city.codigo_ibge?.trim() || !city.nome?.trim()
    ).length;
  }, [citiesData]);

  // DADOS DA ABA SELECIONADA
  const selectedTabData = useMemo(
    () => selectedCity[selectedTabId],
    [selectedCity, selectedTabId]
  );

  const selectedTab = useMemo(
    () => TABS.find((tab) => tab.id === selectedTabId),
    [selectedTabId]
  );

  // HANDLERS
  const handleInputChange = useCallback((field, value) => {
    setCitiesData((prevCities) => {
      const newCities = [...prevCities];
      newCities[selectedCityIndex] = {
        ...newCities[selectedCityIndex],
        [selectedTabId]: {
          ...newCities[selectedCityIndex][selectedTabId],
          [field]: parseFloat(value) || 0,
        },
      };
      return newCities;
    });
  }, [selectedCityIndex, selectedTabId]);

  const handleCityChange = useCallback((index) => {
    setSelectedCityIndex(index);
    setSelectedTabId('iso_37120'); // Reset para primeira aba
  }, []);

  const handleTabChange = useCallback((tabId) => {
    setSelectedTabId(tabId);
    setError(null); // Limpar erros ao trocar aba
  }, []);

  // SUBMIT PARA API
  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSubmitSuccess(false);

    try {
      // Validar mínimo de 2 cidades
      if (citiesData.length < 2) {
        throw new Error(`Mínimo 2 cidades requeridas. Atualmente: ${citiesData.length} cidade(s)`);
      }

      // ✅ Validar campos obrigatórios em todas as cidades
      for (let i = 0; i < citiesData.length; i++) {
        const city = citiesData[i];
        if (!city.codigo_ibge?.trim()) {
          throw new Error(`Cidade ${i + 1}: Código IBGE é obrigatório`);
        }
        if (city.codigo_ibge.trim().length !== 7 || !/^\d+$/.test(city.codigo_ibge.trim())) {
          throw new Error(`Cidade ${i + 1}: Código IBGE deve ter exatamente 7 dígitos numéricos`);
        }
        if (!city.nome?.trim()) {
          throw new Error(`Cidade ${i + 1}: Nome da cidade é obrigatório`);
        }
      }

      // ✅ CORRIGIDO: Payload com TODOS os 47 indicadores (3 ISO standards completos)
      const payload = citiesData.map((city) => ({
        codigo_ibge: city.codigo_ibge,
        nome_cidade: city.nome,
        manual_indicators: {
          iso_37120: city.iso_37120,  // ✅ 16 indicadores
          iso_37122: city.iso_37122,  // ✅ 15 indicadores
          iso_37123: city.iso_37123,  // ✅ 16 indicadores
        },
      }));

      console.log('📤 Enviando payload (47 indicadores):', JSON.stringify(payload, null, 2));

      const response = await fetch(
        'http://localhost:8000/api/v1/topsis/ranking-hibrido',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(payload),
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail || `Erro ${response.status}: ${response.statusText}`
        );
      }

      const data = await response.json();
      console.log('✅ Resposta do servidor:', data);

      setResults(data);
      setSubmitSuccess(true);
      setTimeout(() => setSubmitSuccess(false), 4000);
    } catch (err) {
      console.error('❌ Erro ao enviar:', err);
      setError(err.message || 'Erro ao enviar dados para o servidor');
    } finally {
      setLoading(false);
    }
  }, [citiesData]);

  const handleReset = useCallback(() => {
    setCitiesData(INITIAL_CITIES);
    setResults(null);
    setError(null);
    setSubmitSuccess(false);
    setSelectedCityIndex(0);
    setSelectedTabId('iso_37120');
  }, []);

  // ✅ NOVO: Adicionar cidade dinamicamente com TODOS os 47 indicadores
  const handleAddCity = useCallback(() => {
    const newCity = {
      codigo_ibge: '',
      nome: '',
      estado: 'PR',
      ...INDICADORES_INICIAL,  // ✅ Usa todos os 47 indicadores inicializados a 0
    };
    setCitiesData((prev) => [...prev, newCity]);
    setSelectedCityIndex(citiesData.length); // Seleciona a nova cidade
    setResults(null); // Reset results when modifying cities
    setSelectedResultsTab('ranking'); // Reset to first results tab
  }, [citiesData.length]);

  // ✅ NOVO: Remover cidade
  const handleRemoveCity = useCallback((index) => {
    if (citiesData.length <= 1) {
      setError('Deve haver pelo menos 1 cidade no projeto');
      return;
    }
    setCitiesData((prev) => prev.filter((_, i) => i !== index));
    if (selectedCityIndex >= citiesData.length - 1) {
      setSelectedCityIndex(Math.max(0, citiesData.length - 2));
    }
    setResults(null); // Reset results when modifying cities
    setSelectedResultsTab('ranking'); // Reset to first results tab
  }, [citiesData.length, selectedCityIndex]);

  // ✅ RENDERIZAR INPUTS DINÂMICAMENTE A PARTIR DO INDICADORES_CONFIG
  const renderTabInputs = () => {
    const tabConfig = INDICADORES_CONFIG[selectedTabId];
    if (!tabConfig || !tabConfig.campos) {
      return <p className="text-gray-500">Nenhum campo configurado para esta aba</p>;
    }

    const cityTabData = selectedTabData;

    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {tabConfig.campos.map((campo) => (
          <div key={campo.key} className="relative group">
            <label
              htmlFor={campo.key}
              className="block text-sm font-semibold text-gray-700 mb-2 group-hover:text-orange-600 transition"
            >
              {campo.label}
              <span className="ml-2 text-xs text-gray-500">
                ({campo.unit})
              </span>
            </label>

            <div className="relative">
              <input
                id={campo.key}
                type="number"
                step="0.1"
                min="0"
                value={cityTabData[campo.key] || ''}
                onChange={(e) => handleInputChange(campo.key, e.target.value)}
                placeholder={campo.placeholder}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:border-orange-500 focus:outline-none transition bg-white hover:border-gray-300 disabled:bg-gray-100 disabled:cursor-not-allowed"
                disabled={loading}
              />
            </div>

            <p className="mt-1 text-xs text-gray-500 italic">
              {campo.help}
            </p>
          </div>
        ))}
      </div>
    );
  };

  // RENDERIZAR RESULTADOS
  const renderResults = () => {
    if (!results) return null;

    const ranking = results.ranking || [];
    const detalhes = results.detalhes_calculo || {};

    return (
      <div className="mt-8 bg-gradient-to-br from-emerald-50 to-green-50 rounded-2xl p-8 border-2 border-emerald-200">
        <div className="flex items-center gap-3 mb-6">
          <CheckCircle className="w-8 h-8 text-emerald-600" />
          <h2 className="text-2xl font-bold text-emerald-900">
            Resultados do Ranking TOPSIS
          </h2>
        </div>

        {/* ÍNDICE SMART GERAL (média dos rankings) */}
        {ranking.length > 0 && (
          <div className="mb-8 bg-white rounded-lg p-6 border-l-4 border-orange-500">
            <p className="text-gray-600 text-sm font-semibold uppercase">
              Índice Smart City Médio
            </p>
            <p className="text-4xl font-bold text-orange-600 mt-2">
              {(ranking.reduce((sum, city) => sum + city.indice_smart, 0) / ranking.length).toFixed(4)}
            </p>
            <p className="text-gray-500 text-xs mt-2">
              Média da pontuação TOPSIS de {ranking.length} cidade(s)
            </p>
          </div>
        )}

        {/* TABELA RANKING */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gradient-to-r from-emerald-500 to-green-600 text-white">
                <th className="px-4 py-3 text-left font-semibold">Posição</th>
                <th className="px-4 py-3 text-left font-semibold">Cidade</th>
                <th className="px-4 py-3 text-right font-semibold">
                  Score TOPSIS
                </th>
                <th className="px-4 py-3 text-right font-semibold">
                  Similaridade (%)
                </th>
              </tr>
            </thead>
            <tbody>
              {ranking.map((item, idx) => {
                const medalhas = ['🥇', '🥈', '🥉'];
                const medalha = medalhas[idx] || '•';
                const scoreValue = parseFloat(item.indice_smart || 0);  // ✅ CORRIGIDO: indice_smart
                const similarityPct = (scoreValue * 100).toFixed(2);

                return (
                  <tr
                    key={item.nome_cidade}  // ✅ CORRIGIDO: nome_cidade como key
                    className={`border-b-2 transition ${
                      idx === 0
                        ? 'bg-emerald-100 border-emerald-300'
                        : idx === 1
                          ? 'bg-green-50 border-green-200'
                          : 'bg-white border-gray-200'
                    }`}
                  >
                    <td className="px-4 py-4 font-bold text-lg">
                      {medalha} #{idx + 1}
                    </td>
                    <td className="px-4 py-4 font-semibold text-gray-800">
                      {item.nome_cidade}  {/* ✅ CORRIGIDO: nome_cidade */}
                    </td>
                    <td className="px-4 py-4 text-right font-mono text-orange-600">
                      {scoreValue.toFixed(4)}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <span
                        className={`inline-block px-3 py-1 rounded-full font-semibold text-sm ${
                          scoreValue >= 0.7
                            ? 'bg-emerald-200 text-emerald-800'
                            : scoreValue >= 0.4
                              ? 'bg-yellow-200 text-yellow-800'
                              : 'bg-red-200 text-red-800'
                        }`}
                      >
                        {similarityPct}%
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* LEGENDA */}
        <div className="mt-6 grid grid-cols-3 gap-4">
          <div className="bg-emerald-100 rounded-lg p-3">
            <p className="text-xs text-gray-600">Alto Desempenho</p>
            <p className="text-sm font-bold text-emerald-800">≥ 0.70 (70%)</p>
          </div>
          <div className="bg-yellow-100 rounded-lg p-3">
            <p className="text-xs text-gray-600">Desempenho Médio</p>
            <p className="text-sm font-bold text-yellow-800">0.40 - 0.69</p>
          </div>
          <div className="bg-red-100 rounded-lg p-3">
            <p className="text-xs text-gray-600">Baixo Desempenho</p>
            <p className="text-sm font-bold text-red-800">&lt; 0.40</p>
          </div>
        </div>

        {/* ABAS PARA RESULTADOS DETALHADOS */}
        <div className="mt-8 border-t-2 border-emerald-300 pt-6">
          <div className="flex gap-3 mb-6">
            <button
              onClick={() => setSelectedResultsTab('comparacao')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                selectedResultsTab === 'comparacao'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              📊 Comparação de Indicadores
            </button>
            <button
              onClick={() => setSelectedResultsTab('detalhes')}
              className={`px-4 py-2 rounded-lg font-semibold transition ${
                selectedResultsTab === 'detalhes'
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              📋 Detalhes do Cálculo
            </button>
          </div>

          {/* COMPARAÇÃO DE INDICADORES */}
          {selectedResultsTab === 'comparacao' && detalhes.matriz_normalizada && (
            <div className="bg-white rounded-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Comparação de Indicadores TOPSIS</h3>
              <IndicatorsComparisonChart
                cidades={ranking.map((r) => r.nome_cidade)}
                matrizDecisao={detalhes.matriz_normalizada || detalhes.matriz_decisao || []}
                indicadores={detalhes.indicadores || []}
              />
            </div>
          )}

          {/* DETALHES DO CÁLCULO */}
          {selectedResultsTab === 'detalhes' && (
            <div className="bg-white rounded-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">Detalhes do Cálculo TOPSIS</h3>
              
              {detalhes.indicadores && detalhes.indicadores.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-lg text-gray-700 mb-3">Indicadores Utilizados:</h4>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    {detalhes.indicadores.map((ind, i) => (
                      <li key={i}>{ind}</li>
                    ))}
                  </ul>
                </div>
              )}

              {detalhes.pesos && detalhes.pesos.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-lg text-gray-700 mb-3">Pesos:</h4>
                  <div className="grid grid-cols-2 gap-3">
                    {detalhes.pesos.map((peso, i) => (
                      <div key={i} className="bg-orange-50 p-3 rounded border-l-4 border-orange-500">
                        <p className="text-sm text-gray-600">
                          {detalhes.indicadores?.[i] || `Indicador ${i + 1}`}
                        </p>
                        <p className="text-lg font-bold text-orange-600">{(peso * 100).toFixed(1)}%</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {detalhes.impactos && detalhes.impactos.length > 0 && (
                <div className="mb-6">
                  <h4 className="font-semibold text-lg text-gray-700 mb-3">Impactos:</h4>
                  <div className="grid grid-cols-2 gap-3">
                    {detalhes.impactos.map((impacto, i) => (
                      <div key={i} className="bg-purple-50 p-3 rounded border-l-4 border-purple-500">
                        <p className="text-sm text-gray-600">
                          {detalhes.indicadores?.[i] || `Indicador ${i + 1}`}
                        </p>
                        <p className="text-lg font-bold text-purple-600">
                          {impacto === 1 ? '✅ Benefício' : '⚠️ Custo'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {detalhes.distancia_para_positiva && (
                <div className="grid grid-cols-2 gap-6 mt-6 pt-6 border-t">
                  <div className="bg-green-50 p-4 rounded">
                    <h5 className="font-semibold text-green-800 mb-2">Distância Ideal Positiva</h5>
                    <p className="text-xs text-gray-600">
                      {Array.isArray(detalhes.distancia_para_positiva)
                        ? detalhes.distancia_para_positiva.map((d) => d.toFixed(4)).join(', ')
                        : JSON.stringify(detalhes.distancia_para_positiva)}
                    </p>
                  </div>
                  <div className="bg-red-50 p-4 rounded">
                    <h5 className="font-semibold text-red-800 mb-2">Distância Ideal Negativa</h5>
                    <p className="text-xs text-gray-600">
                      {Array.isArray(detalhes.distancia_para_negativa)
                        ? detalhes.distancia_para_negativa.map((d) => d.toFixed(4)).join(', ')
                        : JSON.stringify(detalhes.distancia_para_negativa)}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* HEADER */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <BarChart3 className="w-10 h-10 text-blue-400" />
            <h1 className="text-4xl font-bold text-white">Smart City Dashboard</h1>
          </div>
          <p className="text-gray-400 ml-13">
            Sistema de Monitoramento Híbrido com Normas ISO 37120, 37122 e 37123
          </p>
        </div>

        {/* ALERTS */}
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 rounded-lg p-4 flex gap-3">
            <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-red-900">Erro ao enviar dados</p>
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          </div>
        )}

        {submitSuccess && (
          <div className="mb-6 bg-emerald-50 border-l-4 border-emerald-500 rounded-lg p-4 flex gap-3 animate-in fade-in duration-300">
            <CheckCircle className="w-6 h-6 text-emerald-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-emerald-900">Sucesso!</p>
              <p className="text-emerald-700 text-sm">
                Dados enviados e ranking calculado com sucesso.
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* SIDEBAR - SELETOR DE CIDADES */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg overflow-hidden sticky top-6">
              {/* HEADER DO SIDEBAR */}
              <div className="bg-gradient-to-r from-orange-600 to-orange-700 px-6 py-4">
                <h3 className="text-white font-bold text-lg">
                  Cidades ({citiesData.length})
                </h3>
              </div>

              {/* VALIDAÇÃO MÍNIMO DE CIDADES */}
              {citiesData.length < 2 && (
                <div className="bg-yellow-50 border-l-4 border-yellow-500 p-3 m-4">
                  <p className="text-xs text-yellow-800 font-semibold">
                    ⚠️ Mínimo 2 cidades necessárias
                  </p>
                  <p className="text-xs text-yellow-700 mt-1">
                    Atualmente: {citiesData.length} cidade(s)
                  </p>
                </div>
              )}

              {/* VALIDAÇÃO CIDADES INCOMPLETAS */}
              {incompleteCities > 0 && (
                <div className="bg-red-50 border-l-4 border-red-500 p-3 m-4">
                  <p className="text-xs text-red-800 font-semibold">
                    ❌ Cidades Incompletas: {incompleteCities}
                  </p>
                  <p className="text-xs text-red-700 mt-1">
                    Código IBGE e Nome são obrigatórios
                  </p>
                </div>
              )}

              {/* LISTA DE CIDADES */}
              <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                {citiesData.map((city, idx) => {
                  const isIncomplete = !city.codigo_ibge?.trim() || !city.nome?.trim();
                  return (
                    <div
                      key={idx}
                      className={`px-6 py-4 transition ${
                        selectedCityIndex === idx
                          ? 'bg-orange-50 border-l-4 border-orange-600'
                          : 'border-l-4 border-transparent'
                      } ${isIncomplete ? 'bg-red-50' : ''}`}
                    >
                      <button
                        onClick={() => handleCityChange(idx)}
                        disabled={loading}
                        className={`w-full text-left transition transform hover:scale-105 ${
                          loading ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        <div className="font-semibold text-gray-900 flex items-center gap-2">
                          {city.nome || 'Nova Cidade'}
                          {isIncomplete && (
                            <span className="text-xs bg-red-500 text-white px-2 py-0.5 rounded">
                              ❌ Incompleta
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-gray-500 mt-1">
                          {city.estado} • {city.codigo_ibge || '(sem IBGE)'}
                        </div>
                      </button>
                      {/* ✅ NOVO: Botão remover cidade */}
                      {citiesData.length > 1 && (
                        <button
                          onClick={() => handleRemoveCity(idx)}
                          disabled={loading}
                          className="mt-2 w-full px-2 py-1 text-xs bg-red-100 text-red-600 rounded hover:bg-red-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          ✕ Remover
                        </button>
                      )}
                    </div>
                  );
                })}
              </div>

              {/* BOTÕES DE AÇÃO */}
              <div className="p-4 bg-gray-50 border-t space-y-2">
                {/* ✅ NOVO: Adicionar cidade */}
                <button
                  onClick={handleAddCity}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-orange-600 text-white rounded-lg font-semibold text-sm hover:bg-orange-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  + Adicionar Cidade
                </button>

                <button
                  onClick={handleReset}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold text-sm hover:bg-gray-300 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  ↺ Limpar Dados
                </button>
              </div>
            </div>
          </div>

          {/* MAIN CONTENT */}
          <div className="lg:col-span-3 space-y-6">
            {/* INFO CARD DA CIDADE */}
            <div className="bg-white rounded-xl shadow-lg p-6 border-t-4 border-orange-500">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-3xl font-bold text-gray-900">
                    {selectedCity.nome}
                  </h2>
                  <p className="text-gray-600 mt-1">
                    Código IBGE: <span className="font-mono font-semibold">{selectedCity.codigo_ibge}</span>
                  </p>
                </div>
                <div className="text-right text-sm text-gray-500">
                  Estado: <span className="font-bold text-gray-900">{selectedCity.estado}</span>
                </div>
              </div>
            </div>

            {/* TABS */}
            <div className="bg-white rounded-xl shadow-lg overflow-hidden">
              <div className="flex gap-0 border-b border-gray-200">
                {TABS.map((tab) => {
                  const TabIcon = tab.icon;
                  const isActive = selectedTabId === tab.id;

                  return (
                    <button
                      key={tab.id}
                      onClick={() => handleTabChange(tab.id)}
                      disabled={loading}
                      className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 font-semibold text-sm transition border-b-2 ${
                        isActive
                          ? `border-b-4 bg-gradient-to-r ${tab.color} text-white`
                          : 'border-b-0 text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                    >
                      <TabIcon className="w-5 h-5" />
                      <span className="hidden sm:inline">{tab.label}</span>
                    </button>
                  );
                })}
              </div>

              {/* TAB DESCRIPTION */}
              <div className={`px-6 py-3 bg-gradient-to-r ${selectedTab?.color || ''} bg-opacity-5 border-b border-gray-100`}>
                <p className="text-sm text-gray-700">
                  {selectedTab?.description}
                </p>
              </div>

              {/* TAB CONTENT */}
              <div className="p-8">
                <form>
                  {renderTabInputs()}
                </form>
              </div>
            </div>

            {/* BUTTONS */}
            <div className="flex gap-4">
              <button
                onClick={handleSubmit}
                disabled={loading || citiesData.length < 2 || !validateCitiesComplete}
                className={`flex-1 bg-gradient-to-r from-orange-600 to-orange-700 text-white font-bold py-4 px-6 rounded-lg transition flex items-center justify-center gap-2 shadow-lg ${
                  citiesData.length < 2 || !validateCitiesComplete
                    ? 'opacity-50 cursor-not-allowed from-gray-400 to-gray-500'
                    : 'hover:from-orange-700 hover:to-orange-800 hover:shadow-xl'
                }`}
                title={
                  citiesData.length < 2
                    ? 'Mínimo 2 cidades necessárias'
                    : !validateCitiesComplete
                    ? `${incompleteCities} cidade(s) sem Código IBGE ou Nome`
                    : 'Calcular ranking TOPSIS'
                }
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    Enviando...
                  </>
                ) : (
                  <>
                    <TrendingUp className="w-5 h-5" />
                    {citiesData.length < 2 
                      ? '⚠️ Adicione mais cidades (Mín: 2)'
                      : !validateCitiesComplete
                      ? `⚠️ Preencha ${incompleteCities} cidade(s)`
                      : 'Calcular Ranking'
                    }
                  </>
                )}
              </button>

              <button
                onClick={handleReset}
                disabled={loading}
                className="px-6 font-semibold py-4 bg-gray-100 text-gray-800 rounded-lg hover:bg-gray-200 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancelar
              </button>
            </div>

            {/* RESULTS SECTION */}
            {renderResults()}
          </div>
        </div>
      </div>
    </div>
  );
}
