import { z } from 'zod';
import { router, publicProcedure } from '../trpc';
import axios from 'axios';

const partnerRecommendationSchema = z.object({
  company_id: z.string(),
  top_k: z.number().default(10),
  filters: z.record(z.any()).optional(),
});

export const partnerRouter = router({
  getRecommendations: publicProcedure
    .input(partnerRecommendationSchema)
    .query(async ({ input }) => {
      try {
        const response = await axios.post(
          `${process.env.PARTNER_RECOMMENDER_URL}/recommend`,
          input
        );
        return response.data;
      } catch (error) {
        throw new Error('Failed to fetch partner recommendations');
      }
    }),

  explainRecommendation: publicProcedure
    .input(z.object({
      company_id: z.string(),
      partner_id: z.string(),
      top_features: z.number().default(10),
    }))
    .query(async ({ input }) => {
      try {
        const response = await axios.get(
          `${process.env.PARTNER_RECOMMENDER_URL}/explain/${input.company_id}`,
          {
            params: {
              partner_id: input.partner_id,
              top_features: input.top_features,
            },
          }
        );
        return response.data;
      } catch (error) {
        throw new Error('Failed to explain recommendation');
      }
    }),

  getModelStatus: publicProcedure
    .query(async () => {
      try {
        const response = await axios.get(
          `${process.env.PARTNER_RECOMMENDER_URL}/model/status`
        );
        return response.data;
      } catch (error) {
        throw new Error('Failed to get model status');
      }
    }),
});