import { useState } from 'react';
import PropTypes from 'prop-types';
import { generateGPX, downloadGPX } from '../../utils/gpxExport';
import { generateRouteUrl, openInNewTab } from '../../utils/mapLinks';

/**
 * ActionButtons Component
 *
 * Displays action buttons for the selected road:
 * - Export GPX: Download route as GPX file for GPS devices (with elevation data)
 * - Open in Google Maps: Open route in Google Maps for navigation
 *
 * Features:
 * - Loading states during operations
 * - Success/error feedback messages
 * - Disabled state when no road selected
 * - Responsive design (mobile-friendly)
 *
 * @param {Object} props
 * @param {Object} props.road - Road object with geometry, code, name, distance_km, curve_count_total
 */
const ActionButtons = ({ road }) => {
  // UI state
  const [isExportingGPX, setIsExportingGPX] = useState(false);
  const [isOpeningMaps, setIsOpeningMaps] = useState(false);
  const [feedback, setFeedback] = useState(null); // { type: 'success'|'error', message: string }

  /**
   * Show feedback message temporarily
   * @param {string} type - 'success' or 'error'
   * @param {string} message - Message to display
   */
  const showFeedback = (type, message) => {
    setFeedback({ type, message });

    // Auto-hide after 3 seconds
    setTimeout(() => {
      setFeedback(null);
    }, 3000);
  };

  /**
   * Export road geometry as GPX file
   * Uses gpxExport utility to generate valid GPX 1.1 XML with elevation data
   */
  const handleExportGPX = async () => {
    if (!road || !road.geometry) {
      showFeedback('error', 'Road data is missing');
      return;
    }

    setIsExportingGPX(true);

    try {
      // Generate GPX using utility
      const result = generateGPX(road);

      if (!result.success) {
        showFeedback('error', result.error || 'Failed to generate GPX');
        return;
      }

      // Trigger download
      const downloadSuccess = downloadGPX(result.blob, result.filename);

      if (downloadSuccess) {
        showFeedback('success', `GPX file downloaded: ${result.filename}`);
      } else {
        showFeedback('error', 'Failed to download GPX file');
      }
    } catch (error) {
      console.error('Error exporting GPX:', error);
      showFeedback('error', 'An unexpected error occurred');
    } finally {
      setIsExportingGPX(false);
    }
  };

  /**
   * Open road location in Google Maps
   * Uses mapLinks utility to generate proper Google Maps URL
   */
  const handleOpenMaps = async () => {
    if (!road || !road.start_lat || !road.start_lon) {
      showFeedback('error', 'Road coordinates are missing');
      return;
    }

    setIsOpeningMaps(true);

    try {
      // Generate Google Maps URL using utility
      const result = generateRouteUrl(road);

      if (!result.success) {
        showFeedback('error', result.error || 'Failed to generate maps link');
        return;
      }

      // Open in new tab
      const openSuccess = openInNewTab(result.url);

      if (openSuccess) {
        showFeedback('success', 'Opened in Google Maps');
      } else {
        showFeedback('error', 'Please allow popups to open Google Maps');
      }
    } catch (error) {
      console.error('Error opening Google Maps:', error);
      showFeedback('error', 'An unexpected error occurred');
    } finally {
      // Reset loading state after a short delay
      setTimeout(() => {
        setIsOpeningMaps(false);
      }, 500);
    }
  };

  return (
    <div className="flex flex-col gap-2 p-4 border-t border-gray-200 bg-white">
      {/* Feedback Message */}
      {feedback && (
        <div
          className={`
            px-3 py-2 rounded-md text-sm font-medium
            flex items-center gap-2
            transition-all duration-300
            ${feedback.type === 'success'
              ? 'bg-green-50 text-green-700 border border-green-200'
              : 'bg-red-50 text-red-700 border border-red-200'
            }
          `}
          role="alert"
        >
          <span className="text-base">
            {feedback.type === 'success' ? '✓' : '⚠'}
          </span>
          <span>{feedback.message}</span>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-2">
        {/* Export GPX Button */}
        <button
          onClick={handleExportGPX}
          disabled={!road || isExportingGPX}
          title="Download GPX file for GPS devices"
          className={`
            flex-1 px-4 py-2.5 rounded-md font-medium text-sm
            flex items-center justify-center gap-2
            transition-all duration-200
            ${!road || isExportingGPX
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-primary/90 active:bg-primary/80 cursor-pointer'
            }
          `}
        >
          {isExportingGPX ? (
            <>
              <span className="animate-spin text-base">⏳</span>
              <span>Exporting...</span>
            </>
          ) : (
            <>
              <span className="text-base">📥</span>
              <span>Export GPX</span>
            </>
          )}
        </button>

        {/* Open in Google Maps Button */}
        <button
          onClick={handleOpenMaps}
          disabled={!road || isOpeningMaps}
          title="Open route in Google Maps"
          className={`
            flex-1 px-4 py-2.5 rounded-md font-medium text-sm
            flex items-center justify-center gap-2
            transition-all duration-200
            ${!road || isOpeningMaps
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-secondary text-white hover:bg-secondary/90 active:bg-secondary/80 cursor-pointer'
            }
          `}
        >
          {isOpeningMaps ? (
            <>
              <span className="animate-spin text-base">⏳</span>
              <span>Opening...</span>
            </>
          ) : (
            <>
              <span className="text-base">🗺️</span>
              <span>Google Maps</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
};

ActionButtons.propTypes = {
  road: PropTypes.object,
};

export default ActionButtons;
