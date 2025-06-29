import posthog from 'posthog-js';

// PostHog Analytics Configuration
const POSTHOG_KEY = process.env.NEXT_PUBLIC_POSTHOG_KEY || '';
const POSTHOG_HOST = process.env.NEXT_PUBLIC_POSTHOG_HOST || 'https://app.posthog.com';

if (typeof window !== 'undefined' && POSTHOG_KEY) {
  posthog.init(POSTHOG_KEY, { api_host: POSTHOG_HOST });
}

/**
 * Track an event with PostHog Analytics
 * @param eventName The name of the event to track
 * @param properties Additional properties to include with the event
 */
export const trackEvent = (eventName: string, properties: Record<string, any> = {}) => {
  if (typeof window !== 'undefined' && POSTHOG_KEY) {
    posthog.capture(eventName, properties);
  }
};

/**
 * Track time spent on a specific step or page
 * @param stepName The name of the step or page
 * @param durationMs Time spent in milliseconds
 */
export const trackTimeOnStep = (stepName: string, durationMs: number) => {
  trackEvent('time_on_step', {
    step_name: stepName,
    duration_ms: durationMs,
  });
};

/**
 * Track when a user clicks on a recommendation
 * @param recommendationId The ID of the recommendation
 * @param matchScore The match score of the recommendation
 */
export const trackRecommendationClick = (recommendationId: string, matchScore: number) => {
  trackEvent('recommend_click', {
    recommendation_id: recommendationId,
    match_score: matchScore,
  });
};

/**
 * Track when a user publishes a campaign
 * @param campaignId The ID of the campaign
 * @param partnerId The ID of the partner
 */
export const trackCampaignPublish = (campaignId: string, partnerId: string) => {
  trackEvent('campaign_publish', {
    campaign_id: campaignId,
    partner_id: partnerId,
  });
};

/**
 * Initialize analytics tracking
 */
export const initAnalytics = () => {
  if (typeof window !== 'undefined' && POSTHOG_KEY) {
    // Track page views
    const trackPageView = () => {
      trackEvent('page_view', {
        path: window.location.pathname,
        title: document.title,
      });
    };

    // Track initial page view
    trackPageView();

    // Track page views on route change (for SPA)
    const originalPushState = window.history.pushState;
    window.history.pushState = function(...args: Parameters<typeof originalPushState>) {
      originalPushState.apply(this, args);
      trackPageView();
    };

    window.addEventListener('popstate', trackPageView);
  }
};