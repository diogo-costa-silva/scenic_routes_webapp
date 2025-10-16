import PropTypes from 'prop-types';
import useRoads from '../../hooks/useRoads';
import RoadListItem from './RoadListItem';

/**
 * RoadList Component
 *
 * Fetches and displays all roads grouped by region:
 * - Continental
 * - Madeira
 * - Açores
 *
 * Handles loading, error, and empty states.
 *
 * @param {Object} props
 * @param {number|null} props.selectedRoadId - ID of currently selected road
 * @param {Function} props.onRoadSelect - Callback when a road is clicked
 * @param {string|null} props.filterRegion - Optional region filter
 * @param {string} props.searchQuery - Search query to filter roads by code or name
 */
const RoadList = ({ selectedRoadId = null, onRoadSelect, filterRegion = null, searchQuery = '' }) => {
  const {
    filteredRoads,
    loading,
    error,
    refetch,
    groupedRoads,
    isEmpty,
    isFiltered,
    resultsCount
  } = useRoads({
    region: filterRegion,
    searchQuery: searchQuery
  });

  // Loading skeleton
  if (loading) {
    return (
      <div className="space-y-2 p-4">
        <div className="text-sm text-gray-500 mb-4">Loading roads...</div>
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
            <div className="h-3 bg-gray-100 rounded w-2/3 mb-3"></div>
            <div className="flex gap-2">
              <div className="h-6 bg-gray-100 rounded w-16"></div>
              <div className="h-6 bg-gray-100 rounded w-16"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Error state
  if (error) {
    const getErrorContent = () => {
      switch (error.type) {
        case 'NO_DATA':
          return {
            icon: '📭',
            title: 'No Roads Yet',
            message: 'The database is empty. Add roads using the Python processing scripts.',
            showRetry: false
          };
        case 'FETCH_ERROR':
          return {
            icon: '❌',
            title: 'Failed to Load Roads',
            message: error.details || 'Unable to fetch roads from database.',
            showRetry: true
          };
        default:
          return {
            icon: '⚠️',
            title: 'Something Went Wrong',
            message: error.message || 'An unexpected error occurred.',
            showRetry: true
          };
      }
    };

    const errorContent = getErrorContent();

    return (
      <div className="p-6 text-center">
        <div className="text-5xl mb-3">{errorContent.icon}</div>
        <h3 className="font-semibold text-gray-800 mb-2">{errorContent.title}</h3>
        <p className="text-sm text-gray-600 mb-4">{errorContent.message}</p>

        {errorContent.showRetry && (
          <button
            onClick={refetch}
            className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-orange-600 transition-colors text-sm font-medium"
          >
            🔄 Try Again
          </button>
        )}

        <div className="mt-4 p-3 bg-gray-50 rounded-lg text-left">
          <p className="text-xs text-gray-600 font-semibold mb-1">💡 Setup Checklist:</p>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>✓ Supabase project created</li>
            <li>✓ Schema applied (scripts/schema.sql)</li>
            <li>✓ Test data loaded (scripts/test_data.sql)</li>
            <li>✓ .env file configured with credentials</li>
          </ul>
        </div>
      </div>
    );
  }

  // Empty state (no error, but no data in database)
  if (isEmpty) {
    return (
      <div className="p-6 text-center">
        <div className="text-5xl mb-3">🗺️</div>
        <h3 className="font-semibold text-gray-800 mb-2">No Roads Available</h3>
        <p className="text-sm text-gray-600">
          Start by adding roads using the Python scripts.
        </p>
      </div>
    );
  }

  // No results after filtering (search + region)
  if (isFiltered && resultsCount === 0) {
    const hasSearch = searchQuery.trim().length > 0;
    const hasRegion = filterRegion !== null;

    // Region icon mapping
    const regionIcons = {
      Continental: '🏔️',
      Madeira: '🏝️',
      Açores: '🌋'
    };

    let icon = '🔍';
    let title = 'No Results Found';
    let message = '';

    if (hasSearch && hasRegion) {
      // Both search and region filter active
      icon = regionIcons[filterRegion] || '🔍';
      title = 'No Matching Roads';
      message = `No roads in ${filterRegion} matching "${searchQuery}".`;
    } else if (hasSearch) {
      // Only search active
      icon = '🔍';
      title = 'No Matching Roads';
      message = `No roads found for "${searchQuery}". Try a different search term.`;
    } else if (hasRegion) {
      // Only region filter active
      icon = regionIcons[filterRegion] || '📍';
      title = `No Roads in ${filterRegion}`;
      message = `No roads available in ${filterRegion} yet.`;
    }

    return (
      <div className="p-6 text-center">
        <div className="text-5xl mb-3">{icon}</div>
        <h3 className="font-semibold text-gray-800 mb-2">{title}</h3>
        <p className="text-sm text-gray-600 mb-4">{message}</p>
        <p className="text-xs text-gray-500">
          Try adjusting your filters or search terms.
        </p>
      </div>
    );
  }

  // Region order for consistent display
  const regionOrder = ['Continental', 'Madeira', 'Açores'];
  const regionsToDisplay = regionOrder.filter(region => groupedRoads[region]?.length > 0);

  return (
    <div className="overflow-y-auto h-full">
      {/* Total count */}
      <div className="px-4 py-3 bg-gray-50 border-b border-gray-200 sticky top-0 z-10">
        <p className="text-sm text-gray-600">
          <span className="font-semibold text-gray-800">{resultsCount}</span>
          {isFiltered ? ' result' + (resultsCount !== 1 ? 's' : '') : ' roads available'}
        </p>
      </div>

      {/* Roads grouped by region */}
      <div>
        {regionsToDisplay.map((region) => {
          const regionRoads = groupedRoads[region];
          const regionColorMap = {
            Continental: 'text-region-continental',
            Madeira: 'text-region-madeira',
            Açores: 'text-region-acores'
          };

          return (
            <div key={region} className="mb-4">
              {/* Region header */}
              <div className="px-4 py-2 bg-gray-100 border-y border-gray-200">
                <h2 className={`font-bold text-sm uppercase tracking-wide ${regionColorMap[region]}`}>
                  {region}
                  <span className="ml-2 text-gray-500 font-normal">
                    ({regionRoads.length})
                  </span>
                </h2>
              </div>

              {/* Roads in this region */}
              <div className="divide-y divide-gray-100">
                {regionRoads.map((road) => (
                  <RoadListItem
                    key={road.id}
                    road={road}
                    isSelected={road.id === selectedRoadId}
                    onClick={onRoadSelect}
                  />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

RoadList.propTypes = {
  selectedRoadId: PropTypes.number,
  onRoadSelect: PropTypes.func.isRequired,
  filterRegion: PropTypes.oneOf(['Continental', 'Madeira', 'Açores', null]),
  searchQuery: PropTypes.string
};

export default RoadList;
