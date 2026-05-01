```javascript
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const API_BASE = 'http://localhost:8000/api';

const apiClient = axios.create({ baseURL: API_BASE });

apiClient.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('aetherion_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  login: (apiKey) => apiClient.post('/auth/login', { api_key: apiKey }),
};

export const tasksAPI = {
  runPipeline: (goal, idempotencyKey) =>
    apiClient.post('/tasks/pipeline', { goal }, {
      headers: { 'Idempotency-Key': idempotencyKey },
    }),
  getStatus: (taskId) => apiClient.get(`/tasks/pipeline/${taskId}`),
  getProgress: (taskId) => apiClient.get(`/tasks/pipeline/${taskId}/progress`),
};

export const agentsAPI = {
  list: () => apiClient.get('/agents'),
  catalog: (wsId) => apiClient.get(`/agent-catalog/${wsId}`),
  updateCatalog: (wsId, agents) => apiClient.put(`/agent-catalog/${wsId}`, { agents }),
};

export const councilAPI = {
  stats: () => apiClient.get('/council/stats'),
  judges: () => apiClient.get('/council/judges'),
};

export default apiClient;
