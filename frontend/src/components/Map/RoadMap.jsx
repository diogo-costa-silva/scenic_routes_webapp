import { useRef, useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import mapboxgl from 'mapbox-gl';
import { wktToGeoJSON, validateRoadCoordinates } from '../../utils/geoUtils';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;
const PORTUGAL_CENTER = [-8.0, 39.5];
const INITIAL_ZOOM = 6;
const LOAD_TIMEOUT = 10000; // 10 seconds

mapboxgl.accessToken = MAPBOX_TOKEN;

const RoadMap = ({
  initialCenter = PORTUGAL_CENTER,
  initialZoom = INITIAL_ZOOM,
  className = '',
  selectedRoad = null
}) => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const loadTimeoutRef = useRef(null);
  const startMarkerRef = useRef(null);
  const endMarkerRef = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);
  const [error, setError] = useState(null);

  const initializeMap = () => {
    // Reset states
    setMapLoaded(false);
    setError(null);

    // Remove existing map if any
    if (map.current) {
      map.current.remove();
      map.current = null;
    }

    if (!MAPBOX_TOKEN) {
      console.error('Mapbox token not found. Please set VITE_MAPBOX_TOKEN in .env file.');
      setError('NO_TOKEN');
      return;
    }

    console.log('🗺️ Initializing Mapbox map...');
    console.log('📍 Center:', initialCenter);
    console.log('🔍 Zoom:', initialZoom);
    console.log('🔑 Token present:', MAPBOX_TOKEN ? 'Yes (hidden)' : 'No');

    try {
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/outdoors-v12',
        center: initialCenter,
        zoom: initialZoom,
      });

      // Add navigation controls (zoom buttons)
      map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

      // Set timeout for loading
      loadTimeoutRef.current = setTimeout(() => {
        console.error('⏱️ Map loading timeout');
        setError('TIMEOUT');
      }, LOAD_TIMEOUT);

      // Success handler
      map.current.on('load', () => {
        console.log('✅ Map loaded successfully');
        clearTimeout(loadTimeoutRef.current);
        setMapLoaded(true);
        setError(null);
      });

      // Error handler
      map.current.on('error', (e) => {
        console.error('❌ Mapbox error:', e);
        clearTimeout(loadTimeoutRef.current);

        // Determine error type
        if (e.error && e.error.message) {
          if (e.error.message.includes('401')) {
            setError('INVALID_TOKEN');
          } else if (e.error.message.includes('network')) {
            setError('NETWORK');
          } else {
            setError('GENERAL');
          }
        } else {
          setError('GENERAL');
        }
      });

    } catch (err) {
      console.error('❌ Failed to initialize map:', err);
      setError('INIT_FAILED');
    }
  };

  // Cleanup function for route and markers
  const cleanupRoute = () => {
    if (!map.current) return;

    // Remove route layer and source
    if (map.current.getLayer('route')) {
      map.current.removeLayer('route');
    }
    if (map.current.getSource('route')) {
      map.current.removeSource('route');
    }

    // Remove markers
    if (startMarkerRef.current) {
      startMarkerRef.current.remove();
      startMarkerRef.current = null;
    }
    if (endMarkerRef.current) {
      endMarkerRef.current.remove();
      endMarkerRef.current = null;
    }
  };

  // Animate line drawing
  const animateLine = (geojson) => {
    const coordinates = geojson.geometry.coordinates;
    const steps = 50;
    const segmentLength = Math.ceil(coordinates.length / steps);
    let step = 0;

    const animate = () => {
      if (step >= steps || !map.current) return;

      const currentCoords = coordinates.slice(0, (step + 1) * segmentLength);

      // Update source data with current coordinates
      if (map.current.getSource('route')) {
        map.current.getSource('route').setData({
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: currentCoords
          }
        });
      }

      step++;
      setTimeout(animate, 50); // 50ms per step = ~2.5s total animation
    };

    animate();
  };

  // Initialize map once
  useEffect(() => {
    if (map.current) return; // Initialize map only once
    initializeMap();

    // Cleanup on unmount
    return () => {
      if (loadTimeoutRef.current) {
        clearTimeout(loadTimeoutRef.current);
      }
      cleanupRoute();
      if (map.current) {
        map.current.remove();
      }
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Handle selectedRoad changes
  useEffect(() => {
    // Wait for map to be loaded
    if (!map.current || !mapLoaded) return;

    // Cleanup previous route
    cleanupRoute();

    // If no road selected, return early
    if (!selectedRoad) {
      console.log('No road selected - map cleared');
      return;
    }

    console.log('🎨 Drawing route for:', selectedRoad.code);

    // Validate coordinates are within Portugal
    const validationResult = validateRoadCoordinates(selectedRoad);
    if (!validationResult.valid) {
      console.error(
        `⚠️ Road ${selectedRoad.code} has invalid coordinates (possibly outside Portugal):`,
        validationResult.errors
      );
      console.error('This road will not be displayed on the map.');
      console.error('Please check the database coordinates for this road.');
      // Don't render roads with invalid coordinates
      return;
    }

    // Validate geometry
    if (!selectedRoad.geometry) {
      console.error('Road has no geometry:', selectedRoad.code);
      return;
    }

    // Handle both WKT (string) and GeoJSON (object) formats
    let geojson;
    if (typeof selectedRoad.geometry === 'string') {
      // WKT format - convert to GeoJSON
      geojson = wktToGeoJSON(selectedRoad.geometry);
      if (!geojson) {
        console.error('Failed to convert WKT to GeoJSON for road:', selectedRoad.code);
        return;
      }
    } else if (typeof selectedRoad.geometry === 'object' && selectedRoad.geometry.type === 'LineString') {
      // Already GeoJSON Geometry - wrap in Feature
      geojson = {
        type: 'Feature',
        geometry: selectedRoad.geometry,
        properties: {}
      };
    } else if (typeof selectedRoad.geometry === 'object' && selectedRoad.geometry.geometry) {
      // Already GeoJSON Feature
      geojson = selectedRoad.geometry;
    } else {
      console.error('Invalid geometry format for road:', selectedRoad.code, selectedRoad.geometry);
      return;
    }

    console.log(`📍 Route has ${geojson.geometry.coordinates.length} coordinates`);

    try {
      // Add route source
      map.current.addSource('route', {
        type: 'geojson',
        data: {
          type: 'Feature',
          geometry: {
            type: 'LineString',
            coordinates: []  // Start with empty coordinates for animation
          }
        }
      });

      // Add route layer
      map.current.addLayer({
        id: 'route',
        type: 'line',
        source: 'route',
        layout: {
          'line-join': 'round',
          'line-cap': 'round'
        },
        paint: {
          'line-color': '#FF6B35',  // Primary orange
          'line-width': 4,
          'line-opacity': 0.9
        }
      });

      // Animate the line drawing
      animateLine(geojson);

      // Add start marker (green)
      if (selectedRoad.start_lat && selectedRoad.start_lon) {
        startMarkerRef.current = new mapboxgl.Marker({ color: '#10B981' })
          .setLngLat([selectedRoad.start_lon, selectedRoad.start_lat])
          .setPopup(
            new mapboxgl.Popup({ offset: 25 })
              .setHTML(`<strong>Start:</strong> ${selectedRoad.start_point_name || 'Unknown'}`)
          )
          .addTo(map.current);
        console.log('✅ Start marker added');
      }

      // Add end marker (red)
      if (selectedRoad.end_lat && selectedRoad.end_lon) {
        endMarkerRef.current = new mapboxgl.Marker({ color: '#EF4444' })
          .setLngLat([selectedRoad.end_lon, selectedRoad.end_lat])
          .setPopup(
            new mapboxgl.Popup({ offset: 25 })
              .setHTML(`<strong>End:</strong> ${selectedRoad.end_point_name || 'Unknown'}`)
          )
          .addTo(map.current);
        console.log('✅ End marker added');
      }

      // Fit bounds to show complete route
      const coordinates = geojson.geometry.coordinates;
      const bounds = new mapboxgl.LngLatBounds();
      coordinates.forEach(coord => bounds.extend(coord));

      map.current.fitBounds(bounds, {
        padding: 50,
        duration: 1500  // 1.5s smooth animation
      });
      console.log('✅ Map fitted to route bounds');

    } catch (err) {
      console.error('Error visualizing route:', err);
      cleanupRoute();
    }

  }, [selectedRoad, mapLoaded]);

  const handleRetry = () => {
    console.log('🔄 Retrying map initialization...');
    initializeMap();
  };

  // Error messages
  const getErrorMessage = () => {
    switch (error) {
      case 'NO_TOKEN':
        return {
          title: 'Mapbox token not configured',
          message: 'Please create a .env file and add your Mapbox token.',
          suggestions: [
            'Create a file named .env in the frontend folder',
            'Add: VITE_MAPBOX_TOKEN=your_token_here',
            'Get your token at: https://account.mapbox.com/access-tokens/'
          ]
        };
      case 'INVALID_TOKEN':
        return {
          title: 'Invalid Mapbox token',
          message: 'The Mapbox token is not valid or doesn\'t have the required permissions.',
          suggestions: [
            'Verify your token at https://account.mapbox.com/access-tokens/',
            'Make sure the token has "Public scopes" enabled',
            'Check if the token is active (not expired or deleted)',
            'Ensure you\'re using a public token (starts with pk.)'
          ]
        };
      case 'NETWORK':
        return {
          title: 'Network connection error',
          message: 'Unable to connect to Mapbox API.',
          suggestions: [
            'Check your internet connection',
            'Disable ad blockers or privacy extensions',
            'Check if api.mapbox.com is blocked by firewall',
            'Try refreshing the page'
          ]
        };
      case 'TIMEOUT':
        return {
          title: 'Map loading timeout',
          message: 'The map is taking too long to load.',
          suggestions: [
            'Check your internet connection speed',
            'Disable browser extensions that might block requests',
            'Try refreshing the page',
            'Check browser console for detailed errors'
          ]
        };
      case 'INIT_FAILED':
        return {
          title: 'Initialization failed',
          message: 'Failed to initialize the Mapbox map.',
          suggestions: [
            'Check browser console for detailed errors',
            'Try refreshing the page',
            'Verify Mapbox GL JS is properly installed'
          ]
        };
      default:
        return {
          title: 'Map loading error',
          message: 'An unexpected error occurred while loading the map.',
          suggestions: [
            'Check browser console for details',
            'Try refreshing the page',
            'Verify your Mapbox configuration'
          ]
        };
    }
  };

  const errorInfo = error ? getErrorMessage() : null;

  return (
    <div className={`relative w-full h-full ${className}`}>
      <div ref={mapContainer} className="map-container" />

      {!mapLoaded && !error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-gray-600">Loading map...</p>
            <p className="text-xs text-gray-500 mt-2">Connecting to Mapbox API</p>
          </div>
        </div>
      )}

      {error && errorInfo && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-50 p-6 overflow-auto">
          <div className="text-center max-w-2xl">
            <div className="text-5xl mb-4">🗺️❌</div>
            <h2 className="text-danger font-bold text-xl mb-2">{errorInfo.title}</h2>
            <p className="text-gray-700 mb-4">{errorInfo.message}</p>

            <div className="bg-white rounded-lg p-4 mb-4 text-left">
              <p className="font-semibold text-sm text-gray-800 mb-2">💡 Possible solutions:</p>
              <ul className="text-sm text-gray-700 space-y-1">
                {errorInfo.suggestions.map((suggestion, idx) => (
                  <li key={idx} className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>{suggestion}</span>
                  </li>
                ))}
              </ul>
            </div>

            <button
              onClick={handleRetry}
              className="bg-primary hover:bg-orange-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
            >
              🔄 Try Again
            </button>

            <p className="text-xs text-gray-500 mt-4">
              Check the browser console (F12) for detailed error messages
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

RoadMap.propTypes = {
  initialCenter: PropTypes.arrayOf(PropTypes.number),
  initialZoom: PropTypes.number,
  className: PropTypes.string,
  selectedRoad: PropTypes.shape({
    id: PropTypes.number,
    code: PropTypes.string,
    name: PropTypes.string,
    geometry: PropTypes.string,
    start_lat: PropTypes.number,
    start_lon: PropTypes.number,
    start_point_name: PropTypes.string,
    end_lat: PropTypes.number,
    end_lon: PropTypes.number,
    end_point_name: PropTypes.string,
  }),
};

export default RoadMap;
