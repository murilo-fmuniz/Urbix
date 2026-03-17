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

export default api;