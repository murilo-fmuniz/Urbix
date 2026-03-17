import React from 'react';
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
import './IndicatorsChart.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function IndicatorsChart({ indicadores, onSelectCity }) {
  // Calcular média de cada indicador (levando em conta apenas coletas com dado_disponivel = true)
  const indicadorMedias = indicadores.map(ind => {
    const coletas = ind.dados_coleta || [];
    const coletasDisponiveis = coletas.filter(c => c.dado_disponivel);
    
    if (coletasDisponiveis.length === 0) {
      return {
        codigo: ind.codigo_indicador,
        nome: ind.nome,
        media: 0,
        contagemCidades: 0,
      };
    }
    
    const soma = coletasDisponiveis.reduce((acc, c) => acc + (c.valor_final || 0), 0);
    const media = soma / coletasDisponiveis.length;
    
    return {
      codigo: ind.codigo_indicador,
      nome: ind.nome,
      media: parseFloat(media.toFixed(2)),
      contagemCidades: coletasDisponiveis.length,
    };
  }).filter(item => item.contagemCidades > 0) // Remover indicadores sem dados
   .sort((a, b) => b.media - a.media); // Ordenar por média decrescente
  
  const data = {
    labels: indicadorMedias.map(item => item.codigo),
    datasets: [
      {
        label: 'Média dos Indicadores',
        data: indicadorMedias.map(item => item.media),
        backgroundColor: [
          'rgba(255, 107, 107, 0.7)',
          'rgba(255, 159, 64, 0.7)',
          'rgba(255, 206, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(153, 102, 255, 0.7)',
          'rgba(201, 203, 207, 0.7)',
        ],
        borderColor: [
          'rgba(255, 107, 107, 1)',
          'rgba(255, 159, 64, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(153, 102, 255, 1)',
          'rgba(201, 203, 207, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
      title: {
        display: true,
        text: 'Média de Indicadores por Cidade',
      },
      tooltip: {
        callbacks: {
          afterLabel: function(context) {
            const itemData = indicadorMedias[context.dataIndex];
            return `Cidades com dados: ${itemData.contagemCidades}`;
          },
        },
      },
    },
    scales: {
      x: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div className="indicators-chart-container">
      <div className="chart-wrapper">
        <Bar data={data} options={options} height={400} />
      </div>
      
      <div className="chart-info">
        <h3>📊 Resumo de Indicadores</h3>
        <div className="info-grid">
          <div className="info-card">
            <h4>Total de Indicadores</h4>
            <p>{indicadorMedias.length}</p>
          </div>
          <div className="info-card">
            <h4>Com Dados Disponíveis</h4>
            <p>{indicadorMedias.filter(i => i.contagemCidades > 0).length}</p>
          </div>
          <div className="info-card">
            <h4>Cidades Cadastradas</h4>
            <p>
              {[...new Set(
                indicadores.flatMap(ind => 
                  (ind.dados_coleta || []).map(c => c.cidade)
                )
              )].length}
            </p>
          </div>
        </div>
      </div>

      <div className="chart-hint">
        <p>💡 Clique em um filtro de cidade abaixo para ver indicadores detalhados</p>
      </div>
    </div>
  );
}

export default IndicatorsChart;
