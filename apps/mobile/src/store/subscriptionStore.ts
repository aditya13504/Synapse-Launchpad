import { create } from 'zustand';
import Purchases, { PurchasesPackage, CustomerInfo, MakePurchaseResult } from 'react-native-purchases';
import { SUBSCRIPTION_PLANS } from '../config';

interface SubscriptionState {
  isLoading: boolean;
  customerInfo: CustomerInfo | null;
  packages: PurchasesPackage[];
  currentPlan: string | null;
  isPro: boolean;
  
  // Actions
  fetchPackages: () => Promise<void>;
  purchasePackage: (pkg: PurchasesPackage) => Promise<boolean>;
  restorePurchases: () => Promise<void>;
  refreshCustomerInfo: () => Promise<void>;
}

export const useSubscriptionStore = create<SubscriptionState>((set, get) => ({
  isLoading: false,
  customerInfo: null,
  packages: [],
  currentPlan: null,
  isPro: false,
  
  fetchPackages: async () => {
    set({ isLoading: true });
    try {
      const offerings = await Purchases.getOfferings();
      if (offerings.current && offerings.current.availablePackages.length > 0) {
        set({ packages: offerings.current.availablePackages });
      }
      
      // Refresh customer info
      await get().refreshCustomerInfo();
    } catch (error) {
      console.error('Failed to fetch packages:', error);
    } finally {
      set({ isLoading: false });
    }
  },
  
  purchasePackage: async (pkg) => {
    set({ isLoading: true });
    try {
      const result: MakePurchaseResult = await Purchases.purchasePackage(pkg);
      set({ customerInfo: result.customerInfo });
      await get().refreshCustomerInfo();
      return true;
    } catch (error) {
      console.error('Purchase failed:', error);
      return false;
    } finally {
      set({ isLoading: false });
    }
  },
  
  restorePurchases: async () => {
    set({ isLoading: true });
    try {
      const customerInfo = await Purchases.restorePurchases();
      set({ customerInfo });
      await get().refreshCustomerInfo();
    } catch (error) {
      console.error('Restore failed:', error);
    } finally {
      set({ isLoading: false });
    }
  },
  
  refreshCustomerInfo: async () => {
    try {
      const customerInfo = await Purchases.getCustomerInfo();
      set({ customerInfo });
      
      // Determine current plan
      const entitlements = customerInfo.entitlements.active;
      let currentPlan = null;
      let isPro = false;
      
      if (entitlements['pro_access']) {
        currentPlan = SUBSCRIPTION_PLANS.PRO;
        isPro = true;
      } else if (entitlements['starter_access']) {
        currentPlan = SUBSCRIPTION_PLANS.STARTER;
      } else if (entitlements['enterprise_access']) {
        currentPlan = SUBSCRIPTION_PLANS.ENTERPRISE;
        isPro = true;
      }
      
      set({ currentPlan, isPro });
    } catch (error) {
      console.error('Failed to refresh customer info:', error);
    }
  }
}));