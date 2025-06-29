import React from 'react';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { QueryClient, QueryClientProvider } from 'react-query';
import * as Linking from 'expo-linking';

import { AuthProvider } from './src/context/AuthContext';
import { useAuthStore } from './src/store/authStore';
import LoginScreen from './src/screens/LoginScreen';
import RecommendationListScreen from './src/screens/RecommendationListScreen';
import CampaignPreviewScreen from './src/screens/CampaignPreviewScreen';

const Stack = createNativeStackNavigator();
const queryClient = new QueryClient();

const prefix = Linking.createURL('/');

const linking = {
  prefixes: [prefix, 'synapselaunchpad://'],
  config: {
    screens: {
      Login: 'login',
      RecommendationList: 'recommendations',
      CampaignPreview: {
        path: 'campaign/:id',
        parse: {
          id: (id: string) => id,
        },
      },
    },
  },
};

export default function App() {
  const { isAuthenticated } = useAuthStore();

  return (
    <SafeAreaProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <NavigationContainer linking={linking}>
            <StatusBar style="light" />
            <Stack.Navigator
              screenOptions={{
                headerStyle: {
                  backgroundColor: '#1E293B',
                },
                headerTintColor: '#fff',
                headerTitleStyle: {
                  fontWeight: 'bold',
                },
                contentStyle: {
                  backgroundColor: '#0F172A',
                },
              }}
            >
              {!isAuthenticated ? (
                <Stack.Screen 
                  name="Login" 
                  component={LoginScreen} 
                  options={{ headerShown: false }}
                />
              ) : (
                <>
                  <Stack.Screen 
                    name="RecommendationList" 
                    component={RecommendationListScreen} 
                    options={{ title: 'Partner Recommendations' }}
                  />
                  <Stack.Screen 
                    name="CampaignPreview" 
                    component={CampaignPreviewScreen} 
                    options={{ title: 'Campaign Preview' }}
                  />
                </>
              )}
            </Stack.Navigator>
          </NavigationContainer>
        </AuthProvider>
      </QueryClientProvider>
    </SafeAreaProvider>
  );
}