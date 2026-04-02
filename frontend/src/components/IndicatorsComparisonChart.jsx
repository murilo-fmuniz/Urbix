import React, { useMemo } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import './IndicatorsComparisonChart.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function IndicatorsComparisonChart({ cidades, matrizDecisao, indicadores }) {
  const chartData = useMemo(() => {
    if (!cidades || !matrizDecisao || !indicadores) {
      return null;
    }

    const colors = [
      '#1a73e8',
      '#4285f4',
      '#ea4335',
      '#fbbc04',
      '#34a853',
      '#8b4bff',
      '#46bdc6',
      '#ff6d00',
    ];

    // Dados para gráfico de barras (por indicador)
    const datasets = cidades.map((cidade, idx) => ({
      label: cidade,
      data: matrizDecisao[idx] || [],
      backgroundColor: colors[idx % colors.length],
      borderColor: colors[idx % colors.length],
      opacity: 0.7,
    }));

    return {
      labels: indicadores,
      datasets,
    };
  }, [cidades, matrizDecisao, indicadores]);

  if (!chartData) {
    return <div className="no-data">Dados de indicadores não disponíveis</div>;
  }

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          font: {
            size: 12,
          },
        },
      },
      title: {
        display: true,
        text: 'Comparação de Indicadores por Cidade',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Valor Normalizado (0-1)',
        },
      },
    },
  };

  return (
    <div className="indicators-comparison-chart">
      <div className="chart-container">
        <Bar data={chartData} options={options} />
      </div>

      <div className="indicators-table">
        <h4>📊 Matriz de Indicadores Normalizada</h4>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Cidade</th>
                {indicadores && indicadores.map((ind, i) => (
                  <th key={i}>{ind}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cidades && cidades.map((cidade, i) => (
                <tr key={i}>
                  <td className="city-name"><strong>{cidade}</strong></td>
                  {matrizDecisao[i] && matrizDecisao[i].map((valor, j) => (
                    <td key={j} className="valor">
                      {typeof valor === 'number' ? valor.toFixed(4) : valor}
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
