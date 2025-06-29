import { createNextApiHandler } from '@trpc/server/adapters/next';
import { appRouter } from '@/lib/server/routers/_app';
import { createContext } from '@/lib/server/trpc';

export default createNextApiHandler({
  router: appRouter,
  createContext,
});