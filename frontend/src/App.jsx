import RoadMap from './components/Map/RoadMap';

function App() {
  return (
    <div className="w-full h-screen">
      <header className="absolute top-0 left-0 right-0 z-10 bg-white shadow-md">
        <div className="container mx-auto px-4 py-3">
          <h1 className="text-2xl font-bold text-secondary">
            🏍️ Road Explorer Portugal
          </h1>
          <p className="text-sm text-gray-600">
            Discover the best motorcycle roads in Portugal
          </p>
        </div>
      </header>

      <main className="w-full h-full pt-20">
        <RoadMap />
      </main>
    </div>
  );
}

export default App;
