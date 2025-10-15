/**
 * Utility functions for formatting road metrics and data
 * Used across the Road Explorer application to ensure consistent formatting
 */

/**
 * Format distance in kilometers
 * @param {number|null} km - Distance in kilometers
 * @returns {string} Formatted distance (e.g., "27.3 km") or "N/A"
 */
export const formatDistance = (km) => {
  if (km === null || km === undefined || isNaN(km)) {
    return 'N/A';
  }
  return `${formatNumber(km, 1)} km`;
};

/**
 * Format elevation in meters
 * @param {number|null} meters - Elevation in meters
 * @returns {string} Formatted elevation (e.g., "523m") or "N/A"
 */
export const formatElevation = (meters) => {
  if (meters === null || meters === undefined || isNaN(meters)) {
    return 'N/A';
  }
  return `${Math.round(meters)}m`;
};

/**
 * Format surface type with verification indicator
 * @param {string|null} surface - Surface type (e.g., "asphalt", "gravel")
 * @param {boolean} verified - Whether the surface has been verified
 * @returns {string} Formatted surface (e.g., "Alcatroado ✓" or "Gravilha (não verificado)")
 */
export const formatSurface = (surface, verified = false) => {
  if (!surface) {
    return 'N/A';
  }

  // Translation map for surface types
  const surfaceTranslations = {
    asphalt: 'Alcatroado',
    gravel: 'Gravilha',
    unpaved: 'Terra batida',
    mixed: 'Misto',
    paved: 'Pavimentado',
  };

  const translatedSurface = surfaceTranslations[surface.toLowerCase()] || surface;
  const verificationIndicator = verified ? ' ✓' : ' (não verificado)';

  return `${translatedSurface}${verificationIndicator}`;
};

/**
 * Format a number with specified decimal places
 * @param {number|null} num - Number to format
 * @param {number} decimals - Number of decimal places (default: 1)
 * @returns {string} Formatted number or "0"
 */
export const formatNumber = (num, decimals = 1) => {
  if (num === null || num === undefined || isNaN(num)) {
    return '0';
  }
  return Number(num).toFixed(decimals);
};

/**
 * Format curve count with label
 * @param {number|null} count - Number of curves
 * @param {string} type - Type of curve (e.g., "suaves", "moderadas", "apertadas")
 * @returns {string} Formatted curve count (e.g., "82 suaves") or "N/A"
 */
export const formatCurveCount = (count, type = '') => {
  if (count === null || count === undefined || isNaN(count)) {
    return 'N/A';
  }
  return type ? `${count} ${type}` : `${count}`;
};

/**
 * Format elevation gain/loss with sign
 * @param {number|null} meters - Elevation change in meters
 * @param {boolean} isGain - Whether this is elevation gain (true) or loss (false)
 * @returns {string} Formatted elevation change (e.g., "+434m" or "-434m") or "N/A"
 */
export const formatElevationChange = (meters, isGain = true) => {
  if (meters === null || meters === undefined || isNaN(meters)) {
    return 'N/A';
  }
  const sign = isGain ? '+' : '-';
  return `${sign}${Math.round(Math.abs(meters))}m`;
};

/**
 * Check if a value is valid (not null, undefined, or NaN)
 * @param {any} value - Value to check
 * @returns {boolean} True if value is valid
 */
export const isValidValue = (value) => {
  return value !== null && value !== undefined && !isNaN(value);
};
