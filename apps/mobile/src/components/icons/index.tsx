import React from 'react';
import Svg, { Path, Circle, Rect, Line } from 'react-native-svg';

interface IconProps {
  width?: number;
  height?: number;
  color?: string;
  fill?: string;
  strokeWidth?: number;
}

export const Zap: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
  </Svg>
);

export const Building: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Rect x="4" y="2" width="16" height="20" rx="2" ry="2" />
    <Line x1="9" y1="22" x2="9" y2="16" />
    <Line x1="15" y1="22" x2="15" y2="16" />
    <Path d="M8 6h.01" />
    <Path d="M16 6h.01" />
    <Path d="M12 6h.01" />
    <Path d="M8 10h.01" />
    <Path d="M16 10h.01" />
    <Path d="M12 10h.01" />
    <Path d="M8 14h.01" />
    <Path d="M16 14h.01" />
    <Path d="M12 14h.01" />
  </Svg>
);

export const TrendingUp: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M23 6l-9.5 9.5-5-5L1 18" />
    <Path d="M17 6h6v6" />
  </Svg>
);

export const MapPin: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
    <Circle cx="12" cy="10" r="3" />
  </Svg>
);

export const Star: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
  </Svg>
);

export const Crown: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M2 4l3 12h14l3-12-6 7-4-7-4 7-6-7zm3 16h14" />
  </Svg>
);

export const Mail: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
    <Path d="M22 6l-10 7L2 6" />
  </Svg>
);

export const Share2: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Circle cx="18" cy="5" r="3" />
    <Circle cx="6" cy="12" r="3" />
    <Circle cx="18" cy="19" r="3" />
    <Line x1="8.59" y1="13.51" x2="15.42" y2="17.49" />
    <Line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
  </Svg>
);

export const ExternalLink: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
    <Path d="M15 3h6v6" />
    <Path d="M10 14L21 3" />
  </Svg>
);

export const Target: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Circle cx="12" cy="12" r="10" />
    <Circle cx="12" cy="12" r="6" />
    <Circle cx="12" cy="12" r="2" />
  </Svg>
);

export const Users: React.FC<IconProps> = ({
  width = 24,
  height = 24,
  color = 'currentColor',
  fill = 'none',
  strokeWidth = 2,
}) => (
  <Svg width={width} height={height} viewBox="0 0 24 24" fill={fill} stroke={color} strokeWidth={strokeWidth} strokeLinecap="round" strokeLinejoin="round">
    <Path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
    <Circle cx="9" cy="7" r="4" />
    <Path d="M23 21v-2a4 4 0 0 0-3-3.87" />
    <Path d="M16 3.13a4 4 0 0 1 0 7.75" />
  </Svg>
);