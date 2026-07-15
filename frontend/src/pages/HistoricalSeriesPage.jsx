import React, { useEffect, useMemo, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { AlertTriangle, BarChart3, CalendarDays, ChevronDown, Loader2, MapPin, TrendingUp } from 'lucide-react';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';
import { getCities, getIndicators, getSnapshots, obterHistoricoIndicadores } from '../services/api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const SCORE_COLOR = '#f97316';
const SCORE_BORDER = '#ea580c';
const SERIES_COLOR = '#2563eb';
const SERIES_BORDER = '#1d4ed8';

const isNonEmptyArray = (value) => Array.isArray(value) && value.length > 0;

const formatPeriod = (periodo) => {
  if (!periodo || typeof periodo !== 'string') {
    return '-';
  }

  const trimmed = periodo.trim();
  if (/^\d{4}-\d{2}$/.test(trimmed)) {
    const [ano, mes] = trimmed.split('-');
    return `${mes}/${ano}`;
  }

  return trimmed;
};

const formatValue = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return '—';
  }

  return Number(value).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const normalizeErrorMessage = (error) => {
  if (!error) {
    return 'Erro inesperado ao carregar a série histórica.';
  }

  if (typeof error === 'string') {
    return error;
  }

  return error.message || 'Erro inesperado ao carregar a série histórica.';
};

const isMissingDataError = (message) => {
  if (!message) {
    return false;
  }

  return /nenhum|não encontrados?|not found|404/i.test(message);
};

const resolveSnapshotIndicatorValue = (snapshotValues, indicatorIndex, indicatorMeta) => {
  if (Array.isArray(snapshotValues)) {
    const raw = snapshotValues[indicatorIndex];
    const numeric = Number(raw);
    return Number.isFinite(numeric) ? numeric : null;
  }

  if (snapshotValues && typeof snapshotValues === 'object') {
    const keyCandidates = [
      indicatorMeta?.codigo,
      indicatorMeta?.nome,
      String(indicatorIndex),
    ].filter(Boolean);

    for (const key of keyCandidates) {
      if (Object.prototype.hasOwnProperty.call(snapshotValues, key)) {
        const numeric = Number(snapshotValues[key]);
        if (Number.isFinite(numeric)) {
          return numeric;
        }
      }
    }
  }

  return null;
};

