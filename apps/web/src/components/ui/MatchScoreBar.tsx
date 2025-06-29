import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface MatchScoreBarProps {
  score: number; // 0-100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

export function MatchScoreBar({ 
  score, 
  size = 'md', 
  showLabel = false, 
  className 
}: MatchScoreBarProps) {
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-yellow-500';
    if (score >= 70) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const getScoreGradient = (score: number) => {
    if (score >= 90) return 'from-green-500 to-green-400';
    if (score >= 80) return 'from-yellow-500 to-yellow-400';
    if (score >= 70) return 'from-orange-500 to-orange-400';
    return 'from-red-500 to-red-400';
  };

  const sizeClasses = {
    sm: 'h-2',
    md: 'h-3',
    lg: 'h-4',
  };

  return (
    <div className={clsx('w-full', className)}>
      <div className={clsx(
        'relative bg-white/10 rounded-full overflow-hidden',
        sizeClasses[size]
      )}>
        <motion.div
          className={clsx(
            'h-full rounded-full bg-gradient-to-r',
            getScoreGradient(score)
          )}
          initial={{ width: 0 }}
          animate={{ width: `${Math.min(100, Math.max(0, score))}%` }}
          transition={{ duration: 1, ease: 'easeOut' }}
        />
        
        {/* Glow effect for high scores */}
        {score >= 90 && (
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-green-500/50 to-green-400/50 rounded-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0, 0.5, 0] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}
      </div>
      
      {showLabel && (
        <div className="flex justify-between mt-1 text-xs text-white/60">
          <span>0%</span>
          <span className={clsx(
            'font-medium',
            score >= 90 ? 'text-green-400' : 
            score >= 80 ? 'text-yellow-400' : 
            score >= 70 ? 'text-orange-400' : 'text-red-400'
          )}>
            {score.toFixed(1)}%
          </span>
          <span>100%</span>
        </div>
      )}
    </div>
  );
}