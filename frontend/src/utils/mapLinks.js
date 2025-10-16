/**
 * Map Links Utility
 *
 * Generate external map service URLs for road navigation.
 * Currently supports:
 * - Google Maps (Directions API)
 *
 * Future support:
 * - Apple Maps
 * - Waze
 * - HERE WeGo
 */

import { validatePortugalCoordinates } from './geoUtils';

/**
 * Generate Google Maps Directions URL
 *
 * Creates a URL that opens Google Maps with directions to the specified destination.
 * On mobile, this will attempt to open the Google Maps app if installed.
 *
 * Uses Google Maps Directions API URL format:
 * https://developers.google.com/maps/documentation/urls/get-started
 *
 * @param {number} lat - Destination latitude
 * @param {number} lon - Destination longitude
 * @param {string} [roadName] - Optional road name for display
 * @returns {Object} Result object with success status and url/error
 *
 * @example
 * const result = generateGoogleMapsUrl(41.1640, -7.7538, "N222");
 * if (result.success) {
 *   window.open(result.url, '_blank', 'noopener,noreferrer');
 * }
 */
export const generateGoogleMapsUrl = (lat, lon, roadName = '') => {
  // Validation: Check if coordinates are provided
  if (lat === undefined || lon === undefined) {
    return {
      success: false,
      error: 'Latitude and longitude are required'
    };
  }

  // Validation: Check if coordinates are numbers
  if (typeof lat !== 'number' || typeof lon !== 'number') {
    return {
      success: false,
      error: 'Latitude and longitude must be numbers'
    };
  }

  // Validation: Check if coordinates are finite
  if (!isFinite(lat) || !isFinite(lon)) {
    return {
      success: false,
      error: 'Latitude and longitude must be finite numbers'
    };
  }

  // Validation: Check if coordinates are within valid ranges
  if (lat < -90 || lat > 90) {
    return {
      success: false,
      error: `Invalid latitude: ${lat} (must be between -90 and 90)`
    };
  }

  if (lon < -180 || lon > 180) {
    return {
      success: false,
      error: `Invalid longitude: ${lon} (must be between -180 and 180)`
    };
  }

  // Warning: Check if coordinates are within Portugal (not an error, just a warning)
  if (!validatePortugalCoordinates(lat, lon)) {
    console.warn(
      `Coordinates (${lat}, ${lon}) are outside Portugal bounds. ` +
      `This may be intentional, but please verify.`
    );
  }

  try {
    // Build Google Maps Directions URL
    // Format: https://www.google.com/maps/dir/?api=1&destination=LAT,LON&destination_place_id=PLACE_ID
    const baseUrl = 'https://www.google.com/maps/dir/';
    const params = new URLSearchParams({
      api: '1',
      destination: `${lat},${lon}`
    });

    // Add optional label (destination name)
    if (roadName && roadName.trim()) {
      params.append('destination_label', roadName.trim());
    }

    const url = `${baseUrl}?${params.toString()}`;

    return {
      success: true,
      url
    };
  } catch (error) {
    console.error('Error generating Google Maps URL:', error);
    return {
      success: false,
      error: `Failed to generate URL: ${error.message}`
    };
  }
};

/**
 * Generate Google Maps Place URL (view only, no directions)
 *
 * Creates a URL that opens Google Maps centered on the specified location.
 * Useful for viewing a location without requesting directions.
 *
 * @param {number} lat - Location latitude
 * @param {number} lon - Location longitude
 * @param {number} [zoom=15] - Zoom level (1-20, default 15)
 * @returns {Object} Result object with success status and url/error
 *
 * @example
 * const result = generateGoogleMapsPlaceUrl(41.1640, -7.7538, 14);
 * if (result.success) {
 *   window.open(result.url, '_blank', 'noopener,noreferrer');
 * }
 */
export const generateGoogleMapsPlaceUrl = (lat, lon, zoom = 15) => {
  // Validation: Check if coordinates are provided
  if (lat === undefined || lon === undefined) {
    return {
      success: false,
      error: 'Latitude and longitude are required'
    };
  }

  // Validation: Check if coordinates are numbers
  if (typeof lat !== 'number' || typeof lon !== 'number') {
    return {
      success: false,
      error: 'Latitude and longitude must be numbers'
    };
  }

  // Validation: Check zoom level
  if (zoom < 1 || zoom > 20) {
    return {
      success: false,
      error: 'Zoom level must be between 1 and 20'
    };
  }

  try {
    // Build Google Maps Place URL
    // Format: https://www.google.com/maps/@LAT,LON,ZOOMz
    const url = `https://www.google.com/maps/@${lat},${lon},${zoom}z`;

    return {
      success: true,
      url
    };
  } catch (error) {
    console.error('Error generating Google Maps place URL:', error);
    return {
      success: false,
      error: `Failed to generate URL: ${error.message}`
    };
  }
};

/**
 * Open URL in new tab/window with security settings
 *
 * Opens the URL in a new browser tab with proper security attributes
 * (noopener, noreferrer) to prevent security vulnerabilities.
 *
 * @param {string} url - URL to open
 * @returns {boolean} True if successfully opened
 *
 * @example
 * const result = generateGoogleMapsUrl(41.1640, -7.7538);
 * if (result.success) {
 *   openInNewTab(result.url);
 * }
 */
export const openInNewTab = (url) => {
  if (!url || typeof url !== 'string') {
    console.error('Invalid URL:', url);
    return false;
  }

  try {
    // Open in new tab with security attributes
    // noopener: Prevents the new page from accessing window.opener
    // noreferrer: Prevents the browser from sending referrer information
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');

    // Check if popup was blocked
    if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
      console.warn('Popup blocked by browser. Please allow popups for this site.');
      return false;
    }

    return true;
  } catch (error) {
    console.error('Error opening URL in new tab:', error);
    return false;
  }
};

/**
 * Generate route URL for road object
 *
 * Convenience function that extracts coordinates from a road object
 * and generates a Google Maps URL.
 *
 * @param {Object} road - Road object
 * @param {number} road.start_lat - Start latitude
 * @param {number} road.start_lon - Start longitude
 * @param {string} [road.code] - Road code for label
 * @returns {Object} Result object with success status and url/error
 *
 * @example
 * const result = generateRouteUrl(selectedRoad);
 * if (result.success) {
 *   openInNewTab(result.url);
 * }
 */
export const generateRouteUrl = (road) => {
  if (!road) {
    return {
      success: false,
      error: 'Road object is required'
    };
  }

  // Check if road has start coordinates
  if (road.start_lat === undefined || road.start_lon === undefined) {
    return {
      success: false,
      error: 'Road must have start_lat and start_lon coordinates'
    };
  }

  // Generate Google Maps URL with road code as label
  return generateGoogleMapsUrl(
    road.start_lat,
    road.start_lon,
    road.code || ''
  );
};
