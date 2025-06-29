import { create } from 'zustand';

interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  interval: 'month' | 'year';
  features: string[];
  limits: {
    campaigns: number;
    partners: number;
    analytics: boolean;
    support: string;
  };
}

interface SubscriptionState {
  currentPlan: SubscriptionPlan | null;
  isLoading: boolean;
  
  // Actions
  setCurrentPlan: (plan: SubscriptionPlan) => void;
  setLoading: (loading: boolean) => void;
}

export const useSubscriptionStore = create<SubscriptionState>((set) => ({
  currentPlan: null,
  isLoading: false,
  
  setCurrentPlan: (plan) => set({ currentPlan: plan }),
  setLoading: (loading) => set({ isLoading: loading }),
}));

export const SUBSCRIPTION_PLANS: SubscriptionPlan[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 49,
    interval: 'month',
    features: [
      'Up to 5 partner recommendations',
      'Basic campaign generation',
      'Email support',
      'Standard analytics',
    ],
    limits: {
      campaigns: 5,
      partners: 10,
      analytics: false,
      support: 'email',
    },
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 149,
    interval: 'month',
    features: [
      'Unlimited partner recommendations',
      'Advanced campaign generation',
      'Psychology-based targeting',
      'Creative asset generation',
      'Priority support',
      'Advanced analytics',
    ],
    limits: {
      campaigns: 50,
      partners: 100,
      analytics: true,
      support: 'priority',
    },
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 499,
    interval: 'month',
    features: [
      'Everything in Pro',
      'Custom integrations',
      'Dedicated account manager',
      'White-label options',
      'API access',
      'Custom analytics',
    ],
    limits: {
      campaigns: -1, // Unlimited
      partners: -1, // Unlimited
      analytics: true,
      support: 'dedicated',
    },
  },
];