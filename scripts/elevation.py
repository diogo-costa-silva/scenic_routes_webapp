#!/usr/bin/env python3
"""
==============================================================================
Elevation Data Functions
==============================================================================
Module: elevation.py
Purpose: Fetch elevation data from Mapbox Tilequery API
Author: Road Explorer Portugal
==============================================================================
"""

import requests
import time
import os
from typing import List, Tuple, Dict, Optional
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# ==============================================================================
# Configuration
# ==============================================================================

MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")
MAPBOX_TILEQUERY_URL = "https://api.mapbox.com/v4/mapbox.mapbox-terrain-v2/tilequery"

# Rate limiting (Mapbox free tier: 100,000 requests/month)
RATE_LIMIT_DELAY = 0.05  # 50ms delay = max 20 requests/second
SAMPLE_INTERVAL = 10  # Sample every Nth point to reduce API calls


# ==============================================================================
# Elevation Fetching
# ==============================================================================

def get_elevation_from_mapbox(lat: float, lon: float) -> Optional[int]:
    """
    Get elevation for a single GPS point from Mapbox Tilequery API.

    Queries Mapbox's terrain contour data to retrieve elevation at a specific
    coordinate. Uses the Tilequery API with mapbox-terrain-v2 dataset.

    Args:
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)

    Returns:
        Optional[int]: Elevation in meters above sea level, or None if:
                       - MAPBOX_TOKEN not configured
                       - API request fails
                       - No elevation data available for this location

    Example:
        >>> elevation = get_elevation_from_mapbox(40.2833, -7.5000)  # Covilhã
        >>> print(f"Elevation: {elevation}m")
        Elevation: 675m

    API Limits:
        - Mapbox free tier: 100,000 requests/month
        - Rate limit: 600 requests/minute
        - Use RATE_LIMIT_DELAY to stay within limits

    Note:
        - Coordinates must be within valid ranges
        - Returns None for ocean points (no elevation data)
        - Accuracy: ±10m for most locations
    """

    if not MAPBOX_TOKEN:
        return None

    try:
        # Build API URL (note: Mapbox uses lon,lat order)
        url = f"{MAPBOX_TILEQUERY_URL}/{lon},{lat}.json"

        # API parameters
        params = {
            "access_token": MAPBOX_TOKEN,
            "layers": "contour"
        }

        # Make request with timeout
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        # Parse JSON response
        data = response.json()

        # Extract elevation from first feature
        if data.get('features') and len(data['features']) > 0:
            elevation = data['features'][0]['properties'].get('ele', 0)
            return int(elevation)

        # No elevation data available for this location
        return None

    except requests.Timeout:
        print(f"   ⚠️  Timeout fetching elevation for ({lat}, {lon})")
        return None
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            print(f"   ❌ Invalid MAPBOX_TOKEN")
        else:
            print(f"   ⚠️  HTTP error {e.response.status_code} for ({lat}, {lon})")
        return None
    except Exception as e:
        print(f"   ⚠️  Error fetching elevation: {e}")
        return None


