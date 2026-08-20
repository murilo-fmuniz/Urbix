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
  "Economia & Governança": ["taxa_desemprego", "taxa_endividamento", "despesas_capital", "receita_propria", "orcamento_per_capita", "mulheres_eleitas", "condenacoes_corrupcao", "participacao_eleitoral"],
  "Urbanismo & Segurança": ["moradias_inadequadas", "sem_teto", "bombeiros", "mortes_incendio", "agentes_policia", "homicidios", "acidentes_industriais"],
  "Educação & Inovação": ["relacao_estudante_professor", "ideb_iniciais", "sobrevivencia_negocios", "empregos_tic", "graduados_stem"],
  "Sustentabilidade": ["energia_residuos", "iluminacao_telegestao", "medidores_inteligentes_energia", "edificios_verdes", "monitoramento_ar", "servicos_urbanos_online", "prontuario_eletronico", "consultas_remotas", "medidores_inteligentes_agua", "areas_cobertas_cameras", "lixeiras_sensores", "semaforos_inteligentes", "frota_onibus_zero_emissao", "escolas_conectadas_telegestao", "seguros_ameacas", "empregos_informais"],
  "Resiliência": ["escolas_plano_emergencia", "populacao_treinada_emergencia", "hospitais_gerador_backup", "seguro_saude_basico", "taxa_imunizacao", "abrigos_emergencia", "edificios_vulneraveis", "rotas_evacuacao", "reservas_alimentos_72h", "mapas_ameacas_publicos", "mortalidade_desastres", "pessoas_afetadas_desastres", "perdas_desastres_pib", "danos_infraestrutura"],
  "Conectividade": ["densidade_banda_larga"]
};

// Termos que indicam custo (quanto maior, pior)
const TERMOS_NEGATIVOS = ["desemprego", "endividamento", "homicidios", "mortes", "inadequadas", "sem_teto", "acidentes", "corrupcao", "mortalidade", "afetadas", "perdas", "danos"];

