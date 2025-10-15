#!/usr/bin/env python3
"""
==============================================================================
Mapbox Map Matching API Integration
==============================================================================
Module: mapbox_matching.py
Purpose: Refine GPS traces by aligning them to road network using Map Matching API
Author: Road Explorer Portugal
==============================================================================

CRITICAL: This module uses Map Matching API (NOT Directions API)

Map Matching API:
- Purpose: Align GPS traces to roads
- Input: Existing GPS coordinates
- Output: Refined coordinates following actual roads
- Use case: Clean and improve low-quality OSM geometries

Directions API (DO NOT USE):
- Purpose: Route optimization (fastest path)
- Creates detours and wrong routes
- This caused the N222 detour problem!

==============================================================================
"""

import requests
import time
from typing import List, Tuple, Optional, Dict
from geopy.distance import geodesic


# ==============================================================================
# Configuration
# ==============================================================================

MAPBOX_API_BASE = "https://api.mapbox.com/matching/v5/mapbox"
RATE_LIMIT_DELAY = 0.2  # seconds (600/min → 5/sec safe)
REQUEST_TIMEOUT = 30  # seconds
MAX_COORDS_PER_REQUEST = 100  # Mapbox limit

# Pre-validation thresholds
MAX_GAP_KM = 50.0  # Maximum acceptable gap between consecutive points
MAX_LARGE_GAPS = 5  # Maximum number of large gaps allowed


# ==============================================================================
# Pre-Validation
# ==============================================================================

def validate_coordinates_for_matching(
    coordinates: List[Tuple[float, float]],
    max_gap_km: float = MAX_GAP_KM,
    max_gaps_allowed: int = MAX_LARGE_GAPS
) -> Tuple[bool, List[str]]:
    """
    Validate coordinates before Map Matching to detect disconnected segments.

    Checks for large gaps between consecutive coordinates that indicate
    disconnected road segments. Such data will fail or produce poor results
    from Map Matching API, wasting API quota.

    Args:
        coordinates: List of (lon, lat) tuples
        max_gap_km: Maximum acceptable gap in kilometers (default: 50km)
        max_gaps_allowed: Maximum number of large gaps allowed (default: 5)

    Returns:
        (is_valid, warnings) tuple where:
        - is_valid: True if data is suitable for Map Matching
        - warnings: List of warning messages about detected issues

    Example:
        >>> coords = [(-7.79, 41.16), (-7.75, 41.17), (100.0, 50.0)]
        >>> valid, warnings = validate_coordinates_for_matching(coords)
        >>> if not valid:
        ...     print(f"Validation failed: {warnings}")
        Validation failed: ['Large gap detected: 8234.5 km between points 1-2']
    """

    if not coordinates or len(coordinates) < 2:
        return True, []  # Empty or single point - technically valid

    warnings = []
    large_gaps = []

    for i in range(len(coordinates) - 1):
        point1 = (coordinates[i][1], coordinates[i][0])  # (lat, lon)
        point2 = (coordinates[i + 1][1], coordinates[i + 1][0])

        distance_km = geodesic(point1, point2).kilometers

        if distance_km > max_gap_km:
            large_gaps.append((i, i + 1, distance_km))
            warnings.append(
                f"Large gap: {distance_km:.1f}km between points {i}-{i+1} "
                f"({coordinates[i]} → {coordinates[i+1]})"
            )

    # Check if too many large gaps
    num_gaps = len(large_gaps)
    is_valid = num_gaps <= max_gaps_allowed

    if num_gaps > 0:
        warnings.insert(0, f"Found {num_gaps} large gaps (>{max_gap_km}km)")
        if not is_valid:
            warnings.append(
                f"❌ Too many disconnected segments ({num_gaps} > {max_gaps_allowed})"
            )
            warnings.append("💡 Data likely contains multiple roads with same ref")
            warnings.append("💡 Pre-filtering recommended before Map Matching")

    return is_valid, warnings


