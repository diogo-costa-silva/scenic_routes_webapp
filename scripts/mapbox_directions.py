#!/usr/bin/env python3
"""
==============================================================================
Mapbox Directions API Module (Layer 4)
==============================================================================
Module: mapbox_directions.py
Purpose: Generate route geometries using Mapbox Directions API with auto-waypoints

IMPORTANT NOTES:
- Directions API generates OPTIMIZED ROUTES (shortest/fastest)
- May take detours or shortcuts
- Different from Map Matching API which aligns GPS traces to roads
- Use for cases where no GPS trace exists

Use Cases:
- Long distance roads where OSM data is fragmented
- Routes between waypoints where we need detailed geometry
- Cases where we trust the routing algorithm

Layer 4 Integration:
- Auto-generates waypoints from town names using Nominatim
- Calls Directions API to get complete route
- Used as last resort when OSM/Map Matching fail

NOT recommended for:
- Roads where precise geometry is critical
- Cases where you have actual GPS traces (use Map Matching instead)
==============================================================================
"""

import requests
from typing import List, Tuple, Optional
import time
from geopy.distance import geodesic

# Import our waypoint generator
from waypoint_generator import generate_waypoints_for_road


def mapbox_directions(
    coordinates: List[Tuple[float, float]],
    mapbox_token: str,
    profile: str = "driving",
    overview: str = "full",
    delay_ms: int = 200
) -> Optional[List[Tuple[float, float]]]:
    """
    Generate route geometry using Mapbox Directions API.

    Args:
        coordinates: List of (lon, lat) tuples (waypoints)
        mapbox_token: Mapbox API token
        profile: Routing profile (driving, walking, cycling)
        overview: full (all points) or simplified (fewer points)
        delay_ms: Delay between requests in milliseconds (rate limiting)

    Returns:
        List of (lon, lat) tuples representing the route, or None if failed

    Raises:
        requests.exceptions.HTTPError: If API request fails

    Example:
        >>> coords = [(-7.4688, 41.7402), (-7.7441, 41.3006)]  # Chaves → Vila Real
        >>> route = mapbox_directions(coords, "pk.xxx")
        >>> len(route)
        1234  # Detailed route with many points
    """
    if not mapbox_token:
        raise ValueError("Mapbox token is required")

    if len(coordinates) < 2:
        raise ValueError("Need at least 2 coordinates")

    if len(coordinates) > 25:
        raise ValueError("Directions API supports max 25 waypoints per request")

    # Format coordinates as "lon1,lat1;lon2,lat2;..."
    coords_str = ";".join([f"{lon},{lat}" for lon, lat in coordinates])

    # Build API URL
    url = (
        f"https://api.mapbox.com/directions/v5/mapbox/{profile}/{coords_str}"
        f"?access_token={mapbox_token}"
        f"&geometries=geojson"
        f"&overview={overview}"
    )

    # Rate limiting delay
    if delay_ms > 0:
        time.sleep(delay_ms / 1000.0)

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        if 'routes' not in data or not data['routes']:
            print(f"❌ No routes found in Directions API response")
            return None

        # Extract geometry from first route
        route = data['routes'][0]
        geometry = route['geometry']

        if geometry['type'] != 'LineString':
            print(f"❌ Unexpected geometry type: {geometry['type']}")
            return None

        # Geometry coordinates are already in [lon, lat] format
        route_coords = [tuple(coord) for coord in geometry['coordinates']]

        # Get route distance for logging
        distance_m = route.get('distance', 0)
        duration_s = route.get('duration', 0)

        print(f"✅ Directions API:")
        print(f"   Waypoints: {len(coordinates)}")
        print(f"   Route points: {len(route_coords)}")
        print(f"   Distance: {distance_m / 1000:.2f} km")
        print(f"   Duration: {duration_s / 60:.1f} min")

        return route_coords

    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP error {e.response.status_code}: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None


def directions_with_multiple_waypoints(
    waypoints: List[Tuple[float, float]],
    mapbox_token: str,
    max_waypoints_per_request: int = 25
) -> Optional[List[Tuple[float, float]]]:
    """
    Generate route through many waypoints by batching requests.

    Directions API has limit of 25 waypoints per request.
    This function splits into batches and merges results.

    Args:
        waypoints: List of (lon, lat) tuples
        mapbox_token: Mapbox API token
        max_waypoints_per_request: Max waypoints per API call (default: 25)

    Returns:
        List of (lon, lat) tuples representing complete route, or None if failed

    Example:
        >>> waypoints = [(lon1, lat1), (lon2, lat2), ..., (lon50, lat50)]
        >>> route = directions_with_multiple_waypoints(waypoints, "pk.xxx")
        >>> # Batches into 2 requests: [1-25] and [25-50]
    """
    if len(waypoints) <= max_waypoints_per_request:
        # Single request
        return mapbox_directions(waypoints, mapbox_token)

    # Multiple batches needed
    print(f"⚠️  {len(waypoints)} waypoints require multiple batches")

    merged_route = []
    num_batches = (len(waypoints) + max_waypoints_per_request - 2) // (max_waypoints_per_request - 1)

    print(f"   Splitting into {num_batches} batches...")

    for i in range(num_batches):
        start_idx = i * (max_waypoints_per_request - 1)
        end_idx = min(start_idx + max_waypoints_per_request, len(waypoints))

        batch_waypoints = waypoints[start_idx:end_idx]

        print(f"\n🔹 Batch {i+1}/{num_batches}: waypoints {start_idx}-{end_idx-1}")

        batch_route = mapbox_directions(batch_waypoints, mapbox_token)

        if not batch_route:
            print(f"   ❌ Batch {i+1} failed")
            return None

        if i == 0:
            # First batch: add all points
            merged_route.extend(batch_route)
        else:
            # Subsequent batches: skip first point to avoid duplication
            merged_route.extend(batch_route[1:])

    print(f"\n🔗 Merged {num_batches} batches into {len(merged_route)} points")

    return merged_route


