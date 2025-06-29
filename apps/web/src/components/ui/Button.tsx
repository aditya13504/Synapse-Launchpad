import { forwardRef } from 'react';
import { motion, HTMLMotionProps } from 'framer-motion';
import { clsx } from 'clsx';
import { Loader2 } from 'lucide-react';

interface ButtonProps extends Omit<HTMLMotionProps<'button'>, 'onAnimationStart'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  children: React.ReactNode;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, disabled, children, ...props }, ref) => {
    const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent';
    
    const variants = {
      primary: 'bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white shadow-lg hover:shadow-xl focus:ring-blue-500',
      secondary: 'bg-white/10 backdrop-blur-sm hover:bg-white/20 text-white border border-white/30 hover:border-white/50 focus:ring-white/50',
      outline: 'border-2 border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white focus:ring-blue-500',
      ghost: 'text-white hover:bg-white/10 focus:ring-white/50',
    };

    const sizes = {
      sm: 'px-3 py-2 text-sm',
      md: 'px-4 py-2.5 text-base',
      lg: 'px-6 py-3 text-lg',
    };

    return (
      <motion.button
        ref={ref}
        className={clsx(
          baseClasses,
          variants[variant],
          sizes[size],
          {
            'opacity-50 cursor-not-allowed': disabled || loading,
            'transform hover:scale-105': !disabled && !loading,
          },
          className
        )}
        disabled={disabled || loading}
        whileHover={!disabled && !loading ? { scale: 1.05 } : {}}
        whileTap={!disabled && !loading ? { scale: 0.95 } : {}}
        {...props}
      >
        {loading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
        {children}
      </motion.button>
    );
  }
);

Button.displayName = 'Button';