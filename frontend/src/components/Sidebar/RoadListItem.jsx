import PropTypes from 'prop-types';

/**
 * RoadListItem Component
 *
 * Displays a single road in the sidebar list with:
 * - Road code (bold, orange)
 * - Road name
 * - Distance badge
 * - Curve count and max elevation badges
 * - Hover and selected states
 *
 * @param {Object} props
 * @param {Object} props.road - Road data object
 * @param {boolean} props.isSelected - Whether this road is currently selected
 * @param {Function} props.onClick - Click handler when road is selected
 */
const RoadListItem = ({ road, isSelected = false, onClick }) => {
  const handleClick = () => {
    if (onClick) {
      onClick(road);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleClick();
    }
  };

  // Region color mapping
  const getRegionColor = (region) => {
    switch (region) {
      case 'Continental':
        return 'bg-region-continental';
      case 'Madeira':
        return 'bg-region-madeira';
      case 'Açores':
        return 'bg-region-acores';
      default:
        return 'bg-gray-500';
    }
  };

  const regionColorClass = getRegionColor(road.region);

  return (
    <div
      className={`
        p-4 cursor-pointer transition-colors duration-150
        hover:bg-gray-50 active:bg-gray-100
        border-l-4
        ${isSelected
          ? `${regionColorClass.replace('bg-', 'border-')} bg-orange-50`
          : 'border-transparent'
        }
      `}
      onClick={handleClick}
      onKeyPress={handleKeyPress}
      role="button"
      tabIndex={0}
      aria-label={`Select ${road.code} - ${road.name}`}
      aria-pressed={isSelected}
    >
      {/* Road Code and Name */}
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-bold text-lg text-primary truncate">
            {road.code}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2">
            {road.name}
          </p>
        </div>

        {/* Distance */}
        <div className="ml-3 flex-shrink-0">
          <span className="text-sm font-medium text-gray-700">
            {road.distance_km ? `${road.distance_km}km` : 'N/A'}
          </span>
        </div>
      </div>

      {/* Badges */}
      <div className="flex gap-2 flex-wrap" role="list" aria-label="Road metrics">
        {/* Curve count badge */}
        {road.curve_count_total !== null && road.curve_count_total !== undefined && (
          <span className="inline-flex items-center px-2 py-1 rounded-md bg-blue-50 text-blue-700 text-xs font-medium" role="listitem">
            <span aria-hidden="true">🌀 </span>
            <span>{road.curve_count_total} curves</span>
          </span>
        )}

        {/* Max elevation badge */}
        {road.elevation_max !== null && road.elevation_max !== undefined && (
          <span className="inline-flex items-center px-2 py-1 rounded-md bg-green-50 text-green-700 text-xs font-medium" role="listitem">
            <span aria-hidden="true">⛰️ </span>
            <span>{road.elevation_max}m elevation</span>
          </span>
        )}

        {/* Region badge (small) */}
        <span
          className={`inline-flex items-center px-2 py-1 rounded-md text-white text-xs font-medium ${regionColorClass}`}
          role="listitem"
        >
          {road.region}
        </span>
      </div>
    </div>
  );
};

RoadListItem.propTypes = {
  road: PropTypes.shape({
    id: PropTypes.number.isRequired,
    code: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    region: PropTypes.string.isRequired,
    distance_km: PropTypes.number,
    curve_count_total: PropTypes.number,
    elevation_max: PropTypes.number,
  }).isRequired,
  isSelected: PropTypes.bool,
  onClick: PropTypes.func
};

export default RoadListItem;
