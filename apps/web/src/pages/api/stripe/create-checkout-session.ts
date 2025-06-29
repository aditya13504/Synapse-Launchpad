import { NextApiRequest, NextApiResponse } from 'next';
import Stripe from 'stripe';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '@/lib/auth';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    const session = await getServerSession(req, res, authOptions);
    
    if (!session?.user?.email) {
      return res.status(401).json({ message: 'Unauthorized' });
    }

    const { planId, billingInterval } = req.body;

    // Define price IDs for each plan
    const priceIds = {
      starter: {
        month: 'price_starter_monthly',
        year: 'price_starter_yearly',
      },
      pro: {
        month: 'price_pro_monthly', 
        year: 'price_pro_yearly',
      },
      enterprise: {
        month: 'price_enterprise_monthly',
        year: 'price_enterprise_yearly',
      },
    };

    const priceId = priceIds[planId as keyof typeof priceIds]?.[billingInterval as 'month' | 'year'];

    if (!priceId) {
      return res.status(400).json({ message: 'Invalid plan or billing interval' });
    }

    // Create Stripe checkout session
    const checkoutSession = await stripe.checkout.sessions.create({
      customer_email: session.user.email,
      payment_method_types: ['card'],
      line_items: [
        {
          price: priceId,
          quantity: 1,
        },
      ],
      mode: 'subscription',
      success_url: `${req.headers.origin}/dashboard?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${req.headers.origin}/pricing`,
      metadata: {
        userId: session.user.id || '',
        planId,
        billingInterval,
      },
    });

    res.status(200).json({ id: checkoutSession.id });
  } catch (error) {
    console.error('Stripe error:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
}