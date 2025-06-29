import React from 'react';
import { View, StyleSheet } from 'react-native';
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withTiming,
  Easing,
} from 'react-native-reanimated';
import { THEME } from '../config';

interface MatchScoreBarProps {
  score: number; // 0-100
  height?: number;
  backgroundColor?: string;
  animated?: boolean;
}

export const MatchScoreBar: React.FC<MatchScoreBarProps> = ({
  score,
  height = 6,
  backgroundColor = '#1E293B',
  animated = true,
}) => {
  const progress = useSharedValue(0);

  React.useEffect(() => {
    if (animated) {
      progress.value = withTiming(score / 100, {
        duration: 1000,
        easing: Easing.bezier(0.25, 0.1, 0.25, 1),
      });
    } else {
      progress.value = score / 100;
    }
  }, [score, animated, progress]);

  const getScoreColor = (score: number) => {
    if (score >= 90) return '#10B981'; // green
    if (score >= 80) return '#FBBF24'; // yellow
    if (score >= 70) return '#F97316'; // orange
    return '#EF4444'; // red
  };

  const progressStyle = useAnimatedStyle(() => {
    return {
      width: `${progress.value * 100}%`,
      backgroundColor: getScoreColor(score),
    };
  });

  return (
    <View
      style={[
        styles.container,
        {
          height,
          backgroundColor,
        },
      ]}
    >
      <Animated.View
        style={[
          styles.progress,
          {
            height,
          },
          progressStyle,
        ]}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    width: '100%',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progress: {
    borderRadius: 4,
  },
});