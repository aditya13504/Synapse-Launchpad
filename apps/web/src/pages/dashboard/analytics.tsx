import { useState, useEffect } from 'react';
import { NextPage } from 'next';
import { motion } from 'framer-motion';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import { 
  BarChart3, TrendingUp, Users, Clock, MousePointer, Send, 
  Filter, Download, Calendar, RefreshCw
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { trackEvent, trackTimeOnStep, trackRecommendationClick, trackCampaignPublish, initAnalytics } from '@/lib/analytics';

// Sample data for PostHog analytics dashboard
const timeOnStepData = [
  { name: 'Business Goals', value: 245 },
  { name: 'Partner Recommendations', value: 312 },
  { name: 'Campaign Editor', value: 178 },
];

const recommendClickData = [
  { name: 'TechFlow AI', value: 42, matchScore: 96.5 },
  { name: 'GreenStart Solutions', value: 38, matchScore: 94.2 },
  { name: 'DataViz Pro', value: 27, matchScore: 91.8 },
  { name: 'CloudScale Systems', value: 19, matchScore: 89.3 },
  { name: 'FinTech Plus', value: 15, matchScore: 87.6 },
];

const campaignPublishData = [
  { name: 'Mon', value: 5 },
  { name: 'Tue', value: 8 },
  { name: 'Wed', value: 12 },
  { name: 'Thu', value: 10 },
  { name: 'Fri', value: 7 },
  { name: 'Sat', value: 3 },
  { name: 'Sun', value: 4 },
];

const sessionData = [
  { name: 'Jan', sessions: 120, newUsers: 80, completedWizards: 45 },
  { name: 'Feb', sessions: 140, newUsers: 90, completedWizards: 55 },
  { name: 'Mar', sessions: 180, newUsers: 110, completedWizards: 70 },
  { name: 'Apr', sessions: 220, newUsers: 130, completedWizards: 85 },
  { name: 'May', sessions: 280, newUsers: 150, completedWizards: 110 },
  { name: 'Jun', sessions: 310, newUsers: 170, completedWizards: 125 },
];

const conversionData = [
  { name: 'Visitors', value: 1000 },
  { name: 'Signups', value: 400 },
  { name: 'Wizard Starts', value: 300 },
  { name: 'Partner Matches', value: 250 },
  { name: 'Campaigns', value: 180 },
  { name: 'Partnerships', value: 80 },
];

const COLORS = ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444'];

const AnalyticsPage: NextPage = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState('30d');
  
  useEffect(() => {
    // Simulate loading data
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1500);
    
    return () => clearTimeout(timer);
  }, []);

  const handleRefresh = () => {
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
    }, 1000);
  };

  const handleExport = () => {
    alert('Analytics data exported successfully!');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Analytics Dashboard</h1>
          <p className="text-blue-200">Track user engagement and campaign performance</p>
        </div>
        <div className="flex space-x-4">
          <div className="flex items-center bg-white/10 rounded-lg p-2">
            <Calendar className="w-4 h-4 text-white/60 mr-2" />
            <select 
              className="bg-transparent text-white border-none focus:ring-0 text-sm"
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
            >
              <option value="7d" className="bg-slate-800">Last 7 days</option>
              <option value="30d" className="bg-slate-800">Last 30 days</option>
              <option value="90d" className="bg-slate-800">Last 90 days</option>
              <option value="1y" className="bg-slate-800">Last year</option>
            </select>
          </div>
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* PostHog Analytics Overview */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-blue-400" />
          PostHog Analytics Overview
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="glass-morphism p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Time on Step</h3>
                <p className="text-sm text-white/60">Average seconds spent on each wizard step</p>
              </div>
              <Clock className="w-5 h-5 text-blue-400" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={timeOnStepData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" stroke="#94A3B8" />
                  <YAxis dataKey="name" type="category" stroke="#94A3B8" width={150} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }}
                    labelStyle={{ color: '#F8FAFC' }}
                    itemStyle={{ color: '#3B82F6' }}
                    formatter={(value: number) => [`${value} seconds`, 'Time Spent']}
                  />
                  <Bar dataKey="value" fill="#3B82F6" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card className="glass-morphism p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Recommendation Clicks</h3>
                <p className="text-sm text-white/60">Most clicked partner recommendations</p>
              </div>
              <MousePointer className="w-5 h-5 text-purple-400" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={recommendClickData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }}
                    labelStyle={{ color: '#F8FAFC' }}
                    formatter={(value: number, name: string, props: any) => {
                      if (name === 'value') return [`${value} clicks`, 'Clicks'];
                      if (name === 'matchScore') return [`${value}%`, 'Match Score'];
                      return [value, name];
                    }}
                  />
                  <Bar dataKey="value" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card className="glass-morphism p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Campaign Publishes</h3>
                <p className="text-sm text-white/60">Campaigns published per day</p>
              </div>
              <Send className="w-5 h-5 text-green-400" />
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={campaignPublishData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }}
                    labelStyle={{ color: '#F8FAFC' }}
                    itemStyle={{ color: '#10B981' }}
                    formatter={(value: number) => [`${value} campaigns`, 'Published']}
                  />
                  <Area type="monotone" dataKey="value" stroke="#10B981" fill="#10B98120" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </div>

      {/* User Engagement Metrics */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4 flex items-center">
          <Users className="w-5 h-5 mr-2 text-blue-400" />
          User Engagement Metrics
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="glass-morphism p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Session Overview</h3>
                <p className="text-sm text-white/60">Sessions, new users, and completed wizards</p>
              </div>
              <div className="flex space-x-2">
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-blue-500 mr-1"></div>
                  <span className="text-xs text-white/60">Sessions</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-purple-500 mr-1"></div>
                  <span className="text-xs text-white/60">New Users</span>
                </div>
                <div className="flex items-center">
                  <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
                  <span className="text-xs text-white/60">Completed</span>
                </div>
              </div>
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={sessionData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="name" stroke="#94A3B8" />
                  <YAxis stroke="#94A3B8" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }}
                    labelStyle={{ color: '#F8FAFC' }}
                  />
                  <Line type="monotone" dataKey="sessions" stroke="#3B82F6" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="newUsers" stroke="#8B5CF6" strokeWidth={2} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="completedWizards" stroke="#10B981" strokeWidth={2} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card className="glass-morphism p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white">Conversion Funnel</h3>
                <p className="text-sm text-white/60">User journey conversion rates</p>
              </div>
              <TrendingUp className="w-5 h-5 text-blue-400" />
            </div>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={conversionData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis type="number" stroke="#94A3B8" />
                  <YAxis dataKey="name" type="category" stroke="#94A3B8" width={100} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }}
                    labelStyle={{ color: '#F8FAFC' }}
                    formatter={(value: number) => [`${value} users`, 'Count']}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {conversionData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      </div>

      {/* Event Breakdown */}
      <div>
        <h2 className="text-xl font-bold text-white mb-4 flex items-center">
          <Filter className="w-5 h-5 mr-2 text-blue-400" />
          Event Breakdown
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="glass-morphism p-6 md:col-span-2">
            <h3 className="text-lg font-semibold text-white mb-4">Event Timeline</h3>
            <div className="space-y-4">
              {[
                { time: '2 hours ago', event: 'campaign_publish', user: 'user_123', details: 'Published campaign for TechFlow AI partnership' },
                { time: '5 hours ago', event: 'recommend_click', user: 'user_456', details: 'Selected GreenStart Solutions (94.2% match)' },
                { time: '1 day ago', event: 'time_on_step', user: 'user_789', details: 'Spent 5m 12s on Partner Recommendations step' },
                { time: '1 day ago', event: 'campaign_publish', user: 'user_234', details: 'Published campaign for DataViz Pro partnership' },
                { time: '2 days ago', event: 'recommend_click', user: 'user_567', details: 'Selected CloudScale Systems (89.3% match)' },
              ].map((item, index) => (
                <div key={index} className="flex">
                  <div className="mr-4 flex flex-col items-center">
                    <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                    {index < 4 && <div className="w-0.5 h-full bg-blue-500/30"></div>}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between">
                      <span className="text-white font-medium">{item.event}</span>
                      <span className="text-white/60 text-sm">{item.time}</span>
                    </div>
                    <p className="text-white/70 text-sm">{item.details}</p>
                    <p className="text-white/50 text-xs">User ID: {item.user}</p>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="glass-morphism p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Event Distribution</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: 'time_on_step', value: 45 },
                      { name: 'recommend_click', value: 30 },
                      { name: 'campaign_publish', value: 15 },
                      { name: 'page_view', value: 10 },
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {COLORS.map((color, index) => (
                      <Cell key={`cell-${index}`} fill={color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155' }}
                    labelStyle={{ color: '#F8FAFC' }}
                    formatter={(value: number) => [`${value}%`, 'Percentage']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4">
              <h4 className="text-white/80 font-medium mb-2">Event Counts</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-white/70 text-sm">time_on_step</span>
                  <span className="text-white text-sm">1,245</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70 text-sm">recommend_click</span>
                  <span className="text-white text-sm">832</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70 text-sm">campaign_publish</span>
                  <span className="text-white text-sm">421</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-white/70 text-sm">page_view</span>
                  <span className="text-white text-sm">2,789</span>
                </div>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;