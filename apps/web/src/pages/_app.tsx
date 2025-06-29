import { AppProps } from 'next/app';
import { useEffect } from 'react';
import { initAnalytics } from '@/lib/analytics';

function MyApp({ Component, pageProps }: AppProps) {
  // Initialize analytics on app load
  useEffect(() => {
    initAnalytics();
  }, []);

  return <Component {...pageProps} />;
}

export default MyApp;