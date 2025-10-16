/**
 * GPX Export Utility
 *
 * Generates valid GPX 1.1 XML files from road geometry data.
 * GPX (GPS Exchange Format) is the standard format for GPS devices and apps.
 *
 * Features:
 * - GPX 1.1 compliant XML generation
 * - Includes elevation data in trackpoints
 * - Proper XML escaping for metadata
 * - Supports both WKT and GeoJSON geometry formats
 * - Browser-compatible (client-side generation)
 *
 * Reference: https://www.topografix.com/gpx.asp
 */

import { wktToGeoJSON } from './geoUtils';

/**
 * Escape XML special characters
 *
 * @param {string} text - Text to escape
 * @returns {string} XML-safe text
 */
const escapeXML = (text) => {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
};

/**
 * Extract coordinates from road geometry
 *
 * Handles multiple geometry formats:
 * - WKT string (from PostGIS)
 * - GeoJSON Geometry object
 * - GeoJSON Feature object
 *
 * @param {string|Object} geometry - Road geometry in WKT or GeoJSON format
 * @returns {Array<Array<number>>|null} Array of [lon, lat] coordinates or null if invalid
 */
const extractCoordinates = (geometry) => {
  try {
    // Case 1: WKT string - convert to GeoJSON first
    if (typeof geometry === 'string') {
      const geojson = wktToGeoJSON(geometry);
      if (!geojson || !geojson.geometry) {
        console.error('Failed to convert WKT to GeoJSON');
        return null;
      }
      return geojson.geometry.coordinates;
    }

    // Case 2: GeoJSON Feature object
    if (geometry.type === 'Feature' && geometry.geometry) {
      return geometry.geometry.coordinates;
    }

    // Case 3: GeoJSON Geometry object
    if (geometry.type === 'LineString' && geometry.coordinates) {
      return geometry.coordinates;
    }

    // Case 4: Object with geometry property (nested GeoJSON)
    if (geometry.geometry && geometry.geometry.coordinates) {
      return geometry.geometry.coordinates;
    }

    console.error('Unsupported geometry format:', geometry);
    return null;
  } catch (error) {
    console.error('Error extracting coordinates:', error);
    return null;
  }
};

/**
 * Get elevation for a coordinate from road data
 *
 * If the road has elevation data array matching coordinates, use it.
 * Otherwise, return null (elevation is optional in GPX).
 *
 * @param {Object} road - Road object
 * @param {number} index - Index of coordinate
 * @returns {number|null} Elevation in meters or null
 */
const getElevation = (road, index) => {
  // Check if road has elevation array
  if (road.elevations && Array.isArray(road.elevations)) {
    const elevation = road.elevations[index];
    if (typeof elevation === 'number' && isFinite(elevation)) {
      return elevation;
    }
  }

  // No elevation data available (this is acceptable - elevation is optional)
  return null;
};

/**
 * Generate GPX 1.1 XML from road data
 *
 * Creates a valid GPX file with:
 * - Metadata (road code, name, description)
 * - Single track with single segment
 * - Track points with lat, lon, and elevation (if available)
 *
 * @param {Object} road - Road object with geometry and metadata
 * @param {string|Object} road.geometry - Road geometry (WKT or GeoJSON)
 * @param {string} road.code - Road code (e.g., "N222")
 * @param {string} road.name - Road name (e.g., "Peso da Régua → Pinhão")
 * @param {number} [road.distance_km] - Distance in kilometers
 * @param {number} [road.curve_count_total] - Total number of curves
 * @param {string} [road.surface] - Surface type (e.g., "asphalt")
 * @param {Array<number>} [road.elevations] - Optional array of elevations matching coordinates
 * @returns {Object} Result object with success status and data/error
 *
 * @example
 * const result = generateGPX(road);
 * if (result.success) {
 *   const { blob, filename } = result;
 *   // Trigger download or use blob
 * } else {
 *   console.error(result.error);
 * }
 */
