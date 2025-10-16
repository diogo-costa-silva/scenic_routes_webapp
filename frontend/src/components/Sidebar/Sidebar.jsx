import { useState } from 'react';
import PropTypes from 'prop-types';
import RoadList from './RoadList';
import SearchBox from './SearchBox';
import RegionFilter from './RegionFilter';
import useDebouncedValue from '../../hooks/useDebouncedValue';

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

  // Debounce search query (300ms delay)
  const debouncedSearchQuery = useDebouncedValue(searchQuery, 300);

  const toggleSidebar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Mobile hamburger button */}
      <button
        onClick={toggleSidebar}
        className="fixed top-24 left-4 z-50 md:hidden bg-white rounded-lg shadow-lg p-3 hover:bg-gray-50 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center"
        aria-label={isOpen ? 'Close road navigation menu' : 'Open road navigation menu'}
        aria-expanded={isOpen}
        aria-controls="road-navigation"
      >
        <svg
          className="w-6 h-6 text-gray-700"
          fill="none"
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth="2"
          viewBox="0 0 24 24"
          stroke="currentColor"
          aria-hidden="true"
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
          onKeyDown={(e) => {
            if (e.key === 'Escape') {
              toggleSidebar();
            }
          }}
          role="button"
          tabIndex={0}
          aria-label="Close sidebar"
        />
      )}

      {/* Sidebar panel */}
      <nav
        id="road-navigation"
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
        role="navigation"
        aria-label="Road navigation"
        aria-hidden={!isOpen && 'md:hidden'}
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
          <SearchBox
            value={searchQuery}
            onChange={setSearchQuery}
            placeholder="Search roads (e.g., N222)..."
          />

          {/* Region filter */}
          <div className="mt-3">
            <RegionFilter
              selectedRegion={filterRegion}
              onRegionChange={setFilterRegion}
            />
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
            searchQuery={debouncedSearchQuery}
          />
        </div>
      </nav>
    </>
  );
};

Sidebar.propTypes = {
  selectedRoadId: PropTypes.number,
  onRoadSelect: PropTypes.func.isRequired,
  className: PropTypes.string
};

export default Sidebar;
