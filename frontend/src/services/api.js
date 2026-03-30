/**
 * API Service - Handles all backend API calls
 */
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000 // 30 seconds
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// ============ Authentication APIs ============

export const registerUser = async (userData) => {
  const response = await api.post('/api/auth/register', userData);
  return response.data;
};

export const getUser = async (walletAddress) => {
  const response = await api.get(`/api/auth/user/${walletAddress}`);
  return response.data;
};

export const getAllUsers = async () => {
  const response = await api.get('/api/auth/users');
  return response.data;
};

// ============ Drug Management APIs ============

export const validateComposition = async (drugName, composition) => {
  const response = await api.post('/api/drugs/validate-composition', {
    drugName,
    composition
  });
  return response.data;
};

export const registerDrug = async (drugData) => {
  const response = await api.post('/api/drugs/register', drugData);
  return response.data;
};

export const transferOwnership = async (transferData) => {
  const response = await api.post('/api/drugs/transfer', transferData);
  return response.data;
};

export const getDrugInfo = async (batchId) => {
  const response = await api.get(`/api/drugs/batch/${batchId}`);
  return response.data;
};

export const getAllDrugs = async () => {
  const response = await api.get('/api/drugs/all');
  return response.data;
};

// ============ Verification APIs ============

export const verifyDrug = async (batchId) => {
  const response = await api.get(`/api/verify/${batchId}`);
  return response.data;
};

export const getOwnershipHistory = async (batchId) => {
  const response = await api.get(`/api/verify/history/${batchId}`);
  return response.data;
};

export const batchVerifyDrugs = async (batchIds) => {
  const response = await api.post('/api/verify/batch-verify', batchIds);
  return response.data;
};

// ============ Audit APIs ============

export const getAuditStatistics = async () => {
  const response = await api.get('/api/audit/statistics');
  return response.data;
};

export const getAnomalies = async () => {
  const response = await api.get('/api/audit/anomalies');
  return response.data;
};

export const getExpiredDrugs = async () => {
  const response = await api.get('/api/audit/expired-drugs');
  return response.data;
};

export const getUserActivity = async (walletAddress) => {
  const response = await api.get(`/api/audit/user-activity/${walletAddress}`);
  return response.data;
};

// ============ Health Check APIs ============

export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
