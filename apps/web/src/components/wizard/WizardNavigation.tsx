import { motion } from 'framer-motion';
import { CheckCircle, LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';
import { trackTimeOnStep } from '@/lib/analytics';

interface Step {
  id: number;
  title: string;
  description: string;
  icon: LucideIcon;
}

interface WizardNavigationProps {
  steps: Step[];
  currentStep: number;
  onStepChange: (step: number) => void;
  canProceedToStep: (step: number) => boolean;
}

export function WizardNavigation({
  steps,
  currentStep,
  onStepChange,
  canProceedToStep,
}: WizardNavigationProps) {
  // Track step change with analytics
  const handleStepChange = (step: number) => {
    if (canProceedToStep(step) && step !== currentStep) {
      // Track time spent on current step before changing
      const stepName = steps.find(s => s.id === currentStep)?.title.toLowerCase().replace(' ', '_');
      if (stepName) {
        trackTimeOnStep(stepName, 0); // We don't know the exact time, but we want to track the change
      }
      
      // Change to the new step
      onStepChange(step);
    }
  };

  return (
    <div className="flex justify-center">
      <div className="flex items-center space-x-8">
        {steps.map((step, index) => {
          const isActive = currentStep === step.id;
          const isCompleted = currentStep > step.id;
          const canAccess = canProceedToStep(step.id);
          const Icon = step.icon;

          return (
            <div key={step.id} className="flex items-center">
              {/* Step Circle */}
              <motion.button
                onClick={() => handleStepChange(step.id)}
                disabled={!canAccess}
                className={clsx(
                  'relative flex items-center justify-center w-16 h-16 rounded-full border-2 transition-all duration-300',
                  {
                    'bg-blue-600 border-blue-600 text-white': isActive,
                    'bg-green-600 border-green-600 text-white': isCompleted,
                    'bg-white/10 border-white/30 text-white/60': !isActive && !isCompleted && canAccess,
                    'bg-white/5 border-white/20 text-white/30 cursor-not-allowed': !canAccess,
                  }
                )}
                whileHover={canAccess ? { scale: 1.05 } : {}}
                whileTap={canAccess ? { scale: 0.95 } : {}}
              >
                {isCompleted ? (
                  <CheckCircle className="w-8 h-8" />
                ) : (
                  <Icon className="w-8 h-8" />
                )}
                
                {isActive && (
                  <motion.div
                    className="absolute inset-0 rounded-full border-2 border-blue-400"
                    initial={{ scale: 1, opacity: 1 }}
                    animate={{ scale: 1.2, opacity: 0 }}
                    transition={{ duration: 1.5, repeat: Infinity }}
                  />
                )}
              </motion.button>

              {/* Step Info */}
              <div className="ml-4 text-left">
                <h3 className={clsx(
                  'font-semibold transition-colors',
                  {
                    'text-white': isActive || isCompleted,
                    'text-white/60': !isActive && !isCompleted && canAccess,
                    'text-white/30': !canAccess,
                  }
                )}>
                  {step.title}
                </h3>
                <p className={clsx(
                  'text-sm transition-colors',
                  {
                    'text-blue-200': isActive,
                    'text-green-200': isCompleted,
                    'text-white/50': !isActive && !isCompleted && canAccess,
                    'text-white/20': !canAccess,
                  }
                )}>
                  {step.description}
                </p>
              </div>

              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className="ml-8 w-16 h-0.5 bg-white/20">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                    initial={{ width: '0%' }}
                    animate={{ 
                      width: currentStep > step.id ? '100%' : '0%' 
                    }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}