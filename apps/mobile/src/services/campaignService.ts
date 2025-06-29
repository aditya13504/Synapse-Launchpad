import axios from 'axios';
import { API_URL } from '../config';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

export interface Campaign {
  id: string;
  name: string;
  objective: string;
  target_audience: string;
  tone: string;
  channels: string[];
  status: string;
  content: any;
  performance: any;
  created_at: string;
  updated_at: string;
}

export const getCampaigns = async (): Promise<Campaign[]> => {
  try {
    const response = await api.get('/api/campaigns');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch campaigns:', error);
    throw error;
  }
};

export const getCampaignDetails = async (campaignId: string): Promise<Campaign> => {
  try {
    const response = await api.get(`/api/campaigns/${campaignId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch campaign details for ${campaignId}:`, error);
    throw error;
  }
};

export const generateCampaign = async (partnerId: string): Promise<Campaign> => {
  try {
    const response = await api.post('/api/campaigns/generate', { partnerId });
    return response.data;
  } catch (error) {
    console.error('Failed to generate campaign:', error);
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