import { createClient } from '@supabase/supabase-js';
import { wktToGeoJSON, geojsonToWKT } from '../utils/geoUtils.js';

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  console.warn('Supabase credentials not found. Please configure .env file.');
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Re-export geo utilities for convenience
export { wktToGeoJSON, geojsonToWKT };

/**
 * Fetch all roads with basic information (optimized for list view)
 * Only fetches necessary fields to reduce payload size
 */
export const fetchRoads = async () => {
  const { data, error } = await supabase
    .from('roads')
    .select('id, code, name, region, distance_km, curve_count_total, elevation_max, geometry, start_lat, start_lon, start_point_name, end_lat, end_lon, end_point_name')
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
 * Fetch roads filtered by region (optimized for list view)
 * Only fetches necessary fields to reduce payload size
 */
export const fetchRoadsByRegion = async (region) => {
  const { data, error } = await supabase
    .from('roads')
    .select('id, code, name, region, distance_km, curve_count_total, elevation_max, geometry, start_lat, start_lon, start_point_name, end_lat, end_lon, end_point_name')
    .eq('region', region)
    .order('code', { ascending: true });

  if (error) {
    console.error('Error fetching roads by region:', error);
    return { data: null, error };
  }

  return { data, error: null };
};

