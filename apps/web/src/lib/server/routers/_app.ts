import { router } from '../trpc';
import { partnerRouter } from './partner';
import { campaignRouter } from './campaign';
import { authRouter } from './auth';
import { subscriptionRouter } from './subscription';

export const appRouter = router({
  partner: partnerRouter,
  campaign: campaignRouter,
  auth: authRouter,
  subscription: subscriptionRouter,
});

export type AppRouter = typeof appRouter;