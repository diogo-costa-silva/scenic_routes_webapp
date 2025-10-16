import { useState, useEffect } from 'react';
import RoadMap from './components/Map/RoadMap';
import Sidebar from './components/Sidebar/Sidebar';
import RoadDetails from './components/Details/RoadDetails';

function App() {
  const [selectedRoad, setSelectedRoad] = useState(null);

  const handleRoadSelect = (road) => {
    console.log('Road selected:', road);
    setSelectedRoad(road);
  };

  // Global keyboard handler for Esc key to close details panel
  useEffect(() => {
    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' && selectedRoad) {
        setSelectedRoad(null);
      }
    };

    window.addEventListener('keydown', handleEscapeKey);
    return () => window.removeEventListener('keydown', handleEscapeKey);
  }, [selectedRoad]);

  return (
    <div className="w-full h-screen flex flex-col" lang="en">
      {/* Skip to main content link for keyboard users */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-primary focus:text-white focus:px-4 focus:py-2 focus:rounded"
      >
        Skip to main content
      </a>

      {/* Header */}
      <header className="flex-shrink-0 bg-white shadow-md z-20" role="banner">
        <div className="px-4 sm:px-6 py-3">
          <h1 className="text-xl sm:text-2xl font-bold text-secondary truncate">
            🏍️ Road Explorer Portugal
          </h1>
          <p className="text-sm text-gray-600">
            Discover the best motorcycle roads in Portugal
          </p>
        </div>
      </header>

      {/* Main content: Sidebar + Map */}
      <main
        id="main-content"
        className="flex-1 flex overflow-hidden"
        role="main"
      >
        {/* Sidebar */}
        <Sidebar
          selectedRoadId={selectedRoad?.id}
          onRoadSelect={handleRoadSelect}
        />

        {/* Map */}
        <section
          className="flex-1 relative"
          aria-label="Interactive map"
          role="region"
        >
          <RoadMap selectedRoad={selectedRoad} />
        </section>

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
