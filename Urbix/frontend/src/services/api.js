import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getIndicators = async () => {
  const response = await api.get('/indicators');
  return response.data;
};

export const getIndicatorById = async (id) => {
  const response = await api.get(`/indicators/${id}`);
  return response.data;
};

export const createIndicator = async (indicatorData) => {
  const response = await api.post('/indicators', indicatorData);
  return response.data;
};

export default api;