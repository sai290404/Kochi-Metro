import axios from 'axios';

const API_BASE_URL = 'https://kochi-metro-system.onrender.com';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API service functions
export const apiService = {
  // Health check
  healthCheck: () => api.get('/health'),

  // Data management
  refreshData: () => api.post('/data/refresh'),

  // Train operations
  getAllTrains: () => api.get('/trains'),
  getTrainDetails: (trainId) => api.get(`/trains/${trainId}`),

  // Optimization
  runOptimization: (params = {}) => api.post('/optimize', params),

  // Dashboard
  getDashboardSummary: () => api.get('/dashboard/summary'),
  getAlerts: () => api.get('/alerts'),

  // Simulation
  runSimulation: (scenarios) => api.post('/simulation', { scenarios }),
};

export default apiService;
