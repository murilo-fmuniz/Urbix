import React, { useState, useEffect } from 'react';
import { criarColeta, getIndicadores } from '../services/api';
import './AdminPage.css';

/**
 * AdminPage - Painel de administração para inserir dados de novas cidades
 * 
 * Indicadores disponíveis (ISO 37122):
 * ECO.1-5 (Economia), EDU.1-6 (Educação), GOV.1-6 (Governança)
 * SAU.1-4 (Saúde), HAB.1-3 (Habitação), AMB.1-6 (Ambiente)
 * SEG.1-3 (Segurança), RES.1-4 (Resiliência)
 */

function AdminPage() {
  const [cidade, setCidade] = useState('');
  const [estado, setEstado] = useState('');
  const [anoReferencia, setAnoReferencia] = useState(2026);
  const [indicadoresDisponíveis, setIndicadoresDisponíveis] = useState([]);
  
  // Seção 1: Denominadores Universais
  const [populacaoTotal, setPopulacaoTotal] = useState('');
  const [areaTotalKm2, setAreaTotalKm2] = useState('');
  const [pibTotal, setPibTotal] = useState('');

  // Seção 2: Dados Demográficos e Sociais
  const [forcaTrabalho, setForcaTrabalho] = useState('');
  const [desempregados, setDesempregados] = useState('');
  const [eleitoresRegistrados, setEleitoresRegistrados] = useState('');
  const [eleitoresVotaram, setEleitoresVotaram] = useState('');
  const [internetBandaLarga, setInternetBandaLarga] = useState('');
  const [planoSaude, setPlanoSaude] = useState('');
  const [moradiasInadequadas, setMoradiasInadequadas] = useState('');
  const [diplomadosSTEM, setDiplomadosSTEM] = useState('');

  // Seção 3: Dados da Prefeitura e Finanças
  const [despesasTotais, setDespesasTotais] = useState('');
  const [despesasAtivosFixos, setDespesasAtivosFixos] = useState('');
  const [novosNegociosAno, setNovosNegociosAno] = useState('');
  const [servicosUrbanosTotais, setServicosUrbanosTotais] = useState('');
  const [servicosOnline, setServicosOnline] = useState('');
  const [visitasPortalDados, setVisitasPortalDados] = useState('');

  // Seção 4: Infraestrutura e Saúde
  const [alunosMatriculados, setAlunosMatriculados] = useState('');
  const [dispositivosDigitais, setDispositivosDigitais] = useState('');
  const [teleconsultas, setTeleconsultas] = useState('');
  const [totalHospitais, setTotalHospitais] = useState('');
  const [hospitaisGerador, setHospitaisGerador] = useState('');
  const [totalEdificios, setTotalEdificios] = useState('');
  const [edificiosVulneraveis, setEdificiosVulneraveis] = useState('');
  const [areaSIGKm2, setAreaSIGKm2] = useState('');

  // Seção 5: Segurança Pública e Desastres
  const [efetivoPoliciais, setEfetivoPoliciais] = useState('');
  const [homicidiosAno, setHomicidiosAno] = useState('');
  const [areaCamerasKm2, setAreaCamerasKm2] = useState('');
  const [equipeEmergencia, setEquipeEmergencia] = useState('');
  const [equipesTreinadas, setEquipesTreinadas] = useState('');
  const [pessoasEvacuadas, setPessoasEvacuadas] = useState('');
  const [perdaFinanceiraDesastres, setPerdaFinanceiraDesastres] = useState('');

  // Seção 6: Meio Ambiente e Saneamento
  const [areaArvoresKm2, setAreaArvoresKm2] = useState('');
  const [volumeAgua, setVolumeAgua] = useState('');
  const [volumeAguaMonitorada, setVolumeAguaMonitorada] = useState('');
  const [plasticoGerado, setPlasticoGerado] = useState('');
  const [plasticoReciclado, setPlasticoReciclado] = useState('');

  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Carregar indicadores disponíveis ao montar componente
  useEffect(() => {
    const carregarIndicadores = async () => {
      try {
        const data = await getIndicadores();
        // Extrai lista única de códigos de indicadores
        const codigos = [...new Set(data.map(ind => ind.codigo_indicador))].sort();
        setIndicadoresDisponíveis(codigos);
      } catch (err) {
        console.error('Erro ao carregar indicadores:', err);
        setError('Falha ao carregar indicadores disponíveis');
      }
    };
    carregarIndicadores();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validações básicas
    if (!cidade.trim()) {
      setError('❌ Cidade é obrigatória');
      return;
    }
    if (!estado.trim() || estado.length !== 2) {
      setError('❌ Estado deve ter 2 letras (ex: PR)');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      // Criar um mapa de código_indicador → valor_final
      const coletas = [
        { codigo: 'ECO.1', valor: populacaoTotal, nome: 'População Total' },
        { codigo: 'ECO.2', valor: areaTotalKm2, nome: 'Área Total' },
        { codigo: 'ECO.3', valor: pibTotal, nome: 'PIB Total' },
        { codigo: 'EDU.1', valor: forcaTrabalho, nome: 'PEA' },
        { codigo: 'EDU.2', valor: desempregados, nome: 'Desemprego' },
        { codigo: 'GOV.1', valor: eleitoresRegistrados, nome: 'Eleitores Registrados' },
        { codigo: 'GOV.2', valor: eleitoresVotaram, nome: 'Comparecimento Eleitoral' },
        { codigo: 'EDU.3', valor: internetBandaLarga, nome: 'Internet Banda Larga' },
        { codigo: 'SAU.1', valor: planoSaude, nome: 'Cobertura Saúde Privada' },
        { codigo: 'HAB.1', valor: moradiasInadequadas, nome: 'Moradias Inadequadas' },
        { codigo: 'EDU.4', valor: diplomadosSTEM, nome: 'Diplomados STEM' },
        { codigo: 'GOV.3', valor: despesasTotais, nome: 'Despesas Totais' },
        { codigo: 'ECO.4', valor: despesasAtivosFixos, nome: 'Despesas CAPEX' },
        { codigo: 'ECO.5', valor: novosNegociosAno, nome: 'Novos Negócios' },
        { codigo: 'GOV.4', valor: servicosUrbanosTotais, nome: 'Serviços Urbanos' },
        { codigo: 'GOV.5', valor: servicosOnline, nome: 'Serviços Online' },
        { codigo: 'GOV.6', valor: visitasPortalDados, nome: 'Visitas Portal Dados' },
        { codigo: 'EDU.5', valor: alunosMatriculados, nome: 'Alunos Matriculados' },
        { codigo: 'EDU.6', valor: dispositivosDigitais, nome: 'Dispositivos Digitais' },
        { codigo: 'SAU.2', valor: teleconsultas, nome: 'Teleconsultas' },
        { codigo: 'SAU.3', valor: totalHospitais, nome: 'Total de Hospitais' },
        { codigo: 'SAU.4', valor: hospitaisGerador, nome: 'Hospitais com Gerador' },
        { codigo: 'HAB.2', valor: totalEdificios, nome: 'Total de Edifícios' },
        { codigo: 'HAB.3', valor: edificiosVulneraveis, nome: 'Edifícios Vulneráveis' },
        { codigo: 'AMB.1', valor: areaSIGKm2, nome: 'Área Gerida por SIG' },
        { codigo: 'SEG.1', valor: efetivoPoliciais, nome: 'Efetivo Policiais' },
        { codigo: 'SEG.2', valor: homicidiosAno, nome: 'Homicídios' },
        { codigo: 'SEG.3', valor: areaCamerasKm2, nome: 'Área Câmeras' },
        { codigo: 'RES.1', valor: equipeEmergencia, nome: 'Equipes Emergência' },
        { codigo: 'RES.2', valor: equipesTreinadas, nome: 'Equipes Treinadas' },
        { codigo: 'RES.3', valor: pessoasEvacuadas, nome: 'Pessoas Evacuadas' },
        { codigo: 'RES.4', valor: perdaFinanceiraDesastres, nome: 'Perdas Desastres' },
        { codigo: 'AMB.2', valor: areaArvoresKm2, nome: 'Área Árvores' },
        { codigo: 'AMB.3', valor: volumeAgua, nome: 'Volume Água' },
        { codigo: 'AMB.4', valor: volumeAguaMonitorada, nome: 'Água Monitorada' },
        { codigo: 'AMB.5', valor: plasticoGerado, nome: 'Plástico Gerado' },
        { codigo: 'AMB.6', valor: plasticoReciclado, nome: 'Plástico Reciclado' },
      ];

      // Filtrar coletas com valores não vazios
      const coletasValidas = coletas.filter(col => col.valor !== '' && col.valor !== null);

      if (coletasValidas.length === 0) {
        setError('❌ Por favor preencha pelo menos um campo com dados');
        setLoading(false);
        return;
      }

      // Submeter cada coleta ao backend
      let sucessos = 0;
      let falhas = 0;
      const errors = [];

      for (const col of coletasValidas) {
        try {
          await criarColeta(col.codigo, {
            cidade,
            estado: estado.toUpperCase(),
            ano_referencia: anoReferencia,
            valor_numerador: null,
            valor_denominador: null,
            valor_final: parseFloat(col.valor) || null,
            dado_disponivel: true,
            auditoria: {
              fonte_nome: `Admin - ${new Date().toLocaleDateString('pt-BR')}`,
              fonte_url: null,
              data_extracao: new Date().toISOString().split('T')[0],
              observacoes: `${col.nome} inserido via painel administrativo`
            }
          });
          sucessos++;
        } catch (err) {
          falhas++;
          errors.push(`${col.codigo}: ${err.response?.data?.detail || err.message}`);
        }
      }

      // Gerar mensagem de resultado
      let resultadoMsg = `✅ ${sucessos} indicadores inseridos com sucesso para ${cidade}!`;
      if (falhas > 0) {
        resultadoMsg += `\n⚠️  ${falhas} indicadores falharam.`;
      }
      
      setMessage(resultadoMsg);
      
      // Se houver falhas, mostrar erros também
      if (falhas > 0) {
        console.warn('Erros ao inserir:', errors);
      }
      
      // Limpar formulário apenas após sucesso total
      if (falhas === 0) {
        setTimeout(() => {
          setCidade('');
          setEstado('');
          setPopulacaoTotal('');
          setAreaTotalKm2('');
          setPibTotal('');
          setForcaTrabalho('');
          setDesempregados('');
          setEleitoresRegistrados('');
          setEleitoresVotaram('');
          setInternetBandaLarga('');
          setPlanoSaude('');
          setMoradiasInadequadas('');
          setDiplomadosSTEM('');
          setDespesasTotais('');
          setDespesasAtivosFixos('');
          setNovosNegociosAno('');
          setServicosUrbanosTotais('');
          setServicosOnline('');
          setVisitasPortalDados('');
          setAlunosMatriculados('');
          setDispositivosDigitais('');
          setTeleconsultas('');
          setTotalHospitais('');
          setHospitaisGerador('');
          setTotalEdificios('');
          setEdificiosVulneraveis('');
          setAreaSIGKm2('');
          setEfetivoPoliciais('');
          setHomicidiosAno('');
          setAreaCamerasKm2('');
          setEquipeEmergencia('');
          setEquipesTreinadas('');
          setPessoasEvacuadas('');
          setPerdaFinanceiraDesastres('');
          setAreaArvoresKm2('');
          setVolumeAgua('');
          setVolumeAguaMonitorada('');
          setPlasticoGerado('');
          setPlasticoReciclado('');
          setMessage('');
        }, 3000);
      }

    } catch (err) {
      setError(`❌ Erro geral: ${err.response?.data?.detail || err.message}`);
      console.error(err);
    }
    
    setLoading(false);
  };

  const FormSection = ({ title, children }) => (
    <div className="form-section">
      <h3>{title}</h3>
      <div className="fields-grid">
        {children}
      </div>
    </div>
  );

  const FormField = ({ label, value, onChange, placeholder = '' }) => (
    <div className="form-field">
      <label>{label}</label>
      <input
        type="number"
        step="0.01"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );

  return (
    <div className="admin-page container">
      <div className="admin-header">
        <h1>🏛️ Painel Admin - Inserir Nova Cidade</h1>
        <p>Preencha os dados de uma nova cidade para gerar todos os indicadores</p>
      </div>

      <form onSubmit={handleSubmit} className="admin-form">
        {/* INFORMAÇÕES BÁSICAS */}
        <div className="form-section basic-info">
          <h3>Informações Básicas</h3>
          <div className="fields-grid">
            <div className="form-field">
              <label>Cidade *</label>
              <input
                type="text"
                value={cidade}
                onChange={(e) => setCidade(e.target.value)}
                placeholder="Ex: Maringá"
                required
              />
            </div>
            <div className="form-field">
              <label>Estado *</label>
              <input
                type="text"
                value={estado}
                onChange={(e) => setEstado(e.target.value)}
                placeholder="Ex: PR"
                maxLength="2"
                required
              />
            </div>
            <div className="form-field">
              <label>Ano de Referência</label>
              <input
                type="number"
                value={anoReferencia}
                onChange={(e) => setAnoReferencia(parseInt(e.target.value))}
              />
            </div>
          </div>
        </div>

        {/* SEÇÃO 1 */}
        <FormSection title="1️⃣ Denominadores Universais (A Base)">
          <FormField 
            label="População Total da Cidade" 
            value={populacaoTotal} 
            onChange={setPopulacaoTotal}
            placeholder="Ex: 130134"
          />
          <FormField 
            label="Área Total da Cidade (km²)" 
            value={areaTotalKm2} 
            onChange={setAreaTotalKm2}
            placeholder="Ex: 556.99"
          />
          <FormField 
            label="Produto Interno Bruto - PIB (R$)" 
            value={pibTotal} 
            onChange={setPibTotal}
            placeholder="Ex: 5000000000"
          />
        </FormSection>

        {/* SEÇÃO 2 */}
        <FormSection title="2️⃣ Dados Demográficos e Sociais">
          <FormField 
            label="Força de Trabalho (PEA)" 
            value={forcaTrabalho} 
            onChange={setForcaTrabalho}
          />
          <FormField 
            label="Número de Desempregados" 
            value={desempregados} 
            onChange={setDesempregados}
          />
          <FormField 
            label="Eleitores Registrados" 
            value={eleitoresRegistrados} 
            onChange={setEleitoresRegistrados}
          />
          <FormField 
            label="Eleitores que Votaram" 
            value={eleitoresVotaram} 
            onChange={setEleitoresVotaram}
          />
          <FormField 
            label="População com Internet de Banda Larga" 
            value={internetBandaLarga} 
            onChange={setInternetBandaLarga}
          />
          <FormField 
            label="População com Plano de Saúde Privado" 
            value={planoSaude} 
            onChange={setPlanoSaude}
          />
          <FormField 
            label="Pessoas em Moradias Inadequadas" 
            value={moradiasInadequadas} 
            onChange={setMoradiasInadequadas}
          />
          <FormField 
            label="Diplomados em Áreas STEM" 
            value={diplomadosSTEM} 
            onChange={setDiplomadosSTEM}
          />
        </FormSection>

        {/* SEÇÃO 3 */}
        <FormSection title="3️⃣ Dados da Prefeitura e Finanças">
          <FormField 
            label="Total de Despesas do Município (R$)" 
            value={despesasTotais} 
            onChange={setDespesasTotais}
          />
          <FormField 
            label="Despesas em Ativos Fixos (R$)" 
            value={despesasAtivosFixos} 
            onChange={setDespesasAtivosFixos}
          />
          <FormField 
            label="Novos Negócios/Empresas do Período" 
            value={novosNegociosAno} 
            onChange={setNovosNegociosAno}
          />
          <FormField 
            label="Serviços Urbanos Oferecidos Pela Prefeitura" 
            value={servicosUrbanosTotais} 
            onChange={setServicosUrbanosTotais}
          />
          <FormField 
            label="Serviços Disponíveis 100% Online" 
            value={servicosOnline} 
            onChange={setServicosOnline}
          />
          <FormField 
            label="Visitas Anuais ao Portal de Dados Abertos" 
            value={visitasPortalDados} 
            onChange={setVisitasPortalDados}
          />
        </FormSection>

        {/* SEÇÃO 4 */}
        <FormSection title="4️⃣ Infraestrutura e Saúde">
          <FormField 
            label="Alunos Matriculados na Rede Pública" 
            value={alunosMatriculados} 
            onChange={setAlunosMatriculados}
          />
          <FormField 
            label="Dispositivos Digitais nas Escolas" 
            value={dispositivosDigitais} 
            onChange={setDispositivosDigitais}
          />
          <FormField 
            label="Teleconsultas Realizadas no Ano" 
            value={teleconsultas} 
            onChange={setTeleconsultas}
          />
          <FormField 
            label="Total de Hospitais na Cidade" 
            value={totalHospitais} 
            onChange={setTotalHospitais}
          />
          <FormField 
            label="Hospitais com Gerador de Energia" 
            value={hospitaisGerador} 
            onChange={setHospitaisGerador}
          />
          <FormField 
            label="Total de Edifícios/Imóveis" 
            value={totalEdificios} 
            onChange={setTotalEdificios}
          />
          <FormField 
            label="Edifícios Classificados como Vulneráveis" 
            value={edificiosVulneraveis} 
            onChange={setEdificiosVulneraveis}
          />
          <FormField 
            label="Área Gerida por SIG (km²)" 
            value={areaSIGKm2} 
            onChange={setAreaSIGKm2}
          />
        </FormSection>

        {/* SEÇÃO 5 */}
        <FormSection title="5️⃣ Segurança Pública e Desastres">
          <FormField 
            label="Efetivo Total de Policiais" 
            value={efetivoPoliciais} 
            onChange={setEfetivoPoliciais}
          />
          <FormField 
            label="Homicídios Registrados no Ano" 
            value={homicidiosAno} 
            onChange={setHomicidiosAno}
          />
          <FormField 
            label="Área Coberta por Câmeras (km²)" 
            value={areaCamerasKm2} 
            onChange={setAreaCamerasKm2}
          />
          <FormField 
            label="Total de Equipes de Emergência" 
            value={equipeEmergencia} 
            onChange={setEquipeEmergencia}
          />
          <FormField 
            label="Equipes com Treinamento para Desastres" 
            value={equipesTreinadas} 
            onChange={setEquipesTreinadas}
          />
          <FormField 
            label="Pessoas Evacuadas/Desalojadas" 
            value={pessoasEvacuadas} 
            onChange={setPessoasEvacuadas}
          />
          <FormField 
            label="Perda Financeira por Desastres (R$)" 
            value={perdaFinanceiraDesastres} 
            onChange={setPerdaFinanceiraDesastres}
          />
        </FormSection>

        {/* SEÇÃO 6 */}
        <FormSection title="6️⃣ Meio Ambiente e Saneamento">
          <FormField 
            label="Área Coberta por Copas de Árvores (km²)" 
            value={areaArvoresKm2} 
            onChange={setAreaArvoresKm2}
          />
          <FormField 
            label="Volume de Água Potável Distribuído" 
            value={volumeAgua} 
            onChange={setVolumeAgua}
          />
          <FormField 
            label="Volume de Água com Monitoramento" 
            value={volumeAguaMonitorada} 
            onChange={setVolumeAguaMonitorada}
          />
          <FormField 
            label="Total de Plástico Gerado (toneladas)" 
            value={plasticoGerado} 
            onChange={setPlasticoGerado}
          />
          <FormField 
            label="Plástico Reciclado (toneladas)" 
            value={plasticoReciclado} 
            onChange={setPlasticoReciclado}
          />
        </FormSection>

        {/* MENSAGENS */}
        {error && <div className="error-message">{error}</div>}
        {message && <div className="success-message">{message}</div>}

        {/* BOTÕES */}
        <div className="form-actions">
          <button 
            type="submit" 
            className="btn-submit"
            disabled={loading}
          >
            {loading ? 'Processando...' : '✅ Inserir Dados da Cidade'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default AdminPage;
