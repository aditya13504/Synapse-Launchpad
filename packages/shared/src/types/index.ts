export interface User {
  id: string;
  email: string;
  name: string;
  company: string;
  plan: 'freemium' | 'premium' | 'enterprise';
  createdAt: Date;
  updatedAt: Date;
}

export interface Company {
  id: string;
  name: string;
  industry: string;
  stage: 'seed' | 'series-a' | 'series-b' | 'series-c' | 'growth';
  fundingAmount: number;
  employeeCount: number;
  technologies: string[];
  targetMarket: string[];
  businessModel: string;
  growthRate: number;
  location: string;
  founded: Date;
  description: string;
}

export interface Partnership {
  id: string;
  companyA: string;
  companyB: string;
  status: 'pending' | 'active' | 'completed' | 'cancelled';
  matchScore: number;
  createdAt: Date;
  updatedAt: Date;
}

export interface Campaign {
  id: string;
  name: string;
  objective: string;
  targetAudience: string;
  tone: string;
  channels: string[];
  status: 'draft' | 'active' | 'paused' | 'completed';
  performance: {
    impressions: number;
    clicks: number;
    conversions: number;
    roi: number;
  };
  createdAt: Date;
  updatedAt: Date;
}

export interface AnalyticsData {
  partnerships: number;
  campaigns: number;
  roi: number;
  engagement: number;
  period: string;
}