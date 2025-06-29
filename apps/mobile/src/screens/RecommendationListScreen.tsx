import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  FlatList,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  RefreshControl,
  Alert,
} from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { useQuery } from 'react-query';
import { SafeAreaView } from 'react-native-safe-area-context';
import { THEME } from '../config';
import { getPartnerRecommendations, selectPartner, PartnerRecommendation } from '../services/partnerService';
import { MatchScoreBar } from '../components/MatchScoreBar';
import { Building, TrendingUp, MapPin, Star } from '../components/icons';
import { useSubscriptionStore } from '../store/subscriptionStore';

const RecommendationListScreen = () => {
  const navigation = useNavigation();
  const { isPro, fetchPackages } = useSubscriptionStore();
  const [selectedPartner, setSelectedPartner] = useState<string | null>(null);

  const {
    data: recommendations,
    isLoading,
    isError,
    refetch,
    isRefetching,
  } = useQuery('partnerRecommendations', getPartnerRecommendations);

  useEffect(() => {
    // Fetch subscription packages on mount
    fetchPackages();
  }, [fetchPackages]);

  const handleSelectPartner = async (partnerId: string) => {
    try {
      setSelectedPartner(partnerId);
      await selectPartner(partnerId);
      (navigation as any).navigate('CampaignPreview', { partnerId });
    } catch (error) {
      console.error('Failed to select partner:', error);
      Alert.alert('Error', 'Failed to select partner. Please try again.');
      setSelectedPartner(null);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#10B981'; // green
    if (score >= 80) return '#FBBF24'; // yellow
    if (score >= 70) return '#F97316'; // orange
    return '#EF4444'; // red
  };

  const getScoreLabel = (score: number) => {
    if (score >= 95) return 'Excellent Match';
    if (score >= 90) return 'Great Match';
    if (score >= 80) return 'Good Match';
    return 'Fair Match';
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={THEME.PRIMARY} />
        <Text style={styles.loadingText}>Finding your perfect partners...</Text>
      </View>
    );
  }

  if (isError) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Failed to load recommendations</Text>
        <TouchableOpacity style={styles.retryButton} onPress={() => refetch()}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // Limit recommendations for non-pro users
  const displayedRecommendations = isPro
    ? recommendations || []
    : (recommendations || []).slice(0, 3);

  return (
    <SafeAreaView edges={['bottom']} style={styles.container}>
      <FlatList
        data={displayedRecommendations}
        keyExtractor={(item) => item.company_id}
        renderItem={({ item }) => (
          <TouchableOpacity
            style={[
              styles.card,
              selectedPartner === item.company_id && styles.selectedCard,
            ]}
            onPress={() => handleSelectPartner(item.company_id)}
          >
            <View style={styles.cardHeader}>
              <Text style={styles.companyName}>{item.company_name}</Text>
              <View style={styles.scoreContainer}>
                <Text
                  style={[
                    styles.scoreValue,
                    { color: getScoreColor(item.match_score) },
                  ]}
                >
                  {item.match_score.toFixed(1)}%
                </Text>
                <Text style={styles.scoreLabel}>
                  {getScoreLabel(item.match_score)}
                </Text>
              </View>
            </View>

            <Text style={styles.description} numberOfLines={2}>
              {item.metadata?.description || 'Innovative company with great partnership potential.'}
            </Text>

            <MatchScoreBar score={item.match_score} />

            <View style={styles.detailsContainer}>
              <View style={styles.detailItem}>
                <Building width={16} height={16} color="#94A3B8" />
                <Text style={styles.detailText}>
                  {item.metadata?.industry || 'Technology'}
                </Text>
              </View>
              <View style={styles.detailItem}>
                <TrendingUp width={16} height={16} color="#94A3B8" />
                <Text style={styles.detailText}>
                  {item.metadata?.stage || 'Series A'}
                </Text>
              </View>
              <View style={styles.detailItem}>
                <MapPin width={16} height={16} color="#94A3B8" />
                <Text style={styles.detailText}>
                  {item.metadata?.location || 'San Francisco, CA'}
                </Text>
              </View>
            </View>

            {selectedPartner === item.company_id && (
              <View style={styles.selectedIndicator}>
                <Star width={16} height={16} color="#fff" fill="#fff" />
              </View>
            )}
          </TouchableOpacity>
        )}
        refreshControl={
          <RefreshControl
            refreshing={isRefetching}
            onRefresh={refetch}
            tintColor={THEME.PRIMARY}
            colors={[THEME.PRIMARY]}
          />
        }
        ListHeaderComponent={
          <Text style={styles.headerText}>
            AI-powered matches based on your business goals
          </Text>
        }
        ListFooterComponent={
          !isPro && recommendations && recommendations.length > 3 ? (
            <View style={styles.upgradeContainer}>
              <Text style={styles.upgradeText}>
                Upgrade to Pro to see {recommendations.length - 3} more partner recommendations
              </Text>
              <TouchableOpacity
                style={styles.upgradeButton}
                onPress={() => (navigation as any).navigate('SubscriptionScreen')}
              >
                <Text style={styles.upgradeButtonText}>Upgrade to Pro</Text>
              </TouchableOpacity>
            </View>
          ) : null
        }
        contentContainerStyle={styles.listContent}
      />
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: THEME.BACKGROUND.DARK,
  },
  listContent: {
    padding: 16,
  },
  headerText: {
    fontSize: 16,
    color: '#94A3B8',
    marginBottom: 16,
    textAlign: 'center',
  },
  card: {
    backgroundColor: THEME.CARD.DARK,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  selectedCard: {
    borderColor: THEME.PRIMARY,
    backgroundColor: `${THEME.PRIMARY}10`,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  companyName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: THEME.TEXT.DARK,
    flex: 1,
  },
  scoreContainer: {
    alignItems: 'flex-end',
  },
  scoreValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  scoreLabel: {
    fontSize: 12,
    color: '#94A3B8',
  },
  description: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 12,
  },
  detailsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 12,
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
  retryButton: {
    backgroundColor: THEME.PRIMARY,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  upgradeContainer: {
    backgroundColor: `${THEME.SECONDARY}20`,
    borderRadius: 16,
    padding: 16,
    marginTop: 8,
    alignItems: 'center',
  },
  upgradeText: {
    fontSize: 14,
    color: THEME.TEXT.DARK,
    marginBottom: 12,
    textAlign: 'center',
  },
  upgradeButton: {
    backgroundColor: THEME.SECONDARY,
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  upgradeButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  selectedIndicator: {
    position: 'absolute',
    top: 12,
    right: 12,
    backgroundColor: THEME.PRIMARY,
    width: 24,
    height: 24,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default RecommendationListScreen;