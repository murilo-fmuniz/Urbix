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
import { AlertTriangle, BarChart3, ChevronDown, Loader2, MapPin, Search } from 'lucide-react';
import { getCities, getIndicators, obterHistoricoIndicadores } from '../services/api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const LINE_COLOR = '#2563eb';
const LINE_BORDER = '#1d4ed8';

const normalizeErrorMessage = (error) => {
  if (!error) return 'Erro inesperado ao carregar a série histórica.';
  if (typeof error === 'string') return error;
  return error.message || 'Erro inesperado ao carregar a série histórica.';
};

const isMissingDataError = (message) => /nenhum|não encontrados?|not found|404/i.test(message || '');

const formatPeriod = (periodo) => {
  if (!periodo || typeof periodo !== 'string') return '-';
  const trimmed = periodo.trim();
  if (/^\d{4}-\d{2}$/.test(trimmed)) {
    const [ano, mes] = trimmed.split('-');
    return `${mes}/${ano}`;
  }
  return trimmed;
};

const formatValue = (value) => {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return Number(value).toLocaleString('pt-BR', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
};

const getSnapshotValue = (snapshotValues, indicatorIndex) => {
  if (Array.isArray(snapshotValues)) {
    const value = Number(snapshotValues[indicatorIndex]);
    return Number.isFinite(value) ? value : null;
  }

  if (snapshotValues && typeof snapshotValues === 'object') {
    const direct = snapshotValues[indicatorIndex] ?? snapshotValues[String(indicatorIndex)];
    const value = Number(direct);
    return Number.isFinite(value) ? value : null;
  }

  return null;
};

function CityIndicatorsHistoryPage() {
  const [cities, setCities] = useState([]);
  const [indicators, setIndicators] = useState([]);
  const [citySearch, setCitySearch] = useState('');
  const [selectedCityCode, setSelectedCityCode] = useState('');
  const [selectedIndicatorIndex, setSelectedIndicatorIndex] = useState(0);
  const [snapshots, setSnapshots] = useState([]);
  const [loadingMeta, setLoadingMeta] = useState(true);
  const [loadingHistory, setLoadingHistory] = useState(false);
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

        if (!mounted) return;

        setCities(citiesResponse || []);
        setIndicators(indicatorsResponse || []);

        const utfprCity = (citiesResponse || []).find((city) => String(city.codigo_ibge) === '9999999');
        const firstCity = utfprCity || (citiesResponse || [])[0];

        if (firstCity?.codigo_ibge) {
          setSelectedCityCode(String(firstCity.codigo_ibge));
          setCitySearch(firstCity.nome || firstCity.nome_cidade || '');
        }

        const defaultIndicator = indicatorsResponse?.[0]?.indice ?? 0;
        setSelectedIndicatorIndex(Number(defaultIndicator));
      } catch (error) {
        if (!mounted) return;
        setMetaError(normalizeErrorMessage(error));
      } finally {
        if (mounted) setLoadingMeta(false);
      }
    };

    loadMeta();

    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedCityCode) {
      setSnapshots([]);
      return;
    }

    const code = String(selectedCityCode).trim();
    if (!/^\d{7,8}$/.test(code)) {
      setSnapshots([]);
      setError('Código IBGE inválido. Use 7 ou 8 dígitos.');
      return;
    }

    let mounted = true;

    const loadHistory = async () => {
      setLoadingHistory(true);
      setError('');

      try {
        const data = await obterHistoricoIndicadores(code, 52);
        if (!mounted) return;
        setSnapshots(Array.isArray(data) ? data : []);
      } catch (error) {
        if (!mounted) return;
        const message = normalizeErrorMessage(error);
        if (isMissingDataError(message)) {
          setSnapshots([]);
          setError('');
        } else {
          setSnapshots([]);
          setError(message);
        }
      } finally {
        if (mounted) setLoadingHistory(false);
      }
    };

    loadHistory();

    return () => {
      mounted = false;
    };
  }, [selectedCityCode]);

  const filteredCities = useMemo(() => {
    const query = citySearch.trim().toLowerCase();

    if (!query) {
      return cities;
    }

    return cities.filter((city) => {
      const code = String(city.codigo_ibge || '').toLowerCase();
      const name = String(city.nome || city.nome_cidade || '').toLowerCase();
      return code.includes(query) || name.includes(query);
    });
  }, [cities, citySearch]);

  const selectedCity = useMemo(() => {
    return cities.find((city) => String(city.codigo_ibge) === String(selectedCityCode));
  }, [cities, selectedCityCode]);

  const selectedIndicator = useMemo(() => {
    return indicators.find((indicator) => Number(indicator.indice) === Number(selectedIndicatorIndex));
  }, [indicators, selectedIndicatorIndex]);

  const selectedSeries = useMemo(() => {
    if (!snapshots.length || !selectedIndicator) return [];

    return snapshots
      .map((snapshot) => ({
        periodo: snapshot.periodo_referencia || snapshot.data_calculo,
        valor: getSnapshotValue(snapshot.valores_indicadores, selectedIndicatorIndex),
      }))
      .filter((item) => item.valor !== null && item.valor !== undefined)
      .reverse();
  }, [snapshots, selectedIndicator, selectedIndicatorIndex]);

  const chartData = useMemo(() => ({
    labels: selectedSeries.map((item) => formatPeriod(item.periodo)),
    datasets: [
      {
        label: selectedIndicator?.nome || 'Indicador selecionado',
        data: selectedSeries.map((item) => item.valor),
        borderColor: LINE_BORDER,
        backgroundColor: 'rgba(37, 99, 235, 0.14)',
        pointBackgroundColor: LINE_BORDER,
        pointBorderColor: '#fff',
        pointRadius: 4,
        pointHoverRadius: 7,
        borderWidth: 3,
        tension: 0.35,
        fill: true,
        spanGaps: true,
      },
    ],
  }), [selectedSeries, selectedIndicator]);

  const chartOptions = useMemo(() => ({
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
        text: selectedIndicator
          ? `Evolução de ${selectedIndicator.nome}`
          : 'Evolução do indicador selecionado',
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${formatValue(context.parsed.y)}`,
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
  }), [selectedIndicator]);

  const latestValue = selectedSeries.at(-1)?.valor ?? null;
  const firstValue = selectedSeries[0]?.valor ?? null;
  const minValue = selectedSeries.length ? Math.min(...selectedSeries.map((item) => Number(item.valor))) : null;
  const maxValue = selectedSeries.length ? Math.max(...selectedSeries.map((item) => Number(item.valor))) : null;

  const handleCityChange = (value) => {
    setCitySearch(value);

    const matchedByCode = cities.find((city) => String(city.codigo_ibge) === String(value));
    if (matchedByCode) {
      setSelectedCityCode(String(matchedByCode.codigo_ibge));
      setCitySearch(matchedByCode.nome || matchedByCode.nome_cidade || matchedByCode.codigo_ibge);
      return;
    }

    const normalized = value.trim().toLowerCase();
    const matchedByName = cities.find((city) => {
      const name = String(city.nome || city.nome_cidade || '').toLowerCase();
      return name === normalized || name.includes(normalized);
    });

    if (matchedByName) {
      setSelectedCityCode(String(matchedByName.codigo_ibge));
    }
  };

  const cityCount = cities.length;
  const indicatorCount = indicators.length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
        <div className="flex flex-col gap-6">
          <section className="overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-r from-orange-500 via-orange-400 to-amber-300 p-6 text-white shadow-lg">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
              <div className="max-w-3xl space-y-3">
                <div className="inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] text-white/90">
                  <BarChart3 size={14} />
                  Indicadores históricos
                </div>
                <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Histórico de Indicadores</h1>
                <p className="max-w-2xl text-sm leading-6 text-white/90 sm:text-base">
                  Acompanhe a evolução temporal de um único indicador para uma cidade específica,
                  com base nos snapshots históricos armazenados no backend.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3 lg:min-w-[420px]">
                <div className="rounded-2xl border border-white/20 bg-white/15 p-4 backdrop-blur-sm">
                  <p className="text-xs font-medium uppercase tracking-wide text-white/80">Cidade</p>
                  <p className="mt-1 text-lg font-semibold">{selectedCity?.nome || selectedCity?.nome_cidade || '—'}</p>
                </div>
                <div className="rounded-2xl border border-white/20 bg-white/15 p-4 backdrop-blur-sm">
                  <p className="text-xs font-medium uppercase tracking-wide text-white/80">Snapshots</p>
                  <p className="mt-1 text-lg font-semibold">{snapshots.length}</p>
                </div>
                <div className="rounded-2xl border border-white/20 bg-white/15 p-4 backdrop-blur-sm">
                  <p className="text-xs font-medium uppercase tracking-wide text-white/80">Indicadores</p>
                  <p className="mt-1 text-lg font-semibold">{indicatorCount}</p>
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

          <section className="grid gap-6 xl:grid-cols-[minmax(0,1.18fr)_minmax(340px,0.82fr)]">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900">Seleção da cidade</h2>
                  <p className="text-sm text-slate-500">
                    Pesquise por nome ou código IBGE e escolha um município da lista.
                  </p>
                </div>
                <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                  <MapPin size={14} />
                  Código IBGE 7 ou 8 dígitos
                </div>
              </div>

                <div className="grid gap-4 md:grid-cols-[minmax(0,1fr)_220px]">
                  <label className="space-y-2">
                    <span className="text-sm font-medium text-slate-700">Buscar município</span>
                    <div className="relative">
                      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                      <input
                        type="text"
                        value={citySearch}
                        onChange={(e) => handleCityChange(e.target.value)}
                        placeholder="Digite o nome ou código IBGE"
                        className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-10 py-3 text-sm outline-none transition focus:border-orange-500 focus:bg-white focus:ring-4 focus:ring-orange-100"
                      />
                    </div>
                  </label>

                  <label className="space-y-2">
                    <span className="text-sm font-medium text-slate-700">Selecionar da lista</span>
                    <div className="relative">
                      <select
                        value={selectedCityCode}
                        onChange={(e) => {
                          setSelectedCityCode(e.target.value);
                          const city = cities.find((item) => String(item.codigo_ibge) === String(e.target.value));
                          if (city) {
                            setCitySearch(city.nome || city.nome_cidade || '');
                          }
                        }}
                        className="w-full appearance-none rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 pr-10 text-sm outline-none transition focus:border-orange-500 focus:bg-white focus:ring-4 focus:ring-orange-100"
                        disabled={loadingMeta}
                      >
                        <option value="">Selecione...</option>
                        {filteredCities.map((city) => (
                          <option key={city.codigo_ibge} value={city.codigo_ibge}>
                            {city.nome || city.nome_cidade} ({city.codigo_ibge})
                          </option>
                        ))}
                      </select>
                      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
                    </div>
                  </label>
                </div>

              <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
                <span className="rounded-full bg-orange-50 px-3 py-1 font-medium text-orange-700">
                  {cityCount} cidades disponíveis
                </span>
                <span className="rounded-full bg-blue-50 px-3 py-1 font-medium text-blue-700">
                  {indicatorCount} indicadores carregados
                </span>
                <span className="rounded-full bg-slate-100 px-3 py-1 font-medium text-slate-600">
                  O gráfico atualiza ao trocar a cidade
                </span>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex items-center gap-3">
                <div className="rounded-2xl bg-blue-100 p-3 text-blue-600">
                  <Loader2 size={18} />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-slate-900">Status da consulta</h2>
                  <p className="text-sm text-slate-500">Resumo rápido da leitura do histórico.</p>
                </div>
              </div>

              {loadingMeta || loadingHistory ? (
                <div className="flex min-h-[180px] items-center justify-center rounded-2xl bg-slate-50 text-slate-600">
                  <div className="flex items-center gap-3">
                    <Loader2 className="h-5 w-5 animate-spin text-orange-500" />
                    <span>Carregando histórico da cidade...</span>
                  </div>
                </div>
              ) : (
                <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Indicador</p>
                    <p className="mt-2 text-lg font-bold text-slate-900">{selectedIndicator?.nome || '—'}</p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Último valor</p>
                    <p className="mt-2 text-2xl font-bold text-slate-900">{formatValue(latestValue)}</p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Primeiro valor</p>
                    <p className="mt-2 text-2xl font-bold text-slate-900">{formatValue(firstValue)}</p>
                  </div>
                  <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Faixa histórica</p>
                    <p className="mt-2 text-2xl font-bold text-slate-900">
                      {minValue !== null && maxValue !== null ? `${formatValue(minValue)} → ${formatValue(maxValue)}` : '—'}
                    </p>
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

          {!loadingMeta && !loadingHistory && selectedCityCode && !error && !snapshots.length && (
            <div className="rounded-3xl border border-dashed border-slate-300 bg-white px-6 py-12 text-center shadow-sm">
              <BarChart3 className="mx-auto h-10 w-10 text-slate-400" />
              <h3 className="mt-4 text-lg font-semibold text-slate-900">Sem dados históricos</h3>
              <p className="mt-2 text-sm text-slate-500">
                Essa cidade ainda não possui snapshots de indicadores para exibir.
              </p>
            </div>
          )}

          <section className="grid gap-6 xl:grid-cols-[minmax(320px,0.7fr)_minmax(0,1.3fr)]">
            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex items-center gap-3">
                <div className="rounded-2xl bg-orange-100 p-3 text-orange-600">
                  <BarChart3 size={18} />
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-slate-900">Seleção do indicador</h2>
                  <p className="text-sm text-slate-500">Escolha apenas um indicador por vez.</p>
                </div>
              </div>

                <label className="space-y-2">
                  <span className="text-sm font-medium text-slate-700">Indicador</span>
                  <div className="relative">
                    <select
                      value={selectedIndicatorIndex}
                      onChange={(e) => setSelectedIndicatorIndex(Number(e.target.value))}
                      className="w-full appearance-none rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 pr-10 text-sm outline-none transition focus:border-orange-500 focus:bg-white focus:ring-4 focus:ring-orange-100"
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
                  <p className="font-medium text-slate-900">Categoria</p>
                  <p className="mt-1">{selectedIndicator?.categoria || '—'}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="font-medium text-slate-900">Impacto</p>
                  <p className="mt-1">{selectedIndicator?.impacto || '—'}</p>
                </div>
                <div className="rounded-2xl bg-slate-50 p-4">
                  <p className="font-medium text-slate-900">Peso</p>
                  <p className="mt-1">{selectedIndicator?.peso ?? '—'}</p>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h2 className="text-xl font-semibold text-slate-900">Evolução temporal do indicador</h2>
                  <p className="text-sm text-slate-500">
                    Gráfico de linhas com os valores históricos do indicador selecionado.
                  </p>
                </div>
                <div className="rounded-full bg-blue-50 px-3 py-1 text-xs font-medium text-blue-700">
                  {selectedSeries.length} pontos carregados
                </div>
              </div>

              {selectedSeries.length > 0 ? (
                <div className="h-[390px] rounded-2xl bg-slate-50 p-4">
                  <Line data={chartData} options={chartOptions} />
                </div>
              ) : (
                <div className="flex min-h-[390px] items-center justify-center rounded-2xl bg-slate-50 text-center text-slate-500">
                  <div>
                    <BarChart3 className="mx-auto h-10 w-10 text-slate-400" />
                    <p className="mt-3 font-medium">Selecione uma cidade com histórico</p>
                    <p className="mt-1 text-sm">Os valores do indicador aparecerão aqui após a consulta.</p>
                  </div>
                </div>
              )}
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}

export default CityIndicatorsHistoryPage;