function IndicatorsComparisonChart({ cidades, matrizDecisao, indicadores }) {
  
  const chartDataPerCity = useMemo(() => {
    if (!cidades || !matrizDecisao || !indicadores) return null;

    // 1. Filtra Eixos que possuem dados
    const activeAxes = Object.entries(AXES_MAPPING).filter(([_, axisIndicators]) => {
      return axisIndicators.some(ind => indicadores.includes(ind));
    });

    if (activeAxes.length === 0) return null;

    // 2. Acha Máximo e Mínimo Global para cada indicador (para a escala de 0 a 100)
    const statsPerIndicator = {};
    indicadores.forEach(ind => {
      const vals = cidades.map((_, i) => Number(matrizDecisao[i]?.[ind]) || 0);
      statsPerIndicator[ind] = {
        min: Math.min(...vals),
        max: Math.max(...vals)
      };
    });

    const axisScoresPerCity = cidades.map(() => ({}));

    // 3. Normalização (0 a 100%)
    cidades.forEach((_, cityIdx) => {
      activeAxes.forEach(([axisName, axisIndicators]) => {
        let totalScore = 0;
        let count = 0;

        axisIndicators.forEach(ind => {
          if (indicadores.includes(ind)) {
            const rawVal = Number(matrizDecisao[cityIdx]?.[ind]) || 0;
            const { min, max } = statsPerIndicator[ind];

            let normalized = 0;
            if (max === min) {
              normalized = 1; // Empate
            } else {
              normalized = (rawVal - min) / (max - min);
            }

            // Inverte nota se for custo (ex: desemprego alto = nota baixa)
            if (TERMOS_NEGATIVOS.some(termo => ind.includes(termo))) {
              normalized = 1 - normalized; 
            }

            // Para gráficos separados, o valor real de 0 a 100 fica ótimo
            totalScore += (normalized * 100);
            count++;
          }
        });

        axisScoresPerCity[cityIdx][axisName] = count > 0 ? (totalScore / count) : 0;
      });
    });

    const axesNames = activeAxes.map(([name]) => name);
    
    // Paleta de Cores (Uma cor para cada cidade)
    const colors = [
      { border: "rgba(59, 130, 246, 1)", bg: "rgba(59, 130, 246, 0.3)" }, // Azul (Cidade 1)
      { border: "rgba(239, 68, 68, 1)", bg: "rgba(239, 68, 68, 0.3)" },   // Vermelho (Cidade 2)
      { border: "rgba(34, 197, 94, 1)", bg: "rgba(34, 197, 94, 0.3)" },   // Verde (Cidade 3)
      { border: "rgba(245, 158, 11, 1)", bg: "rgba(245, 158, 11, 0.3)" }  // Laranja (Cidade 4)
    ];

    // 4. Monta um dataset isolado para cada cidade
    return cidades.map((cidade, idx) => {
      return {
        cidadeName: cidade,
        chartData: {
          labels: axesNames,
          datasets: [{
            label: cidade,
            data: axesNames.map(axis => axisScoresPerCity[idx][axis]),
            borderColor: colors[idx % colors.length].border,
            backgroundColor: colors[idx % colors.length].bg,
            pointBackgroundColor: colors[idx % colors.length].border,
            pointBorderColor: '#fff',
            pointHoverRadius: 6,
            borderWidth: 2,
            fill: true,
          }]
        }
      };
    });
  }, [cidades, matrizDecisao, indicadores]);

  if (!chartDataPerCity) return <div className="no-data">📊 Dados insuficientes para montar o Radar.</div>;

  const baseOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }, // Esconde a legenda pois o título já diz a cidade
      tooltip: {
        callbacks: {
          label: (context) => `Score: ${(context.raw).toFixed(1)} / 100`
        }
      }
    },
    scales: {
      r: {
        min: 0,
        max: 100, // Trava o gráfico rigorosamente de 0 a 100
        beginAtZero: true,
        ticks: { stepSize: 25, display: false },
        pointLabels: { font: { size: 12, weight: "600" }, color: '#475569' }
      }
    }
  };

  return (
    <div className="indicators-comparison-chart">
      <div className="bg-slate-50 border-l-4 border-slate-500 p-4 mb-6 rounded-r shadow-sm">
        <h4 className="font-bold text-slate-800 mb-1">ℹ️ Desempenho Relativo por Eixo (0 a 100)</h4>
        <p className="text-sm text-slate-600">
          Cada cidade possui seu próprio gráfico de atributos. A escala de 0 a 100 representa o desempenho relativo entre as cidades comparadas. Indicadores de impacto negativo (como desemprego ou sem-teto) foram invertidos.
        </p>
      </div>

      {/* GRID RESPONSIVO PARA OS GRÁFICOS SEPARADOS */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        {chartDataPerCity.map((data, index) => (
          <div key={index} className="bg-white p-6 border rounded-xl shadow-sm flex flex-col items-center">
            <h3 className="text-2xl font-bold text-slate-800 mb-4">{data.cidadeName}</h3>
            <div style={{ height: '400px', width: '100%' }}>
              <Radar data={data.chartData} options={baseOptions} />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-8 border-t-2 border-emerald-300 pt-6">
        <h4 className="text-xl font-bold text-gray-800 mb-4">📋 Consulta Rápida: Valores Brutos Extraídos</h4>
        <div className="overflow-x-auto">
          <table className="min-w-full bg-white border rounded-lg shadow-sm">
            <thead className="bg-slate-100">
              <tr>
                <th className="px-4 py-3 border-b border-r text-left font-semibold text-slate-700">Indicador Validado</th>
                {cidades.map((cidade, i) => (
                  <th key={i} className="px-4 py-3 border-b text-right font-semibold text-emerald-800">{cidade}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {indicadores.map((ind, i) => (
                <tr key={i} className="hover:bg-slate-50 transition-colors">
                  <td className="px-4 py-2 border-b border-r font-medium text-slate-600 capitalize">
                    {ind.replace(/_/g, ' ')}
                  </td>
                  {cidades.map((_, cidadeIdx) => {
                    const val = Number(matrizDecisao[cidadeIdx]?.[ind]) || 0;
                    return (
                      <td key={cidadeIdx} className="px-4 py-2 border-b text-right font-mono text-sm text-slate-800">
                        {val.toLocaleString('pt-BR', { maximumFractionDigits: 2 })}
                      </td>
                    );
                  })}
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