import { NextApiRequest, NextApiResponse } from 'next';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only allow GET requests
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Get session and verify authentication
    const session = await getServerSession(req, res, authOptions);
    
    if (!session?.user) {
      return res.status(401).json({ message: 'Unauthorized' });
    }
    
    // Get query parameters
    const { timeframe = '30d' } = req.query;
    
    // In a real implementation, we would:
    // 1. Query the database for analytics data
    // 2. Process and aggregate the data
    // 3. Return the formatted data for the dashboard
    
    // For now, we'll return mock data
    const mockData = generateMockData(timeframe as string);
    
    // Return the data
    return res.status(200).json(mockData);
    
  } catch (error) {
    console.error('Error fetching analytics data:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
}

function generateMockData(timeframe: string) {
  // Generate different data based on timeframe
  const multiplier = timeframe === '7d' ? 0.25 : 
                    timeframe === '30d' ? 1 : 
                    timeframe === '90d' ? 3 : 12;
  
  return {
    timeframe,
    summary: {
      total_events: Math.round(5243 * multiplier),
      unique_users: Math.round(842 * multiplier),
      average_session_duration: 325, // seconds
      conversion_rate: 0.068,
    },
    events: {
      time_on_step: {
        count: Math.round(1245 * multiplier),
        average_duration: 245, // seconds
        by_step: {
          business_goals: Math.round(245 * multiplier),
          partner_recommendations: Math.round(312 * multiplier),
          campaign_editor: Math.round(178 * multiplier),
        }
      },
      recommend_click: {
        count: Math.round(832 * multiplier),
        top_recommendations: [
          { name: 'TechFlow AI', count: Math.round(42 * multiplier), match_score: 96.5 },
          { name: 'GreenStart Solutions', count: Math.round(38 * multiplier), match_score: 94.2 },
          { name: 'DataViz Pro', count: Math.round(27 * multiplier), match_score: 91.8 },
          { name: 'CloudScale Systems', count: Math.round(19 * multiplier), match_score: 89.3 },
          { name: 'FinTech Plus', count: Math.round(15 * multiplier), match_score: 87.6 },
        ]
      },
      campaign_publish: {
        count: Math.round(421 * multiplier),
        by_day: [
          { day: 'Mon', count: Math.round(5 * multiplier) },
          { day: 'Tue', count: Math.round(8 * multiplier) },
          { day: 'Wed', count: Math.round(12 * multiplier) },
          { day: 'Thu', count: Math.round(10 * multiplier) },
          { day: 'Fri', count: Math.round(7 * multiplier) },
          { day: 'Sat', count: Math.round(3 * multiplier) },
          { day: 'Sun', count: Math.round(4 * multiplier) },
        ]
      }
    },
    user_journey: {
      funnel: [
        { stage: 'Visitors', count: Math.round(1000 * multiplier) },
        { stage: 'Signups', count: Math.round(400 * multiplier) },
        { stage: 'Wizard Starts', count: Math.round(300 * multiplier) },
        { stage: 'Partner Matches', count: Math.round(250 * multiplier) },
        { stage: 'Campaigns', count: Math.round(180 * multiplier) },
        { stage: 'Partnerships', count: Math.round(80 * multiplier) },
      ],
      conversion_rates: {
        visitor_to_signup: 0.40,
        signup_to_wizard: 0.75,
        wizard_to_match: 0.83,
        match_to_campaign: 0.72,
        campaign_to_partnership: 0.44,
      }
    },
    trends: {
      sessions: [
        { period: 'Jan', count: Math.round(120 * multiplier) },
        { period: 'Feb', count: Math.round(140 * multiplier) },
        { period: 'Mar', count: Math.round(180 * multiplier) },
        { period: 'Apr', count: Math.round(220 * multiplier) },
        { period: 'May', count: Math.round(280 * multiplier) },
        { period: 'Jun', count: Math.round(310 * multiplier) },
      ],
      new_users: [
        { period: 'Jan', count: Math.round(80 * multiplier) },
        { period: 'Feb', count: Math.round(90 * multiplier) },
        { period: 'Mar', count: Math.round(110 * multiplier) },
        { period: 'Apr', count: Math.round(130 * multiplier) },
        { period: 'May', count: Math.round(150 * multiplier) },
        { period: 'Jun', count: Math.round(170 * multiplier) },
      ],
      completed_wizards: [
        { period: 'Jan', count: Math.round(45 * multiplier) },
        { period: 'Feb', count: Math.round(55 * multiplier) },
        { period: 'Mar', count: Math.round(70 * multiplier) },
        { period: 'Apr', count: Math.round(85 * multiplier) },
        { period: 'May', count: Math.round(110 * multiplier) },
        { period: 'Jun', count: Math.round(125 * multiplier) },
      ]
    }
  };
}