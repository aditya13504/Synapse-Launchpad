import { NextApiRequest, NextApiResponse } from 'next';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Only allow POST requests
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Get session (optional - we'll track anonymous events too)
    const session = await getServerSession(req, res, authOptions);
    
    // Get event data from request body
    const { event_name, properties } = req.body;
    
    if (!event_name) {
      return res.status(400).json({ message: 'Missing event_name' });
    }
    
    // Create event object
    const event = {
      event_name,
      properties: properties || {},
      user_id: session?.user?.id || null,
      session_id: req.body.session_id || null,
      timestamp: new Date().toISOString(),
      ip_address: req.headers['x-forwarded-for'] || req.socket.remoteAddress,
      user_agent: req.headers['user-agent'],
    };
    
    // In a real implementation, we would:
    // 1. Store the event in the database
    // 2. Send the event to River Analytics
    // 3. Process the event for real-time analytics
    
    // For now, we'll just log it and return success
    console.log('Tracked event:', event);
    
    // Return success
    return res.status(200).json({ success: true });
    
  } catch (error) {
    console.error('Error tracking event:', error);
    return res.status(500).json({ message: 'Internal server error' });
  }
}