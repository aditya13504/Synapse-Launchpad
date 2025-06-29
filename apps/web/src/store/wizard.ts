import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface BusinessGoals {
  primaryObjective: string;
  targetMarket: string[];
  growthStage: string;
  budget: number;
  timeline: string;
  successMetrics: string[];
}

interface PartnerRecommendation {
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

interface CampaignData {
  campaign_id: string;
  campaign_brief: {
    objective: string;
    key_message: string;
    hooks: string[];
    fomo_angle: string;
    psychological_triggers: string[];
    success_metrics: string[];
  };
  channel_mix_plan: Array<{
    channel: string;
    allocation_percentage: number;
    rationale: string;
    optimal_timing: string;
    content_types: string[];
    psychological_approach: string;
  }>;
  channel_content: Array<{
    channel: string;
    content_type: string;
    copy_variants: Array<{
      variant_id: string;
      big_five_target: string;
      headline: string;
      body_text: string;
      cta: string;
      psychological_triggers: string[];
      tone_analysis: Record<string, number>;
      estimated_performance: Record<string, number>;
    }>;
    creative_assets: Array<Record<string, any>>;
    localized_versions?: Record<string, any>;
  }>;
  psychological_insights: Record<string, any>;
  performance_predictions: Record<string, any>;
  optimization_recommendations: string[];
  created_at: string;
}

interface WizardState {
  // Current step
  currentStep: number;
  
  // Step 1: Business Goals
  businessGoals: BusinessGoals | null;
  
  // Step 2: Partner Recommendations
  selectedPartner: PartnerRecommendation | null;
  partnerRecommendations: PartnerRecommendation[];
  
  // Step 3: Campaign Data
  campaignData: CampaignData | null;
  
  // Actions
  setCurrentStep: (step: number) => void;
  setBusinessGoals: (goals: BusinessGoals) => void;
  setSelectedPartner: (partner: PartnerRecommendation) => void;
  setPartnerRecommendations: (recommendations: PartnerRecommendation[]) => void;
  setCampaignData: (campaign: CampaignData) => void;
  resetWizard: () => void;
  
  // Computed
  canProceedToStep: (step: number) => boolean;
}

export const useWizardStore = create<WizardState>()(
  persist(
    (set, get) => ({
      currentStep: 1,
      businessGoals: null,
      selectedPartner: null,
      partnerRecommendations: [],
      campaignData: null,
      
      setCurrentStep: (step) => set({ currentStep: step }),
      
      setBusinessGoals: (goals) => set({ businessGoals: goals }),
      
      setSelectedPartner: (partner) => set({ selectedPartner: partner }),
      
      setPartnerRecommendations: (recommendations) => 
        set({ partnerRecommendations: recommendations }),
      
      setCampaignData: (campaign) => set({ campaignData: campaign }),
      
      resetWizard: () => set({
        currentStep: 1,
        businessGoals: null,
        selectedPartner: null,
        partnerRecommendations: [],
        campaignData: null,
      }),
      
      canProceedToStep: (step) => {
        const state = get();
        switch (step) {
          case 1:
            return true;
          case 2:
            return state.businessGoals !== null;
          case 3:
            return state.businessGoals !== null && state.selectedPartner !== null;
          default:
            return false;
        }
      },
    }),
    {
      name: 'wizard-storage',
      partialize: (state) => ({
        businessGoals: state.businessGoals,
        selectedPartner: state.selectedPartner,
        campaignData: state.campaignData,
      }),
    }
  )
);