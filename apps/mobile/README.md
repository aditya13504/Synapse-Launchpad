# Synapse LaunchPad Mobile App

This is the mobile app for Synapse LaunchPad, built with Expo and React Native. It shares components and logic with the web app through the Turborepo monorepo structure.

## 🚀 Features

- **Login/Authentication**: Secure login with JWT token storage
- **Partner Recommendations**: View AI-powered partner recommendations
- **Campaign Preview**: Preview and generate marketing campaigns
- **Deep Linking**: Seamless navigation between web and mobile
- **In-App Purchases**: RevenueCat integration for subscription management

## 🛠️ Tech Stack

- **Expo**: React Native framework for cross-platform development
- **React Navigation**: Navigation library for React Native
- **RevenueCat**: In-app purchase and subscription management
- **React Query**: Data fetching and caching
- **Zustand**: State management
- **Reanimated**: Animations library

## 🏗️ Project Structure

```
apps/mobile/
├── assets/              # Images, fonts, and other static assets
├── src/
│   ├── components/      # Reusable UI components
│   ├── context/         # React context providers
│   ├── hooks/           # Custom React hooks
│   ├── screens/         # Screen components
│   ├── services/        # API services
│   ├── store/           # Zustand state stores
│   └── utils/           # Utility functions
├── App.tsx              # Main app component
├── app.json             # Expo configuration
├── eas.json             # EAS Build configuration
└── package.json         # Dependencies and scripts
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- pnpm 8+
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator or Android Emulator (optional)

### Installation

```bash
# Install dependencies from the root of the monorepo
pnpm install

# Start the development server
pnpm --filter @synapse/mobile dev
```

### Running on Devices

```bash
# iOS
pnpm --filter @synapse/mobile ios

# Android
pnpm --filter @synapse/mobile android
```

## 📱 Deep Linking

The app supports deep linking for seamless navigation between web and mobile:

- `synapselaunchpad://login` - Opens the login screen
- `synapselaunchpad://recommendations` - Opens the recommendations list
- `synapselaunchpad://campaign/:id` - Opens a specific campaign

### Testing Deep Links

```bash
# iOS Simulator
xcrun simctl openurl booted "synapselaunchpad://recommendations"

# Android Emulator
adb shell am start -a android.intent.action.VIEW -d "synapselaunchpad://recommendations"
```

## 💰 RevenueCat Integration

The app uses RevenueCat for in-app purchases and subscription management:

1. **Subscription Tiers**:
   - Starter: Basic features with limited recommendations
   - Pro: Unlimited recommendations and advanced features
   - Enterprise: Custom features and dedicated support

2. **Upgrade Flow**:
   - Users can upgrade from Starter to Pro within the app
   - Subscription status syncs between web and mobile

3. **Configuration**:
   - RevenueCat API keys are stored in environment variables
   - Products are configured in the RevenueCat dashboard

## 🔄 Shared Components

The app shares components with the web app through the Turborepo monorepo structure:

- **Shared Types**: Common TypeScript interfaces in `packages/shared`
- **Business Logic**: Shared hooks and utilities
- **Design System**: Consistent styling and components

## 📦 Building for Production

```bash
# Build for iOS and Android
pnpm --filter @synapse/mobile build

# Build for specific platform
pnpm --filter @synapse/mobile build:ios
pnpm --filter @synapse/mobile build:android

# Submit to app stores
pnpm --filter @synapse/mobile submit
```

## 🧪 Testing

```bash
# Run tests
pnpm --filter @synapse/mobile test

# Run linting
pnpm --filter @synapse/mobile lint
```

## 📝 Environment Variables

Create a `.env` file in the `apps/mobile` directory with the following variables:

```
EXPO_PUBLIC_API_URL=https://api.synapse-launchpad.com
EXPO_PUBLIC_REVENUECAT_API_KEY_IOS=your_ios_key
EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID=your_android_key
```

## 🔗 Useful Links

- [Expo Documentation](https://docs.expo.dev/)
- [React Native Documentation](https://reactnative.dev/docs/getting-started)
- [RevenueCat Documentation](https://docs.revenuecat.com/)
- [EAS Build Documentation](https://docs.expo.dev/build/introduction/)