function HistoricalSeriesPage() {
  const [cities, setCities] = useState([]);
  const [indicators, setIndicators] = useState([]);
  const [selectedCityCode, setSelectedCityCode] = useState('');
  const [selectedIndicatorIndex, setSelectedIndicatorIndex] = useState(0);
  const [indicatorHistory, setIndicatorHistory] = useState([]);
  const [rankingHistory, setRankingHistory] = useState([]);
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [loadingCityData, setLoadingCityData] = useState(false);
  const [error, setError] = useState('');
  const [metaError, setMetaError] = useState('');

  useEffect(() => {
    let mounted = true;

    const loadMeta = async () => {
      setLoadingMeta(true);
      setMetaError('');

      try {
        const [citiesResponse, indicatorsResponse] = await Promise.all([
          getCities(),
          getIndicators(),
        ]);

        if (!mounted) {
          return;
        }

        setCities(citiesResponse || []);
        setIndicators(indicatorsResponse || []);

        const defaultIndicator = indicatorsResponse?.[0]?.indice ?? 0;
        setSelectedIndicatorIndex(Number(defaultIndicator));

        const utfprCity = (citiesResponse || []).find((city) => city.codigo_ibge === '9999999');
        const fallbackCity = (citiesResponse || [])[0];
        const initialCity = utfprCity || fallbackCity;

        if (initialCity?.codigo_ibge) {
          setSelectedCityCode(String(initialCity.codigo_ibge));
        }
      } catch (error) {
        if (!mounted) {
          return;
        }
        setMetaError(normalizeErrorMessage(error));
      } finally {
        if (mounted) {
          setLoadingMeta(false);
        }
      }
    };

    loadMeta();

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedCityCode) {
      setIndicatorHistory([]);
      setRankingHistory([]);
      return;
    }

    const validCode = String(selectedCityCode).trim();
    if (!/^\d{7,8}$/.test(validCode)) {
      setIndicatorHistory([]);
      setRankingHistory([]);
      setError('Código IBGE inválido. Use 7 ou 8 dígitos.');
      return;
    }

    let mounted = true;

    const loadCityHistoricalData = async () => {
      setLoadingCityData(true);
      setError('');

      const [indicatorResult, rankingResult] = await Promise.allSettled([
        obterHistoricoIndicadores(validCode, 52),
        getSnapshots(validCode),
      ]);

      if (!mounted) {
        return;
      }

      const nextIndicatorHistory = indicatorResult.status === 'fulfilled' ? indicatorResult.value || [] : [];
      const nextRankingHistory = rankingResult.status === 'fulfilled' ? rankingResult.value || [] : [];

      setIndicatorHistory(nextIndicatorHistory);
      setRankingHistory(nextRankingHistory);

      const errors = [];

      if (indicatorResult.status === 'rejected') {
        const message = normalizeErrorMessage(indicatorResult.reason);
        if (!isMissingDataError(message)) {
          errors.push(`Indicadores: ${message}`);
        }
      }

      if (rankingResult.status === 'rejected') {
        const message = normalizeErrorMessage(rankingResult.reason);
        if (!isMissingDataError(message)) {
          errors.push(`Ranking: ${message}`);
        }
      }

      setError(errors.join(' | '));
      setLoadingCityData(false);
    };

    loadCityHistoricalData();

    return () => {
      mounted = false;
    };
  }, [selectedCityCode]);

  const selectedCity = useMemo(() => {
    return cities.find((city) => String(city.codigo_ibge) === String(selectedCityCode));
  }, [cities, selectedCityCode]);

  const selectedIndicatorMeta = useMemo(() => {
    return indicators.find((indicator) => Number(indicator.indice) === Number(selectedIndicatorIndex));
  }, [indicators, selectedIndicatorIndex]);

  const scoreSeries = useMemo(() => {
    if (!isNonEmptyArray(rankingHistory) || !selectedCity) {
      return [];
    }

    return rankingHistory
      .map((snapshot) => {
        const rankingData = Array.isArray(snapshot.ranking_data) ? snapshot.ranking_data : [];
        const cityEntry = rankingData.find((entry) => entry?.nome_cidade === selectedCity.nome || entry?.nome_cidade === selectedCity.nome_cidade);

        return {
          periodo: snapshot.periodo_referencia || snapshot.data_calculo,
          data: snapshot.data_calculo,
          score: cityEntry?.indice_smart ?? null,
          position: cityEntry?.posicao ?? null,
        };
      })
      .filter((item) => item.score !== null && item.score !== undefined)
      .sort((a, b) => String(a.data).localeCompare(String(b.data)));
  }, [rankingHistory, selectedCity]);

  const indicatorSeries = useMemo(() => {
    if (!isNonEmptyArray(indicatorHistory)) {
      return [];
    }

    return indicatorHistory
      .map((snapshot) => {
        const value = resolveSnapshotIndicatorValue(snapshot.valores_indicadores, selectedIndicatorIndex, selectedIndicatorMeta);

        return {
          periodo: snapshot.periodo_referencia || snapshot.data_calculo,
          data: snapshot.data_calculo,
          value,
        };
      })
      .filter((item) => item.value !== null && item.value !== undefined)
      .sort((a, b) => String(a.data).localeCompare(String(b.data)));
  }, [indicatorHistory, selectedIndicatorIndex, selectedIndicatorMeta]);

  const latestScore = scoreSeries.at(-1)?.score ?? null;
  const bestScore = scoreSeries.length > 0 ? Math.max(...scoreSeries.map((item) => Number(item.score))) : null;
  const latestPosition = scoreSeries.at(-1)?.position ?? null;
  const latestIndicatorValue = indicatorSeries.at(-1)?.value ?? null;
  const averageScore = scoreSeries.length > 0
    ? scoreSeries.reduce((acc, item) => acc + Number(item.score || 0), 0) / scoreSeries.length
    : null;

  const scoreChartData = useMemo(() => ({
    labels: scoreSeries.map((item) => formatPeriod(item.periodo)),
    datasets: [
      {
        label: 'Score TOPSIS',
        data: scoreSeries.map((item) => (item.score !== null ? Number(item.score) * 100 : null)),
        borderColor: SCORE_BORDER,
        backgroundColor: 'rgba(249, 115, 22, 0.16)',
        pointBackgroundColor: SCORE_BORDER,
        pointBorderColor: '#fff',
        pointRadius: 4,
        pointHoverRadius: 7,
        borderWidth: 3,
        tension: 0.35,
        fill: true,
        spanGaps: true,
      },
    ],
  }), [scoreSeries]);

  const indicatorChartData = useMemo(() => ({
    labels: indicatorSeries.map((item) => formatPeriod(item.periodo)),
    datasets: [
      {
        label: selectedIndicatorMeta?.nome || 'Indicador selecionado',
        data: indicatorSeries.map((item) => item.value),
        borderColor: SERIES_BORDER,
        backgroundColor: 'rgba(37, 99, 235, 0.14)',
        pointBackgroundColor: SERIES_BORDER,
        pointBorderColor: '#fff',
        pointRadius: 4,
        pointHoverRadius: 7,
        borderWidth: 3,
        tension: 0.35,
        fill: true,
        spanGaps: true,
      },
    ],
  }), [indicatorSeries, selectedIndicatorMeta]);

  const scoreChartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'line',
        },
      },
      title: {
        display: true,
        text: 'Evolução do Score TOPSIS',
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${(Number(context.parsed.y) || 0).toFixed(2)}%`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        suggestedMax: 100,
        ticks: {
          callback: (value) => `${value}%`,
        },
      },
    },
  }), []);

  const indicatorChartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'line',
        },
      },
      title: {
        display: true,
        text: selectedIndicatorMeta
          ? `Evolução de ${selectedIndicatorMeta.nome}`
          : 'Evolução do indicador selecionado',
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const value = context.parsed.y;
            return `${context.dataset.label}: ${formatValue(value)}`;
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: (value) => formatValue(value),
        },
      },
    },
  }), [selectedIndicatorMeta]);

  const cityLabel = selectedCity?.nome || selectedCity?.nome_cidade || (selectedCityCode ? `IBGE ${selectedCityCode}` : 'Nenhuma cidade selecionada');
  const availableDataPoints = Math.max(scoreSeries.length, indicatorSeries.length);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Sidebar />

      <div className="lg:pl-64">
        <div className="sticky top-0 z-20">
          <div className="border-b border-slate-200 bg-white/95 backdrop-blur-sm shadow-sm">
            <Header />
          </div>
        </div>

        <main className="px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <div className="mx-auto flex w-full max-w-7xl flex-col gap-6">
            <section className="overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-r from-orange-500 via-orange-400 to-amber-300 p-6 text-white shadow-lg">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="max-w-3xl space-y-3">
                  <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white/90">
                    <TrendingUp size={14} />
                    Série histórica
                  </div>
                  <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
                    HistoricalSeriesPage
                  </h1>
                  <p className="max-w-2xl text-sm leading-6 text-white/90 sm:text-base">
                    Acompanhe a evolução temporal do Score TOPSIS e dos 50 indicadores da cidade selecionada.
                    Os dados vêm dos snapshots históricos do backend e mantêm a paleta visual do Urbix.
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[420px]">
                  <div className="rounded-2xl border border-white/20 bg-white/15 p-4 backdrop-blur-sm">
                    <p className="text-xs font-medium uppercase tracking-wide text-white/80">Cidade</p>
                    <p className="mt-1 text-lg font-semibold">{cityLabel}</p>
                  </div>
                  <div className="rounded-2xl border border-white/20 bg-white/15 p-4 backdrop-blur-sm">
                    <p className="text-xs font-medium uppercase tracking-wide text-white/80">Score atual</p>
                    <p className="mt-1 text-lg font-semibold">
                      {latestScore !== null ? `${(Number(latestScore) * 100).toFixed(2)}%` : '—'}
                    </p>
                  </div>
                  <div className="rounded-2xl border border-white/20 bg-white/15 p-4 backdrop-blur-sm">
                    <p className="text-xs font-medium uppercase tracking-wide text-white/80">Pontos</p>
                    <p className="mt-1 text-lg font-semibold">{availableDataPoints}</p>
                  </div>
                </div>
              </div>
            </section>

            {metaError && (
              <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 shadow-sm">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="mt-0.5 h-4 w-4" />
                  <span>{metaError}</span>
                </div>
              </div>
            )}

            <section className="grid gap-6 xl:grid-cols-[minmax(0,1.25fr)_minmax(340px,0.75fr)]">
              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">Selecionar cidade</h2>
                    <p className="text-sm text-slate-500">
                      Escolha uma cidade do dropdown ou digite o código IBGE manualmente.
                    </p>
                  </div>
                  <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                    <MapPin size={14} />
                    IBGE 7 ou 8 dígitos
                  </div>
                </div>

                <div className="grid gap-4 md:grid-cols-2">
                  <label className="space-y-2">
                    <span className="text-sm font-medium text-slate-700">Município</span>
                    <div className="relative">
                      <select
                        value={selectedCityCode}
                        onChange={(e) => setSelectedCityCode(e.target.value)}
                        className="w-full appearance-none rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 pr-10 text-sm outline-none transition focus:border-orange-500 focus:bg-white focus:ring-4 focus:ring-orange-100"
                        disabled={loadingMeta}
                      >
                        <option value="">Selecione uma cidade...</option>
                        {cities.map((city) => (
                          <option key={city.codigo_ibge} value={city.codigo_ibge}>
                            {city.nome} ({city.codigo_ibge})
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    </div>
                  </label>

                  <label className="space-y-2">
                    <span className="text-sm font-medium text-slate-700">Ou digite o código IBGE</span>
                    <input
                      type="text"
                      inputMode="numeric"
                      placeholder="Ex.: 9999999"
                      value={selectedCityCode}
                      onChange={(e) => setSelectedCityCode(e.target.value.replace(/\D/g, '').slice(0, 8))}
                      className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-orange-500 focus:bg-white focus:ring-4 focus:ring-orange-100"
                    />
                  </label>
                </div>

                <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                  <span className="rounded-full bg-orange-50 px-3 py-1 font-medium text-orange-700">{cities.length} cidades disponíveis</span>
                  <span className="rounded-full bg-blue-50 px-3 py-1 font-medium text-blue-700">{indicators.length} indicadores</span>
                  <span className="rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-600">Atualização automática ao selecionar cidade</span>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center gap-3">
                  <div className="rounded-2xl bg-orange-100 p-3 text-orange-600">
                    <CalendarDays size={18} />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">Resumo da série</h2>
                    <p className="text-sm text-slate-500">Visão rápida da cidade selecionada.</p>
                  </div>
                </div>

                {loadingMeta || loadingCityData ? (
                  <div className="flex min-h-[180px] items-center justify-center rounded-2xl bg-slate-50 text-slate-600">
                    <div className="flex items-center gap-3">
                      <Loader2 className="h-5 w-5 animate-spin text-orange-500" />
                      <span>Carregando séries históricas...</span>
                    </div>
                  </div>
                ) : (
                  <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Último Score</p>
                      <p className="mt-2 text-2xl font-bold text-slate-900">
                        {latestScore !== null ? `${(Number(latestScore) * 100).toFixed(2)}%` : '—'}
                      </p>
                      <p className="text-sm text-slate-500">Score TOPSIS mais recente</p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Melhor score</p>
                      <p className="mt-2 text-2xl font-bold text-slate-900">
                        {bestScore !== null ? `${(Number(bestScore) * 100).toFixed(2)}%` : '—'}
                      </p>
                      <p className="text-sm text-slate-500">Pico histórico observado</p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Última posição</p>
                      <p className="mt-2 text-2xl font-bold text-slate-900">{latestPosition ?? '—'}</p>
                      <p className="text-sm text-slate-500">Posição no ranking</p>
                    </div>

                    <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Média do score</p>
                      <p className="mt-2 text-2xl font-bold text-slate-900">
                        {averageScore !== null ? `${(Number(averageScore) * 100).toFixed(2)}%` : '—'}
                      </p>
                      <p className="text-sm text-slate-500">Média dos snapshots carregados</p>
                    </div>
                  </div>
                )}
              </div>
            </section>

            {error && (
              <div className="rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800 shadow-sm">
                <div className="flex items-start gap-2">
                  <AlertTriangle className="mt-0.5 h-4 w-4" />
                  <span>{error}</span>
                </div>
              </div>
            )}

            {!loadingMeta && !loadingCityData && selectedCityCode && !error && !isNonEmptyArray(scoreSeries) && !isNonEmptyArray(indicatorSeries) && (
              <div className="rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center shadow-sm">
                <BarChart3 className="mx-auto h-10 w-10 text-slate-400" />
                <h3 className="mt-4 text-lg font-semibold text-slate-900">Sem dados históricos</h3>
                <p className="mt-2 text-sm text-slate-500">
                  Esta cidade ainda não possui snapshots suficientes para montar a série temporal.
                </p>
              </div>
            )}

            {isNonEmptyArray(scoreSeries) && (
              <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">Evolução do Score TOPSIS</h2>
                    <p className="text-sm text-slate-500">
                      Linha temporal do desempenho geral da cidade no ranking TOPSIS.
                    </p>
                  </div>
                  <div className="rounded-full bg-orange-50 px-3 py-1 text-xs font-medium text-orange-700">
                    {scoreSeries.length} pontos carregados
                  </div>
                </div>

                <div className="h-[360px] rounded-2xl bg-slate-50 p-4">
                  <Line data={scoreChartData} options={scoreChartOptions} />
                </div>
              </section>
            )}

            <section className="grid gap-6 xl:grid-cols-[minmax(0,0.82fr)_minmax(0,1.18fr)]">
              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex items-center gap-3">
                  <div className="rounded-2xl bg-blue-100 p-3 text-blue-600">
                    <BarChart3 size={18} />
                  </div>
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">Selecionar indicador</h2>
                    <p className="text-sm text-slate-500">
                      Escolha um dos 50 indicadores para ver a sua evolução específica.
                    </p>
                  </div>
                </div>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-slate-700">Indicador</span>
                  <div className="relative">
                    <select
                      value={selectedIndicatorIndex}
                      onChange={(e) => setSelectedIndicatorIndex(Number(e.target.value))}
                      className="w-full appearance-none rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 pr-10 text-sm outline-none transition focus:border-blue-500 focus:bg-white focus:ring-4 focus:ring-blue-100"
                      disabled={!indicators.length}
                    >
                      {indicators.map((indicator) => (
                        <option key={indicator.indice} value={indicator.indice}>
                          {String(indicator.indice).padStart(2, '0')} · {indicator.nome}
                        </option>
                      ))}
                    </select>
                    <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                  </div>
                </label>

                <div className="mt-4 space-y-3 text-sm text-slate-600">
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="font-medium text-slate-900">Indicador selecionado</p>
                    <p className="mt-1">{selectedIndicatorMeta?.nome || 'Carregando...'}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="font-medium text-slate-900">Categoria</p>
                    <p className="mt-1">{selectedIndicatorMeta?.categoria || '—'}</p>
                  </div>
                  <div className="rounded-2xl bg-slate-50 p-4">
                    <p className="font-medium text-slate-900">Último valor</p>
                    <p className="mt-1">{formatValue(latestIndicatorValue)}</p>
                  </div>
                </div>
              </div>

              <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
                <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <h2 className="text-xl font-semibold text-slate-900">Evolução do indicador</h2>
                    <p className="text-sm text-slate-500">
                      Linha temporal do indicador selecionado para a cidade atual.
                    </p>
                  </div>
                  <div className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                    {indicatorSeries.length} pontos carregados
                  </div>
                </div>

                {isNonEmptyArray(indicatorSeries) ? (
                  <div className="h-[360px] rounded-2xl bg-slate-50 p-4">
                    <Line data={indicatorChartData} options={indicatorChartOptions} />
                  </div>
                ) : (
                  <div className="flex min-h-[360px] items-center justify-center rounded-2xl bg-slate-50 text-center text-slate-500">
                    <div>
                      <BarChart3 className="mx-auto h-10 w-10 text-slate-400" />
                      <p className="mt-3 font-medium">Sem dados para o indicador selecionado</p>
                      <p className="mt-1 text-sm">Tente outro indicador ou outra cidade.</p>
                    </div>
                  </div>
                )}
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  );
}

export default HistoricalSeriesPage;
