import PropTypes from 'prop-types';

/**
 * RegionFilter Component
 *
 * Filter roads by region with responsive design:
 * - Desktop (≥768px): Horizontal tabs
 * - Mobile (<768px): Dropdown/select
 *
 * Options: All, Continental 🏔️, Madeira 🏝️, Açores 🌋
 *
 * @param {Object} props
 * @param {string|null} props.selectedRegion - Currently selected region (null = All)
 * @param {Function} props.onRegionChange - Callback when region changes
 */
const RegionFilter = ({ selectedRegion = null, onRegionChange }) => {
  const regions = [
    { value: null, label: 'All', icon: '🌍', color: 'bg-gray-500' },
    { value: 'Continental', label: 'Continental', icon: '🏔️', color: 'bg-region-continental' },
    { value: 'Madeira', label: 'Madeira', icon: '🏝️', color: 'bg-region-madeira' },
    { value: 'Açores', label: 'Açores', icon: '🌋', color: 'bg-region-acores' }
  ];

  const handleRegionClick = (regionValue) => {
    // Toggle: if clicking same region, deselect (go to All)
    onRegionChange(regionValue === selectedRegion ? null : regionValue);
  };

  const handleDropdownChange = (e) => {
    const value = e.target.value === '' ? null : e.target.value;
    onRegionChange(value);
  };

  const selectedRegionData = regions.find(r => r.value === selectedRegion) || regions[0];

  return (
    <>
      {/* Desktop: Tabs (≥768px) */}
      <div className="hidden md:flex gap-2" role="tablist" aria-label="Region filter">
        {regions.map((region) => {
          const isActive = region.value === selectedRegion;

          return (
            <button
              key={region.value || 'all'}
              onClick={() => handleRegionClick(region.value)}
              role="tab"
              aria-selected={isActive}
              aria-label={`Filter by ${region.label}`}
              className={`
                flex-1 px-3 py-2 text-sm font-medium rounded-md
                transition-all duration-200
                focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-1
                ${isActive
                  ? `${region.color} text-white shadow-md transform scale-105`
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-sm'
                }
              `}
            >
              <span className="mr-1.5" aria-hidden="true">{region.icon}</span>
              <span>{region.label}</span>
            </button>
          );
        })}
      </div>

      {/* Mobile: Dropdown (<768px) */}
      <div className="md:hidden">
        <label htmlFor="region-select" className="sr-only">
          Select region
        </label>
        <div className="relative">
          {/* Icon prefix */}
          <span
            className="absolute left-3 top-1/2 -translate-y-1/2 text-lg pointer-events-none"
            aria-hidden="true"
          >
            {selectedRegionData.icon}
          </span>

          {/* Dropdown */}
          <select
            id="region-select"
            value={selectedRegion || ''}
            onChange={handleDropdownChange}
            className="w-full pl-10 pr-10 py-2.5 text-sm font-medium
                       bg-white border border-gray-300 rounded-lg
                       appearance-none cursor-pointer
                       focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                       transition-all"
          >
            {regions.map((region) => (
              <option key={region.value || 'all'} value={region.value || ''}>
                {region.icon} {region.label}
              </option>
            ))}
          </select>

          {/* Dropdown arrow icon */}
          <svg
            className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>
    </>
  );
};

RegionFilter.propTypes = {
  selectedRegion: PropTypes.oneOf(['Continental', 'Madeira', 'Açores', null]),
  onRegionChange: PropTypes.func.isRequired
};

export default RegionFilter;
