import { useState } from 'react';
import { useRouter } from 'next/router';
import { motion, AnimatePresence } from 'framer-motion';
import { useWizardStore } from '@/store/wizard';
import { WizardNavigation } from '@/components/wizard/WizardNavigation';
import { BusinessGoalsStep } from '@/components/wizard/BusinessGoalsStep';
import { PartnerRecommendationsStep } from '@/components/wizard/PartnerRecommendationsStep';
import { CampaignEditorStep } from '@/components/wizard/CampaignEditorStep';
import { CheckCircle, Target, Users, Zap } from 'lucide-react';

const steps = [
  {
    id: 1,
    title: 'Business Goals',
    description: 'Define your partnership objectives',
    icon: Target,
  },
  {
    id: 2,
    title: 'Partner Recommendations',
    description: 'AI-powered partner matching',
    icon: Users,
  },
  {
    id: 3,
    title: 'Campaign Generation',
    description: 'Auto-generated marketing campaigns',
    icon: Zap,
  },
];

export default function WizardPage() {
  const router = useRouter();
  const { currentStep, setCurrentStep, canProceedToStep, resetWizard } = useWizardStore();

  const handleStepChange = (step: number) => {
    if (canProceedToStep(step)) {
      setCurrentStep(step);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return <BusinessGoalsStep />;
      case 2:
        return <PartnerRecommendationsStep />;
      case 3:
        return <CampaignEditorStep />;
      default:
        return <BusinessGoalsStep />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <motion.h1
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-white mb-4"
          >
            Partnership Wizard
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-blue-200 max-w-2xl mx-auto"
          >
            Let AI guide you through finding the perfect partners and creating winning campaigns
          </motion.p>
        </div>

        {/* Step Navigation */}
        <WizardNavigation
          steps={steps}
          currentStep={currentStep}
          onStepChange={handleStepChange}
          canProceedToStep={canProceedToStep}
        />

        {/* Step Content */}
        <div className="mt-12">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              {renderStepContent()}
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Reset Button */}
        <div className="fixed bottom-8 left-8">
          <button
            onClick={resetWizard}
            className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Reset Wizard
          </button>
        </div>
      </div>
    </div>
  );
}