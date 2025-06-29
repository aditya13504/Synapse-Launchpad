import { create } from 'zustand';

interface AuthState {
  isLoading: boolean;
  isAuthenticated: boolean;
  user: any | null;
  setLoading: (isLoading: boolean) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  setUser: (user: any | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  isLoading: true,
  isAuthenticated: false,
  user: null,
  setLoading: (isLoading) => set({ isLoading }),
  setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
  setUser: (user) => set({ user }),
}));