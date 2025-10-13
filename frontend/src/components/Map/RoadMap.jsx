import { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN;
const PORTUGAL_CENTER = [-8.0, 39.5];
const INITIAL_ZOOM = 6;

mapboxgl.accessToken = MAPBOX_TOKEN;

const RoadMap = () => {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const [mapLoaded, setMapLoaded] = useState(false);

  useEffect(() => {
    if (map.current) return; // Initialize map only once

    if (!MAPBOX_TOKEN) {
      console.error('Mapbox token not found. Please set VITE_MAPBOX_TOKEN in .env file.');
      return;
    }

    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/outdoors-v12',
      center: PORTUGAL_CENTER,
      zoom: INITIAL_ZOOM,
    });

    // Add navigation controls (zoom buttons)
    map.current.addControl(new mapboxgl.NavigationControl(), 'top-right');

    map.current.on('load', () => {
      console.log('Map loaded successfully');
      setMapLoaded(true);
    });

    // Cleanup on unmount
    return () => {
      if (map.current) {
        map.current.remove();
      }
    };
  }, []);

  return (
    <div className="relative w-full h-full">
      <div ref={mapContainer} className="map-container" />

      {!mapLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-gray-600">Loading map...</p>
          </div>
        </div>
      )}

      {!MAPBOX_TOKEN && (
        <div className="absolute inset-0 flex items-center justify-center bg-red-50">
          <div className="text-center p-6 max-w-md">
            <p className="text-red-600 font-semibold mb-2">Mapbox token not configured</p>
            <p className="text-sm text-gray-700">
              Please create a <code className="bg-gray-200 px-1 rounded">.env</code> file
              and add your Mapbox token.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default RoadMap;
