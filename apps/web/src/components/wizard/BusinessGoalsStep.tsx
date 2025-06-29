import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useWizardStore } from '@/store/wizard';
import { Target, TrendingUp, Users, DollarSign, Calendar, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { trackTimeOnStep } from '@/lib/analytics';

const businessGoalsSchema = z.object({
  primaryObjective: z.string().min(1, 'Please select a primary objective'),
  targetMarket: z.array(z.string()).min(1, 'Please select at least one target market'),
  growthStage: z.string().min(1, 'Please select your growth stage'),
  budget: z.number().min(1000, 'Budget must be at least $1,000'),
  timeline: z.string().min(1, 'Please select a timeline'),
  successMetrics: z.array(z.string()).min(1, 'Please select at least one success metric'),
});

type BusinessGoalsForm = z.infer<typeof businessGoalsSchema>;

const objectives = [
  { id: 'growth', label: 'Accelerate Growth', icon: TrendingUp, description: 'Scale revenue and user base' },
  { id: 'market', label: 'Market Expansion', icon: Users, description: 'Enter new markets or segments' },
  { id: 'product', label: 'Product Development', icon: Target, description: 'Enhance or build new products' },
  { id: 'funding', label: 'Fundraising Support', icon: DollarSign, description: 'Prepare for next funding round' },
];

const targetMarkets = [
  'Enterprise (B2B)',
  'SMB (Small-Medium Business)',
  'Consumer (B2C)',
  'Healthcare',
  'FinTech',
  'EdTech',
  'E-commerce',
  'SaaS',
  'AI/ML',
  'Sustainability',
];

const growthStages = [
  { id: 'pre-seed', label: 'Pre-Seed', description: 'Idea to MVP' },
  { id: 'seed', label: 'Seed', description: 'Product-market fit' },
  { id: 'series-a', label: 'Series A', description: 'Scaling operations' },
  { id: 'series-b', label: 'Series B+', description: 'Market expansion' },
  { id: 'growth', label: 'Growth Stage', description: 'Mature scaling' },
];

const timelines = [
  { id: '1-3', label: '1-3 months', description: 'Quick wins' },
  { id: '3-6', label: '3-6 months', description: 'Medium-term goals' },
  { id: '6-12', label: '6-12 months', description: 'Long-term strategy' },
  { id: '12+', label: '12+ months', description: 'Strategic partnerships' },
];

const successMetrics = [
  'Revenue Growth',
  'User Acquisition',
  'Market Share',
  'Brand Awareness',
  'Product Adoption',
  'Customer Retention',
  'Partnership ROI',
  'Media Coverage',
];

export function BusinessGoalsStep() {
  const { businessGoals, setBusinessGoals, setCurrentStep } = useWizardStore();
  const [selectedMarkets, setSelectedMarkets] = useState<string[]>(businessGoals?.targetMarket || []);
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(businessGoals?.successMetrics || []);
  const [startTime] = useState<number>(Date.now());

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isValid },
  } = useForm<BusinessGoalsForm>({
    resolver: zodResolver(businessGoalsSchema),
    defaultValues: businessGoals || {
      primaryObjective: '',
      targetMarket: [],
      growthStage: '',
      budget: 10000,
      timeline: '',
      successMetrics: [],
    },
  });

  const watchedObjective = watch('primaryObjective');
  const watchedStage = watch('growthStage');
  const watchedTimeline = watch('timeline');

  // Track time spent on this step when unmounting
  useEffect(() => {
    return () => {
      const timeSpentMs = Date.now() - startTime;
      trackTimeOnStep('business_goals', timeSpentMs);
    };
  }, [startTime]);

  const onSubmit = (data: BusinessGoalsForm) => {
    setBusinessGoals({
      ...data,
      targetMarket: selectedMarkets,
      successMetrics: selectedMetrics,
    });
    setCurrentStep(2);
  };

  const toggleMarket = (market: string) => {
    const updated = selectedMarkets.includes(market)
      ? selectedMarkets.filter(m => m !== market)
      : [...selectedMarkets, market];
    setSelectedMarkets(updated);
    setValue('targetMarket', updated);
  };

  const toggleMetric = (metric: string) => {
    const updated = selectedMetrics.includes(metric)
      ? selectedMetrics.filter(m => m !== metric)
      : [...selectedMetrics, metric];
    setSelectedMetrics(updated);
    setValue('successMetrics', updated);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-4xl mx-auto"
    >
      <Card className="glass-morphism p-8">
        <div className="text-center mb-8">
          <Target className="w-12 h-12 text-blue-400 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Define Your Business Goals</h2>
          <p className="text-blue-200">Help us understand your objectives to find the perfect partners</p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
          {/* Primary Objective */}
          <div>
            <label className="block text-white font-semibold mb-4">
              What's your primary objective?
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {objectives.map((objective) => {
                const Icon = objective.icon;
                const isSelected = watchedObjective === objective.id;
                
                return (
                  <motion.label
                    key={objective.id}
                    className={`relative cursor-pointer p-4 rounded-xl border-2 transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-500/20'
                        : 'border-white/20 bg-white/5 hover:border-white/40'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <input
                      type="radio"
                      value={objective.id}
                      {...register('primaryObjective')}
                      className="sr-only"
                    />
                    <div className="flex items-start space-x-3">
                      <Icon className={`w-6 h-6 mt-1 ${isSelected ? 'text-blue-400' : 'text-white/60'}`} />
                      <div>
                        <h3 className={`font-semibold ${isSelected ? 'text-white' : 'text-white/80'}`}>
                          {objective.label}
                        </h3>
                        <p className={`text-sm ${isSelected ? 'text-blue-200' : 'text-white/60'}`}>
                          {objective.description}
                        </p>
                      </div>
                    </div>
                  </motion.label>
                );
              })}
            </div>
            {errors.primaryObjective && (
              <p className="text-red-400 text-sm mt-2">{errors.primaryObjective.message}</p>
            )}
          </div>

          {/* Target Markets */}
          <div>
            <label className="block text-white font-semibold mb-4">
              Target Markets (select all that apply)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {targetMarkets.map((market) => {
                const isSelected = selectedMarkets.includes(market);
                
                return (
                  <motion.button
                    key={market}
                    type="button"
                    onClick={() => toggleMarket(market)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-white/20 bg-white/5 text-white/80 hover:border-white/40'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    {market}
                  </motion.button>
                );
              })}
            </div>
            {errors.targetMarket && (
              <p className="text-red-400 text-sm mt-2">{errors.targetMarket.message}</p>
            )}
          </div>

          {/* Growth Stage */}
          <div>
            <label className="block text-white font-semibold mb-4">
              Current Growth Stage
            </label>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {growthStages.map((stage) => {
                const isSelected = watchedStage === stage.id;
                
                return (
                  <motion.label
                    key={stage.id}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-500/20'
                        : 'border-white/20 bg-white/5 hover:border-white/40'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <input
                      type="radio"
                      value={stage.id}
                      {...register('growthStage')}
                      className="sr-only"
                    />
                    <div className="text-center">
                      <h3 className={`font-semibold ${isSelected ? 'text-white' : 'text-white/80'}`}>
                        {stage.label}
                      </h3>
                      <p className={`text-xs mt-1 ${isSelected ? 'text-blue-200' : 'text-white/60'}`}>
                        {stage.description}
                      </p>
                    </div>
                  </motion.label>
                );
              })}
            </div>
            {errors.growthStage && (
              <p className="text-red-400 text-sm mt-2">{errors.growthStage.message}</p>
            )}
          </div>

          {/* Budget */}
          <div>
            <label className="block text-white font-semibold mb-4">
              Partnership Budget (USD)
            </label>
            <div className="relative">
              <DollarSign className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/60" />
              <input
                type="number"
                {...register('budget', { valueAsNumber: true })}
                className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20"
                placeholder="10000"
                min="1000"
                step="1000"
              />
            </div>
            {errors.budget && (
              <p className="text-red-400 text-sm mt-2">{errors.budget.message}</p>
            )}
          </div>

          {/* Timeline */}
          <div>
            <label className="block text-white font-semibold mb-4">
              Expected Timeline
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {timelines.map((timeline) => {
                const isSelected = watchedTimeline === timeline.id;
                
                return (
                  <motion.label
                    key={timeline.id}
                    className={`cursor-pointer p-4 rounded-xl border-2 transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-500/20'
                        : 'border-white/20 bg-white/5 hover:border-white/40'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <input
                      type="radio"
                      value={timeline.id}
                      {...register('timeline')}
                      className="sr-only"
                    />
                    <div className="text-center">
                      <Calendar className={`w-6 h-6 mx-auto mb-2 ${isSelected ? 'text-blue-400' : 'text-white/60'}`} />
                      <h3 className={`font-semibold ${isSelected ? 'text-white' : 'text-white/80'}`}>
                        {timeline.label}
                      </h3>
                      <p className={`text-xs mt-1 ${isSelected ? 'text-blue-200' : 'text-white/60'}`}>
                        {timeline.description}
                      </p>
                    </div>
                  </motion.label>
                );
              })}
            </div>
            {errors.timeline && (
              <p className="text-red-400 text-sm mt-2">{errors.timeline.message}</p>
            )}
          </div>

          {/* Success Metrics */}
          <div>
            <label className="block text-white font-semibold mb-4">
              Success Metrics (select all that apply)
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {successMetrics.map((metric) => {
                const isSelected = selectedMetrics.includes(metric);
                
                return (
                  <motion.button
                    key={metric}
                    type="button"
                    onClick={() => toggleMetric(metric)}
                    className={`p-3 rounded-lg border-2 text-sm font-medium transition-all ${
                      isSelected
                        ? 'border-blue-500 bg-blue-500/20 text-white'
                        : 'border-white/20 bg-white/5 text-white/80 hover:border-white/40'
                    }`}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <BarChart3 className={`w-4 h-4 mx-auto mb-1 ${isSelected ? 'text-blue-400' : 'text-white/60'}`} />
                    {metric}
                  </motion.button>
                );
              })}
            </div>
            {errors.successMetrics && (
              <p className="text-red-400 text-sm mt-2">{errors.successMetrics.message}</p>
            )}
          </div>

          {/* Submit Button */}
          <div className="flex justify-end pt-6">
            <Button
              type="submit"
              disabled={!isValid}
              className="btn-primary px-8 py-3"
            >
              Find Partners →
            </Button>
          </div>
        </form>
      </Card>
    </motion.div>
  );
}