import PropTypes from 'prop-types';

/**
 * ErrorMessage Component
 *
 * Reusable error display component with:
 * - Icon, title, and message
 * - Optional retry button
 * - Configurable variants (error, warning, info)
 * - Proper ARIA roles for accessibility
 * - Keyboard accessible
 *
 * @param {Object} props
 * @param {string} props.title - Error title
 * @param {string} props.message - Error description
 * @param {Function} props.onRetry - Optional retry callback
 * @param {string} props.variant - 'error', 'warning', or 'info'
 * @param {string} props.icon - Optional custom icon (emoji or text)
 * @param {string} props.className - Additional CSS classes
 */
const ErrorMessage = ({
  title,
  message,
  onRetry = null,
  variant = 'error',
  icon = null,
  className = ''
}) => {
  // Variant configurations
  const variantConfig = {
    error: {
      icon: '❌',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800',
      buttonColor: 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
    },
    warning: {
      icon: '⚠️',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      buttonColor: 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500'
    },
    info: {
      icon: 'ℹ️',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      buttonColor: 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
    }
  };

  const config = variantConfig[variant] || variantConfig.error;
  const displayIcon = icon || config.icon;

  return (
    <div
      className={`
        ${config.bgColor} ${config.borderColor}
        border rounded-lg p-6 text-center
        ${className}
      `}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      {/* Icon */}
      {displayIcon && (
        <div className="text-5xl mb-3" aria-hidden="true">
          {displayIcon}
        </div>
      )}

      {/* Title */}
      {title && (
        <h3 className={`font-semibold text-lg mb-2 ${config.textColor}`}>
          {title}
        </h3>
      )}

      {/* Message */}
      {message && (
        <p className={`text-sm mb-4 ${config.textColor}`}>
          {message}
        </p>
      )}

      {/* Retry Button */}
      {onRetry && (
        <button
          onClick={onRetry}
          className={`
            px-4 py-2 rounded-lg text-white font-medium text-sm
            transition-colors duration-200
            focus:outline-none focus:ring-2 focus:ring-offset-2
            ${config.buttonColor}
          `}
          aria-label="Retry action"
        >
          🔄 Try Again
        </button>
      )}
    </div>
  );
};

ErrorMessage.propTypes = {
  title: PropTypes.string,
  message: PropTypes.string,
  onRetry: PropTypes.func,
  variant: PropTypes.oneOf(['error', 'warning', 'info']),
  icon: PropTypes.string,
  className: PropTypes.string
};

export default ErrorMessage;
