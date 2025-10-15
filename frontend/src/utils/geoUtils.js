/**
 * Geographic Utilities
 *
 * Helper functions for working with geographic data formats:
 * - WKT (Well-Known Text) ↔ GeoJSON conversion
 * - Coordinate validation
 * - Portugal-specific geographic validation
 *
 * Used for converting between PostGIS (WKT) and Mapbox (GeoJSON) formats.
 */

/**
 * Portugal geographic bounds (includes Continental + Islands)
 *
 * Continental Portugal: ~37-42°N, ~-10 to -6°W
 * Madeira: ~32-33°N, ~-17 to -16°W
 * Açores: ~37-40°N, ~-32 to -25°W
 */
const PORTUGAL_BOUNDS = {
  lat: { min: 32, max: 43 },   // Includes all territories
  lon: { min: -32, max: -6 }   // Includes Açores to mainland
};

/**
 * Convert WKT LINESTRING to GeoJSON Feature
 *
 * Converts PostGIS geometry from Supabase to Mapbox-compatible GeoJSON format.
 *
 * @param {string} wkt - WKT geometry string (e.g., "LINESTRING(-7.7880 41.1640, -7.7850 41.1650)")
 * @returns {Object|null} GeoJSON Feature object or null if invalid
 *
 * @example
 * const geojson = wktToGeoJSON(road.geometry);
 * map.getSource('route').setData(geojson);
 */
export const wktToGeoJSON = (wkt) => {
  if (!wkt || typeof wkt !== 'string') {
    console.error('Invalid WKT input:', wkt);
    return null;
  }

  try {
    // Remove "LINESTRING(" and ")" from WKT string
    const coordsString = wkt.replace('LINESTRING(', '').replace(')', '');
    const coordPairs = coordsString.split(',');

    // Parse coordinate pairs into [longitude, latitude] arrays
    const coordinates = coordPairs.map(pair => {
      const [lon, lat] = pair.trim().split(' ').map(Number);
      return [lon, lat];
    });

    // Validate coordinates before returning
    if (!validateCoordinates(coordinates)) {
      console.error('WKT contains invalid coordinates');
      return null;
    }

    // Return GeoJSON Feature
    return {
      type: 'Feature',
      geometry: {
        type: 'LineString',
        coordinates: coordinates
      },
      properties: {}
    };
  } catch (error) {
    console.error('Error converting WKT to GeoJSON:', error);
    return null;
  }
};

/**
 * Convert GeoJSON to WKT LINESTRING format
 *
 * Used for future features where we need to send geometry to Supabase.
 *
 * @param {Object} geojson - GeoJSON Feature or Geometry object
 * @returns {string|null} WKT LINESTRING string or null if invalid
 *
 * @example
 * const wkt = geojsonToWKT(geojsonFeature);
 * // Returns: "LINESTRING(-7.7880 41.1640, -7.7850 41.1650)"
 */
export const geojsonToWKT = (geojson) => {
  if (!geojson) {
    console.error('Invalid GeoJSON input:', geojson);
    return null;
  }

  try {
    // Handle both Feature and Geometry objects
    const geometry = geojson.type === 'Feature' ? geojson.geometry : geojson;

    if (geometry.type !== 'LineString') {
      console.error('Only LineString geometry is supported');
      return null;
    }

    // Validate coordinates before converting
    if (!validateCoordinates(geometry.coordinates)) {
      console.error('GeoJSON contains invalid coordinates');
      return null;
    }

    // Convert coordinates to WKT format: "lon lat, lon lat, ..."
    const coordsWKT = geometry.coordinates
      .map(([lon, lat]) => `${lon} ${lat}`)
      .join(', ');

    return `LINESTRING(${coordsWKT})`;
  } catch (error) {
    console.error('Error converting GeoJSON to WKT:', error);
    return null;
  }
};

/**
 * Validate coordinate array
 *
 * Checks if coordinates are valid for geographic use:
 * - Array of [longitude, latitude] pairs
 * - Longitude: -180 to 180
 * - Latitude: -90 to 90
 * - At least 2 points (minimum for LineString)
 *
 * @param {Array} coordinates - Array of [lon, lat] pairs
 * @returns {boolean} True if coordinates are valid
 *
 * @example
 * const coords = [[-7.7880, 41.1640], [-7.7850, 41.1650]];
 * if (validateCoordinates(coords)) {
 *   // Use coordinates
 * }
 */
export const validateCoordinates = (coordinates) => {
  // Check if coordinates is an array
  if (!Array.isArray(coordinates)) {
    console.error('Coordinates must be an array');
    return false;
  }

  // Check minimum length (at least 2 points for LineString)
  if (coordinates.length < 2) {
    console.error('Coordinates must have at least 2 points');
    return false;
  }

  // Validate each coordinate pair
  for (let i = 0; i < coordinates.length; i++) {
    const coord = coordinates[i];

    // Check if coordinate is an array of 2 numbers
    if (!Array.isArray(coord) || coord.length !== 2) {
      console.error(`Invalid coordinate at index ${i}:`, coord);
      return false;
    }

    const [lon, lat] = coord;

    // Check if both values are numbers
    if (typeof lon !== 'number' || typeof lat !== 'number') {
      console.error(`Non-numeric coordinate at index ${i}:`, coord);
      return false;
    }

    // Check if values are finite (not NaN or Infinity)
    if (!isFinite(lon) || !isFinite(lat)) {
      console.error(`Non-finite coordinate at index ${i}:`, coord);
      return false;
    }

    // Validate longitude range (-180 to 180)
    if (lon < -180 || lon > 180) {
      console.error(`Longitude out of range at index ${i}: ${lon}`);
      return false;
    }

    // Validate latitude range (-90 to 90)
    if (lat < -90 || lat > 90) {
      console.error(`Latitude out of range at index ${i}: ${lat}`);
      return false;
    }
  }

  return true;
};