export const generateGPX = (road) => {
  // Validation: Check required fields
  if (!road) {
    return {
      success: false,
      error: 'Road data is required'
    };
  }

  if (!road.geometry) {
    return {
      success: false,
      error: 'Road geometry is required'
    };
  }

  if (!road.code || !road.name) {
    return {
      success: false,
      error: 'Road code and name are required'
    };
  }

  try {
    // Extract coordinates from geometry
    const coordinates = extractCoordinates(road.geometry);

    if (!coordinates || coordinates.length === 0) {
      return {
        success: false,
        error: 'Failed to extract coordinates from geometry'
      };
    }

    // Build metadata description
    const descParts = [];
    if (road.distance_km) {
      descParts.push(`${road.distance_km}km`);
    }
    if (road.curve_count_total) {
      descParts.push(`${road.curve_count_total} curves`);
    }
    if (road.surface) {
      descParts.push(road.surface);
    }
    const description = descParts.length > 0
      ? descParts.join(' • ')
      : 'Road Explorer Portugal';

    // Generate GPX XML
    const gpxXML = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1"
     creator="Road Explorer Portugal"
     xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
  <metadata>
    <name>${escapeXML(road.code)} - ${escapeXML(road.name)}</name>
    <desc>${escapeXML(description)}</desc>
    <author>
      <name>Road Explorer Portugal</name>
    </author>
  </metadata>
  <trk>
    <name>${escapeXML(road.code)}</name>
    <desc>${escapeXML(road.name)}</desc>
    <trkseg>
${coordinates.map((coord, index) => {
  const [lon, lat] = coord;
  const elevation = getElevation(road, index);

  // Track point with elevation (if available)
  let trkpt = `      <trkpt lat="${lat}" lon="${lon}">`;
  if (elevation !== null) {
    trkpt += `\n        <ele>${elevation}</ele>\n      `;
  }
  trkpt += `</trkpt>`;

  return trkpt;
}).join('\n')}
    </trkseg>
  </trk>
</gpx>`;

    // Create blob
    const blob = new Blob([gpxXML], { type: 'application/gpx+xml' });

    // Generate safe filename (replace slashes and special chars)
    const filename = `${road.code.replace(/[\/\\:*?"<>|]/g, '-')}.gpx`;

    return {
      success: true,
      blob,
      filename,
      xml: gpxXML
    };
  } catch (error) {
    console.error('Error generating GPX:', error);
    return {
      success: false,
      error: `Failed to generate GPX: ${error.message}`
    };
  }
};

/**
 * Trigger download of GPX file in browser
 *
 * Creates a temporary download link and triggers click.
 *
 * @param {Blob} blob - GPX file blob
 * @param {string} filename - Filename for download
 */
export const downloadGPX = (blob, filename) => {
  try {
    // Create object URL for blob
    const url = URL.createObjectURL(blob);

    // Create temporary link element
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;

    // Append to body (required for Firefox)
    document.body.appendChild(link);

    // Trigger download
    link.click();

    // Cleanup
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    return true;
  } catch (error) {
    console.error('Error downloading GPX:', error);
    return false;
  }
};

/**
 * Validate GPX XML structure (basic validation)
 *
 * Checks if the generated XML has the required GPX structure.
 *
 * @param {string} xml - GPX XML string
 * @returns {boolean} True if valid GPX structure
 */
export const validateGPXStructure = (xml) => {
  if (!xml || typeof xml !== 'string') {
    return false;
  }

  // Check for required GPX elements
  const hasXMLDeclaration = xml.includes('<?xml version="1.0"');
  const hasGPXRoot = xml.includes('<gpx') && xml.includes('</gpx>');
  const hasTrack = xml.includes('<trk>') && xml.includes('</trk>');
  const hasTrackSegment = xml.includes('<trkseg>') && xml.includes('</trkseg>');
  const hasTrackPoints = xml.includes('<trkpt');

  return hasXMLDeclaration && hasGPXRoot && hasTrack && hasTrackSegment && hasTrackPoints;
};
