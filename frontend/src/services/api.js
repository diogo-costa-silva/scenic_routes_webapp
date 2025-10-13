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