/**
 * Calculate bounding box from coordinates
 *
 * Helper function to calculate the bounding box (bbox) of a coordinate array.
 * Useful for map fitting and spatial queries.
 *
 * @param {Array} coordinates - Array of [lon, lat] pairs
 * @returns {Array|null} [minLon, minLat, maxLon, maxLat] or null if invalid
 *
 * @example
 * const bbox = calculateBounds(coordinates);
 * map.fitBounds([[bbox[0], bbox[1]], [bbox[2], bbox[3]]]);
 */
export const calculateBounds = (coordinates) => {
  if (!validateCoordinates(coordinates)) {
    return null;
  }

  let minLon = Infinity;
  let minLat = Infinity;
  let maxLon = -Infinity;
  let maxLat = -Infinity;

  coordinates.forEach(([lon, lat]) => {
    if (lon < minLon) minLon = lon;
    if (lon > maxLon) maxLon = lon;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  });

  return [minLon, minLat, maxLon, maxLat];
};

/**
 * Validate if coordinates are within Portugal's geographic bounds
 *
 * Checks if a coordinate pair (latitude, longitude) falls within Portugal's territory,
 * including Continental Portugal, Madeira, and Açores.
 *
 * This helps detect data errors such as:
 * - Inverted lat/lon coordinates
 * - Coordinates from wrong location
 * - Data entry mistakes
 *
 * @param {number} lat - Latitude (-90 to 90)
 * @param {number} lon - Longitude (-180 to 180)
 * @returns {boolean} True if coordinates are within Portugal bounds
 *
 * @example
 * validatePortugalCoordinates(41.16, -7.78);  // true (Peso da Régua)
 * validatePortugalCoordinates(-7.78, 41.16);  // false (inverted - Africa!)
 * validatePortugalCoordinates(48.85, 2.35);   // false (Paris, France)
 */
export const validatePortugalCoordinates = (lat, lon) => {
  // Check if values are numbers
  if (typeof lat !== 'number' || typeof lon !== 'number') {
    console.warn('validatePortugalCoordinates: lat and lon must be numbers');
    return false;
  }

  // Check if values are finite
  if (!isFinite(lat) || !isFinite(lon)) {
    console.warn('validatePortugalCoordinates: lat and lon must be finite numbers');
    return false;
  }

  // Check Portugal bounds
  const inLatBounds = lat >= PORTUGAL_BOUNDS.lat.min && lat <= PORTUGAL_BOUNDS.lat.max;
  const inLonBounds = lon >= PORTUGAL_BOUNDS.lon.min && lon <= PORTUGAL_BOUNDS.lon.max;

  if (!inLatBounds || !inLonBounds) {
    console.warn(
      `Coordinates (${lat}, ${lon}) are outside Portugal bounds. ` +
      `Expected: lat ${PORTUGAL_BOUNDS.lat.min}-${PORTUGAL_BOUNDS.lat.max}, ` +
      `lon ${PORTUGAL_BOUNDS.lon.min}-${PORTUGAL_BOUNDS.lon.max}`
    );
    return false;
  }

  return true;
};

/**
 * Validate if a road's coordinates are within Portugal
 *
 * Checks start and end points, plus all geometry coordinates if provided.
 *
 * @param {Object} road - Road object with start/end coordinates
 * @param {number} road.start_lat - Start latitude
 * @param {number} road.start_lon - Start longitude
 * @param {number} road.end_lat - End latitude
 * @param {number} road.end_lon - End longitude
 * @param {Array} [road.coordinates] - Optional array of [lon, lat] pairs
 * @returns {Object} { valid: boolean, errors: Array<string> }
 *
 * @example
 * const result = validateRoadCoordinates(road);
 * if (!result.valid) {
 *   console.error('Invalid road:', result.errors);
 * }
 */
export const validateRoadCoordinates = (road) => {
  const errors = [];

  // Validate start point
  if (road.start_lat !== undefined && road.start_lon !== undefined) {
    if (!validatePortugalCoordinates(road.start_lat, road.start_lon)) {
      errors.push(`Start point (${road.start_lat}, ${road.start_lon}) outside Portugal`);
    }
  }

  // Validate end point
  if (road.end_lat !== undefined && road.end_lon !== undefined) {
    if (!validatePortugalCoordinates(road.end_lat, road.end_lon)) {
      errors.push(`End point (${road.end_lat}, ${road.end_lon}) outside Portugal`);
    }
  }

  // Validate geometry coordinates if provided
  if (road.coordinates && Array.isArray(road.coordinates)) {
    road.coordinates.forEach(([lon, lat], index) => {
      if (!validatePortugalCoordinates(lat, lon)) {
        errors.push(`Geometry point ${index} (${lat}, ${lon}) outside Portugal`);
      }
    });
  }

  return {
    valid: errors.length === 0,
    errors
  };
};
