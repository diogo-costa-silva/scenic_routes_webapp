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

    Args:
        lat (float): Latitude
        lon (float): Longitude

    Returns:
        Optional[int]: Elevation in meters, or None if request fails

    Example:
        >>> elevation = get_elevation_from_mapbox(39.5, -8.0)
        >>> print(f"Elevation: {elevation}m")
        Elevation: 523m
    """

    # Placeholder implementation
    print(f"🚧 [PLACEHOLDER] Would fetch elevation for ({lat}, {lon})")

    if not MAPBOX_TOKEN:
        print("⚠️  Warning: MAPBOX_TOKEN not set in .env")
        return None

    # TODO: Implement actual Mapbox Tilequery API request
    # url = f"{MAPBOX_TILEQUERY_URL}/{lon},{lat}.json"
    # params = {
    #     "access_token": MAPBOX_TOKEN,
    #     "layers": "contour"
    # }
    # response = requests.get(url, params=params)
    # data = response.json()
    # if data.get('features'):
    #     return data['features'][0]['properties'].get('ele', 0)

    return None


def get_elevations_for_route(
    coordinates: List[Tuple[float, float]],
    sample_interval: int = SAMPLE_INTERVAL
) -> List[int]:
    """
    Get elevation data for a route, sampling every Nth point.

    Args:
        coordinates (List[Tuple[float, float]]): List of (lon, lat) tuples
        sample_interval (int): Sample every Nth point (default: 10)

    Returns:
        List[int]: List of elevations in meters

    Note:
        Sampling reduces API calls. For a 1000-point route with interval=10,
        only 100 API requests will be made.
    """

    # Placeholder implementation
    print(f"🚧 [PLACEHOLDER] Would fetch elevations for route")
    print(f"   Total points: {len(coordinates)}")
    print(f"   Sample interval: {sample_interval}")
    print(f"   API calls needed: {len(coordinates) // sample_interval}")

    # TODO: Implement batched elevation fetching
    # Sample coordinates at interval
    # Fetch elevations with rate limiting
    # Return list of elevations

    return []


# ==============================================================================
# Elevation Metrics Calculation
# ==============================================================================

def calculate_elevation_metrics(elevations: List[int]) -> Dict[str, int]:
    """
    Calculate elevation statistics from elevation data.

    Args:
        elevations (List[int]): List of elevations in meters

    Returns:
        Dict[str, int]: Dictionary with elevation metrics:
            - elevation_max: Maximum altitude (meters)
            - elevation_min: Minimum altitude (meters)
            - elevation_gain: Total elevation gain (meters)
            - elevation_loss: Total elevation loss (meters)

    Example:
        >>> elevations = [100, 150, 200, 180, 250]
        >>> metrics = calculate_elevation_metrics(elevations)
        >>> print(f"Max: {metrics['elevation_max']}m")
        Max: 250m
    """

    # Placeholder implementation
    print(f"🚧 [PLACEHOLDER] Would calculate elevation metrics")
    print(f"   Elevation points: {len(elevations)}")

    if not elevations:
        return {
            'elevation_max': 0,
            'elevation_min': 0,
            'elevation_gain': 0,
            'elevation_loss': 0
        }

    # TODO: Implement elevation metrics calculation
    # elevation_max = max(elevations)
    # elevation_min = min(elevations)
    #
    # Calculate cumulative gain/loss
    # elevation_gain = 0
    # elevation_loss = 0
    # for i in range(len(elevations) - 1):
    #     diff = elevations[i+1] - elevations[i]
    #     if diff > 0:
    #         elevation_gain += diff
    #     else:
    #         elevation_loss += abs(diff)

    return {
        'elevation_max': 0,
        'elevation_min': 0,
        'elevation_gain': 0,
        'elevation_loss': 0
    }


def calculate_elevation_for_coordinates(
    coordinates: List[Tuple[float, float]],
    sample_interval: int = SAMPLE_INTERVAL
) -> Dict[str, int]:
    """
    Complete pipeline: fetch elevations and calculate metrics.

    Args:
        coordinates (List[Tuple[float, float]]): List of (lon, lat) tuples
        sample_interval (int): Sample every Nth point

    Returns:
        Dict[str, int]: Elevation metrics dictionary

    Example:
        >>> coords = [(-8.0, 39.5), (-8.01, 39.51), ...]
        >>> metrics = calculate_elevation_for_coordinates(coords)
        >>> print(f"Elevation gain: {metrics['elevation_gain']}m")
    """

    # Placeholder implementation
    print(f"🚧 [PLACEHOLDER] Complete elevation pipeline")

    # TODO: Implement complete pipeline
    # 1. Fetch elevations for route
    # 2. Calculate metrics
    # 3. Return combined results

    return calculate_elevation_metrics([])


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
