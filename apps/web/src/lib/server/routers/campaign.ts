import { z } from 'zod';
import { router, publicProcedure } from '../trpc';
import axios from 'axios';

const campaignRequestSchema = z.object({
  partner_pair: z.object({
    company_a: z.record(z.any()),
    company_b: z.record(z.any()),
    match_score: z.number(),
    synergies: z.array(z.string()),
  }),
  launch_window: z.object({
    start_date: z.string(),
    end_date: z.string(),
    optimal_timing: z.string(),
    market_conditions: z.record(z.any()),
  }),
  audience_segment: z.object({
    segment_name: z.string(),
    demographics: z.record(z.any()),
    psychographics: z.record(z.any()),
    big_five_traits: z.record(z.number()),
    preferred_channels: z.array(z.string()),
    messaging_preferences: z.record(z.any()),
  }),
  campaign_objectives: z.array(z.string()),
  budget_range: z.record(z.number()).optional(),
  brand_guidelines: z.record(z.any()).optional(),
  localization_targets: z.array(z.string()).optional(),
});

export const campaignRouter = router({
  generateCampaign: publicProcedure
    .input(campaignRequestSchema)
    .mutation(async ({ input }) => {
      try {
        const response = await axios.post(
          `${process.env.CAMPAIGN_MAKER_URL}/generate-campaign`,
          input
        );
        return response.data;
      } catch (error) {
        throw new Error('Failed to generate campaign');
      }
    }),

  optimizeContent: publicProcedure
    .input(z.object({
      campaign_id: z.string(),
      channel: z.string(),
      performance_data: z.record(z.any()),
    }))
    .mutation(async ({ input }) => {
      try {
        const response = await axios.post(
          `${process.env.CAMPAIGN_MAKER_URL}/optimize-content`,
          input
        );
        return response.data;
      } catch (error) {
        throw new Error('Failed to optimize content');
      }
    }),

  generateCreativeAssets: publicProcedure
    .input(z.object({
      content_brief: z.record(z.any()),
      asset_types: z.array(z.string()),
      dimensions: z.array(z.record(z.number())),
    }))
    .mutation(async ({ input }) => {
      try {
        const response = await axios.post(
          `${process.env.CAMPAIGN_MAKER_URL}/generate-creative-assets`,
          input
        );
        return response.data;
      } catch (error) {
        throw new Error('Failed to generate creative assets');
      }
    }),

  getPsychologyInsights: publicProcedure
    .input(z.object({
      audience_segment: z.string(),
    }))
    .query(async ({ input }) => {
      try {
        const response = await axios.get(
          `${process.env.CAMPAIGN_MAKER_URL}/psychology-insights/${input.audience_segment}`
        );
        return response.data;
      } catch (error) {
        throw new Error('Failed to get psychology insights');
      }
    }),
});