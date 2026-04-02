import React, { useState, useEffect } from 'react';
import { salvarDadosManualCidade, obterDadosManualCidade } from '../services/api';
import './ManualDataForm.css';

/**
 * ManualDataForm Refatorado - Formulário dinâmico para 47 indicadores ISO
 * 
 * Arquitetura:
 * - INDICADORES_CONFIG: Mapeamento dinâmico de todos os 47 indicadores
 * - Nested State: Indicadores organizados por ISO (iso_37120, iso_37122, iso_37123)
 * - Tabs UI: Alternar entre 3 normas ISO
 * - Dynamic Rendering: Loop através da config para criar inputs
 * - Tailwind Grid: Responsivo (1 col mobile, 2 col tablet, 3 col desktop)
 * 
 * Campos Totais: 47
 * - ISO 37120: 16 indicadores (economia, governança, habitação, segurança)
 * - ISO 37122: 15 indicadores (smart cities, TIC, energia, infraestrutura)
 * - ISO 37123 + Sendai: 16 indicadores (resiliência, gestão desastres)
 */

// ==========================================
// CONFIGURAÇÃO DINÂMICA DE INDICADORES (47 campos totais)
// ==========================================

const INDICADORES_CONFIG = {
  iso_37120: {
    titulo: "Qualidade de Vida (ISO 37120)",
    descricao: "Cidades Sustentáveis e Resilientes",
    icone: "🏙️",
    cor: "from-purple-500 to-purple-700",
    campos: [
      // Economia e Finanças
      { key: "taxa_desemprego_pct", label: "Taxa de Desemprego", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "taxa_endividamento_pct", label: "Taxa de Endividamento", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "despesas_capital_pct", label: "Despesas de Capital", unidade: "% orçamento", tipo: "number", min: 0, max: 100 },
      { key: "receita_propria_pct", label: "Receita Própria", unidade: "% receita total", tipo: "number", min: 0, max: 100 },
      { key: "orcamento_per_capita", label: "Orçamento per capita", unidade: "R$", tipo: "number", min: 0 },
      // Governança
      { key: "mulheres_eleitas_pct", label: "Mulheres Eleitas em Cargos", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "condenacoes_corrupcao_100k", label: "Condenações por Corrupção", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "participacao_eleitoral_pct", label: "Participação Eleitoral", unidade: "%", tipo: "number", min: 0, max: 100 },
      // Habitação
      { key: "moradias_inadequadas_pct", label: "Moradias Inadequadas", unidade: "% população", tipo: "number", min: 0, max: 100 },
      { key: "sem_teto_100k", label: "Sem-teto", unidade: "/100k hab", tipo: "number", min: 0 },
      // Segurança
      { key: "bombeiros_100k", label: "Bombeiros", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "mortes_incendio_100k", label: "Mortes por Incêndio", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "agentes_policia_100k", label: "Agentes de Polícia", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "homicidios_100k", label: "Homicídios", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "acidentes_industriais_100k", label: "Acidentes Industriais", unidade: "/100k hab", tipo: "number", min: 0 },
    ]
  },
  iso_37122: {
    titulo: "Cidades Inteligentes (ISO 37122)",
    descricao: "Indicadores de Smart Cities",
    icone: "🤖",
    cor: "from-orange-500 to-orange-700",
    campos: [
      // Economia Smart e Educação
      { key: "sobrevivencia_novos_negocios_100k", label: "Sobrevivência Novos Negócios", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "empregos_tic_pct", label: "Empregos em TIC", unidade: "% força trabalho", tipo: "number", min: 0, max: 100 },
      { key: "graduados_stem_100k", label: "Graduados STEM", unidade: "/100k hab", tipo: "number", min: 0 },
      // Energia e Meio Ambiente
      { key: "energia_residuos_pct", label: "Energia de Resíduos", unidade: "% energia total", tipo: "number", min: 0, max: 100 },
      { key: "iluminacao_telegestao_pct", label: "Iluminação Pública com Telegestão", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "medidores_inteligentes_energia_pct", label: "Medidores Inteligentes de Energia", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "edificios_verdes_pct", label: "Edifícios Verdes Certificados", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "monitoramento_ar_tempo_real_pct", label: "Monitoramento de Ar em Tempo Real", unidade: "%", tipo: "number", min: 0, max: 100 },
      // Serviços e Saúde
      { key: "servicos_urbanos_online_pct", label: "Serviços Urbanos Online", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "prontuario_eletronico_pct", label: "Prontuário Eletrônico", unidade: "% população", tipo: "number", min: 0, max: 100 },
      { key: "consultas_remotas_100k", label: "Consultas Remotas", unidade: "/100k hab", tipo: "number", min: 0 },
      // Infraestrutura e Mobilidade
      { key: "medidores_inteligentes_agua_pct", label: "Medidores Inteligentes de Água", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "areas_cobertas_cameras_pct", label: "Áreas Cobertas por Câmeras", unidade: "% cidade", tipo: "number", min: 0, max: 100 },
      { key: "lixeiras_sensores_pct", label: "Lixeiras com Sensores", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "semaforos_inteligentes_pct", label: "Semáforos Inteligentes", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "frota_onibus_limpos_pct", label: "Frota de Ônibus Zero Emissão", unidade: "%", tipo: "number", min: 0, max: 100 },
    ]
  },
  iso_37123: {
    titulo: "Resiliência e Segurança (ISO 37123 + Sendai)",
    descricao: "Indicadores de Resiliência e Gestão de Riscos de Desastres",
    icone: "🛡️",
    cor: "from-red-500 to-red-700",
    campos: [
      // Resiliência Econômica e Social
      { key: "seguro_ameacas_pct", label: "População com Seguro contra Ameaças", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "empregos_informais_pct", label: "Empregos Informais", unidade: "% força trabalho", tipo: "number", min: 0, max: 100 },
      { key: "escolas_preparacao_emergencia_pct", label: "Escolas com Plano de Emergência", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "populacao_treinada_emergencia_pct", label: "População Treinada para Emergência", unidade: "%", tipo: "number", min: 0, max: 100 },
      // Saúde e Preparação
      { key: "hospitais_geradores_backup_pct", label: "Hospitais com Gerador Backup", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "seguro_saude_basico_pct", label: "População com Seguro Saúde Básico", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "imunizacao_pct", label: "Taxa de Imunização", unidade: "% população", tipo: "number", min: 0, max: 100 },
      // Infraestrutura e Prevenção
      { key: "abrigos_emergencia_100k", label: "Abrigos de Emergência", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "edificios_vulneraveis_pct", label: "Edifícios Vulneráveis a Desastres", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "rotas_evacuacao_100k", label: "Rotas de Evacuação Identificadas", unidade: "/100k", tipo: "number", min: 0 },
      { key: "reservas_alimentos_72h_pct", label: "Cidades com Reservas 72h Alimentos", unidade: "%", tipo: "number", min: 0, max: 100 },
      { key: "mapas_ameacas_publicos_pct", label: "Mapas de Ameaças Públicos e Atualizados", unidade: "%", tipo: "number", min: 0, max: 100 },
      // Marco de Sendai - Redução de Riscos
      { key: "mortalidade_desastres_100k", label: "Mortalidade por Desastres", unidade: "/100k hab", tipo: "number", min: 0 },
      { key: "pessoas_afetadas_desastres_100k", label: "Pessoas Afetadas por Desastres", unidade: "/100k", tipo: "number", min: 0 },
      { key: "perdas_desastres_pct_pib", label: "Perdas Econômicas por Desastres", unidade: "% PIB", tipo: "number", min: 0 },
      { key: "danos_infraestrutura_basica_pct", label: "Danos à Infraestrutura Básica", unidade: "%", tipo: "number", min: 0, max: 100 },
    ]
  }
};

