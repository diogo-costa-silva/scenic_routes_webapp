import { useState } from 'react';
import RoadMap from './components/Map/RoadMap';
import Sidebar from './components/Sidebar/Sidebar';

// Import connection test for development
import './utils/testConnection';

function App() {
  const [selectedRoad, setSelectedRoad] = useState(null);

  const handleRoadSelect = (road) => {
    console.log('Road selected:', road);
    setSelectedRoad(road);
    // TODO: Next session - update RoadMap to visualize selected road
  };

  return (
    <div className="w-full h-screen flex flex-col">
      {/* Header */}
      <header className="flex-shrink-0 bg-white shadow-md z-20">
        <div className="px-4 py-3">
          <h1 className="text-2xl font-bold text-secondary">
            🏍️ Road Explorer Portugal
          </h1>
          <p className="text-sm text-gray-600">
            Discover the best motorcycle roads in Portugal
          </p>
        </div>
      </header>

      {/* Main content: Sidebar + Map */}
      <main className="flex-1 flex overflow-hidden">
        {/* Sidebar */}
        <Sidebar
          selectedRoadId={selectedRoad?.id}
          onRoadSelect={handleRoadSelect}
        />

        {/* Map */}
        <div className="flex-1 relative">
          <RoadMap selectedRoad={selectedRoad} />

          {/* Selected road info (floating) */}
          {selectedRoad && (
            <div className="absolute top-4 right-4 bg-white shadow-lg rounded-lg p-4 max-w-sm z-10">
              <h3 className="font-bold text-primary text-lg mb-1">
                {selectedRoad.code}
              </h3>
              <p className="text-sm text-gray-600 mb-2">{selectedRoad.name}</p>
              <div className="flex gap-2 text-xs text-gray-700">
                <span>📏 {selectedRoad.distance_km}km</span>
                {selectedRoad.curve_count_total && (
                  <span>🌀 {selectedRoad.curve_count_total} curves</span>
                )}
                {selectedRoad.elevation_max && (
                  <span>⛰️ {selectedRoad.elevation_max}m</span>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
