import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Synapse LaunchPad - AI-Powered Startup Matchmaking',
  description: 'AI-powered startup matchmaking platform that combines data-driven insights with behavioral science to accelerate your growth through strategic partnerships.',
  keywords: ['startup', 'AI', 'matchmaking', 'partnerships', 'behavioral science'],
  authors: [{ name: 'Synapse LaunchPad Team' }],
  openGraph: {
    title: 'Synapse LaunchPad - AI-Powered Startup Matchmaking',
    description: 'AI-powered startup matchmaking platform that combines data-driven insights with behavioral science to accelerate your growth through strategic partnerships.',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}