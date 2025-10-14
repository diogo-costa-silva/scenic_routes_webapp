import { createClient } from '@supabase/supabase-js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials not found. Please configure .env file.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Fetch all roads with basic information
 */
export const fetchRoads = async () => {
  const { data, error } = await supabase
    .from('roads')
    .select('*')
    .order('region', { ascending: true })
    .order('code', { ascending: true });

  if (error) {
    console.error('Error fetching roads:', error);
    return { data: null, error };
  }

  return { data, error: null };
};

/**
 * Fetch a single road by ID with full details
 */
export const fetchRoadById = async (roadId) => {
  const { data, error } = await supabase
    .from('roads')
    .select('*')
    .eq('id', roadId)
    .single();

  if (error) {
    console.error('Error fetching road:', error);
    return { data: null, error };
  }

  return { data, error: null };
};

/**
 * Fetch roads filtered by region
 */
export const fetchRoadsByRegion = async (region) => {
  const { data, error } = await supabase
    .from('roads')
    .select('*')
    .eq('region', region)
    .order('code', { ascending: true });

  if (error) {
    console.error('Error fetching roads by region:', error);
    return { data: null, error };
  }

  return { data, error: null };
};

/**
 * Convert WKT LINESTRING to GeoJSON Feature
 * Used to convert PostGIS geometry from Supabase to Mapbox-compatible format
 *
 * @param {string} wkt - WKT geometry string (e.g., "LINESTRING(-7.7880 41.1640, -7.7850 41.1650)")
 * @returns {Object} GeoJSON Feature object
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
 * Used for future features where we need to send geometry to Supabase
 *
 * @param {Object} geojson - GeoJSON Feature or Geometry object
 * @returns {string} WKT LINESTRING string
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