// ==========================================
// ESTADO INICIAL PARA TODOS OS INDICADORES (47 campos)
// ==========================================

const INDICADORES_INICIAL = {
  iso_37120: Object.fromEntries(INDICADORES_CONFIG.iso_37120.campos.map(c => [c.key, ''])),
  iso_37122: Object.fromEntries(INDICADORES_CONFIG.iso_37122.campos.map(c => [c.key, ''])),
  iso_37123: Object.fromEntries(INDICADORES_CONFIG.iso_37123.campos.map(c => [c.key, ''])),
};

// ==========================================
// COMPONENTE PRINCIPAL
// ==========================================

function ManualDataForm() {
  // State - Identificação
  const [codigoIBGE, setCodigoIBGE] = useState('');
  const [nomeCidade, setNomeCidade] = useState('');
  const [usuarioAtualizou, setUsuarioAtualizou] = useState('');
  
  // State - Indicadores (ANINHADOS por ISO)
  const [indicadores, setIndicadores] = useState(INDICADORES_INICIAL);
  
  // State - UI
  const [abaSelecionada, setAbaSelecionada] = useState('iso_37120');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  // ==========================================
  // EFEITO - CARREGAR DADOS AO MUDAR IBGE
  // ==========================================

  useEffect(() => {
    const carregarDados = async () => {
      if (!codigoIBGE || codigoIBGE.length !== 7) return;
      
      try {
        setLoading(true);
        const response = await obterDadosManualCidade(codigoIBGE);
        
        if (response.success && response.data) {
          const dados = response.data.dados || {};
          
          // Mapear dados do backend para o novo formato aninhado
          setIndicadores({
            iso_37120: dados.iso_37120 || INDICADORES_INICIAL.iso_37120,
            iso_37122: dados.iso_37122 || INDICADORES_INICIAL.iso_37122,
            iso_37123: dados.iso_37123 || INDICADORES_INICIAL.iso_37123,
          });
          
          setNomeCidade(response.data.nome_cidade || '');
          setIsEditing(true);
          setMessage('');
          setError('');
        }
      } catch (err) {
        // Cidade não tem dados ainda - OK para criar novo
        setIsEditing(false);
        setIndicadores(INDICADORES_INICIAL);
      } finally {
        setLoading(false);
      }
    };
    
    carregarDados();
  }, [codigoIBGE]);

  // ==========================================
  // HANDLER - MUDANÇA DE INDICADOR (NESTED STATE)
  // ==========================================

  /**
   * Atualiza indicador mantendo a estrutura aninhada
   * @param {string} isoNorm - Chave da norma (iso_37120, iso_37122, iso_37123)
   * @param {string} fieldKey - Chave do campo dentro da norma
   * @param {string|number} value - Novo valor
   */
  const handleManualIndicatorChange = (isoNorm, fieldKey, value) => {
    setIndicadores(prev => ({
      ...prev,
      [isoNorm]: {
        ...prev[isoNorm],
        [fieldKey]: value
      }
    }));
  };

  // ==========================================
  // HANDLER - ENVIO DO FORMULÁRIO
  // ==========================================

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validações
    if (!codigoIBGE || codigoIBGE.length !== 7) {
      setError('❌ Código IBGE deve ter 7 dígitos');
      return;
    }
    
    if (!nomeCidade.trim()) {
      setError('❌ Nome da cidade é obrigatório');
      return;
    }
    
    if (!usuarioAtualizou.trim()) {
      setError('❌ Descrição do usuário/responsável é obrigatória');
      return;
    }
    
    // Validar que pelo menos um indicador foi preenchido
    const temIndicador = Object.values(indicadores).some(iso =>
      Object.values(iso).some(val => val !== '' && val !== null && val !== 0)
    );
    
    if (!temIndicador) {
      setError('❌ Preencha pelo menos um indicador');
      return;
    }

    setLoading(true);
    setMessage('');
    setError('');

    try {
      // Converter strings vazias para null e fazer parse de números
      const dados_limpos = {};
      Object.entries(indicadores).forEach(([isoKey, isoData]) => {
        dados_limpos[isoKey] = {};
        Object.entries(isoData).forEach(([fieldKey, value]) => {
          if (value === '' || value === null) {
            dados_limpos[isoKey][fieldKey] = null;
          } else {
            dados_limpos[isoKey][fieldKey] = parseFloat(value) || null;
          }
        });
      });

      const payload = {
        nome_cidade: nomeCidade,
        usuario_atualizou: usuarioAtualizou,
        dados: dados_limpos
      };

      await salvarDadosManualCidade(codigoIBGE, payload);
      
      setMessage(`✅ ${isEditing ? 'Dados atualizados' : 'Dados salvos'} com sucesso para ${nomeCidade}!`);
      setIsEditing(true);
      
      // Limpar mensagem após 3 segundos
      setTimeout(() => {
        setMessage('');
      }, 3000);
      
    } catch (err) {
      setError(`❌ Erro ao salvar dados: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // HANDLER - LIMPAR FORMULÁRIO
  // ==========================================

  const handleLimpar = () => {
    setCodigoIBGE('');
    setNomeCidade('');
    setUsuarioAtualizou('');
    setIndicadores(INDICADORES_INICIAL);
    setAbaSelecionada('iso_37120');
    setIsEditing(false);
    setMessage('');
    setError('');
  };

  // ==========================================
  // RENDER
  // ==========================================

  return (
    <div className="manual-data-form-container">
      <div className="form-header">
        <h2>📊 Dados Manuais de Cidades</h2>
        <p className="form-subtitle">
          47 indicadores ISO 37120/37122/37123 coletados manualmente por prefeituras
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="manual-data-form">
        
        {/* SEÇÃO: IDENTIFICAÇÃO */}
        <div className="form-section section-identification">
          <h3 className="section-title">🏛️ Identificação da Cidade</h3>
          
          <div className="form-row">
            <div className="form-group form-group-half">
              <label htmlFor="codigoIBGE">Código IBGE *</label>
              <input
                type="text"
                id="codigoIBGE"
                value={codigoIBGE}
                onChange={(e) => setCodigoIBGE(e.target.value.replace(/\D/g, '').slice(0, 7))}
                placeholder="Ex: 4101408"
                maxLength="7"
                disabled={isEditing && codigoIBGE.length === 7}
                className="input-field"
                required
              />
              <small>Código IBGE (7 dígitos) - Não pode ser alterado após criar</small>
            </div>
            
            <div className="form-group form-group-half">
              <label htmlFor="nomeCidade">Nome da Cidade *</label>
              <input
                type="text"
                id="nomeCidade"
                value={nomeCidade}
                onChange={(e) => setNomeCidade(e.target.value)}
                placeholder="Ex: Apucarana"
                className="input-field"
                required
              />
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="usuarioAtualizou">Responsável pela Atualização *</label>
            <input
              type="text"
              id="usuarioAtualizou"
              value={usuarioAtualizou}
              onChange={(e) => setUsuarioAtualizou(e.target.value)}
              placeholder="Ex: João Silva (joao@prefeitura.com)"
              className="input-field"
              required
            />
            <small>Nome e/ou email do responsável pela atualização dos dados</small>
          </div>
        </div>

        {/* MENSAGENS */}
        {message && <div className="message-success">{message}</div>}
        {error && <div className="message-error">{error}</div>}

        {/* SEÇÃO: INDICADORES COM ABAS */}
        <div className="form-section section-indicators">
          <h3 className="section-title">📈 Indicadores por Norma ISO</h3>
          
          {/* NAVEGAÇÃO DE ABAS */}
          <div className="tabs-navigation">
            {Object.entries(INDICADORES_CONFIG).map(([isoKey, isoData]) => (
              <button
                key={isoKey}
                type="button"
                className={`tab-button ${abaSelecionada === isoKey ? 'active' : ''}`}
                onClick={() => setAbaSelecionada(isoKey)}
              >
                <span className="tab-icon">{isoData.icone}</span>
                <span className="tab-title">{isoData.titulo}</span>
              </button>
            ))}
          </div>

          {/* CONTEÚDO DAS ABAS */}
          <div className="tabs-content">
            {Object.entries(INDICADORES_CONFIG).map(([isoKey, isoData]) => (
              abaSelecionada === isoKey && (
                <div key={isoKey} className={`tab-pane tab-pane-${isoKey}`}>
                  <div className={`tab-header bg-gradient-to-r ${isoData.cor}`}>
                    <h4>{isoData.titulo}</h4>
                    <p>{isoData.descricao}</p>
                  </div>

                  {/* GRID DE CAMPOS - RESPONSIVO */}
                  <div className="indicators-grid">
                    {isoData.campos.map((campo) => (
                      <div key={campo.key} className="indicator-field">
                        <label htmlFor={campo.key}>
                          {campo.label}
                          <span className="unit-badge">{campo.unidade}</span>
                        </label>
                        <input
                          id={campo.key}
                          type={campo.tipo}
                          min={campo.min}
                          max={campo.max}
                          step="0.01"
                          value={indicadores[isoKey][campo.key] || ''}
                          onChange={(e) => handleManualIndicatorChange(isoKey, campo.key, e.target.value)}
                          placeholder="Digite o valor..."
                          className="input-number"
                        />
                      </div>
                    ))}
                  </div>

                  <div className="tab-footer">
                    <p className="fields-count">
                      <strong>{isoData.campos.length} indicadores</strong> | 
                      <strong>Preenchidos: {Object.values(indicadores[isoKey]).filter(v => v !== '').length}</strong>
                    </p>
                  </div>
                </div>
              )
            ))}
          </div>
        </div>

        {/* BOTÕES DE AÇÃO */}
        <div className="form-actions">
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? '⏳ Salvando...' : `💾 ${isEditing ? 'Atualizar' : 'Salvar'} Dados`}
          </button>
          <button
            type="button"
            onClick={handleLimpar}
            disabled={loading}
            className="btn btn-secondary"
          >
            🔄 Limpar Formulário
          </button>
        </div>

        {isEditing && (
          <div className="info-box">
            ℹ️ <strong>Modo de edição:</strong> Você pode atualizar os dados desta cidade. 
            Cada alteração é registrada automaticamente no histórico para auditoria.
          </div>
        )}
      </form>
    </div>
  );
}

export default ManualDataForm;
