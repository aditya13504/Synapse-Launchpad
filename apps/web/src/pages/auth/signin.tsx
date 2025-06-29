import { useState } from 'react';
import { signIn, getProviders } from 'next-auth/react';
import { GetServerSideProps } from 'next';
import { motion } from 'framer-motion';
import { Github, Mail, Chrome, ArrowRight, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface Provider {
  id: string;
  name: string;
  type: string;
  signinUrl: string;
  callbackUrl: string;
}

interface SignInPageProps {
  providers: Record<string, Provider>;
}

export default function SignInPage({ providers }: SignInPageProps) {
  const [isLoading, setIsLoading] = useState<string | null>(null);

  const handleSignIn = async (providerId: string) => {
    setIsLoading(providerId);
    try {
      await signIn(providerId, { callbackUrl: '/wizard' });
    } catch (error) {
      console.error('Sign in error:', error);
    } finally {
      setIsLoading(null);
    }
  };

  const getProviderIcon = (providerId: string) => {
    switch (providerId) {
      case 'google':
        return Chrome;
      case 'github':
        return Github;
      case 'email':
        return Mail;
      default:
        return Mail;
    }
  };

  const getProviderColor = (providerId: string) => {
    switch (providerId) {
      case 'google':
        return 'from-red-500 to-yellow-500';
      case 'github':
        return 'from-gray-700 to-gray-900';
      case 'email':
        return 'from-blue-500 to-purple-600';
      default:
        return 'from-blue-500 to-purple-600';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-purple-900 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-6"
          >
            <Zap className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-3xl font-bold text-white mb-2">Welcome to Synapse</h1>
          <p className="text-blue-200">Sign in to start finding perfect partners</p>
        </div>

        <Card className="p-8">
          <div className="space-y-4">
            {Object.values(providers).map((provider, index) => {
              const Icon = getProviderIcon(provider.id);
              const isProviderLoading = isLoading === provider.id;

              return (
                <motion.div
                  key={provider.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                >
                  <Button
                    onClick={() => handleSignIn(provider.id)}
                    loading={isProviderLoading}
                    className={`w-full bg-gradient-to-r ${getProviderColor(provider.id)} hover:scale-105`}
                    size="lg"
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    Continue with {provider.name}
                    <ArrowRight className="w-4 h-4 ml-auto" />
                  </Button>
                </motion.div>
              );
            })}
          </div>

          <div className="mt-8 text-center">
            <p className="text-white/60 text-sm">
              By signing in, you agree to our{' '}
              <a href="/terms" className="text-blue-400 hover:text-blue-300">
                Terms of Service
              </a>{' '}
              and{' '}
              <a href="/privacy" className="text-blue-400 hover:text-blue-300">
                Privacy Policy
              </a>
            </p>
          </div>
        </Card>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="mt-8 text-center"
        >
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-white">500+</div>
              <div className="text-white/60 text-sm">Partnerships</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">96%</div>
              <div className="text-white/60 text-sm">Match Accuracy</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-white">3.2x</div>
              <div className="text-white/60 text-sm">ROI Increase</div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}

export const getServerSideProps: GetServerSideProps = async () => {
  const providers = await getProviders();
  
  return {
    props: {
      providers: providers ?? {},
    },
  };
};