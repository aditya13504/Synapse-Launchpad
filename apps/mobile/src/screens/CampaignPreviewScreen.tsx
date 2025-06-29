import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Linking,
} from 'react-native';
import { useRoute, useNavigation } from '@react-navigation/native';
import { useQuery } from 'react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import { THEME, WEB_URL } from '../config';
import { getCampaignDetails, generateCampaign } from '../services/campaignService';
import { getPartnerDetails } from '../services/partnerService';
import { Mail, Share2, ExternalLink, Zap, Target, Users, Building, TrendingUp } from '../components/icons';
import { formatDistanceToNow } from 'date-fns';

const CampaignPreviewScreen = () => {
  const route = useRoute();
  const navigation = useNavigation();
  const { partnerId } = route.params as { partnerId: string };
  const [isGenerating, setIsGenerating] = useState(false);

  // Fetch partner details
  const {
    data: partner,
    isLoading: isLoadingPartner,
    isError: isPartnerError,
  } = useQuery(['partner', partnerId], () => getPartnerDetails(partnerId));

  // Fetch campaign if it exists
  const {
    data: campaign,
    isLoading: isLoadingCampaign,
    isError: isCampaignError,
    refetch: refetchCampaign,
  } = useQuery(['campaign', partnerId], () => getCampaignDetails(partnerId), {
    enabled: !!partnerId,
    retry: false,
    onError: () => {}, // Suppress error since campaign might not exist yet
  });

  const handleGenerateCampaign = async () => {
    setIsGenerating(true);
    try {
      await generateCampaign(partnerId);
      await refetchCampaign();
    } catch (error) {
      console.error('Failed to generate campaign:', error);
      Alert.alert('Error', 'Failed to generate campaign. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const openWebDashboard = () => {
    const url = `${WEB_URL}/dashboard/campaigns/${campaign?.id || ''}`;
    Linking.openURL(url).catch((err) => {
      console.error('Failed to open URL:', err);
      Alert.alert('Error', 'Could not open web dashboard');
    });
  };

  if (isLoadingPartner) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={THEME.PRIMARY} />
        <Text style={styles.loadingText}>Loading partner details...</Text>
      </View>
    );
  }

  if (isPartnerError) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load partner details</Text>
        <TouchableOpacity
          style={styles.button}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.buttonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const isLoading = isLoadingCampaign || isGenerating;

  return (
    <SafeAreaView edges={['bottom']} style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Partner Info */}
        <View style={styles.partnerCard}>
          <Text style={styles.partnerName}>{partner?.company_name}</Text>
          <Text style={styles.matchScore}>
            {partner?.match_score.toFixed(1)}% Match
          </Text>
          <Text style={styles.partnerDescription}>
            {partner?.metadata?.description ||
              'This partner has strong synergy potential with your business.'}
          </Text>
          
          <View style={styles.detailsContainer}>
            <View style={styles.detailItem}>
              <Building width={16} height={16} color="#94A3B8" />
              <Text style={styles.detailText}>
                {partner?.metadata?.industry || 'Technology'}
              </Text>
            </View>
            <View style={styles.detailItem}>
              <TrendingUp width={16} height={16} color="#94A3B8" />
              <Text style={styles.detailText}>
                {partner?.metadata?.stage || 'Series A'}
              </Text>
            </View>
            <View style={styles.detailItem}>
              <Users width={16} height={16} color="#94A3B8" />
              <Text style={styles.detailText}>
                {partner?.metadata?.employee_count || '25-50'} employees
              </Text>
            </View>
          </View>
        </View>

        {/* Campaign Preview */}
        {campaign ? (
          <View style={styles.campaignContainer}>
            <View style={styles.campaignHeader}>
              <Text style={styles.campaignTitle}>{campaign.name}</Text>
              <Text style={styles.campaignDate}>
                Created {formatDistanceToNow(new Date(campaign.created_at))} ago
              </Text>
            </View>

            <View style={styles.objectiveContainer}>
              <Target width={20} height={20} color={THEME.PRIMARY} />
              <Text style={styles.objectiveText}>{campaign.objective}</Text>
            </View>

            {campaign.channels.map((channel) => (
              <View key={channel} style={styles.channelCard}>
                <View style={styles.channelHeader}>
                  {channel === 'email' ? (
                    <Mail width={20} height={20} color="#94A3B8" />
                  ) : (
                    <Share2 width={20} height={20} color="#94A3B8" />
                  )}
                  <Text style={styles.channelName}>
                    {channel.charAt(0).toUpperCase() + channel.slice(1)}
                  </Text>
                </View>
                
                <Text style={styles.contentPreview}>
                  {campaign.content?.[channel]?.subject_line && (
                    <Text style={styles.subjectLine}>
                      {campaign.content[channel].subject_line}
                    </Text>
                  )}
                  {campaign.content?.[channel]?.content
                    ? campaign.content[channel].content.substring(0, 150) + '...'
                    : 'No content available for this channel.'}
                </Text>
              </View>
            ))}

            <TouchableOpacity
              style={styles.webButton}
              onPress={openWebDashboard}
            >
              <Text style={styles.webButtonText}>Edit in Web Dashboard</Text>
              <ExternalLink width={16} height={16} color="#fff" />
            </TouchableOpacity>
          </View>
        ) : (
          <View style={styles.noCampaignContainer}>
            <Zap width={40} height={40} color={THEME.PRIMARY} />
            <Text style={styles.noCampaignTitle}>
              Generate Partnership Campaign
            </Text>
            <Text style={styles.noCampaignText}>
              Create an AI-powered marketing campaign optimized for this partnership
            </Text>
            <TouchableOpacity
              style={styles.generateButton}
              onPress={handleGenerateCampaign}
              disabled={isLoading}
            >
              {isLoading ? (
                <ActivityIndicator color="#fff" />
              ) : (
                <Text style={styles.generateButtonText}>Generate Campaign</Text>
              )}
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME.BACKGROUND.DARK,
  },
  scrollContent: {
    padding: 16,
  },
  partnerCard: {
    backgroundColor: THEME.CARD.DARK,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  partnerName: {
    fontSize: 20,
    fontWeight: 'bold',
    color: THEME.TEXT.DARK,
    marginBottom: 4,
  },
  matchScore: {
    fontSize: 16,
    fontWeight: '600',
    color: '#10B981',
    marginBottom: 8,
  },
  partnerDescription: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 12,
    lineHeight: 20,
  },
  detailsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 8,
  },
  detailItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
    marginBottom: 4,
  },
  detailText: {
    fontSize: 12,
    color: '#94A3B8',
    marginLeft: 4,
  },
  campaignContainer: {
    backgroundColor: THEME.CARD.DARK,
    borderRadius: 16,
    padding: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  campaignHeader: {
    marginBottom: 12,
  },
  campaignTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: THEME.TEXT.DARK,
    marginBottom: 4,
  },
  campaignDate: {
    fontSize: 12,
    color: '#64748B',
  },
  objectiveContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: `${THEME.PRIMARY}15`,
    padding: 12,
    borderRadius: 8,
    marginBottom: 16,
  },
  objectiveText: {
    fontSize: 14,
    color: THEME.TEXT.DARK,
    marginLeft: 8,
    flex: 1,
  },
  channelCard: {
    backgroundColor: '#1E293B',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
  },
  channelHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  channelName: {
    fontSize: 16,
    fontWeight: '600',
    color: THEME.TEXT.DARK,
    marginLeft: 8,
  },
  contentPreview: {
    fontSize: 14,
    color: '#94A3B8',
    lineHeight: 20,
  },
  subjectLine: {
    fontWeight: 'bold',
    color: THEME.TEXT.DARK,
  },
  webButton: {
    backgroundColor: THEME.SECONDARY,
    borderRadius: 12,
    padding: 14,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 16,
  },
  webButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginRight: 8,
  },
  noCampaignContainer: {
    backgroundColor: THEME.CARD.DARK,
    borderRadius: 16,
    padding: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#334155',
  },
  noCampaignTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: THEME.TEXT.DARK,
    marginTop: 16,
    marginBottom: 8,
  },
  noCampaignText: {
    fontSize: 14,
    color: '#94A3B8',
    textAlign: 'center',
    marginBottom: 24,
    lineHeight: 20,
  },
  generateButton: {
    backgroundColor: THEME.PRIMARY,
    borderRadius: 12,
    padding: 16,
    width: '100%',
    alignItems: 'center',
  },
  generateButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: THEME.BACKGROUND.DARK,
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: THEME.TEXT.DARK,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: THEME.BACKGROUND.DARK,
    padding: 20,
  },
  errorText: {
    fontSize: 16,
    color: THEME.TEXT.DARK,
    marginBottom: 16,
    textAlign: 'center',
  },
  button: {
    backgroundColor: THEME.PRIMARY,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  buttonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
});

export default CampaignPreviewScreen;