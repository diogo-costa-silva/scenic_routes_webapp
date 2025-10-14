import { useState } from 'react';
import PropTypes from 'prop-types';
import RoadList from './RoadList';

/**
 * Sidebar Component
 *
 * Container for the road list sidebar with:
 * - Fixed 300px width on desktop
 * - Collapsible on mobile (hamburger menu)
 * - Search functionality
 * - Region filter (optional)
 *
 * @param {Object} props
 * @param {number|null} props.selectedRoadId - Currently selected road ID
 * @param {Function} props.onRoadSelect - Callback when road is selected
 * @param {string} props.className - Additional CSS classes
 */
const Sidebar = ({ selectedRoadId = null, onRoadSelect, className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRegion, setFilterRegion] = useState(null);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  const handleRegionFilter = (region) => {
    setFilterRegion(region === filterRegion ? null : region);
  };

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        onClick={toggleSidebar}
        className="fixed top-24 left-4 z-50 md:hidden bg-white rounded-lg shadow-lg p-3 hover:bg-gray-50 transition-colors"
        aria-label="Toggle sidebar"
        aria-expanded={isOpen}
      >
        <svg
          className="w-6 h-6 text-gray-700"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          {isOpen ? (
            <path d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path d="M4 6h16M4 12h16M4 18h16" />
          )}
        </svg>
      </button>

      {/* Overlay for mobile */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30 md:hidden"
          onClick={toggleSidebar}
          aria-hidden="true"
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`
          fixed md:relative
          top-0 left-0
          h-full md:h-auto
          w-80 md:w-[300px]
          bg-white
          shadow-xl md:shadow-none
          z-40
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          flex flex-col
          ${className}
        `}
      >
        {/* Sidebar header */}
        <div className="flex-shrink-0 p-4 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-lg font-bold text-gray-800">Road Explorer</h2>
            <button
              onClick={toggleSidebar}
              className="md:hidden text-gray-500 hover:text-gray-700"
              aria-label="Close sidebar"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Search box */}
          <div className="relative">
            <input
              type="text"
              placeholder="Search roads..."
              value={searchQuery}
              onChange={handleSearchChange}
              className="w-full px-3 py-2 pl-9 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-sm"
            />
            <svg
              className="absolute left-3 top-2.5 w-4 h-4 text-gray-400"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>

          {/* Region filter buttons */}
          <div className="flex gap-2 mt-3">
            {['Continental', 'Madeira', 'Açores'].map((region) => {
              const isActive = filterRegion === region;
              const colorMap = {
                Continental: 'bg-region-continental hover:bg-blue-600',
                Madeira: 'bg-region-madeira hover:bg-orange-600',
                Açores: 'bg-region-acores hover:bg-purple-600'
              };

              return (
                <button
                  key={region}
                  onClick={() => handleRegionFilter(region)}
                  className={`
                    flex-1 px-2 py-1 text-xs font-medium rounded-md transition-all
                    ${isActive
                      ? `${colorMap[region]} text-white`
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }
                  `}
                  aria-pressed={isActive}
                >
                  {region}
                </button>
              );
            })}
          </div>
        </div>

        {/* Road list - scrollable area */}
        <div className="flex-1 overflow-hidden">
          <RoadList
            selectedRoadId={selectedRoadId}
            onRoadSelect={(road) => {
              onRoadSelect(road);
              // Close sidebar on mobile after selection
              if (window.innerWidth < 768) {
                setIsOpen(false);
              }
            }}
            filterRegion={filterRegion}
          />
        </div>
      </aside>
    </>
  );
};

Sidebar.propTypes = {
  selectedRoadId: PropTypes.number,
  onRoadSelect: PropTypes.func.isRequired,
  className: PropTypes.string
};

export default Sidebar;
