import { useState } from 'react';
import PropTypes from 'prop-types';
import MetricsPanel from './MetricsPanel';
import ActionButtons from './ActionButtons';

/**
 * RoadDetails Component
 *
 * Comprehensive details panel for selected road with responsive behavior:
 * - Desktop (≥768px): Fixed right panel (400px width, full height)
 * - Mobile (<768px): Bottom sheet overlay (collapsed/expanded states)
 *
 * Features:
 * - Smooth slide-in/out animations
 * - Close button to deselect road
 * - Scrollable content area
 * - Sticky header and footer
 *
 * @param {Object} props
 * @param {Object|null} props.selectedRoad - Currently selected road object
 * @param {Function} props.onClose - Callback to clear road selection
 */
const RoadDetails = ({ selectedRoad, onClose }) => {
  // Mobile bottom sheet state (collapsed vs expanded)
  const [isExpanded, setIsExpanded] = useState(false);

  // Don't render if no road is selected
  if (!selectedRoad) {
    return null;
  }

  // Toggle expand/collapse on mobile
  const handleToggleExpand = () => {
    setIsExpanded(!isExpanded);
  };

  // Close and reset expansion state
  const handleClose = () => {
    setIsExpanded(false);
    onClose();
  };

  return (
    <>
      {/* Mobile: Backdrop overlay (only when expanded) */}
      <div
        className={`
          fixed inset-0 bg-black/30 z-40 md:hidden
          transition-opacity duration-300
          ${isExpanded ? 'opacity-100' : 'opacity-0 pointer-events-none'}
        `}
        onClick={handleClose}
        onKeyDown={(e) => {
          if (e.key === 'Escape') {
            handleClose();
          }
        }}
        role="button"
        tabIndex={isExpanded ? 0 : -1}
        aria-label="Close details panel"
      />

      {/* Details Panel */}
      <aside
        className={`
          fixed bg-white shadow-2xl z-50
          flex flex-col
          transition-all duration-300 ease-in-out

          /* Desktop: Right panel (always visible when selectedRoad exists) */
          md:right-0 md:top-0 md:h-screen md:w-[400px]
          md:translate-y-0

          /* Mobile: Bottom sheet */
          bottom-0 left-0 right-0 rounded-t-2xl
          ${isExpanded
            ? 'max-h-[85vh]'
            : 'h-[80px]'
          }
        `}
        role="complementary"
        aria-label="Road details"
        aria-expanded={isExpanded}
      >
        {/* Header - Always visible */}
        <div
          className={`
            flex-shrink-0 px-4 py-3 border-b border-gray-200 bg-white
            ${isExpanded ? '' : 'rounded-t-2xl'}
            md:cursor-default cursor-pointer
          `}
          onClick={handleToggleExpand}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0 mr-3">
              {/* Road Code */}
              <h2 className="text-xl font-bold text-primary truncate">
                {selectedRoad.code}
              </h2>

              {/* Road Name */}
              <p className="text-sm text-gray-600 line-clamp-2 mt-1">
                {selectedRoad.name}
              </p>
            </div>

            {/* Close Button */}
            <button
              onClick={(e) => {
                e.stopPropagation(); // Prevent triggering expand on mobile
                handleClose();
              }}
              className="
                flex-shrink-0 min-w-[44px] min-h-[44px] rounded-full
                flex items-center justify-center
                text-gray-500 hover:text-danger hover:bg-red-50
                transition-colors duration-200
              "
              aria-label={`Close ${selectedRoad.code} details`}
              title="Close"
            >
              <span className="text-xl leading-none" aria-hidden="true">×</span>
            </button>
          </div>

          {/* Mobile: Expand indicator (only when collapsed) */}
          <div className={`
            md:hidden mt-2 flex justify-center
            ${isExpanded ? 'hidden' : 'block'}
          `}>
            <div className="w-12 h-1 bg-gray-300 rounded-full" />
          </div>
        </div>

        {/* Content - Scrollable (hidden when collapsed on mobile) */}
        <div
          className={`
            flex-1 overflow-y-auto p-4
            ${isExpanded ? 'block' : 'hidden md:block'}
          `}
        >
          <MetricsPanel road={selectedRoad} />
        </div>

        {/* Footer - Action Buttons (hidden when collapsed on mobile) */}
        <div
          className={`
            flex-shrink-0
            ${isExpanded ? 'block' : 'hidden md:block'}
          `}
        >
          <ActionButtons road={selectedRoad} />
        </div>
      </aside>
    </>
  );
};

RoadDetails.propTypes = {
  selectedRoad: PropTypes.shape({
    id: PropTypes.number.isRequired,
    code: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    region: PropTypes.string,
    distance_km: PropTypes.number,
    elevation_max: PropTypes.number,
    elevation_min: PropTypes.number,
    elevation_gain: PropTypes.number,
    elevation_loss: PropTypes.number,
    curve_count_total: PropTypes.number,
    curve_count_gentle: PropTypes.number,
    curve_count_moderate: PropTypes.number,
    curve_count_sharp: PropTypes.number,
    straight_count: PropTypes.number,
    longest_straight_km: PropTypes.number,
    surface: PropTypes.string,
    surface_verified: PropTypes.bool,
    start_point_name: PropTypes.string,
    end_point_name: PropTypes.string,
  }),
  onClose: PropTypes.func.isRequired,
};

export default RoadDetails;
