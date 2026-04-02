import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==========================================
// INDICADORES - GET (Consulta)
// ==========================================

export const getIndicadores = async (filtros = {}) => {
  const params = new URLSearchParams();
  if (filtros.cidade) params.append('cidade', filtros.cidade);
  if (filtros.norma) params.append('norma', filtros.norma);
  if (filtros.grande_area) params.append('grande_area', filtros.grande_area);
  
  const response = await api.get(`/indicadores?${params.toString()}`);
  return response.data;
};

export const getIndicadorDetalhes = async (codigoIndicador) => {
  const response = await api.get(`/indicadores/${codigoIndicador}`);
  return response.data;
};

// ==========================================
// INDICADORES - POST (Inserção)
// ==========================================

export const criarIndicador = async (indicadorData) => {
  const response = await api.post('/indicadores', indicadorData);
  return response.data;
};

export const criarColeta = async (codigoIndicador, coletaData) => {
  const response = await api.post(
    `/indicadores/${codigoIndicador}/coletas`,
    coletaData
  );
  return response.data;
};

// ==========================================
// INDICADORES - PUT (Atualização)
// ==========================================

export const atualizarColeta = async (coletaId, coletaData) => {
  const response = await api.put(
    `/indicadores/coletas/${coletaId}`,
    coletaData
  );
  return response.data;
};

// ==========================================
// RANKING HÍBRIDO - TOPSIS com dados API + Prefeitura
// ==========================================

/**
 * Obtém ranking de cidades usando método TOPSIS com dados híbridos
 * 
 * @param {Array<{codigo_ibge: string, manual_indicators?: {...}}>} cities
 * @returns {Promise<{ranking: Array, detalhes_calculo: {...}}>}
 * 
 * Exemplo:
 * const result = await getHybridRanking([
 *   { codigo_ibge: "4101408" }, // Apucarana - só APIs
 *   { 
 *     codigo_ibge: "4113700", // Londrina - com dados manuais
 *     manual_indicators: {
 *       pontos_iluminacao_telegestao: 85,
 *       medidores_inteligentes_energia: 60
 *     }
 *   }
 * ]);
 */
export const getHybridRanking = async (cities) => {
  try {
    const response = await api.post('/topsis/ranking-hibrido', cities);
    return response.data;
  } catch (error) {
    // Tratamento de erros específicos
    if (error.response) {
      const status = error.response.status;
      const detail = error.response.data?.detail || 'Erro desconhecido';
      
      if (status === 422) {
        // Validação Pydantic
        throw new Error(
          `Dados inválidos: ${detail}`
        );
      }
      if (status === 400) {
        // Bad request (ex: <2 cidades)
        throw new Error(detail);
      }
      if (status === 502) {
        throw new Error(
          'Falha ao conectar com APIs externas (IBGE, SICONFI, DataSUS). Tente novamente mais tarde.'
        );
      }
      if (status === 500) {
        throw new Error(
          'Erro no servidor. Verifique os dados enviados: ' + detail
        );
      }
      throw new Error(detail);
    }
    throw new Error('Erro de rede ao conectar ao servidor');
  }
};

// ==========================================
// DADOS MANUAIS - Manual City Data
// ==========================================

/**
 * Cria ou atualiza dados manuais de uma cidade
 * 
 * @param {string} codigoIBGE - Código IBGE da cidade (ex: "4101408")
 * @param {Object} data - Dados manuais da cidade
 * @returns {Promise<{codigo_ibge, nome_cidade, dados, data_criacao, data_atualizacao}>}
 */
export const salvarDadosManualCidade = async (codigoIBGE, data) => {
  const response = await api.post(`/manual-data/${codigoIBGE}`, data);
  return response.data;
};

/**
 * Obtém dados manuais atuais de uma cidade
 * 
 * @param {string} codigoIBGE - Código IBGE da cidade
 * @returns {Promise<Object>} Dados da cidade
 */
export const obterDadosManualCidade = async (codigoIBGE) => {
  const response = await api.get(`/manual-data/${codigoIBGE}`);
  return response.data;
};

/**
 * Atualiza parcialmente dados manuais de uma cidade
 * 
 * @param {string} codigoIBGE - Código IBGE da cidade
 * @param {Object} data - Dados parciais a atualizar
 * @returns {Promise<Object>}
 */
export const atualizarDadosManualCidade = async (codigoIBGE, data) => {
  const response = await api.patch(`/manual-data/${codigoIBGE}`, data);
  return response.data;
};

/**
 * Obtém histórico completo de alterações dos dados manuais
 * 
 * @param {string} codigoIBGE - Código IBGE da cidade
 * @param {number} limit - Número máximo de registros (padrão: 10)
 * @returns {Promise<Array>} Lista de alterações com before/after
 */
export const obterHistoricoDadosManual = async (codigoIBGE, limit = 10) => {
  const response = await api.get(`/manual-data/${codigoIBGE}/history?limit=${limit}`);
  return response.data;
};

/**
 * Obtém série histórica dos indicadores calculados
 * 
 * @param {string} codigoIBGE - Código IBGE da cidade
 * @param {number} limit - Número de períodos (padrão: 12)
 * @returns {Promise<Array>} Lista de snapshots com indicadores ao longo do tempo
 */
export const obterHistoricoIndicadores = async (codigoIBGE, limit = 12) => {
  const response = await api.get(`/manual-data/${codigoIBGE}/indicadores/historico?limit=${limit}`);
  return response.data;
};

/**
 * Obtém série histórica dos rankings
 * 
 * @param {number} limit - Número de períodos (padrão: 24)
 * @returns {Promise<Array>} Lista de snapshots dos rankings ao longo do tempo
 */
export const obterHistoricoRankings = async (limit = 24) => {
  const response = await api.get(`/manual-data/rankings/historico?limit=${limit}`);
  return response.data;
};

/**
 * Obtém ranking de um período específico
 * 
 * @param {string} periodoReferencia - Período em formato "YYYY-MM"
 * @returns {Promise<Array>} Rankings do período especificado
 */
export const obterRankingPeriodo = async (periodoReferencia) => {
  const response = await api.get(`/manual-data/rankings/periodo/${periodoReferencia}`);
  return response.data;
};

export default api;