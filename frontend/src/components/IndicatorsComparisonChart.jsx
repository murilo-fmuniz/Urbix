import React, { useState, useMemo } from 'react';
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

// ✅ Função para determinar categoria ISO baseado no índice do indicador
const getIndicatorCategory = (index) => {
  if (index < 18) return 'iso_37120'; // 0-17: ISO 37120 (18 indicadores)
  if (index < 34) return 'iso_37122'; // 18-33: ISO 37122 (16 indicadores)
  return 'iso_37123'; // 34-49: ISO 37123 + Sendai (16 indicadores)
};

// ✅ Mapa de categorias para exibição
const CATEGORY_INFO = {
  iso_37120: { label: 'ISO 37120 (Finanças, Governança)', color: '#ff9800', bgColor: '#fff3e0' },
  iso_37122: { label: 'ISO 37122 (Tecnologia, Energia)', color: '#9c27b0', bgColor: '#f3e5f5' },
  iso_37123: { label: 'ISO 37123 + Sendai (Resiliência, Saúde)', color: '#2196f3', bgColor: '#e3f2fd' },
};

const formatNormalizedAsPercent = (value) => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '—';
  }

  return `${(value * 100).toFixed(2)}%`;
};

function IndicatorsComparisonChart({ cidades, matrizDecisao, indicadores }) {
  // ✅ Estado para filtro de categorias ISO
  const [selectedCategories, setSelectedCategories] = useState(new Set(['iso_37120', 'iso_37122', 'iso_37123']));

  // ✅ Função para toggle de categoria
  const toggleCategory = (category) => {
    const newCategories = new Set(selectedCategories);
    if (newCategories.has(category)) {
      newCategories.delete(category);
    } else {
      newCategories.add(category);
    }
    setSelectedCategories(newCategories);
  };

  // ✅ Selecionar/deselecionar todas
  const selectAllCategories = () => {
    setSelectedCategories(new Set(['iso_37120', 'iso_37122', 'iso_37123']));
  };

  const deselectAllCategories = () => {
    setSelectedCategories(new Set());
  };

  // ✅ Filtra indicadores e dados baseado em categorias selecionadas
  const filteredData = useMemo(() => {
    if (!cidades || !matrizDecisao || !indicadores || selectedCategories.size === 0) {
      return null;
    }

    // Encontrar índices dos indicadores que devem ser exibidos
    const indicesToShow = indicadores
      .map((ind, idx) => ({ ind, idx }))
      .filter(({ idx }) => selectedCategories.has(getIndicatorCategory(idx)));

    if (indicesToShow.length === 0) {
      return null;
    }

    const colors = [
      '#1a73e8', '#4285f4', '#ea4335', '#fbbc04', '#34a853',
      '#8b4bff', '#46bdc6', '#ff6d00',
    ];

    // Dados para gráfico de barras (por indicador)
    const datasets = cidades.map((cidade, cidadeIdx) => ({
      label: cidade,
      data: indicesToShow.map(({ idx }) => matrizDecisao[cidadeIdx]?.[idx] || 0),
      backgroundColor: colors[cidadeIdx % colors.length],
      borderColor: colors[cidadeIdx % colors.length],
      opacity: 0.7,
    }));

    return {
      labels: indicesToShow.map(({ ind }) => ind),
      datasets,
      indicesToShow, // Guardar para uso na tabela
    };
  }, [cidades, matrizDecisao, indicadores, selectedCategories]);

  const chartData = useMemo(() => {
    if (!filteredData) {
      return null;
    }

    return {
      labels: filteredData.labels,
      datasets: filteredData.datasets,
    };
  }, [filteredData]);

  if (!chartData) {
    return (
      <div className="no-data">
        {selectedCategories.size === 0
          ? '⚠️ Selecione pelo menos uma categoria ISO'
          : '📊 Dados de indicadores não disponíveis'}
      </div>
    );
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
        text: `Comparação de Indicadores por Cidade (${filteredData.indicesToShow.length} indicadores, escala 0-100%)`,
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => `${context.dataset.label}: ${formatNormalizedAsPercent(context.parsed.y)}`,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Valor Normalizado (%)',
        },
        ticks: {
          callback: (value) => `${Number(value) * 100}%`,
        },
      },
    },
  };

  return (
    <div className="indicators-comparison-chart">
      {/* ✅ FILTRO ISO CATEGORIES */}
      <div className="iso-filter-section">
        <div className="filter-header">
          <h4>🏷️ Filtrar por Categoria ISO</h4>
          <div className="filter-buttons">
            <button
              className="filter-btn-small"
              onClick={selectAllCategories}
              title="Selecionar todas as categorias"
            >
              ✓ Todas
            </button>
            <button
              className="filter-btn-small"
              onClick={deselectAllCategories}
              title="Desselecionar todas as categorias"
            >
              ✗ Nenhuma
            </button>
          </div>
        </div>

        <div className="filter-checkboxes">
          {Object.entries(CATEGORY_INFO).map(([key, info]) => (
            <label key={key} className="filter-checkbox">
              <input
                type="checkbox"
                checked={selectedCategories.has(key)}
                onChange={() => toggleCategory(key)}
              />
              <span
                className="checkbox-label"
                style={{
                  borderLeft: `4px solid ${info.color}`,
                  paddingLeft: '8px',
                }}
              >
                {info.label}
              </span>
              <span className="checkbox-count">
                {key === 'iso_37120' ? '(18)' : key === 'iso_37122' ? '(16)' : '(16)'}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* GRÁFICO */}
      <div className="chart-container">
        <Bar data={chartData} options={options} />
      </div>

      {/* TABELA */}
      <div className="indicators-table">
        <h4>📊 Matriz de Indicadores Normalizada (escala percentual)</h4>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Cidade</th>
                {filteredData.indicesToShow && filteredData.indicesToShow.map(({ ind, idx }) => (
                  <th key={idx} title={`${ind} (${getIndicatorCategory(idx)})`}>
                    <span className="indicator-header">{ind}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {cidades && cidades.map((cidade, cidadeIdx) => (
                <tr key={cidadeIdx}>
                  <td className="city-name"><strong>{cidade}</strong></td>
                  {filteredData.indicesToShow && filteredData.indicesToShow.map(({ idx }) => (
                    <td key={idx} className="valor">
                      {formatNormalizedAsPercent(matrizDecisao[cidadeIdx]?.[idx])}
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
