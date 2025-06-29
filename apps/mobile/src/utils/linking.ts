import * as Linking from 'expo-linking';
import { Platform } from 'react-native';
import { WEB_URL } from '../config';

/**
 * Opens the web dashboard with deep linking
 * @param path The path to open in the web dashboard
 */
export const openWebDashboard = (path: string = '') => {
  const url = `${WEB_URL}${path}`;
  Linking.openURL(url);
};

/**
 * Creates a deep link to the mobile app
 * @param screen The screen to link to
 * @param params The parameters to pass to the screen
 */
export const createDeepLink = (screen: string, params: Record<string, string> = {}) => {
  return Linking.createURL(screen, { queryParams: params });
};

/**
 * Handles incoming deep links
 * @param url The URL to handle
 * @param navigation The navigation object
 */
export const handleDeepLink = (url: string, navigation: any) => {
  const { path, queryParams } = Linking.parse(url);
  
  if (path === 'recommendations') {
    navigation.navigate('RecommendationList');
  } else if (path?.startsWith('campaign/')) {
    const campaignId = path.replace('campaign/', '');
    navigation.navigate('CampaignPreview', { campaignId });
  }
};

/**
 * Configures deep linking for the app
 */
export const configureLinking = () => {
  // Set up deep link listener
  const linkingConfig = {
    prefixes: [Linking.createURL('/'), 'synapselaunchpad://'],
    config: {
      screens: {
        Login: 'login',
        RecommendationList: 'recommendations',
        CampaignPreview: 'campaign/:id',
      },
    },
  };
  
  return linkingConfig;
};