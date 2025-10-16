import PropTypes from 'prop-types';
import { wktToGeoJSON } from '../../utils/geoUtils';

/**
 * ActionButtons Component
 *
 * Displays action buttons for the selected road:
 * - Export GPX: Download route as GPX file for GPS devices
 * - Open in Google Maps: Open route in Google Maps for navigation
 *
 * @param {Object} props
 * @param {Object} props.road - Road object with geometry, code, name, distance_km, curve_count_total
 */
const ActionButtons = ({ road }) => {
  /**
   * Export road geometry as GPX file
   * Converts WKT geometry to GeoJSON, then to GPX format with metadata
   */
  const handleExportGPX = () => {
    if (!road || !road.geometry) {
      console.error('Cannot export GPX: Road data or geometry missing');
      return;
    }

    try {
      // Handle both WKT (string) and GeoJSON (object) formats
      let geojson;
      if (typeof road.geometry === 'string') {
        // WKT format - convert to GeoJSON
        geojson = wktToGeoJSON(road.geometry);
        if (!geojson) {
          console.error('Failed to convert WKT to GeoJSON');
          return;
        }
      } else if (typeof road.geometry === 'object' && road.geometry.type === 'LineString') {
        // Already GeoJSON Geometry - wrap in Feature and clean up
        geojson = {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: road.geometry.coordinates  // Remove crs and other non-standard properties
          },
          properties: {}
        };
      } else if (typeof road.geometry === 'object' && road.geometry.geometry) {
        // Already GeoJSON Feature - clean up geometry
        geojson = {
          type: 'Feature',
          geometry: {
            type: road.geometry.geometry.type,
            coordinates: road.geometry.geometry.coordinates
          },
          properties: road.geometry.properties || {}
        };
      } else {
        console.error('Invalid geometry format');
        return;
      }

      // Extract coordinates from the GeoJSON
      const coordinates = geojson.geometry.coordinates;

      // Manually create GPX XML
      const gpxHeader = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="Road Explorer Portugal" xmlns="http://www.topografix.com/GPX/1/1">
  <metadata>
    <name>${road.code} - ${road.name}</name>
    <desc>${road.distance_km}km • ${road.curve_count_total || 0} curves • Road Explorer Portugal</desc>
  </metadata>
  <trk>
    <name>${road.code}</name>
    <trkseg>`;

      const gpxPoints = coordinates
        .map(([lon, lat]) => `      <trkpt lat="${lat}" lon="${lon}"></trkpt>`)
        .join('\n');

      const gpxFooter = `
    </trkseg>
  </trk>
</gpx>`;

      const gpx = gpxHeader + '\n' + gpxPoints + gpxFooter;

      // Create blob and trigger download
      const blob = new Blob([gpx], { type: 'application/gpx+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${road.code.replace(/\//g, '-')}.gpx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      console.log(`GPX exported successfully: ${road.code}.gpx`);
    } catch (error) {
      console.error('Error exporting GPX:', error);
      alert('Failed to export GPX file. Please try again.');
    }
  };

  /**
   * Open road location in Google Maps
   * Opens Google Maps Directions with the road's start point as destination
   */
  const handleOpenMaps = () => {
    if (!road || !road.start_lat || !road.start_lon) {
      console.error('Cannot open Google Maps: Road coordinates missing');
      return;
    }

    try {
      // Construct Google Maps Directions URL with start point
      const url = `https://www.google.com/maps/dir/?api=1&destination=${road.start_lat},${road.start_lon}`;
      window.open(url, '_blank', 'noopener,noreferrer');

      console.log(`Opened Google Maps for: ${road.code}`);
    } catch (error) {
      console.error('Error opening Google Maps:', error);
      alert('Failed to open Google Maps. Please try again.');
    }
  };

  return (
    <div className="flex flex-col sm:flex-row gap-2 p-4 border-t border-gray-200 bg-white">
      {/* Export GPX Button */}
      <button
        onClick={handleExportGPX}
        disabled={!road}
        title="Download GPX file for GPS devices"
        className={`
          flex-1 px-4 py-2.5 rounded-md font-medium text-sm
          flex items-center justify-center gap-2
          transition-all duration-200
          ${!road
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
        disabled={!road}
        title="Open route in Google Maps"
        className={`
          flex-1 px-4 py-2.5 rounded-md font-medium text-sm
          flex items-center justify-center gap-2
          transition-all duration-200
          ${!road
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
  road: PropTypes.object,
};

export default ActionButtons;