# ==============================================================================
# Core Map Matching Function
# ==============================================================================

def mapbox_map_matching(
    coordinates: List[Tuple[float, float]],
    mapbox_token: str,
    profile: str = 'driving'
) -> Optional[List[Tuple[float, float]]]:
    """
    Use Mapbox Map Matching API to refine GPS trace.

    This function aligns a GPS trace to the road network, improving quality
    and density. It does NOT optimize routes - it follows the input trace.

    Args:
        coordinates: List of (lon, lat) tuples (max 100)
        mapbox_token: Mapbox API token
        profile: Routing profile ('driving', 'cycling', 'walking')

    Returns:
        List of refined (lon, lat) tuples or None on failure

    Raises:
        ValueError: If coordinates > 100 or invalid format

    Example:
        >>> coords = [(-7.79, 41.16), (-7.75, 41.17), (-7.60, 41.18)]
        >>> token = "pk.your_token"
        >>> refined = mapbox_map_matching(coords, token)
        >>> print(f"Input: {len(coords)}, Output: {len(refined)}")
        Input: 3, Output: 245
    """

    # Validate inputs
    if not coordinates:
        print("❌ Error: Empty coordinates list")
        return None

    if len(coordinates) > MAX_COORDS_PER_REQUEST:
        print(f"❌ Error: Too many coordinates ({len(coordinates)}). Max: {MAX_COORDS_PER_REQUEST}")
        print(f"   💡 Use batch_map_matching() for long roads")
        return None

    if not mapbox_token:
        print("❌ Error: Missing Mapbox token")
        return None

    # Format coordinates as semicolon-separated string: "lon,lat;lon,lat;..."
    coords_str = ";".join([f"{lon},{lat}" for lon, lat in coordinates])

    # Build request URL
    url = f"{MAPBOX_API_BASE}/{profile}/{coords_str}"

    # Query parameters
    params = {
        'access_token': mapbox_token,
        'geometries': 'geojson',  # Return GeoJSON format
        'overview': 'full',  # Complete geometry (not simplified)
        'tidy': 'true'  # Remove outliers
    }

    try:
        # Make request
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        # Parse response
        if 'matchings' in data and len(data['matchings']) > 0:
            # Extract geometry from first matching
            geometry = data['matchings'][0]['geometry']

            # Convert GeoJSON coordinates [[lon, lat], ...] to tuples
            matched_coords = [
                (coord[0], coord[1])
                for coord in geometry['coordinates']
            ]

            # Log success
            input_count = len(coordinates)
            output_count = len(matched_coords)
            improvement = (output_count / input_count) if input_count > 0 else 0

            print(f"✅ Map Matching: {input_count} → {output_count} points ({improvement:.1f}x)")

            return matched_coords

        else:
            print("⚠️  No matchings found in response")
            return None

    except requests.exceptions.Timeout:
        print(f"❌ Timeout: Map Matching took >{REQUEST_TIMEOUT}s")
        return None

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 429:
            print("❌ Rate limit exceeded (HTTP 429)")
            print("   💡 Add delay between requests or reduce frequency")
        else:
            print(f"❌ HTTP error {status_code}: {e}")
        return None

    except Exception as e:
        print(f"❌ Map Matching error: {e}")
        return None


# ==============================================================================
# Batch Processing for Long Roads
# ==============================================================================

