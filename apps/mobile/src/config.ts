import { Platform } from 'react-native';

// API Configuration
export const API_URL = process.env.EXPO_PUBLIC_API_URL || 'https://api.synapse-launchpad.com';

// RevenueCat Configuration
export const REVENUECAT_API_KEY = process.env.EXPO_PUBLIC_REVENUECAT_API_KEY || 
  (Platform.OS === 'ios' 
    ? 'ios_revenuecat_api_key' 
    : 'android_revenuecat_api_key');

// Deep Linking
export const WEB_URL = 'https://synapse-launchpad.com';

// Subscription Plans
export const SUBSCRIPTION_PLANS = {
  STARTER: 'starter_monthly',
  PRO: 'pro_monthly',
  ENTERPRISE: 'enterprise_monthly',
};

// Feature Flags
export const FEATURES = {
  ENABLE_ANALYTICS: true,
  ENABLE_NOTIFICATIONS: true,
  ENABLE_DEEP_LINKING: true,
};

// Theme Configuration
export const THEME = {
  PRIMARY: '#3B82F6',
  SECONDARY: '#8B5CF6',
  BACKGROUND: {
    DARK: '#0F172A',
    LIGHT: '#F8FAFC',
  },
  TEXT: {
    DARK: '#F8FAFC',
    LIGHT: '#1E293B',
  },
  CARD: {
    DARK: '#1E293B',
    LIGHT: '#FFFFFF',
  },
};