def get_elevations_for_route(
    coordinates: List[Tuple[float, float]],
    sample_interval: int = SAMPLE_INTERVAL
) -> List[int]:
    """
    Get elevation data for a route, sampling every Nth point.

    Fetches elevation for sampled points along the route to reduce API calls
    while maintaining reasonable accuracy. Includes rate limiting to respect
    Mapbox API guidelines.

    Args:
        coordinates (List[Tuple[float, float]]): List of (lon, lat) tuples
        sample_interval (int): Sample every Nth point (default: 10)

    Returns:
        List[int]: List of elevations in meters (may be shorter than input
                   if some API calls fail)

    Example:
        >>> coords = [(-8.0, 39.5), (-8.01, 39.51), ...]  # 100 points
        >>> elevations = get_elevations_for_route(coords, sample_interval=10)
        >>> print(len(elevations))
        10

    Note:
        - Sampling reduces API calls: 1000 points → 100 calls (interval=10)
        - Rate limiting: 50ms delay between requests
        - Failed requests are skipped (not included in result)
        - Always includes first and last point elevations
    """

    if not coordinates or len(coordinates) < 2:
        return []

    elevations = []

    # Sample coordinates at specified interval
    # Always include first and last points
    sampled_indices = list(range(0, len(coordinates), sample_interval))
    if sampled_indices[-1] != len(coordinates) - 1:
        sampled_indices.append(len(coordinates) - 1)

    print(f"   📊 Sampling {len(sampled_indices)} points from {len(coordinates)} total")
    print(f"   ⏱️  Estimated time: {len(sampled_indices) * RATE_LIMIT_DELAY:.1f}s")

    # Fetch elevations with rate limiting
    for idx, coord_idx in enumerate(sampled_indices):
        lon, lat = coordinates[coord_idx]

        # Fetch elevation
        elevation = get_elevation_from_mapbox(lat, lon)

        if elevation is not None:
            elevations.append(elevation)

        # Rate limiting (except for last request)
        if idx < len(sampled_indices) - 1:
            time.sleep(RATE_LIMIT_DELAY)

        # Progress indicator every 20 points
        if (idx + 1) % 20 == 0:
            print(f"   📍 Progress: {idx + 1}/{len(sampled_indices)} points")

    print(f"   ✅ Fetched {len(elevations)} elevation values")

    return elevations


# ==============================================================================
# Elevation Metrics Calculation
# ==============================================================================

def calculate_elevation_metrics(elevations: List[int]) -> Dict[str, int]:
    """
    Calculate elevation statistics from elevation data.

    Computes maximum, minimum, and cumulative elevation changes along a route.
    Cumulative gain/loss represents total climbing/descending, which can exceed
    the simple difference between start and end elevations.

    Args:
        elevations (List[int]): List of elevations in meters (ordered by route)

    Returns:
        Dict[str, int]: Dictionary with elevation metrics:
            - elevation_max: Maximum altitude (meters)
            - elevation_min: Minimum altitude (meters)
            - elevation_gain: Total cumulative elevation gain (meters)
            - elevation_loss: Total cumulative elevation loss (meters)

    Example:
        >>> elevations = [100, 150, 200, 180, 250, 230]
        >>> metrics = calculate_elevation_metrics(elevations)
        >>> print(f"Max: {metrics['elevation_max']}m")
        Max: 250m
        >>> print(f"Gain: {metrics['elevation_gain']}m")
        Gain: 170m

    Note:
        - Requires at least 2 elevation points
        - Gain/loss are cumulative (sum of all ups/downs)
        - Empty input returns all zeros
    """

    if not elevations or len(elevations) < 1:
        return {
            'elevation_max': 0,
            'elevation_min': 0,
            'elevation_gain': 0,
            'elevation_loss': 0
        }

    # Calculate max and min elevations
    elevation_max = max(elevations)
    elevation_min = min(elevations)

    # Calculate cumulative elevation gain and loss
    elevation_gain = 0
    elevation_loss = 0

    for i in range(len(elevations) - 1):
        diff = elevations[i+1] - elevations[i]

        if diff > 0:
            # Going uphill
            elevation_gain += diff
        elif diff < 0:
            # Going downhill
            elevation_loss += abs(diff)

    return {
        'elevation_max': int(elevation_max),
        'elevation_min': int(elevation_min),
        'elevation_gain': int(elevation_gain),
        'elevation_loss': int(elevation_loss)
    }


