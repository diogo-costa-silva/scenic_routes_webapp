import { useRef, useEffect } from 'react';
import PropTypes from 'prop-types';

/**
 * SearchBox Component
 *
 * Search input with:
 * - Search icon (🔍)
 * - Clear button (X) when text present
 * - Keyboard shortcuts:
 *   - "/" → Focus input
 *   - Esc → Clear input
 *
 * Note: Debouncing should be handled by parent component using useDebouncedValue
 *
 * @param {Object} props
 * @param {string} props.value - Current search value
 * @param {Function} props.onChange - Callback when value changes
 * @param {string} props.placeholder - Input placeholder text
 */
const SearchBox = ({
  value = '',
  onChange,
  placeholder = 'Search roads (e.g., N222)...'
}) => {
  const inputRef = useRef(null);

  /**
   * Keyboard shortcuts handler
   * "/" → Focus input
   * Esc → Clear input
   */
  useEffect(() => {
    const handleKeyDown = (e) => {
      // "/" → Focus search input (unless already in an input/textarea)
      if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
        e.preventDefault();
        inputRef.current?.focus();
      }

      // Esc → Clear search (only if search input is focused)
      if (e.key === 'Escape' && document.activeElement === inputRef.current) {
        e.preventDefault();
        onChange('');
        inputRef.current?.blur(); // Optional: remove focus after clearing
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onChange]);

  const handleChange = (e) => {
    onChange(e.target.value);
  };

  const handleClear = () => {
    onChange('');
    inputRef.current?.focus(); // Keep focus on input after clearing
  };

  const showClearButton = value.length > 0;

  return (
    <div className="relative">
      {/* Search Icon */}
      <svg
        className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none"
        fill="none"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>

      {/* Search Input */}
      <input
        ref={inputRef}
        type="text"
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full px-3 py-2 pl-9 pr-9 border border-gray-300 rounded-lg
                   focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent
                   text-sm transition-all"
        aria-label="Search roads"
      />

      {/* Clear Button (X) - only shown when there's text */}
      {showClearButton && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2
                     text-gray-400 hover:text-gray-600
                     transition-colors focus:outline-none focus:text-gray-600"
          aria-label="Clear search"
          tabIndex={0}
        >
          <svg
            className="w-4 h-4"
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
      )}

      {/* Keyboard Hint (subtle) */}
      {!value && (
        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <kbd className="hidden sm:inline-block px-1.5 py-0.5 text-xs text-gray-400 bg-gray-100 border border-gray-200 rounded">
            /
          </kbd>
        </div>
      )}
    </div>
  );
};

SearchBox.propTypes = {
  value: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  placeholder: PropTypes.string
};

export default SearchBox;
