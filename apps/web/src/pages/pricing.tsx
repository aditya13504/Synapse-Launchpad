import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Star, Zap, Crown, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { SUBSCRIPTION_PLANS } from '@/store/subscription';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);

export default function PricingPage() {
  const [billingInterval, setBillingInterval] = useState<'month' | 'year'>('month');
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleSubscribe = async (planId: string) => {
    setIsLoading(planId);
    
    try {
      const stripe = await stripePromise;
      if (!stripe) throw new Error('Stripe failed to load');

      // Create checkout session
      const response = await fetch('/api/stripe/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          planId,
          billingInterval,
        }),
      });

      const session = await response.json();

      // Redirect to Stripe Checkout
      const result = await stripe.redirectToCheckout({
        sessionId: session.id,
      });

      if (result.error) {
        console.error('Stripe error:', result.error);
      }
    } catch (error) {
      console.error('Subscription error:', error);
    } finally {
      setIsLoading(null);
    }
  };

  const getPlanIcon = (planId: string) => {
    switch (planId) {
      case 'starter':
        return Star;
      case 'pro':
        return Zap;
      case 'enterprise':
        return Crown;
      default:
        return Star;
    }
  };

  const getPlanColor = (planId: string) => {
    switch (planId) {
      case 'starter':
        return 'from-blue-500 to-cyan-500';
      case 'pro':
        return 'from-purple-500 to-pink-500';
      case 'enterprise':
        return 'from-yellow-500 to-orange-500';
      default:
        return 'from-blue-500 to-cyan-500';
    }
  };

  const getYearlyDiscount = (monthlyPrice: number) => {
    const yearlyPrice = monthlyPrice * 10; // 2 months free
    const savings = (monthlyPrice * 12) - yearlyPrice;
    return Math.round((savings / (monthlyPrice * 12)) * 100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <h1 className="text-5xl font-bold text-white mb-6">
            Choose Your Growth Plan
          </h1>
          <p className="text-xl text-blue-200 max-w-3xl mx-auto mb-8">
            Accelerate your startup partnerships with AI-powered matching and campaign generation. 
            Start free, scale as you grow.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-white/10 backdrop-blur-sm rounded-xl p-1 border border-white/20">
            <button
              onClick={() => setBillingInterval('month')}
              className={`px-6 py-2 rounded-lg font-medium transition-all ${
                billingInterval === 'month'
                  ? 'bg-white text-slate-900 shadow-lg'
                  : 'text-white hover:text-blue-200'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingInterval('year')}
              className={`px-6 py-2 rounded-lg font-medium transition-all relative ${
                billingInterval === 'year'
                  ? 'bg-white text-slate-900 shadow-lg'
                  : 'text-white hover:text-blue-200'
              }`}
            >
              Yearly
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-2 py-1 rounded-full">
                Save 17%
              </span>
            </button>
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {SUBSCRIPTION_PLANS.map((plan, index) => {
            const Icon = getPlanIcon(plan.id);
            const isPopular = plan.id === 'pro';
            const price = billingInterval === 'year' ? plan.price * 10 : plan.price;
            const yearlyDiscount = getYearlyDiscount(plan.price);

            return (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                {isPopular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 z-10">
                    <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                      Most Popular
                    </div>
                  </div>
                )}

                <Card className={`p-8 h-full relative overflow-hidden ${
                  isPopular ? 'ring-2 ring-purple-500 bg-white/15' : ''
                }`}>
                  {/* Background Gradient */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${getPlanColor(plan.id)} opacity-5`} />
                  
                  <div className="relative z-10">
                    {/* Plan Header */}
                    <div className="text-center mb-8">
                      <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-r ${getPlanColor(plan.id)} mb-4`}>
                        <Icon className="w-8 h-8 text-white" />
                      </div>
                      <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                      <div className="text-center">
                        <span className="text-4xl font-bold text-white">${price}</span>
                        <span className="text-white/60">/{billingInterval}</span>
                        {billingInterval === 'year' && (
                          <div className="text-green-400 text-sm font-medium mt-1">
                            Save {yearlyDiscount}% annually
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Features */}
                    <div className="space-y-4 mb-8">
                      {plan.features.map((feature, featureIndex) => (
                        <motion.div
                          key={featureIndex}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: (index * 0.1) + (featureIndex * 0.05) }}
                          className="flex items-start space-x-3"
                        >
                          <Check className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                          <span className="text-white/80">{feature}</span>
                        </motion.div>
                      ))}
                    </div>

                    {/* Limits */}
                    <div className="bg-white/5 rounded-lg p-4 mb-8">
                      <h4 className="text-white font-semibold mb-3">Plan Limits</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-white/70">Campaigns per month:</span>
                          <span className="text-white">
                            {plan.limits.campaigns === -1 ? 'Unlimited' : plan.limits.campaigns}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/70">Partner recommendations:</span>
                          <span className="text-white">
                            {plan.limits.partners === -1 ? 'Unlimited' : plan.limits.partners}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/70">Advanced analytics:</span>
                          <span className="text-white">
                            {plan.limits.analytics ? 'Included' : 'Basic only'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/70">Support:</span>
                          <span className="text-white capitalize">{plan.limits.support}</span>
                        </div>
                      </div>
                    </div>

                    {/* CTA Button */}
                    <Button
                      onClick={() => handleSubscribe(plan.id)}
                      loading={isLoading === plan.id}
                      className={`w-full ${
                        isPopular 
                          ? 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600' 
                          : 'btn-primary'
                      }`}
                      size="lg"
                    >
                      {plan.id === 'starter' ? 'Start Free Trial' : 'Get Started'}
                      <ArrowRight className="w-5 h-5 ml-2" />
                    </Button>

                    {plan.id === 'enterprise' && (
                      <p className="text-center text-white/60 text-sm mt-4">
                        Contact sales for custom pricing
                      </p>
                    )}
                  </div>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* FAQ Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-20 text-center"
        >
          <h2 className="text-3xl font-bold text-white mb-8">Frequently Asked Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {[
              {
                question: "Can I change plans anytime?",
                answer: "Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately."
              },
              {
                question: "Is there a free trial?",
                answer: "Yes, all plans come with a 14-day free trial. No credit card required for the Starter plan."
              },
              {
                question: "What payment methods do you accept?",
                answer: "We accept all major credit cards, PayPal, and bank transfers for Enterprise plans."
              },
              {
                question: "Can I cancel anytime?",
                answer: "Yes, you can cancel your subscription at any time. You'll retain access until the end of your billing period."
              }
            ].map((faq, index) => (
              <Card key={index} className="p-6 text-left">
                <h3 className="text-white font-semibold mb-2">{faq.question}</h3>
                <p className="text-white/70">{faq.answer}</p>
              </Card>
            ))}
          </div>
        </motion.div>

        {/* Enterprise CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="mt-20"
        >
          <Card className="p-12 text-center bg-gradient-to-r from-yellow-500/10 to-orange-500/10 border-yellow-500/30">
            <Crown className="w-16 h-16 text-yellow-400 mx-auto mb-6" />
            <h2 className="text-3xl font-bold text-white mb-4">Need Something Custom?</h2>
            <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
              Enterprise plans include custom integrations, dedicated support, and white-label options.
            </p>
            <Button size="lg" className="bg-gradient-to-r from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600">
              Contact Sales
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Card>
        </motion.div>
      </div>
    </div>
  );
}