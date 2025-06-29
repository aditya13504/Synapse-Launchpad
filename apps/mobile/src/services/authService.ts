import axios from 'axios';
import { API_URL } from '../config';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export const login = async (email: string, password: string) => {
  try {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data.user;
  } catch (error) {
    console.error('Login error:', error);
    throw error;
  }
};

export const logout = async () => {
  try {
    await api.post('/api/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
    throw error;
  }
};

export const register = async (name: string, email: string, password: string, company: string) => {
  try {
    const response = await api.post('/api/auth/register', { name, email, password, company });
    return response.data.user;
  } catch (error) {
    console.error('Register error:', error);
    throw error;
  }
};

export const checkAuth = async () => {
  try {
    const response = await api.get('/api/auth/me');
    return response.data.user;
  } catch (error) {
    // Not authenticated
    return null;
  }
};

// Add token to all requests
api.interceptors.request.use(
  async (config) => {
    // You would typically get the token from secure storage
    // const token = await SecureStore.getItemAsync('token');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);