def calculate_elevation_for_coordinates(
    coordinates: List[Tuple[float, float]],
    sample_interval: int = SAMPLE_INTERVAL
) -> Dict[str, int]:
    """
    Complete pipeline: fetch elevations and calculate metrics.

    Convenience function that combines elevation fetching and metrics
    calculation in a single call. This is the recommended way to get
    elevation data for a route.

    Args:
        coordinates (List[Tuple[float, float]]): List of (lon, lat) tuples
        sample_interval (int): Sample every Nth point (default: 10)

    Returns:
        Dict[str, int]: Elevation metrics dictionary with:
            - elevation_max: Maximum altitude (meters)
            - elevation_min: Minimum altitude (meters)
            - elevation_gain: Total elevation gain (meters)
            - elevation_loss: Total elevation loss (meters)

    Example:
        >>> coords = [(-8.0, 39.5), (-8.01, 39.51), ...]
        >>> metrics = calculate_elevation_for_coordinates(coords)
        >>> print(f"Elevation gain: {metrics['elevation_gain']}m")
        Elevation gain: 434m

    Note:
        - This function makes API calls to Mapbox
        - Requires MAPBOX_TOKEN in .env
        - Uses rate limiting (50ms delay per request)
        - May take several seconds for long routes
    """

    if not coordinates or len(coordinates) < 2:
        return {
            'elevation_max': 0,
            'elevation_min': 0,
            'elevation_gain': 0,
            'elevation_loss': 0
        }

    # Step 1: Fetch elevations for sampled route points
    print(f"   🏔️  Fetching elevation data...")
    elevations = get_elevations_for_route(coordinates, sample_interval)

    # Step 2: Calculate metrics from elevation data
    if not elevations:
        print(f"   ⚠️  No elevation data retrieved")
        return {
            'elevation_max': 0,
            'elevation_min': 0,
            'elevation_gain': 0,
            'elevation_loss': 0
        }

    metrics = calculate_elevation_metrics(elevations)

    print(f"   ✅ Elevation metrics calculated:")
    print(f"      Max: {metrics['elevation_max']}m")
    print(f"      Min: {metrics['elevation_min']}m")
    print(f"      Gain: {metrics['elevation_gain']}m")
    print(f"      Loss: {metrics['elevation_loss']}m")

    return metrics


# ==============================================================================
# Helper Functions
# ==============================================================================

def estimate_api_calls(coordinates: List[Tuple[float, float]], sample_interval: int) -> int:
    """
    Estimate number of API calls needed.

    Args:
        coordinates (List[Tuple[float, float]]): List of coordinates
        sample_interval (int): Sample interval

    Returns:
        int: Estimated number of API calls
    """
    return len(coordinates) // sample_interval


def estimate_time(coordinates: List[Tuple[float, float]], sample_interval: int) -> float:
    """
    Estimate time needed for elevation fetching (with rate limiting).

    Args:
        coordinates (List[Tuple[float, float]]): List of coordinates
        sample_interval (int): Sample interval

    Returns:
        float: Estimated time in seconds
    """
    api_calls = estimate_api_calls(coordinates, sample_interval)
    return api_calls * RATE_LIMIT_DELAY


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Elevation Data - Placeholder Test")
    print("=" * 70)

    # Check if MAPBOX_TOKEN is set
    if MAPBOX_TOKEN:
        print(f"✅ MAPBOX_TOKEN is set (starts with: {MAPBOX_TOKEN[:10]}...)")
    else:
        print("⚠️  MAPBOX_TOKEN not found in .env file")
        print("   Copy .env.example to .env and add your token")

    # Test with sample coordinates (Covilhã, Portugal)
    test_lat, test_lon = 40.2833, -7.5000
    print(f"\nTesting elevation fetch for: ({test_lat}, {test_lon})")

    elevation = get_elevation_from_mapbox(test_lat, test_lon)
    print(f"Result: {elevation}m")

    # Test metrics calculation
    test_elevations = [100, 150, 200, 180, 250, 230]
    print(f"\nTesting metrics with sample elevations: {test_elevations}")

    metrics = calculate_elevation_metrics(test_elevations)
    print(f"Metrics: {metrics}")

    print("\n✅ Module loaded successfully (placeholder mode)")
    print("ℹ️  Actual implementation coming soon!")
