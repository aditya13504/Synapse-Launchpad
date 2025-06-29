import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useWizardStore } from '@/store/wizard';
import { trpc } from '@/lib/trpc';
import { Users, Star, TrendingUp, Building, MapPin, Calendar, ChevronRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { MatchScoreBar } from '@/components/ui/MatchScoreBar';
import { trackTimeOnStep, trackRecommendationClick } from '@/lib/analytics';

interface PartnerRecommendation {
  company_id: string;
  company_name: string;
  match_score: number;
  confidence: number;
  reasoning: {
    compatibility_factors: Record<string, number>;
    timing_score: number;
    behavioral_alignment: number;
  };
  metadata: Record<string, any>;
}

export function PartnerRecommendationsStep() {
  const { 
    businessGoals, 
    selectedPartner, 
    setSelectedPartner, 
    partnerRecommendations,
    setPartnerRecommendations,
    setCurrentStep 
  } = useWizardStore();
  
  const [isLoading, setIsLoading] = useState(false);
  const [selectedRecommendation, setSelectedRecommendation] = useState<PartnerRecommendation | null>(selectedPartner);
  const [startTime] = useState<number>(Date.now());

  // Mock data for demonstration
  const mockRecommendations: PartnerRecommendation[] = [
    {
      company_id: 'techflow_ai',
      company_name: 'TechFlow AI',
      match_score: 96.5,
      confidence: 94.2,
      reasoning: {
        compatibility_factors: {
          industry_alignment: 0.95,
          stage_compatibility: 0.92,
          technology_overlap: 0.88,
          market_synergy: 0.94
        },
        timing_score: 0.91,
        behavioral_alignment: 0.89
      },
      metadata: {
        industry: 'AI/ML',
        stage: 'Series A',
        location: 'San Francisco, CA',
        founded: '2022',
        employees: '25-50',
        funding: '$5.2M',
        description: 'AI-powered workflow automation for enterprise teams'
      }
    },
    {
      company_id: 'greenstart_solutions',
      company_name: 'GreenStart Solutions',
      match_score: 94.2,
      confidence: 91.8,
      reasoning: {
        compatibility_factors: {
          industry_alignment: 0.87,
          stage_compatibility: 0.95,
          technology_overlap: 0.82,
          market_synergy: 0.91
        },
        timing_score: 0.88,
        behavioral_alignment: 0.92
      },
      metadata: {
        industry: 'Sustainability',
        stage: 'Seed',
        location: 'Austin, TX',
        founded: '2023',
        employees: '10-25',
        funding: '$2.1M',
        description: 'Carbon tracking and sustainability analytics platform'
      }
    },
    {
      company_id: 'dataviz_pro',
      company_name: 'DataViz Pro',
      match_score: 91.8,
      confidence: 89.5,
      reasoning: {
        compatibility_factors: {
          industry_alignment: 0.89,
          stage_compatibility: 0.88,
          technology_overlap: 0.91,
          market_synergy: 0.85
        },
        timing_score: 0.86,
        behavioral_alignment: 0.87
      },
      metadata: {
        industry: 'Data Analytics',
        stage: 'Series A',
        location: 'New York, NY',
        founded: '2021',
        employees: '50-100',
        funding: '$8.5M',
        description: 'Advanced data visualization and business intelligence tools'
      }
    },
    {
      company_id: 'cloudscale_systems',
      company_name: 'CloudScale Systems',
      match_score: 89.3,
      confidence: 87.1,
      reasoning: {
        compatibility_factors: {
          industry_alignment: 0.84,
          stage_compatibility: 0.90,
          technology_overlap: 0.86,
          market_synergy: 0.88
        },
        timing_score: 0.85,
        behavioral_alignment: 0.84
      },
      metadata: {
        industry: 'Cloud Infrastructure',
        stage: 'Series B',
        location: 'Seattle, WA',
        founded: '2020',
        employees: '100-250',
        funding: '$15.3M',
        description: 'Scalable cloud infrastructure and DevOps automation'
      }
    },
    {
      company_id: 'fintech_plus',
      company_name: 'FinTech Plus',
      match_score: 87.6,
      confidence: 85.3,
      reasoning: {
        compatibility_factors: {
          industry_alignment: 0.82,
          stage_compatibility: 0.89,
          technology_overlap: 0.84,
          market_synergy: 0.86
        },
        timing_score: 0.83,
        behavioral_alignment: 0.88
      },
      metadata: {
        industry: 'FinTech',
        stage: 'Series A',
        location: 'Boston, MA',
        founded: '2022',
        employees: '25-50',
        funding: '$6.8M',
        description: 'AI-driven financial planning and investment tools'
      }
    }
  ];

  useEffect(() => {
    if (partnerRecommendations.length === 0) {
      // Simulate API call
      setIsLoading(true);
      setTimeout(() => {
        setPartnerRecommendations(mockRecommendations);
        setIsLoading(false);
      }, 2000);
    }
  }, [partnerRecommendations, setPartnerRecommendations]);

  // Track time spent on this step when unmounting
  useEffect(() => {
    return () => {
      const timeSpentMs = Date.now() - startTime;
      trackTimeOnStep('partner_recommendations', timeSpentMs);
    };
  }, [startTime]);

  const handleSelectPartner = (partner: PartnerRecommendation) => {
    setSelectedRecommendation(partner);
    setSelectedPartner(partner);
    
    // Track recommendation click
    trackRecommendationClick(partner.company_id, partner.match_score);
  };

  const handleProceed = () => {
    if (selectedRecommendation) {
      setCurrentStep(3);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getMatchScoreLabel = (score: number) => {
    if (score >= 95) return 'Excellent Match';
    if (score >= 90) return 'Great Match';
    if (score >= 80) return 'Good Match';
    return 'Fair Match';
  };

  if (isLoading) {
    return (
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="max-w-4xl mx-auto"
      >
        <Card className="glass-morphism p-12 text-center">
          <Loader2 className="w-12 h-12 text-blue-400 mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-white mb-2">Finding Perfect Partners</h2>
          <p className="text-blue-200 mb-6">Our AI is analyzing thousands of companies to find your ideal matches...</p>
          <div className="space-y-2 text-left max-w-md mx-auto">
            <div className="flex items-center text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse"></div>
              Analyzing company profiles and compatibility
            </div>
            <div className="flex items-center text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
              Calculating market synergies and timing
            </div>
            <div className="flex items-center text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse" style={{ animationDelay: '1s' }}></div>
              Ranking recommendations by match score
            </div>
          </div>
        </Card>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-6xl mx-auto"
    >
      <div className="text-center mb-8">
        <Users className="w-12 h-12 text-blue-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Partner Recommendations</h2>
        <p className="text-blue-200">AI-powered matches based on your business goals</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recommendations List */}
        <div className="lg:col-span-2 space-y-4">
          {partnerRecommendations.map((partner, index) => (
            <motion.div
              key={partner.company_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card 
                className={`glass-morphism p-6 cursor-pointer transition-all hover:bg-white/10 ${
                  selectedRecommendation?.company_id === partner.company_id 
                    ? 'ring-2 ring-blue-500 bg-blue-500/10' 
                    : ''
                }`}
                onClick={() => handleSelectPartner(partner)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-xl font-bold text-white">{partner.company_name}</h3>
                      <span className={`text-2xl font-bold ${getMatchScoreColor(partner.match_score)}`}>
                        {partner.match_score.toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-blue-200 mb-3">{partner.metadata.description}</p>
                    
                    {/* Company Details */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div className="flex items-center text-white/70">
                        <Building className="w-4 h-4 mr-2" />
                        {partner.metadata.industry}
                      </div>
                      <div className="flex items-center text-white/70">
                        <TrendingUp className="w-4 h-4 mr-2" />
                        {partner.metadata.stage}
                      </div>
                      <div className="flex items-center text-white/70">
                        <MapPin className="w-4 h-4 mr-2" />
                        {partner.metadata.location}
                      </div>
                      <div className="flex items-center text-white/70">
                        <Calendar className="w-4 h-4 mr-2" />
                        Founded {partner.metadata.founded}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className={`text-sm font-medium ${getMatchScoreColor(partner.match_score)}`}>
                      {getMatchScoreLabel(partner.match_score)}
                    </div>
                    <div className="text-white/60 text-sm">
                      {partner.confidence.toFixed(1)}% confidence
                    </div>
                  </div>
                </div>

                {/* Match Score Breakdown */}
                <div className="space-y-2">
                  <div className="text-sm text-white/80 font-medium">Compatibility Factors:</div>
                  {Object.entries(partner.reasoning.compatibility_factors).map(([factor, score]) => (
                    <div key={factor} className="flex items-center justify-between">
                      <span className="text-sm text-white/70 capitalize">
                        {factor.replace('_', ' ')}
                      </span>
                      <MatchScoreBar score={score * 100} size="sm" />
                    </div>
                  ))}
                </div>

                {/* Selection Indicator */}
                {selectedRecommendation?.company_id === partner.company_id && (
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    className="absolute top-4 right-4 w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center"
                  >
                    <Star className="w-4 h-4 text-white fill-current" />
                  </motion.div>
                )}
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Selected Partner Details */}
        <div className="lg:col-span-1">
          <Card className="glass-morphism p-6 sticky top-8">
            {selectedRecommendation ? (
              <div>
                <h3 className="text-xl font-bold text-white mb-4">
                  {selectedRecommendation.company_name}
                </h3>
                
                {/* Overall Match Score */}
                <div className="mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-white/80">Overall Match</span>
                    <span className={`font-bold ${getMatchScoreColor(selectedRecommendation.match_score)}`}>
                      {selectedRecommendation.match_score.toFixed(1)}%
                    </span>
                  </div>
                  <MatchScoreBar score={selectedRecommendation.match_score} />
                </div>

                {/* Detailed Metrics */}
                <div className="space-y-4 mb-6">
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-white/70">Timing Score</span>
                      <span className="text-sm text-white">
                        {(selectedRecommendation.reasoning.timing_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <MatchScoreBar score={selectedRecommendation.reasoning.timing_score * 100} size="sm" />
                  </div>
                  
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-sm text-white/70">Behavioral Alignment</span>
                      <span className="text-sm text-white">
                        {(selectedRecommendation.reasoning.behavioral_alignment * 100).toFixed(1)}%
                      </span>
                    </div>
                    <MatchScoreBar score={selectedRecommendation.reasoning.behavioral_alignment * 100} size="sm" />
                  </div>
                </div>

                {/* Company Info */}
                <div className="space-y-3 mb-6 text-sm">
                  <div className="flex justify-between">
                    <span className="text-white/70">Funding:</span>
                    <span className="text-white">{selectedRecommendation.metadata.funding}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Employees:</span>
                    <span className="text-white">{selectedRecommendation.metadata.employees}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Stage:</span>
                    <span className="text-white">{selectedRecommendation.metadata.stage}</span>
                  </div>
                </div>

                <Button
                  onClick={handleProceed}
                  className="w-full btn-primary"
                >
                  Generate Campaign
                  <ChevronRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            ) : (
              <div className="text-center text-white/60">
                <Users className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Select a partner to view detailed analysis</p>
              </div>
            )}
          </Card>
        </div>
      </div>
    </motion.div>
  );
}