import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import Purchases, { PurchasesPackage } from 'react-native-purchases';
import { useSubscriptionStore } from '../store/subscriptionStore';
import { THEME } from '../config';
import { Zap, Star, Crown } from '../components/icons';

const SubscriptionScreen = () => {
  const navigation = useNavigation();
  const { 
    isLoading, 
    packages, 
    currentPlan, 
    fetchPackages, 
    purchasePackage, 
    restorePurchases 
  } = useSubscriptionStore();
  const [selectedPackage, setSelectedPackage] = useState<string | null>(null);

  useEffect(() => {
    fetchPackages();
  }, [fetchPackages]);

  const handlePurchase = async (pkg: PurchasesPackage) => {
    try {
      const success = await purchasePackage(pkg);
      if (success) {
        Alert.alert(
          'Subscription Successful',
          'Thank you for your purchase! Your subscription is now active.',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      }
    } catch (error) {
      console.error('Purchase failed:', error);
      Alert.alert('Purchase Failed', 'There was an error processing your purchase. Please try again.');
    }
  };

  const handleRestore = async () => {
    try {
      await restorePurchases();
      Alert.alert('Purchases Restored', 'Your purchases have been restored successfully.');
    } catch (error) {
      console.error('Restore failed:', error);
      Alert.alert('Restore Failed', 'There was an error restoring your purchases. Please try again.');
    }
  };

  const getPlanIcon = (identifier: string) => {
    if (identifier.includes('starter')) {
      return <Star width={24} height={24} color={THEME.PRIMARY} />;
    } else if (identifier.includes('pro')) {
      return <Zap width={24} height={24} color="#8B5CF6" />;
    } else if (identifier.includes('enterprise')) {
      return <Crown width={24} height={24} color="#F59E0B" />;
    }
    return <Star width={24} height={24} color={THEME.PRIMARY} />;
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={THEME.PRIMARY} />
        <Text style={styles.loadingText}>Loading subscription options...</Text>
      </View>
    );
  }

  return (
    <SafeAreaView edges={['bottom']} style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <Text style={styles.title}>Choose Your Plan</Text>
        <Text style={styles.subtitle}>
          Upgrade to access more partner recommendations and advanced features
        </Text>

        {packages.map((pkg) => {
          const isCurrentPlan = currentPlan === pkg.identifier;
          const isPro = pkg.identifier.includes('pro');
          const isEnterprise = pkg.identifier.includes('enterprise');
          
          return (
            <TouchableOpacity
              key={pkg.identifier}
              style={[
                styles.planCard,
                selectedPackage === pkg.identifier && styles.selectedPlan,
                isCurrentPlan && styles.currentPlan,
              ]}
              onPress={() => setSelectedPackage(pkg.identifier)}
              disabled={isCurrentPlan}
            >
              <View style={styles.planHeader}>
                <View style={styles.planIconContainer}>
                  {getPlanIcon(pkg.identifier)}
                </View>
                <View style={styles.planInfo}>
                  <Text style={styles.planName}>
                    {pkg.product.title || 'Unknown Plan'}
                  </Text>
                  <Text style={styles.planPrice}>
                    {pkg.product.priceString}
                  </Text>
                </View>
                {isCurrentPlan && (
                  <View style={styles.currentPlanBadge}>
                    <Text style={styles.currentPlanText}>Current</Text>
                  </View>
                )}
              </View>

              <View style={styles.planFeatures}>
                {isPro ? (
                  <>
                    <Text style={styles.featureText}>✓ Unlimited partner recommendations</Text>
                    <Text style={styles.featureText}>✓ Advanced campaign generation</Text>
                    <Text style={styles.featureText}>✓ Psychology-based targeting</Text>
                    <Text style={styles.featureText}>✓ Priority support</Text>
                  </>
                ) : isEnterprise ? (
                  <>
                    <Text style={styles.featureText}>✓ Everything in Pro</Text>
                    <Text style={styles.featureText}>✓ Custom integrations</Text>
                    <Text style={styles.featureText}>✓ Dedicated account manager</Text>
                    <Text style={styles.featureText}>✓ White-label options</Text>
                  </>
                ) : (
                  <>
                    <Text style={styles.featureText}>✓ Up to 5 partner recommendations</Text>
                    <Text style={styles.featureText}>✓ Basic campaign generation</Text>
                    <Text style={styles.featureText}>✓ Email support</Text>
                    <Text style={styles.featureText}>✓ Standard analytics</Text>
                  </>
                )}
              </View>

              {!isCurrentPlan && (
                <TouchableOpacity
                  style={[
                    styles.purchaseButton,
                    isPro && styles.proPurchaseButton,
                    isEnterprise && styles.enterprisePurchaseButton,
                  ]}
                  onPress={() => handlePurchase(pkg)}
                >
                  <Text style={styles.purchaseButtonText}>
                    {isPro || isEnterprise ? 'Upgrade Now' : 'Subscribe'}
                  </Text>
                </TouchableOpacity>
              )}
            </TouchableOpacity>
          );
        })}

        <TouchableOpacity style={styles.restoreButton} onPress={handleRestore}>
          <Text style={styles.restoreButtonText}>Restore Purchases</Text>
        </TouchableOpacity>
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
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: THEME.TEXT.DARK,
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 24,
    textAlign: 'center',
  },
  planCard: {
    backgroundColor: THEME.CARD.DARK,
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#334155',
  },
  selectedPlan: {
    borderColor: THEME.PRIMARY,
    backgroundColor: `${THEME.PRIMARY}10`,
  },
  currentPlan: {
    borderColor: '#10B981',
    backgroundColor: `#10B98110`,
  },
  planHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  planIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#1E293B',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  planInfo: {
    flex: 1,
  },
  planName: {
    fontSize: 18,
    fontWeight: 'bold',
    color: THEME.TEXT.DARK,
    marginBottom: 4,
  },
  planPrice: {
    fontSize: 14,
    color: '#94A3B8',
  },
  currentPlanBadge: {
    backgroundColor: '#10B981',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  currentPlanText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: '600',
  },
  planFeatures: {
    marginBottom: 16,
  },
  featureText: {
    fontSize: 14,
    color: '#94A3B8',
    marginBottom: 8,
    lineHeight: 20,
  },
  purchaseButton: {
    backgroundColor: THEME.PRIMARY,
    borderRadius: 12,
    padding: 14,
    alignItems: 'center',
  },
  proPurchaseButton: {
    backgroundColor: '#8B5CF6',
  },
  enterprisePurchaseButton: {
    backgroundColor: '#F59E0B',
  },
  purchaseButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  restoreButton: {
    padding: 16,
    alignItems: 'center',
  },
  restoreButtonText: {
    color: THEME.PRIMARY,
    fontSize: 14,
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
});

export default SubscriptionScreen;