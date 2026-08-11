
import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export const login = (email, password) => {
  return api.post('/token', new URLSearchParams({
    'username': email,
    'password': password
  }), {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
  });
};

export const register = (email, password) => {
  return api.post('/register', { email, password });
};

export const getHistory = () => {
  return api.get('/history');
};

export const submitQuestionnaire = (answers) => {
  return api.post('/predict_questionnaire', { answers });
};

export const predictMenopause = (data) => {
  return api.post('/predict_questionnaire', { answers: data });
};

export const getModelColumns = () => {
  return api.get('/model/columns');
};

export default api;