def get_road_geometry_with_auto_waypoints(
    road_code: str,
    start_town: str,
    end_town: str,
    expected_distance_km: float,
    mapbox_token: str,
    intermediate_towns: Optional[List[str]] = None
) -> Optional[List[Tuple[float, float]]]:
    """
    Get complete road geometry using auto-generated waypoints + Directions API (Layer 4).

    This is the high-level function that integrates:
    1. Waypoint generation (from town names via Nominatim)
    2. Mapbox Directions API (routing between waypoints)

    Used as Layer 4 fallback when OSM/Map Matching fail.

    Args:
        road_code: Road code (e.g., "N103")
        start_town: Starting town name (e.g., "Viana do Castelo")
        end_town: Ending town name (e.g., "Bragança")
        expected_distance_km: Expected road distance
        mapbox_token: Mapbox API token
        intermediate_towns: Optional list of intermediate towns

    Returns:
        List of (lon, lat) coordinates if successful, None otherwise

    Example:
        >>> coords = get_road_geometry_with_auto_waypoints(
        ...     "N103",
        ...     "Viana do Castelo",
        ...     "Bragança",
        ...     274.0,
        ...     "pk.xxx",
        ...     ["Ponte de Lima", "Chaves"]
        ... )
        >>> len(coords)
        2431
    """

    print(f"\n📍 Layer 4: Auto-waypoints + Directions API")

    # Step 1: Generate waypoints from town names
    print(f"   🌍 Generating waypoints from town names...")

    waypoints = generate_waypoints_for_road(
        road_code=road_code,
        start_town=start_town,
        end_town=end_town,
        expected_distance_km=expected_distance_km,
        intermediate_towns=intermediate_towns
    )

    if not waypoints or len(waypoints) < 2:
        print(f"   ❌ Failed to generate waypoints")
        return None

    print(f"   ✅ Generated {len(waypoints)} waypoints")

    # Step 2: Fetch route from Directions API
    # Note: waypoints are (lat, lon), need to convert to (lon, lat) for Directions API
    waypoints_lonlat = [(wp[1], wp[0]) for wp in waypoints]

    print(f"   🗺️  Fetching route from Directions API...")
    coordinates = directions_with_multiple_waypoints(waypoints_lonlat, mapbox_token)

    if not coordinates:
        print(f"   ❌ Directions API failed")
        return None

    # Calculate distance for validation
    distance_km = 0.0
    for i in range(len(coordinates) - 1):
        point1 = (coordinates[i][1], coordinates[i][0])  # (lat, lon)
        point2 = (coordinates[i + 1][1], coordinates[i + 1][0])
        distance_km += geodesic(point1, point2).kilometers

    print(f"   📏 Route distance: {distance_km:.2f}km (expected: {expected_distance_km:.2f}km)")

    # Distance validation
    distance_diff_pct = abs(distance_km - expected_distance_km) / expected_distance_km
    if distance_diff_pct > 0.20:  # 20% tolerance
        print(f"   ⚠️  Warning: Distance differs {distance_diff_pct*100:.1f}% from expected")

    density = len(coordinates) / distance_km if distance_km > 0 else 0
    print(f"   📊 Density: {density:.2f} pts/km")

    return coordinates


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    print("=" * 70)
    print("Mapbox Directions API - Test Suite")
    print("=" * 70)

    load_dotenv()
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

    if not MAPBOX_TOKEN:
        print("❌ Error: MAPBOX_TOKEN not found in .env")
        exit(1)

    # Test 1: Simple 2-point route
    print("\n🧪 Test 1: Chaves → Vila Real")
    print("-" * 70)

    coords = [
        (-7.4688, 41.7402),  # Chaves
        (-7.7441, 41.3006)   # Vila Real
    ]

    route = mapbox_directions(coords, MAPBOX_TOKEN)

    if route:
        print(f"✅ Test 1 PASSED: {len(route)} points")
    else:
        print(f"❌ Test 1 FAILED")

    # Test 2: Multi-waypoint route
    print("\n🧪 Test 2: Chaves → Vila Real → Lamego")
    print("-" * 70)

    coords = [
        (-7.4688, 41.7402),  # Chaves
        (-7.7441, 41.3006),  # Vila Real
        (-7.8099, 41.0974)   # Lamego
    ]

    route = mapbox_directions(coords, MAPBOX_TOKEN)

    if route:
        print(f"✅ Test 2 PASSED: {len(route)} points")
    else:
        print(f"❌ Test 2 FAILED")

    print("\n" + "=" * 70)
    print("✅ Module loaded successfully!")
    print("=" * 70)
