import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useWizardStore } from '@/store/wizard';
import { Zap, Copy, Download, Check, Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { trackTimeOnStep, trackCampaignPublish } from '@/lib/analytics';

export function CampaignEditorStep() {
  const { selectedPartner, campaignData, setCampaignData } = useWizardStore();
  const [isLoading, setIsLoading] = useState(true);
  const [isCopied, setIsCopied] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [isPublished, setIsPublished] = useState(false);
  const [startTime] = useState<number>(Date.now());

  // Mock campaign data
  const mockCampaignData = {
    campaign_id: `campaign_${Date.now()}`,
    campaign_brief: {
      objective: "Establish a strategic partnership to accelerate growth and market penetration",
      key_message: "Combining our technologies creates an unparalleled solution for enterprise customers",
      hooks: [
        "Increase revenue by 35% through combined market access",
        "Reduce customer acquisition costs by 40%",
        "Launch innovative joint solution within 90 days"
      ],
      fomo_angle: "Limited partnership slots available this quarter - secure priority integration",
      psychological_triggers: [
        "scarcity",
        "social_proof",
        "authority",
        "reciprocity"
      ],
      success_metrics: [
        "Joint revenue growth",
        "Customer acquisition efficiency",
        "Market share expansion",
        "Brand authority enhancement"
      ]
    },
    channel_mix_plan: [
      {
        channel: "email",
        allocation_percentage: 40,
        rationale: "Direct communication for personalized partnership proposal",
        optimal_timing: "Tuesday/Wednesday mornings, 9-11am",
        content_types: ["partnership_proposal", "case_studies", "integration_roadmap"],
        psychological_approach: "Authority + Scarcity"
      },
      {
        channel: "linkedin",
        allocation_percentage: 30,
        rationale: "Professional network for industry credibility and reach",
        optimal_timing: "Weekdays, 1-3pm",
        content_types: ["thought_leadership", "partnership_announcement", "success_stories"],
        psychological_approach: "Social Proof + Authority"
      },
      {
        channel: "direct_outreach",
        allocation_percentage: 20,
        rationale: "High-touch approach for key decision makers",
        optimal_timing: "Thursday/Friday, scheduled meetings",
        content_types: ["executive_presentation", "custom_proposal", "demo"],
        psychological_approach: "Reciprocity + Commitment"
      },
      {
        channel: "webinar",
        allocation_percentage: 10,
        rationale: "Educational approach to showcase joint value proposition",
        optimal_timing: "Mid-month, 11am or 2pm",
        content_types: ["joint_presentation", "q_and_a", "case_study_deep_dive"],
        psychological_approach: "Authority + Liking"
      }
    ],
    channel_content: [
      {
        channel: "email",
        content_type: "partnership_proposal",
        copy_variants: [
          {
            variant_id: "email_conscientious_1",
            big_five_target: "conscientiousness",
            headline: "Strategic Partnership Opportunity: Data-Driven Results Within 90 Days",
            body_text: "Hi [Name],\n\nI hope this message finds you well. Based on our analysis of market synergies between our companies, I'm reaching out to propose a strategic partnership that could deliver measurable results within the next quarter.\n\nOur data shows that companies implementing this partnership model have experienced:\n• 35% average revenue growth in joint markets\n• 40% reduction in customer acquisition costs\n• 90-day timeline from agreement to market\n\nI've attached a detailed analysis of our compatibility factors and a structured implementation roadmap.\n\nWould you be available for a 30-minute call next Tuesday at 10am to discuss the specifics?\n\nBest regards,\n[Your Name]",
            cta: "Schedule Partnership Discussion",
            psychological_triggers: ["authority", "scarcity", "reciprocity"],
            tone_analysis: {
              formality: 0.85,
              enthusiasm: 0.65,
              urgency: 0.70,
              trustworthiness: 0.90
            },
            estimated_performance: {
              open_rate: 0.35,
              response_rate: 0.15,
              meeting_conversion: 0.08
            }
          },
          {
            variant_id: "email_openness_1",
            big_five_target: "openness",
            headline: "Innovative Partnership Opportunity: Reimagining What's Possible Together",
            body_text: "Hi [Name],\n\nI've been following the innovative work at [Partner Company] and see an exciting opportunity to create something truly groundbreaking together.\n\nImagine combining our [key technology] with your [partner strength] to pioneer a new approach that could transform how [industry] operates.\n\nThe possibilities are fascinating:\n• Creating entirely new market categories\n• Developing novel solutions to persistent industry challenges\n• Establishing thought leadership in emerging spaces\n\nI'd love to explore these ideas with you in a free-flowing conversation. Are you open to connecting for a creative discussion next week?\n\nLooking forward to the possibilities,\n[Your Name]",
            cta: "Let's Explore Together",
            psychological_triggers: ["novelty", "curiosity", "vision"],
            tone_analysis: {
              formality: 0.60,
              enthusiasm: 0.90,
              urgency: 0.50,
              trustworthiness: 0.75
            },
            estimated_performance: {
              open_rate: 0.38,
              response_rate: 0.12,
              meeting_conversion: 0.06
            }
          }
        ],
        creative_assets: []
      },
      {
        channel: "linkedin",
        content_type: "partnership_announcement",
        copy_variants: [
          {
            variant_id: "linkedin_extraversion_1",
            big_five_target: "extraversion",
            headline: "Exciting News: [Your Company] and [Partner Company] Join Forces!",
            body_text: "We're thrilled to announce our strategic partnership with [Partner Company]! 🚀\n\nBy combining our [your strength] with their industry-leading [partner strength], we're creating unprecedented opportunities for [target audience].\n\nThis collaboration will enable both our communities to:\n• Access innovative solutions that weren't possible before\n• Achieve results faster and more efficiently\n• Connect with a broader network of industry leaders\n\nWe can't wait to share the amazing things we'll build together! Stay tuned for upcoming joint events, shared resources, and special opportunities for our community members.\n\nTag someone who should know about this partnership! 👇\n\n#StrategicPartnership #Innovation #[Industry]",
            cta: "Learn more about our partnership",
            psychological_triggers: ["social_proof", "excitement", "community"],
            tone_analysis: {
              formality: 0.40,
              enthusiasm: 0.95,
              urgency: 0.60,
              trustworthiness: 0.75
            },
            estimated_performance: {
              engagement_rate: 0.08,
              share_rate: 0.03,
              click_through_rate: 0.05
            }
          }
        ],
        creative_assets: []
      }
    ],
    psychological_insights: {
      primary_motivation: "Growth and competitive advantage",
      decision_factors: ["ROI potential", "implementation complexity", "strategic alignment"],
      emotional_triggers: ["fear of missing out", "desire for innovation", "competitive pressure"],
      communication_preferences: {
        style: "direct and data-driven",
        format: "structured with clear next steps",
        frequency: "focused and purposeful"
      }
    },
    performance_predictions: {
      channel_predictions: {
        email: {
          estimated_reach: 500,
          click_rate: 0.12,
          engagement_rate: 0.08,
          conversion_rate: 0.04,
          estimated_meetings: 20
        },
        linkedin: {
          estimated_reach: 2500,
          click_rate: 0.05,
          engagement_rate: 0.07,
          conversion_rate: 0.01,
          estimated_impressions: 7500
        }
      },
      overall_metrics: {
        total_reach: 3000,
        total_engagement: 210,
        total_conversions: 30,
        roi_estimate: 4.2
      }
    },
    optimization_recommendations: [
      "A/B test email subject lines with varying urgency levels",
      "Personalize outreach with industry-specific case studies",
      "Follow up within 3 days of initial contact",
      "Include social proof from similar companies in your sector"
    ],
    created_at: new Date().toISOString()
  };

  useEffect(() => {
    // Simulate API call to generate campaign
    if (!campaignData) {
      const timer = setTimeout(() => {
        setCampaignData(mockCampaignData);
        setIsLoading(false);
      }, 3000);
      
      return () => clearTimeout(timer);
    } else {
      setIsLoading(false);
    }
  }, [campaignData, setCampaignData]);

  // Track time spent on this step when unmounting
  useEffect(() => {
    return () => {
      const timeSpentMs = Date.now() - startTime;
      trackTimeOnStep('campaign_editor', timeSpentMs);
    };
  }, [startTime]);

  const handleCopyJSON = () => {
    navigator.clipboard.writeText(JSON.stringify(campaignData, null, 2));
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const handleDownloadJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(campaignData, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `campaign_${campaignData?.campaign_id}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handlePublishCampaign = () => {
    setIsPublishing(true);
    
    // Simulate API call to publish campaign
    setTimeout(() => {
      setIsPublishing(false);
      setIsPublished(true);
      
      // Track campaign publish event
      if (campaignData && selectedPartner) {
        trackCampaignPublish(campaignData.campaign_id, selectedPartner.company_id);
      }
    }, 2000);
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
          <h2 className="text-2xl font-bold text-white mb-2">Generating Your Campaign</h2>
          <p className="text-blue-200 mb-6">Our AI is crafting the perfect partnership campaign...</p>
          <div className="space-y-2 text-left max-w-md mx-auto">
            <div className="flex items-center text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse"></div>
              Analyzing partnership synergies
            </div>
            <div className="flex items-center text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse" style={{ animationDelay: '0.5s' }}></div>
              Crafting personalized messaging
            </div>
            <div className="flex items-center text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse" style={{ animationDelay: '1s' }}></div>
              Optimizing for psychological impact
            </div>
            <div className="flex items-center text-white/60">
              <div className="w-2 h-2 bg-blue-400 rounded-full mr-3 animate-pulse" style={{ animationDelay: '1.5s' }}></div>
              Finalizing multi-channel strategy
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
        <Zap className="w-12 h-12 text-blue-400 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Campaign Generation</h2>
        <p className="text-blue-200">AI-powered campaign for your partnership with {selectedPartner?.company_name}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Campaign JSON */}
        <div className="lg:col-span-2">
          <Card className="glass-morphism p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white">Campaign JSON</h3>
              <div className="flex space-x-2">
                <Button
                  onClick={handleCopyJSON}
                  variant="ghost"
                  className="text-white/70 hover:text-white"
                >
                  {isCopied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                  {isCopied ? 'Copied!' : 'Copy'}
                </Button>
                <Button
                  onClick={handleDownloadJSON}
                  variant="ghost"
                  className="text-white/70 hover:text-white"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-4 overflow-auto max-h-[600px]">
              <pre className="text-white/90 text-sm">
                {JSON.stringify(campaignData, null, 2)}
              </pre>
            </div>
          </Card>
        </div>

        {/* Campaign Summary */}
        <div className="lg:col-span-1">
          <Card className="glass-morphism p-6 sticky top-8">
            <h3 className="text-xl font-bold text-white mb-4">Campaign Summary</h3>
            
            <div className="space-y-6">
              <div>
                <h4 className="text-white/80 font-semibold mb-2">Campaign Brief</h4>
                <p className="text-white/70 text-sm mb-2">{campaignData?.campaign_brief.key_message}</p>
                <div className="bg-white/5 rounded-lg p-3">
                  <p className="text-white/80 text-sm font-medium">Top Hooks:</p>
                  <ul className="list-disc list-inside text-white/70 text-sm mt-1">
                    {campaignData?.campaign_brief.hooks.slice(0, 2).map((hook, index) => (
                      <li key={index}>{hook}</li>
                    ))}
                  </ul>
                </div>
              </div>
              
              <div>
                <h4 className="text-white/80 font-semibold mb-2">Channel Mix</h4>
                <div className="space-y-2">
                  {campaignData?.channel_mix_plan.map((channel, index) => (
                    <div key={index} className="flex justify-between items-center">
                      <span className="text-white/70 capitalize">{channel.channel}</span>
                      <div className="flex items-center">
                        <span className="text-white/80 text-sm mr-2">{channel.allocation_percentage}%</span>
                        <div className="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-blue-500 rounded-full" 
                            style={{ width: `${channel.allocation_percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h4 className="text-white/80 font-semibold mb-2">Performance Prediction</h4>
                <div className="bg-white/5 rounded-lg p-3">
                  <div className="flex justify-between mb-1">
                    <span className="text-white/70 text-sm">Total Reach:</span>
                    <span className="text-white text-sm">{campaignData?.performance_predictions.overall_metrics.total_reach.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between mb-1">
                    <span className="text-white/70 text-sm">Conversions:</span>
                    <span className="text-white text-sm">{campaignData?.performance_predictions.overall_metrics.total_conversions}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70 text-sm">Estimated ROI:</span>
                    <span className="text-green-400 text-sm font-medium">{campaignData?.performance_predictions.overall_metrics.roi_estimate}x</span>
                  </div>
                </div>
              </div>
              
              <Button
                onClick={handlePublishCampaign}
                className="w-full btn-primary"
                disabled={isPublishing || isPublished}
              >
                {isPublishing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Publishing...
                  </>
                ) : isPublished ? (
                  <>
                    <Check className="w-4 h-4 mr-2" />
                    Published
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4 mr-2" />
                    Publish Campaign
                  </>
                )}
              </Button>
              
              {isPublished && (
                <p className="text-green-400 text-sm text-center mt-2">
                  Campaign generated successfully!
                </p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </motion.div>
  );
}