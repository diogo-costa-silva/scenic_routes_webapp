import PropTypes from 'prop-types';
import MetricRow from '../UI/MetricRow';
import {
  formatDistance,
  formatElevation,
  formatElevationChange,
  formatSurface,
  isValidValue,
} from '../../utils/formatters';

/**
 * MetricsPanel Component
 *
 * Displays comprehensive metrics for a selected road, organized into sections:
 * 1. Distance & Elevation
 * 2. Curves breakdown
 * 3. Straights information
 * 4. Surface type
 *
 * @param {Object} props
 * @param {Object} props.road - Road object with all metrics
 */
const MetricsPanel = ({ road }) => {
  if (!road) {
    return null;
  }

  // Check if we have any curve data
  const hasCurveData = isValidValue(road.curve_count_total);
  const hasCurveBreakdown =
    isValidValue(road.curve_count_gentle) ||
    isValidValue(road.curve_count_moderate) ||
    isValidValue(road.curve_count_sharp);

  // Check if we have straight data
  const hasStraightData =
    isValidValue(road.straight_count) ||
    isValidValue(road.longest_straight_km);

  return (
    <div className="metrics-panel">
      {/* Section 1: Distance & Elevation */}
      <div className="space-y-1">
        <MetricRow
          icon="📏"
          label="Distância"
          value={formatDistance(road.distance_km)}
        />
        <MetricRow
          icon="🏔️"
          label="Altitude Máxima"
          value={formatElevation(road.elevation_max)}
          optional
        />
        <MetricRow
          icon="🏞️"
          label="Altitude Mínima"
          value={formatElevation(road.elevation_min)}
          optional
        />
        <MetricRow
          icon="📈"
          label="Desnível Subida"
          value={formatElevationChange(road.elevation_gain, true)}
          optional
        />
        <MetricRow
          icon="📉"
          label="Desnível Descida"
          value={formatElevationChange(road.elevation_loss, false)}
          optional
        />
      </div>

      {/* Divider */}
      {hasCurveData && (
        <div className="border-t border-gray-200 my-4" />
      )}

      {/* Section 2: Curves */}
      {hasCurveData && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-800 flex items-center gap-2 mb-2">
            <span className="text-base">🌀</span>
            <span>Curvas</span>
          </h3>

          <div className="pl-6 space-y-1">
            <MetricRow
              label="Total"
              value={road.curve_count_total}
            />

            {hasCurveBreakdown && (
              <div className="space-y-1 mt-2">
                <MetricRow
                  label="Suaves"
                  value={road.curve_count_gentle || 0}
                  optional
                />
                <MetricRow
                  label="Moderadas"
                  value={road.curve_count_moderate || 0}
                  optional
                />
                <MetricRow
                  label="Apertadas"
                  value={road.curve_count_sharp || 0}
                  optional
                />
              </div>
            )}
          </div>
        </div>
      )}

      {/* Divider */}
      {hasStraightData && (
        <div className="border-t border-gray-200 my-4" />
      )}

      {/* Section 3: Straights */}
      {hasStraightData && (
        <div className="space-y-2">
          <h3 className="text-sm font-semibold text-gray-800 flex items-center gap-2 mb-2">
            <span className="text-base">➡️</span>
            <span>Retas</span>
          </h3>

          <div className="pl-6 space-y-1">
            <MetricRow
              label="Total"
              value={road.straight_count || 'N/A'}
              optional
            />
            <MetricRow
              label="Mais longa"
              value={formatDistance(road.longest_straight_km)}
              optional
            />
          </div>
        </div>
      )}

      {/* Divider */}
      {road.surface && (
        <div className="border-t border-gray-200 my-4" />
      )}

      {/* Section 4: Surface */}
      {road.surface && (
        <div className="space-y-1">
          <MetricRow
            icon="🛣️"
            label="Tipo de Piso"
            value={formatSurface(road.surface, road.surface_verified)}
          />
        </div>
      )}

      {/* Optional: Start and End Points */}
      {(road.start_point_name || road.end_point_name) && (
        <>
          <div className="border-t border-gray-200 my-4" />
          <div className="space-y-1">
            {road.start_point_name && (
              <MetricRow
                icon="🟢"
                label="Início"
                value={road.start_point_name}
              />
            )}
            {road.end_point_name && (
              <MetricRow
                icon="🔴"
                label="Fim"
                value={road.end_point_name}
              />
            )}
          </div>
        </>
      )}
    </div>
  );
};

MetricsPanel.propTypes = {
  road: PropTypes.shape({
    // Basic info
    code: PropTypes.string,
    name: PropTypes.string,
    region: PropTypes.string,

    // Distance
    distance_km: PropTypes.number,

    // Elevation
    elevation_max: PropTypes.number,
    elevation_min: PropTypes.number,
    elevation_gain: PropTypes.number,
    elevation_loss: PropTypes.number,

    // Curves
    curve_count_total: PropTypes.number,
    curve_count_gentle: PropTypes.number,
    curve_count_moderate: PropTypes.number,
    curve_count_sharp: PropTypes.number,

    // Straights
    straight_count: PropTypes.number,
    longest_straight_km: PropTypes.number,

    // Surface
    surface: PropTypes.string,
    surface_verified: PropTypes.bool,

    // Points
    start_point_name: PropTypes.string,
    end_point_name: PropTypes.string,
  }),
};

export default MetricsPanel;
