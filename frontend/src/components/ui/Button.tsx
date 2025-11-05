/**
 * Button Component
 * 
 * Reusable button component with variants, sizes, and loading states.
 */

import { forwardRef, ButtonHTMLAttributes } from 'react';
import { clsx } from 'clsx';

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  fullWidth?: boolean;
  leftIcon?: any;
  rightIcon?: any;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      fullWidth = false,
      leftIcon: LeftIcon,
      rightIcon: RightIcon,
      children,
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseClasses = [
      'inline-flex items-center justify-center font-medium rounded-md',
      'focus:outline-none focus:ring-2 focus:ring-offset-2',
      'transition-colors duration-200',
      'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
    ];

    const variantClasses = {
      primary: [
        'bg-primary-600 text-white',
        'hover:bg-primary-700',
        'focus:ring-primary-500',
        'active:bg-primary-800',
      ],
      secondary: [
        'bg-gray-200 text-gray-900',
        'hover:bg-gray-300',
        'focus:ring-gray-500',
        'active:bg-gray-400',
      ],
      danger: [
        'bg-red-600 text-white',
        'hover:bg-red-700',
        'focus:ring-red-500',
        'active:bg-red-800',
      ],
      ghost: [
        'text-gray-700',
        'hover:bg-gray-100',
        'focus:ring-gray-500',
        'active:bg-gray-200',
      ],
      outline: [
        'border border-gray-300 text-gray-700',
        'hover:bg-gray-50',
        'focus:ring-gray-500',
        'active:bg-gray-100',
      ],
    };

    const sizeClasses = {
      sm: ['px-3 py-1.5 text-xs'],
      md: ['px-4 py-2 text-sm'],
      lg: ['px-6 py-3 text-base'],
    };

    const classes = clsx(
      baseClasses,
      variantClasses[variant],
      sizeClasses[size],
      fullWidth && 'w-full',
      className
    );

    return (
      <button
        ref={ref}
        className={classes}
        disabled={disabled || loading}
        {...props}
      >
        {loading ? (
          <>
            <svg
              className={clsx(
                'animate-spin',
                size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4',
                children && 'mr-2'
              )}
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            {children && 'Loading...'}
          </>
        ) : (
          <>
            {LeftIcon && (
              <LeftIcon
                className={clsx(
                  size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4',
                  children && 'mr-2'
                )}
              />
            )}
            {children}
            {RightIcon && (
              <RightIcon
                className={clsx(
                  size === 'sm' ? 'w-3 h-3' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4',
                  children && 'ml-2'
                )}
              />
            )}
          </>
        )}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;