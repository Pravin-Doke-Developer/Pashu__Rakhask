import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000',
  timeout: 120000,
});

export const checkHealth = () => api.get('/health');
export const getModelsStatus = () => api.get('/status');

export const predictDisease = (formData) =>
  api.post('/predict/disease', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const predictBreed = (formData) =>
  api.post('/predict/breed', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const getPredictionHistory = () => api.get('/history');

export default api;