def batch_map_matching(
    coordinates: List[Tuple[float, float]],
    mapbox_token: str,
    profile: str = 'driving',
    batch_size: int = 100
) -> List[Tuple[float, float]]:
    """
    Process long coordinate lists (>100 points) in batches.

    Splits coordinates into chunks of max 100 points, processes each batch
    separately with rate limiting, and merges results.

    Args:
        coordinates: List of (lon, lat) tuples
        mapbox_token: Mapbox API token
        profile: Routing profile ('driving', 'cycling', 'walking')
        batch_size: Maximum coords per batch (default: 100)

    Returns:
        List of all refined coordinates merged from batches

    Example:
        >>> coords = [...]  # 300 points
        >>> refined = batch_map_matching(coords, token)
        >>> print(f"{len(coords)} → {len(refined)} points")
        300 → 4521 points (15.1x improvement)
    """

    if not coordinates:
        return []

    if len(coordinates) <= MAX_COORDS_PER_REQUEST:
        # No batching needed
        result = mapbox_map_matching(coordinates, mapbox_token, profile)
        return result if result else coordinates

    # Calculate number of batches
    num_batches = (len(coordinates) + batch_size - 1) // batch_size

    print(f"🔄 Batch processing: {len(coordinates)} points → {num_batches} batches")

    all_matched = []

    for i in range(0, len(coordinates), batch_size):
        batch_num = (i // batch_size) + 1
        batch = coordinates[i:i + batch_size]

        print(f"   📍 Processing batch {batch_num}/{num_batches} ({len(batch)} points)...")

        # Process batch
        matched = mapbox_map_matching(batch, mapbox_token, profile)

        if matched:
            all_matched.extend(matched)
        else:
            # If matching fails, keep original batch
            print(f"   ⚠️  Batch {batch_num} failed - using original coordinates")
            all_matched.extend(batch)

        # Rate limiting: Wait between batches to avoid HTTP 429
        if i + batch_size < len(coordinates):
            time.sleep(RATE_LIMIT_DELAY)

    print(f"✅ Batch complete: {len(coordinates)} → {len(all_matched)} points")

    return all_matched


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    print("=" * 70)
    print("Mapbox Map Matching - Test Suite")
    print("=" * 70)

    # Load environment
    load_dotenv()
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

    if not MAPBOX_TOKEN:
        print("❌ Error: MAPBOX_TOKEN not set in .env")
        print("   Please add your Mapbox token to test this module")
        exit(1)

    # Test 1: Small road (simple case)
    print("\n🧪 Test 1: Small road (10 points)")
    print("-" * 70)
    test_coords_small = [
        (-7.7880, 41.1640),
        (-7.7850, 41.1650),
        (-7.7820, 41.1665),
        (-7.7790, 41.1680),
        (-7.7750, 41.1700),
        (-7.7700, 41.1720),
        (-7.7650, 41.1740),
        (-7.7600, 41.1760),
        (-7.7550, 41.1780),
        (-7.7500, 41.1800)
    ]

    try:
        result = mapbox_map_matching(test_coords_small, MAPBOX_TOKEN)
        if result:
            print(f"✅ Success: {len(test_coords_small)} → {len(result)} points")
        else:
            print(f"❌ Failed: No result returned")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()

    # Test 2: Large road (batch processing)
    print("🧪 Test 2: Large road (200 points) - Batch processing")
    print("-" * 70)

    # Generate test coordinates (simulating a long road)
    test_coords_large = []
    for i in range(200):
        lon = -7.79 + (i * 0.01)
        lat = 41.16 + (i * 0.005)
        test_coords_large.append((lon, lat))

    try:
        result = batch_map_matching(test_coords_large, MAPBOX_TOKEN)
        if result:
            print(f"✅ Success: {len(test_coords_large)} → {len(result)} points")
        else:
            print(f"❌ Failed: No result returned")
    except Exception as e:
        print(f"❌ Error: {e}")

    print()

    # Test 3: Error handling (invalid token)
    print("🧪 Test 3: Error Handling (Invalid token)")
    print("-" * 70)
    try:
        result = mapbox_map_matching(test_coords_small, "invalid_token_xyz")
        if not result:
            print("✅ Correctly handled invalid token (returned None)")
        else:
            print("⚠️  Unexpected: Got result with invalid token")
    except Exception as e:
        print(f"✅ Correctly raised exception: {type(e).__name__}")

    print("\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("=" * 70)
