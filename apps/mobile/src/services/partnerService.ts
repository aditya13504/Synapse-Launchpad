import axios from 'axios';
import { API_URL } from '../config';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export interface PartnerRecommendation {
  company_id: string;
  company_name: string;
  match_score: number;
  confidence: number;
  reasoning: {
    compatibility_factors: Record<string, number>;
    timing_score: number;
    behavioral_alignment: number;
  };
  metadata: Record<string, any>;
}

export const getPartnerRecommendations = async (): Promise<PartnerRecommendation[]> => {
  try {
    const response = await api.get('/api/partners/recommendations');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch partner recommendations:', error);
    throw error;
  }
};

export const getPartnerDetails = async (partnerId: string): Promise<PartnerRecommendation> => {
  try {
    const response = await api.get(`/api/partners/${partnerId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch partner details for ${partnerId}:`, error);
    throw error;
  }
};

export const selectPartner = async (partnerId: string): Promise<void> => {
  try {
    await api.post('/api/partners/select', { partnerId });
  } catch (error) {
    console.error('Failed to select partner:', error);
    throw error;
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