import { useState } from 'react';
import RoadMap from './components/Map/RoadMap';
import Sidebar from './components/Sidebar/Sidebar';
import RoadDetails from './components/Details/RoadDetails';

// Import connection test for development
import './utils/testConnection';

function App() {
  const [selectedRoad, setSelectedRoad] = useState(null);

  const handleRoadSelect = (road) => {
    console.log('Road selected:', road);
    setSelectedRoad(road);
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
        </div>

        {/* Road Details Panel */}
        <RoadDetails
          selectedRoad={selectedRoad}
          onClose={() => setSelectedRoad(null)}
        />
      </main>
    </div>
  );
}

export default App;
