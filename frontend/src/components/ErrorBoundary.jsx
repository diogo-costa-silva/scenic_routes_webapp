import { Component } from 'react';
import PropTypes from 'prop-types';

/**
 * Error Boundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 *
 * Features:
 * - Catches errors during rendering, in lifecycle methods, and in constructors
 * - Logs errors to console (can be extended to error reporting service)
 * - Provides graceful fallback UI with reload option
 * - Prevents entire app from crashing due to component errors
 *
 * Note: Error boundaries do NOT catch errors in:
 * - Event handlers (use try-catch instead)
 * - Asynchronous code (e.g., setTimeout, promises)
 * - Server-side rendering
 * - Errors thrown in the error boundary itself
 *
 * Reference: https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary
 *
 * @example
 * <ErrorBoundary>
 *   <App />
 * </ErrorBoundary>
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  /**
   * Update state when an error is caught
   * This lifecycle method is called after an error is thrown by a descendant component
   */
  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error
    };
  }

  /**
   * Log error details when an error is caught
   * This lifecycle method is called after an error has been thrown by a descendant component
   *
   * @param {Error} error - The error that was thrown
   * @param {Object} errorInfo - Object with componentStack key containing information about component stack
   */
  componentDidCatch(error, errorInfo) {
    // Log error details to console
    console.error('🚨 Error caught by Error Boundary:', error);
    console.error('📍 Component stack trace:', errorInfo.componentStack);

    // Store error info in state for display
    this.setState({
      errorInfo
    });

    // TODO: Send error to error reporting service (e.g., Sentry, LogRocket)
    // Example:
    // errorReportingService.logError(error, errorInfo);
  }

  /**
   * Handle reload button click
   */
  handleReload = () => {
    // Reset error state
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });

    // Reload the page
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Render fallback UI
      return (
        <div
          className="min-h-screen flex items-center justify-center bg-red-50 p-6"
          role="alert"
          aria-live="assertive"
        >
          <div className="max-w-2xl w-full bg-white rounded-lg shadow-xl p-8">
            {/* Error Icon */}
            <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full">
              <span className="text-4xl" role="img" aria-label="Error">
                ⚠️
              </span>
            </div>

            {/* Error Title */}
            <h1 className="text-2xl font-bold text-red-600 text-center mb-4">
              Oops! Something went wrong
            </h1>

            {/* Error Message */}
            <p className="text-gray-700 text-center mb-6">
              The application encountered an unexpected error and needs to reload.
              Your progress has been saved where possible.
            </p>

            {/* Error Details (Development Only) */}
            {import.meta.env.MODE === 'development' && this.state.error && (
              <details className="mb-6 p-4 bg-gray-50 rounded-lg text-left">
                <summary className="cursor-pointer font-semibold text-gray-800 mb-2">
                  🔍 Error Details (Development Only)
                </summary>
                <div className="mt-2">
                  <p className="text-sm font-mono text-red-600 mb-2">
                    <strong>Error:</strong> {this.state.error.toString()}
                  </p>
                  {this.state.errorInfo && (
                    <div className="text-xs font-mono text-gray-600 overflow-auto max-h-48">
                      <strong>Component Stack:</strong>
                      <pre className="mt-1 whitespace-pre-wrap">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </div>
                  )}
                </div>
              </details>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={this.handleReload}
                className="px-6 py-3 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 active:bg-primary/80 transition-colors duration-200"
                type="button"
              >
                🔄 Reload Application
              </button>

              <a
                href="/"
                className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg font-medium hover:bg-gray-300 active:bg-gray-400 transition-colors duration-200 text-center"
              >
                🏠 Go to Homepage
              </a>
            </div>

            {/* Help Text */}
            <p className="text-xs text-gray-500 text-center mt-6">
              If this problem persists, please contact support or check the browser console (F12) for more details.
            </p>
          </div>
        </div>
      );
    }

    // No error, render children normally
    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired
};

export default ErrorBoundary;
