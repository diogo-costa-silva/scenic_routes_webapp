import PropTypes from 'prop-types';

/**
 * ActionButtons Component
 *
 * Displays action buttons for the selected road:
 * - Export GPX: Download route as GPX file for GPS devices
 * - Open in Google Maps: Open route in Google Maps for navigation
 *
 * NOTE: For this session, buttons are UI-only (disabled with "Coming soon" tooltip).
 * Functionality will be implemented in the next session.
 *
 * @param {Object} props
 * @param {Function} props.onExportGPX - Callback for GPX export (optional)
 * @param {Function} props.onOpenMaps - Callback for opening in Google Maps (optional)
 * @param {Object} props.road - Road object (for future functionality)
 */
const ActionButtons = ({ onExportGPX, onOpenMaps, road }) => {
  // For this session, buttons are disabled
  // TODO: Next session - implement actual functionality
  const isDisabled = true;

  const handleExportGPX = () => {
    if (!isDisabled && onExportGPX) {
      onExportGPX(road);
    }
  };

  const handleOpenMaps = () => {
    if (!isDisabled && onOpenMaps) {
      onOpenMaps(road);
    }
  };

  return (
    <div className="flex flex-col sm:flex-row gap-2 p-4 border-t border-gray-200 bg-white">
      {/* Export GPX Button */}
      <button
        onClick={handleExportGPX}
        disabled={isDisabled}
        title={isDisabled ? 'Coming soon' : 'Download GPX file'}
        className={`
          flex-1 px-4 py-2.5 rounded-md font-medium text-sm
          flex items-center justify-center gap-2
          transition-all duration-200
          ${isDisabled
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : 'bg-primary text-white hover:bg-primary/90 active:bg-primary/80 cursor-pointer'
          }
        `}
      >
        <span className="text-base">📥</span>
        <span>Export GPX</span>
      </button>

      {/* Open in Google Maps Button */}
      <button
        onClick={handleOpenMaps}
        disabled={isDisabled}
        title={isDisabled ? 'Coming soon' : 'Open in Google Maps'}
        className={`
          flex-1 px-4 py-2.5 rounded-md font-medium text-sm
          flex items-center justify-center gap-2
          transition-all duration-200
          ${isDisabled
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : 'bg-secondary text-white hover:bg-secondary/90 active:bg-secondary/80 cursor-pointer'
          }
        `}
      >
        <span className="text-base">🗺️</span>
        <span>Google Maps</span>
      </button>
    </div>
  );
};

ActionButtons.propTypes = {
  onExportGPX: PropTypes.func,
  onOpenMaps: PropTypes.func,
  road: PropTypes.object,
};

export default ActionButtons;
