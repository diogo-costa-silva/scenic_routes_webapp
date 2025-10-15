import PropTypes from 'prop-types';

/**
 * MetricRow Component
 *
 * Reusable component for displaying a single metric in a consistent format.
 * Used throughout the details panel to show road statistics.
 *
 * Layout: [icon] Label                Value
 *
 * @param {Object} props
 * @param {string|React.ReactNode} props.icon - Icon to display (emoji or React element)
 * @param {string} props.label - Label for the metric (e.g., "Distância", "Altitude Máxima")
 * @param {string|number} props.value - Value to display (e.g., "27.3 km", "523m")
 * @param {boolean} props.optional - If true and value is null/N/A, component won't render
 */
const MetricRow = ({ icon, label, value, optional = false }) => {
  // Don't render if optional and value is missing
  if (optional && (value === null || value === undefined || value === 'N/A')) {
    return null;
  }

  return (
    <div className="flex items-center justify-between py-2 px-1 hover:bg-gray-50 rounded transition-colors">
      {/* Icon and Label */}
      <div className="flex items-center gap-3 flex-1">
        {icon && (
          <span className="text-lg flex-shrink-0" aria-hidden="true">
            {icon}
          </span>
        )}
        <span className="text-sm text-gray-700 font-normal">
          {label}
        </span>
      </div>

      {/* Value */}
      <span className="text-sm font-medium text-gray-900 flex-shrink-0 ml-2">
        {value}
      </span>
    </div>
  );
};

MetricRow.propTypes = {
  icon: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.node
  ]),
  label: PropTypes.string.isRequired,
  value: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number
  ]),
  optional: PropTypes.bool
};

export default MetricRow;
