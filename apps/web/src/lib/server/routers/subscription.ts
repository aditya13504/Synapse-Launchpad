import { z } from 'zod';
import { publicProcedure, router } from '../trpc';

export const subscriptionRouter = router({
  getPlans: publicProcedure
    .query(async () => {
      // TODO: Implement actual plan fetching logic
      return [
        {
          id: 'freemium',
          name: 'Freemium',
          price: 0,
          features: ['Basic partner matching', 'Limited campaigns'],
        },
        {
          id: 'pro',
          name: 'Pro',
          price: 99,
          features: ['Advanced matching', 'Unlimited campaigns', 'Analytics'],
        },
        {
          id: 'enterprise',
          name: 'Enterprise',
          price: 299,
          features: ['Custom integrations', 'Priority support', 'White-label'],
        },
      ];
    }),

  createCheckoutSession: publicProcedure
    .input(z.object({
      planId: z.string(),
      successUrl: z.string().url(),
      cancelUrl: z.string().url(),
    }))
    .mutation(async ({ input }) => {
      // TODO: Implement actual Stripe checkout session creation
      return {
        success: true,
        sessionId: 'mock-session-id',
        url: 'https://checkout.stripe.com/mock',
      };
    }),

  getSubscription: publicProcedure
    .query(async () => {
      // TODO: Implement actual subscription fetching logic
      return {
        plan: 'freemium',
        status: 'active',
        currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      };
    }),
}); 