import React, { useMemo } from 'react';
import { Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js';
import { formatIndicatorLabel, formatIndicatorValue } from './RankingTable';
import './IndicatorsComparisonChart.css';

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

const AXES_MAPPING = {
  'Economia & Governança': [
    'taxa_geracao_empregos',
    'taxa_desemprego',
    'despesas_capital',
    'receita_propria',
    'orcamento_per_capita',
  ],
  'Sociedade & Segurança': ['bombeiros', 'agentes_policia', 'homicidios', 'sem_teto'],
  'Educação & Inovação': ['relacao_estudante_professor', 'ideb_iniciais', 'empregos_tic'],
  'Sustentabilidade & Smart City': [
    'estrutura_tic_municipal',
    'servicos_informativos_municipio',
    'canal_telefonico_municipal',
    'medidores_inteligentes_agua',
    'atendimento_agua_snis',
    'atendimento_esgoto_snis',
    'perdas_distribuicao_agua_snis',
    'coleta_esgoto_snis',
    'tratamento_esgoto_snis',
    'investimento_saneamento_snis',
    'despesa_saneamento_snis',
  ],
  Resiliência: ['abrigos_emergencia', 'rotas_evacuacao', 'mapas_ameacas_publicos'],
  Conectividade: ['densidade_banda_larga'],
};

const TERMOS_NEGATIVOS = [
  'desemprego', 'endividamento', 'homicidios', 'mortes', 'inadequadas',
  'sem_teto', 'acidentes', 'corrupcao', 'mortalidade', 'afetadas',
  'perdas', 'danos',
];

const COLORS = [
  { border: 'rgba(37, 99, 235, 1)', background: 'rgba(37, 99, 235, 0.18)' },
  { border: 'rgba(220, 38, 38, 1)', background: 'rgba(220, 38, 38, 0.18)' },
  { border: 'rgba(22, 163, 74, 1)', background: 'rgba(22, 163, 74, 0.18)' },
  { border: 'rgba(217, 119, 6, 1)', background: 'rgba(217, 119, 6, 0.18)' },
];

function isNumber(value) {
  return value !== null && value !== undefined && value !== '' && Number.isFinite(Number(value));
}

function IndicatorsComparisonChart({ cidades, matrizDecisao, indicadores }) {
  const chartData = useMemo(() => {
    if (!cidades?.length || !matrizDecisao?.length || !indicadores?.length) return null;

    const activeAxes = Object.entries(AXES_MAPPING).filter(([, axisIndicators]) =>
      axisIndicators.some((indicator) => indicadores.includes(indicator))
    );

    if (!activeAxes.length) return null;

    const axisScores = cidades.map(() => ({}));

    activeAxes.forEach(([axisName, axisIndicators]) => {
      const availableIndicators = axisIndicators.filter((indicator) => indicadores.includes(indicator));

      cidades.forEach((_, cityIndex) => {
        const normalizedValues = availableIndicators
          .map((indicator) => {
            const values = cidades
              .map((__, index) => matrizDecisao[index]?.[indicator])
              .filter(isNumber)
              .map(Number);
            const value = matrizDecisao[cityIndex]?.[indicator];
            if (!isNumber(value) || !values.length) return null;

            const min = Math.min(...values);
            const max = Math.max(...values);
            let normalized = max === min ? 1 : (Number(value) - min) / (max - min);

            if (TERMOS_NEGATIVOS.some((term) => indicator.includes(term))) {
              normalized = 1 - normalized;
            }
            return normalized * 100;
          })
          .filter((value) => value !== null);

        axisScores[cityIndex][axisName] = normalizedValues.length
          ? normalizedValues.reduce((sum, value) => sum + value, 0) / normalizedValues.length
          : 0;
      });
    });

    return {
      labels: activeAxes.map(([axisName]) => axisName),
      datasets: cidades.map((cidade, index) => ({
        label: cidade,
        data: activeAxes.map(([axisName]) => axisScores[index][axisName]),
        borderColor: COLORS[index % COLORS.length].border,
        backgroundColor: COLORS[index % COLORS.length].background,
        pointBackgroundColor: COLORS[index % COLORS.length].border,
        pointBorderColor: '#fff',
        pointHoverRadius: 6,
        borderWidth: 2,
        fill: true,
      })),
    };
  }, [cidades, matrizDecisao, indicadores]);

  if (!chartData) {
    return <div className="no-data">📊 Dados insuficientes para montar o Radar.</div>;
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'bottom',
        labels: { usePointStyle: true, padding: 16 },
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${Number(context.raw).toFixed(1)} / 100`,
        },
      },
    },
    scales: {
      r: {
        min: 0,
        max: 100,
        beginAtZero: true,
        ticks: { stepSize: 25, display: false },
        pointLabels: { font: { size: 12, weight: '600' }, color: '#475569' },
      },
    },
  };

  return (
    <div className="indicators-comparison-chart">
      <div className="bg-slate-50 border-l-4 border-slate-500 p-4 mb-6 rounded-r shadow-sm">
        <h4 className="font-bold text-slate-800 mb-1">ℹ️ Desempenho Relativo por Eixo (0 a 100)</h4>
        <p className="text-sm text-slate-600">
          Um único radar compara os municípios selecionados. Cada linha representa uma cidade e cada eixo resume os indicadores disponíveis naquele tema.
        </p>
      </div>

      <div className="bg-white p-6 border rounded-xl shadow-sm mb-10">
        <div style={{ height: '520px', width: '100%' }}>
          <Radar data={chartData} options={options} />
        </div>
      </div>

      <div className="mt-8 border-t-2 border-emerald-300 pt-6">
        <h4 className="text-xl font-bold text-gray-800 mb-4">📋 Valores dos Indicadores</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded-lg shadow-sm">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-3 border-b border-r text-left font-semibold text-slate-700">Indicador</th>
                {cidades.map((cidade) => (
                  <th key={cidade} className="px-4 py-3 border-b text-right font-semibold text-emerald-800">{cidade}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {indicadores.map((indicator) => (
                <tr key={indicator} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-2 border-b border-r font-medium text-slate-600">
                    {formatIndicatorLabel(indicator)}
                  </td>
                  {cidades.map((_, cityIndex) => (
                    <td key={`${indicator}-${cityIndex}`} className="px-4 py-2 border-b text-right font-mono text-sm text-slate-800">
                      {formatIndicatorValue(indicator, matrizDecisao[cityIndex]?.[indicator])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default IndicatorsComparisonChart;
