import PropTypes from 'prop-types';

/**
 * Loader Component
 *
 * Reusable loading indicator with multiple variants:
 * - spinner: Animated circular spinner (default)
 * - skeleton: Content placeholder blocks
 *
 * Sizes: sm, md (default), lg
 *
 * Features:
 * - ARIA live region for screen readers
 * - Optional text label
 * - Configurable styling
 *
 * @param {Object} props
 * @param {string} props.variant - 'spinner' or 'skeleton'
 * @param {string} props.size - 'sm', 'md', or 'lg'
 * @param {string} props.text - Optional loading text
 * @param {string} props.className - Additional CSS classes
 */
const Loader = ({
  variant = 'spinner',
  size = 'md',
  text = '',
  className = ''
}) => {
  // Size configurations
  const sizeMap = {
    spinner: {
      sm: 'h-4 w-4 border-2',
      md: 'h-8 w-8 border-2',
      lg: 'h-12 w-12 border-4'
    },
    skeleton: {
      sm: 'h-4',
      md: 'h-6',
      lg: 'h-8'
    }
  };

  const textSizeMap = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base'
  };

  if (variant === 'spinner') {
    return (
      <div
        className={`flex flex-col items-center justify-center ${className}`}
        role="status"
        aria-live="polite"
        aria-busy="true"
      >
        {/* Spinner */}
        <div
          className={`
            animate-spin rounded-full border-b-primary border-t-transparent
            ${sizeMap.spinner[size]}
          `}
          aria-hidden="true"
        />

        {/* Loading text */}
        {text && (
          <p className={`mt-3 text-gray-600 ${textSizeMap[size]}`}>
            {text}
          </p>
        )}

        {/* Screen reader text */}
        <span className="sr-only">
          {text || 'Loading'}
        </span>
      </div>
    );
  }

  if (variant === 'skeleton') {
    return (
      <div
        className={`space-y-3 ${className}`}
        role="status"
        aria-live="polite"
        aria-busy="true"
      >
        {/* Skeleton lines */}
        <div className={`animate-pulse bg-gray-200 rounded ${sizeMap.skeleton[size]} w-full`} />
        <div className={`animate-pulse bg-gray-200 rounded ${sizeMap.skeleton[size]} w-5/6`} />
        <div className={`animate-pulse bg-gray-200 rounded ${sizeMap.skeleton[size]} w-4/6`} />

        {/* Screen reader text */}
        <span className="sr-only">
          {text || 'Loading content'}
        </span>
      </div>
    );
  }

  return null;
};

Loader.propTypes = {
  variant: PropTypes.oneOf(['spinner', 'skeleton']),
  size: PropTypes.oneOf(['sm', 'md', 'lg']),
  text: PropTypes.string,
  className: PropTypes.string
};

export default Loader;
