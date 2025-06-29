import React, { createContext, useContext, useEffect } from 'react';
import { useAuthStore } from '../store/authStore';
import { login, logout, checkAuth } from '../services/authService';

type AuthContextType = {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isLoading: boolean;
  isAuthenticated: boolean;
  user: any | null;
};

const AuthContext = createContext<AuthContextType>({
  login: async () => {},
  logout: async () => {},
  isLoading: false,
  isAuthenticated: false,
  user: null,
});

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoading, isAuthenticated, user, setLoading, setAuthenticated, setUser } = useAuthStore();

  useEffect(() => {
    const checkAuthStatus = async () => {
      setLoading(true);
      try {
        const userData = await checkAuth();
        if (userData) {
          setUser(userData);
          setAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const handleLogin = async (email: string, password: string) => {
    setLoading(true);
    try {
      const userData = await login(email, password);
      setUser(userData);
      setAuthenticated(true);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    try {
      await logout();
      setUser(null);
      setAuthenticated(false);
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        login: handleLogin,
        logout: handleLogout,
        isLoading,
        isAuthenticated,
        user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);