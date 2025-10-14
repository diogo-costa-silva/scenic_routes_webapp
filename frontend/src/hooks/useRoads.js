import { useState, useEffect, useCallback } from 'react';
import { fetchRoads, fetchRoadsByRegion } from '../services/api';

/**
 * Custom hook for fetching and managing roads data from Supabase
 *
 * @param {Object} options - Hook options
 * @param {string|null} options.region - Filter by region ('Continental', 'Madeira', 'Açores', or null for all)
 * @param {boolean} options.fetchOnMount - Whether to fetch data on component mount (default: true)
 *
 * @returns {Object} - { roads, loading, error, refetch, groupedRoads }
 */
const useRoads = ({ region = null, fetchOnMount = true } = {}) => {
  const [roads, setRoads] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Fetch roads from Supabase
   */
  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const { data, error: fetchError } = region
        ? await fetchRoadsByRegion(region)
        : await fetchRoads();

      if (fetchError) {
        console.error('Error fetching roads:', fetchError);
        setError({
          type: 'FETCH_ERROR',
          message: 'Failed to load roads from database',
          details: fetchError.message
        });
        setRoads([]);
      } else if (!data || data.length === 0) {
        console.warn('No roads found in database');
        setError({
          type: 'NO_DATA',
          message: 'No roads available yet',
          details: 'The database is empty. Please add roads using the Python scripts.'
        });
        setRoads([]);
      } else {
        console.log(`✅ Loaded ${data.length} roads${region ? ` from ${region}` : ''}`);
        setRoads(data);
        setError(null);
      }
    } catch (err) {
      console.error('Unexpected error fetching roads:', err);
      setError({
        type: 'UNKNOWN_ERROR',
        message: 'An unexpected error occurred',
        details: err.message
      });
      setRoads([]);
    } finally {
      setLoading(false);
    }
  }, [region]);

  /**
   * Refetch roads manually
   */
  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  /**
   * Fetch data on mount if enabled
   */
  useEffect(() => {
    if (fetchOnMount) {
      fetchData();
    }
  }, [fetchData, fetchOnMount]);

  /**
   * Group roads by region for easier rendering
   * Returns: { Continental: [...], Madeira: [...], Açores: [...] }
   */
  const groupedRoads = roads.reduce((acc, road) => {
    const region = road.region || 'Other';
    if (!acc[region]) {
      acc[region] = [];
    }
    acc[region].push(road);
    return acc;
  }, {});

  return {
    roads,
    loading,
    error,
    refetch,
    groupedRoads,
    isEmpty: roads.length === 0 && !loading && !error
  };
};

export default useRoads;
