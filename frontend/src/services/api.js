import { createClient } from '@supabase/supabase-js';
import {
  wktToGeoJSON,
  geojsonToWKT,
  validatePortugalCoordinates,
  validateRoadCoordinates
} from '../utils/geoUtils.js';

/**
 * @typedef {Object} Road
 * @property {number} id - Unique road identifier
 * @property {string} code - Road code (e.g., "N222", "N2")
 * @property {string} name - Road name (e.g., "Peso da Régua → Pinhão")
 * @property {string} [description] - Optional road description
 * @property {string} region - Region ('Continental', 'Madeira', 'Açores')
 * @property {string} [category] - Optional category (e.g., 'Serra', 'Costa')
 * @property {string} geometry - PostGIS geometry (WKT LINESTRING format)
 * @property {string} [start_point_name] - Start location name
 * @property {number} start_lat - Start latitude
 * @property {number} start_lon - Start longitude
 * @property {string} [end_point_name] - End location name
 * @property {number} end_lat - End latitude
 * @property {number} end_lon - End longitude
 * @property {number} distance_km - Total distance in kilometers
 * @property {number} [elevation_max] - Maximum elevation (meters)
 * @property {number} [elevation_min] - Minimum elevation (meters)
 * @property {number} [elevation_gain] - Total elevation gain (meters)
 * @property {number} [elevation_loss] - Total elevation loss (meters)
 * @property {number} [curve_count_total] - Total number of curves
 * @property {number} [curve_count_gentle] - Gentle curves (20-45°)
 * @property {number} [curve_count_moderate] - Moderate curves (45-90°)
 * @property {number} [curve_count_sharp] - Sharp curves (>90°)
 * @property {number} [straight_count] - Number of straight sections
 * @property {number} [longest_straight_km] - Longest straight section (km)
 * @property {string} [surface] - Surface type (default: 'asphalt')
 * @property {boolean} [surface_verified] - Surface verified flag
 * @property {string} [data_source] - Data source ('osm_recursive', 'mapbox_matching', 'hybrid')
 * @property {string} [last_validated_at] - Last validation timestamp
 * @property {string} [created_at] - Creation timestamp
 * @property {string} [updated_at] - Last update timestamp
 */

/**
 * @typedef {Object} ApiResponse
 * @property {Road[]|Road|null} data - Response data or null on error
 * @property {Error|null} error - Error object or null on success
 */

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials not found. Please configure .env file.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Re-export geo utilities for convenience
export {
  wktToGeoJSON,
  geojsonToWKT,
  validatePortugalCoordinates,
  validateRoadCoordinates
};

/**
 * Fetch all roads with basic information (optimized for list view)
 * Only fetches necessary fields to reduce payload size
 *
 * @returns {Promise<ApiResponse>} Promise resolving to roads data or error
 *
 * @example
 * const { data, error } = await fetchRoads();
 * if (error) {
 *   console.error('Failed to fetch roads:', error);
 * } else {
 *   console.log(`Loaded ${data.length} roads`);
 * }
 */
export const fetchRoads = async () => {
  const { data, error } = await supabase
    .from('roads')
    .select('id, code, name, region, distance_km, curve_count_total, elevation_max, geometry, start_lat, start_lon, start_point_name, end_lat, end_lon, end_point_name, data_source')
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
 *
 * @param {number} roadId - The unique ID of the road to fetch
 * @returns {Promise<ApiResponse>} Promise resolving to single road data or error
 *
 * @example
 * const { data, error } = await fetchRoadById(1);
 * if (!error && data) {
 *   console.log(`Road: ${data.code} - ${data.name}`);
 * }
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
 * Fetch roads filtered by region (optimized for list view)
 * Only fetches necessary fields to reduce payload size
 *
 * @param {string} region - Region filter ('Continental', 'Madeira', 'Açores')
 * @returns {Promise<ApiResponse>} Promise resolving to filtered roads data or error
 *
 * @example
 * const { data, error } = await fetchRoadsByRegion('Continental');
 * if (!error && data) {
 *   console.log(`Found ${data.length} roads in Continental Portugal`);
 * }
 */
export const fetchRoadsByRegion = async (region) => {
  const { data, error } = await supabase
    .from('roads')
    .select('id, code, name, region, distance_km, curve_count_total, elevation_max, geometry, start_lat, start_lon, start_point_name, end_lat, end_lon, end_point_name, data_source')
    .eq('region', region)
    .order('code', { ascending: true });

  if (error) {
    console.error('Error fetching roads by region:', error);
    return { data: null, error };
  }

  return { data, error: null };
};

