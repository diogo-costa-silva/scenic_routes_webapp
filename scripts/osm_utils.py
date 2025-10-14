#!/usr/bin/env python3
"""
==============================================================================
OpenStreetMap Utility Functions
==============================================================================
Module: osm_utils.py
Purpose: Fetch road geometry data from OpenStreetMap Overpass API
Author: Road Explorer Portugal
==============================================================================
"""

import requests
import time
import json
import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict


# ==============================================================================
# Configuration
# ==============================================================================

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"  # Primary server
REQUEST_TIMEOUT = 120  # seconds (reasonable timeout)
RATE_LIMIT_DELAY = 1.0  # seconds between requests (be respectful!)

# Cache configuration
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_MAX_AGE_DAYS = 30  # Cache expires after 30 days

# Segmentation configuration (for long roads)
SEGMENTATION_ENABLED = True  # Auto-segment on timeout
NUM_SEGMENTS = 4  # Divide bbox into 4 vertical segments


# ==============================================================================
# Cache Functions
# ==============================================================================

def _load_cache(road_ref: str) -> Optional[List[Tuple[float, float]]]:
    """
    Load road coordinates from cache if exists and fresh.

    Args:
        road_ref: Road reference (e.g., "N 222")

    Returns:
        Cached coordinates if available and fresh, None otherwise
    """
    if not CACHE_DIR.exists():
        return None

    # Normalize road_ref for filename (remove spaces, special chars)
    cache_filename = road_ref.replace(" ", "_").replace("/", "_") + ".json"
    cache_file = CACHE_DIR / cache_filename

    if not cache_file.exists():
        return None

    # Check cache age
    import time
    age_seconds = time.time() - cache_file.stat().st_mtime
    age_days = age_seconds / 86400

    if age_days > CACHE_MAX_AGE_DAYS:
        print(f"   ⚠️  Cache expired ({int(age_days)} days old), re-fetching...")
        return None

    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
            print(f"   💾 Loaded from cache ({len(data)} points, {int(age_days)}d old)")
            return [tuple(coord) for coord in data]
    except Exception as e:
        print(f"   ⚠️  Cache read error: {e}")
        return None


def _save_cache(road_ref: str, coordinates: List[Tuple[float, float]]) -> None:
    """
    Save road coordinates to cache.

    Args:
        road_ref: Road reference (e.g., "N 222")
        coordinates: List of (lon, lat) tuples
    """
    try:
        # Create cache directory if doesn't exist
        CACHE_DIR.mkdir(exist_ok=True)

        # Normalize road_ref for filename
        cache_filename = road_ref.replace(" ", "_").replace("/", "_") + ".json"
        cache_file = CACHE_DIR / cache_filename

        # Save coordinates as JSON
        with open(cache_file, 'w') as f:
            json.dump(coordinates, f)

        print(f"   💾 Saved to cache ({len(coordinates)} points)")
    except Exception as e:
        print(f"   ⚠️  Cache save error: {e}")


# ==============================================================================
# Segmentation Functions (for Long Roads)
# ==============================================================================

def _divide_bbox_vertical(bbox: Tuple[float, float, float, float], num_segments: int) -> List[Tuple[float, float, float, float]]:
    """
    Divide bounding box into vertical segments (North to South).

    Useful for long roads that span large distances vertically.

    Args:
        bbox: Original bounding box (south, west, north, east)
        num_segments: Number of segments to create

    Returns:
        List of bounding boxes, one per segment
    """
    south, west, north, east = bbox
    lat_step = (north - south) / num_segments

    segments = []
    for i in range(num_segments):
        seg_south = south + (i * lat_step)
        seg_north = seg_south + lat_step
        segments.append((seg_south, west, seg_north, east))

    return segments


def _fetch_single_segment(road_ref: str, bbox: Tuple[float, float, float, float], timeout: int = REQUEST_TIMEOUT) -> List[Tuple[float, float]]:
    """
    Fetch road geometry for a single bbox segment.

    Args:
        road_ref: Road reference
        bbox: Bounding box for this segment
        timeout: Timeout for query

    Returns:
        List of coordinates, or empty list if nothing found
    """
    # Simplified query (relation only, faster)
    overpass_query = f"""
    [out:json][timeout:{timeout}];
    (
      relation["ref"="{road_ref}"]["highway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out geom;
    """

    try:
        time.sleep(RATE_LIMIT_DELAY)
        data = query_overpass_api(overpass_query)
        return extract_coordinates_from_response(data, bbox)
    except requests.Timeout:
        return []
    except Exception as e:
        print(f"   ⚠️  Segment fetch error: {e}")
        return []


def _fetch_segmented(road_ref: str, bbox: Tuple[float, float, float, float]) -> List[Tuple[float, float]]:
    """
    Fetch road geometry using segmentation strategy for long roads.

    Divides the bounding box into multiple segments and fetches each separately,
    then merges the results intelligently.

    Args:
        road_ref: Road reference
        bbox: Original bounding box

    Returns:
        Merged coordinates from all segments

    Raises:
        Exception: If no segments return data
    """
    print(f"   🔄 Using segmentation strategy ({NUM_SEGMENTS} segments)...")

    segments_bbox = _divide_bbox_vertical(bbox, NUM_SEGMENTS)
    all_coords_lists = []

    for i, segment_bbox in enumerate(segments_bbox):
        print(f"   📍 Processing segment {i+1}/{NUM_SEGMENTS}...")

        coords = _fetch_single_segment(road_ref, segment_bbox, timeout=60)

        if coords:
            print(f"      ✅ Found {len(coords)} points in segment {i+1}")
            all_coords_lists.append(coords)
        else:
            print(f"      ⚠️  No data in segment {i+1}")

    if not all_coords_lists:
        raise Exception("No segments returned data - road may not exist or OSM server issues")

    # Merge all segment coordinates
    print(f"   🔗 Merging {len(all_coords_lists)} segments...")
    merged = merge_way_segments(all_coords_lists)

    print(f"   ✅ Segmentation complete: {len(merged)} total points")
    return merged


# ==============================================================================
# Main Functions
# ==============================================================================

def get_road_from_osm(road_ref: str, bbox: Optional[Tuple[float, float, float, float]] = None) -> List[Tuple[float, float]]:
    """
    Fetch road geometry from OpenStreetMap using Overpass API with smart fallbacks.

    This function implements a multi-tier strategy:
    1. Try loading from local cache (instant if available)
    2. Try normal Overpass query (works for most roads)
    3. Fallback to segmentation if timeout (handles long roads like N2)

    Features:
    - Automatic caching (30-day validity)
    - Intelligent segmentation for long roads
    - Alternative ref format attempts
    - Robust error handling

    Args:
        road_ref (str): OSM road reference (e.g., "N 222", "N 2", "N222")
                       Will try multiple formats if initial query fails
        bbox (Optional[Tuple[float, float, float, float]]): Bounding box (south, west, north, east)
                       Defaults to Portugal bounds if not provided

    Returns:
        List[Tuple[float, float]]: List of (longitude, latitude) coordinates
                                   Returns empty list if road not found

    Raises:
        requests.RequestException: If API request fails
        ValueError: If invalid road_ref provided

    Example:
        >>> coords = get_road_from_osm("N 222")
        >>> print(f"Found {len(coords)} GPS points")
        Found 1247 GPS points
    """

    if not validate_road_ref(road_ref):
        raise ValueError(f"Invalid road reference: {road_ref}")

    # Default to Portugal bounding box if not provided
    # Portugal mainland only (tighter bbox for better performance)
    if bbox is None:
        bbox = (37.0, -9.5, 42.2, -6.2)  # Continental only - faster queries

    print(f"📡 Fetching road data for: {road_ref}")

    # STEP 1: Try loading from cache
    cached = _load_cache(road_ref)
    if cached:
        return cached

    # Build Overpass QL query with bounding box
    # Portuguese roads typically use "name" tag rather than "ref"
    # Query both by name and ref to cover all cases
    # The bbox format in Overpass is (south, west, north, east)

    # Clean road_ref for name matching (remove spaces/hyphens for regex)
    road_name_pattern = road_ref.replace(" ", "").replace("-", "")

    # Initial query: try both ways and relations (relations preferred for major roads)
    overpass_query = f"""
    [out:json][timeout:{REQUEST_TIMEOUT}];
    (
      relation["ref"="{road_ref}"]["highway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
      way["ref"="{road_ref}"]["highway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
    );
    out geom;
    """

    # STEP 2: Try normal query
    try:
        # Execute query with rate limiting
        time.sleep(RATE_LIMIT_DELAY)
        data = query_overpass_api(overpass_query)

        # Extract coordinates from response (pass bbox for filtering)
        coordinates = extract_coordinates_from_response(data, bbox)

        # If no results, try alternative ref formats
        if not coordinates:
            print(f"   ⚠️  No results with '{road_ref}', trying alternative formats...")

            # Generate alternative formats
            alternatives = _generate_ref_alternatives(road_ref)

            for alt_ref in alternatives:
                if alt_ref == road_ref:
                    continue  # Skip the one we already tried

                print(f"   🔄 Trying: {alt_ref}")
                alt_name_pattern = alt_ref.replace(" ", "").replace("-", "")
                # For major roads, prefer relations over individual ways
                alt_query = f"""
                [out:json][timeout:{REQUEST_TIMEOUT}];
                (
                  relation["ref"="{alt_ref}"]["highway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
                  relation["name"~"^{alt_name_pattern}$"]["highway"]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});
                );
                out geom;
                """

                time.sleep(RATE_LIMIT_DELAY)
                data = query_overpass_api(alt_query)
                coordinates = extract_coordinates_from_response(data, bbox)

                if coordinates:
                    print(f"   ✅ Found {len(coordinates)} GPS points with format: {alt_ref}")
                    _save_cache(road_ref, coordinates)
                    return coordinates

            # Still no results after trying alternatives
            print(f"   ❌ No coordinates found for {road_ref} (tried {len(alternatives)} formats)")
            print(f"   💡 Tip: Check if road exists in OSM with this ref tag")
            return []

        print(f"   ✅ Found {len(coordinates)} GPS points")
        _save_cache(road_ref, coordinates)
        return coordinates

    except requests.Timeout:
        # STEP 3: Fallback to segmentation for long roads
        if SEGMENTATION_ENABLED:
            print(f"   ⚠️  Timeout occurred - road may be very long (>100km)")
            print(f"   🔄 Falling back to segmentation strategy...")

            try:
                coordinates = _fetch_segmented(road_ref, bbox)
                if coordinates:
                    _save_cache(road_ref, coordinates)
                    return coordinates
                else:
                    print(f"   ❌ Segmentation also failed")
                    return []
            except Exception as seg_error:
                print(f"   ❌ Segmentation error: {seg_error}")
                raise requests.Timeout(f"Both normal query and segmentation failed for {road_ref}")
        else:
            print(f"   ❌ Timeout: OSM API took longer than {REQUEST_TIMEOUT}s")
            print(f"   💡 Tip: Enable SEGMENTATION_ENABLED for long roads")
            raise

    except requests.RequestException as e:
        print(f"   ❌ Network error: {e}")
        raise
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        raise


def _generate_ref_alternatives(road_ref: str) -> List[str]:
    """
    Generate alternative ref formats to try.

    Portuguese roads can be tagged in OSM with different formats:
    - Real life: "N 222", "N222" → OSM: "EN 222", "EN222" (Estrada Nacional)
    - Real life: "N 2", "N2" → OSM: "EN 2", "EN2"
    - Municipal: "EM XXX" (Estrada Municipal)
    - Regional: "ER XXX" (Estrada Regional)

    Args:
        road_ref: Original road reference

    Returns:
        List of alternative formats to try
    """
    alternatives = [road_ref]  # Start with original

    # Remove all spaces and hyphens to get base
    base = road_ref.replace(" ", "").replace("-", "")

    # Try to split into letter prefix and number
    if len(base) >= 2:
        # Find where numbers start
        i = 0
        while i < len(base) and base[i].isalpha():
            i += 1

        if i > 0 and i < len(base):
            prefix = base[:i].upper()  # e.g., "N", "EN", "EM"
            number = base[i:]  # e.g., "222", "2"

            # If prefix is "N", try "EN" (Estrada Nacional) variants
            prefixes_to_try = [prefix]
            if prefix == "N":
                prefixes_to_try = ["EN", "N"]  # Try EN first for Portuguese roads
            elif prefix == "EN":
                prefixes_to_try = ["EN"]

            # Generate alternatives for each prefix
            for pref in prefixes_to_try:
                alternatives.append(f"{pref} {number}")  # "EN 222"
                alternatives.append(f"{pref}{number}")   # "EN222"
                alternatives.append(f"{pref}-{number}")  # "EN-222"

    # Remove duplicates while preserving order
    seen = set()
    unique_alternatives = []
    for alt in alternatives:
        if alt not in seen:
            seen.add(alt)
            unique_alternatives.append(alt)

    return unique_alternatives


def query_overpass_api(query: str) -> dict:
    """
    Execute a raw Overpass QL query.

    Args:
        query (str): Overpass QL query string

    Returns:
        dict: JSON response from Overpass API

    Raises:
        requests.RequestException: If API request fails
        requests.Timeout: If request times out
        ValueError: If response is not valid JSON
    """

    try:
        response = requests.post(
            OVERPASS_API_URL,
            data={'data': query},
            timeout=REQUEST_TIMEOUT,
            headers={'User-Agent': 'RoadExplorerPortugal/1.0'}
        )

        # Check for HTTP errors
        response.raise_for_status()

        # Parse JSON response
        return response.json()

    except requests.Timeout:
        raise requests.Timeout(f"Overpass API request timed out after {REQUEST_TIMEOUT}s")
    except requests.HTTPError as e:
        if e.response.status_code == 429:
            raise requests.RequestException("Rate limited by Overpass API - please wait and retry")
        elif e.response.status_code == 504:
            raise requests.Timeout("Overpass API gateway timeout - query too complex or server busy")
        else:
            raise requests.RequestException(f"HTTP error {e.response.status_code}: {e}")
    except ValueError as e:
        raise ValueError(f"Invalid JSON response from Overpass API: {e}")
    except requests.RequestException as e:
        raise requests.RequestException(f"Failed to query Overpass API: {e}")


def extract_coordinates_from_response(data: dict, bbox: Optional[Tuple[float, float, float, float]] = None) -> List[Tuple[float, float]]:
    """
    Extract coordinates from Overpass API response.

    Handles both 'way' and 'relation' elements from OSM data.
    When using 'out geom;' modifier, ways include a 'geometry' field
    with coordinates already resolved.

    Args:
        data (dict): JSON response from Overpass API
        bbox (Optional[Tuple]): Bounding box to filter coordinates (south, west, north, east)

    Returns:
        List[Tuple[float, float]]: List of (longitude, latitude) coordinates
    """

    coordinates = []
    segments = []

    # Parse elements from response
    elements = data.get('elements', [])

    if not elements:
        return []

    # If multiple relations, select the largest one WITHIN the bbox
    # This handles cases where OSM returns multiple roads with same ref from different countries
    relations = [e for e in elements if e.get('type') == 'relation']

    if len(relations) > 1 and bbox:
        print(f"   ⚠️  Found {len(relations)} relations, filtering by bbox...")

        # For each relation, count how many members are within bbox
        best_relation = None
        best_member_count = 0

        for relation in relations:
            members = relation.get('members', [])
            valid_members = 0

            for member in members:
                if member.get('type') == 'way' and 'geometry' in member:
                    # Check if any point is within bbox
                    for node in member['geometry']:
                        lon, lat = node['lon'], node['lat']
                        if bbox[1] <= lon <= bbox[3] and bbox[0] <= lat <= bbox[2]:
                            valid_members += 1
                            break

            if valid_members > best_member_count:
                best_member_count = valid_members
                best_relation = relation

        if best_relation:
            rel_id = best_relation.get('id')
            rel_tags = best_relation.get('tags', {})
            print(f"   ✅ Selected relation {rel_id} with {best_member_count} valid members")
            print(f"      ref: {rel_tags.get('ref', 'N/A')}")
            # Use only the best relation
            elements = [best_relation]
        else:
            print(f"   ⚠️  No valid relation found within bbox")

    for element in elements:
        element_type = element.get('type')

        if element_type == 'way':
            # Extract geometry from way
            geometry = element.get('geometry', [])
            if geometry:
                # Each geometry node has 'lon' and 'lat'
                way_coords = [(node['lon'], node['lat']) for node in geometry]
                segments.append(way_coords)

        elif element_type == 'relation':
            # Relations contain multiple ways as members
            # These should be handled by querying member ways
            members = element.get('members', [])
            for member in members:
                if member.get('type') == 'way' and 'geometry' in member:
                    member_coords = [(node['lon'], node['lat']) for node in member['geometry']]
                    segments.append(member_coords)

    # Merge segments if we have multiple ways
    if len(segments) == 0:
        return []
    elif len(segments) == 1:
        return segments[0]
    else:
        # Multiple segments - merge them intelligently
        return merge_way_segments(segments)


def validate_road_ref(road_ref: str) -> bool:
    """
    Validate that road reference is in correct format.

    Basic validation to ensure road_ref is not empty and contains
    expected characters. Portuguese roads typically follow format:
    - National: "N XXX" (e.g., "N 222", "N 2")
    - Municipal: "EM XXX" (e.g., "EM 567")

    Args:
        road_ref (str): Road reference to validate

    Returns:
        bool: True if valid format, False otherwise
    """

    if not road_ref or not isinstance(road_ref, str):
        return False

    # Remove whitespace and check not empty
    if not road_ref.strip():
        return False

    # Basic length check (should be at least 2 characters like "N2")
    if len(road_ref.strip()) < 2:
        return False

    return True


def merge_way_segments(segments: List[List[Tuple[float, float]]]) -> List[Tuple[float, float]]:
    """
    Merge multiple OSM way segments into a single continuous line.

    Roads in OSM can be split into multiple 'way' elements. This function
    intelligently connects segments by finding matching endpoints.

    Algorithm:
    1. Start with first segment
    2. Find next segment that connects (matching start/end points)
    3. Handle segment direction (may need to reverse)
    4. Continue until all segments merged or no more connections

    Args:
        segments (List[List[Tuple[float, float]]]): List of coordinate segments

    Returns:
        List[Tuple[float, float]]: Merged coordinates forming continuous line
    """

    if not segments:
        return []

    if len(segments) == 1:
        return segments[0]

    # Start with first segment
    merged = list(segments[0])
    remaining = segments[1:]

    # Keep trying to connect segments until no more can be connected
    while remaining:
        connected = False

        for i, segment in enumerate(remaining):
            # Check if segment connects to end of merged
            if _points_match(merged[-1], segment[0]):
                # Segment connects at start - append it
                merged.extend(segment[1:])  # Skip first point (duplicate)
                remaining.pop(i)
                connected = True
                break
            elif _points_match(merged[-1], segment[-1]):
                # Segment connects at end (reversed) - append reversed
                merged.extend(reversed(segment[:-1]))  # Skip last point (duplicate)
                remaining.pop(i)
                connected = True
                break
            # Check if segment connects to start of merged
            elif _points_match(merged[0], segment[-1]):
                # Segment connects at start - prepend it
                merged = segment[:-1] + merged  # Skip last point (duplicate)
                remaining.pop(i)
                connected = True
                break
            elif _points_match(merged[0], segment[0]):
                # Segment connects at start (reversed) - prepend reversed
                merged = list(reversed(segment[1:])) + merged  # Skip first point (duplicate)
                remaining.pop(i)
                connected = True
                break

        # If no segment connected, add remaining as separate parts
        # (This handles disconnected road segments)
        if not connected:
            print(f"   ⚠️  Warning: {len(remaining)} segment(s) could not be connected")
            # Add remaining segments anyway
            for segment in remaining:
                merged.extend(segment)
            break

    return merged


def _points_match(point1: Tuple[float, float], point2: Tuple[float, float], tolerance: float = 0.0001) -> bool:
    """
    Check if two GPS points are the same (within tolerance).

    Args:
        point1: First point (lon, lat)
        point2: Second point (lon, lat)
        tolerance: Maximum difference to consider points equal (degrees)

    Returns:
        bool: True if points match within tolerance
    """
    return (abs(point1[0] - point2[0]) < tolerance and
            abs(point1[1] - point2[1]) < tolerance)


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OSM Utils - Test Suite")
    print("=" * 70)

    # Test 1: N222 (Famous Douro Valley road)
    print("\n🧪 Test 1: N222 (Peso da Régua → Pinhão)")
    print("-" * 70)
    try:
        coords_n222 = get_road_from_osm("N 222")
        if coords_n222:
            print(f"   ✅ Success: {len(coords_n222)} coordinates")
            print(f"   📍 Start: {coords_n222[0]}")
            print(f"   📍 End: {coords_n222[-1]}")

            # Validate coordinates are in Portugal bounds
            lons = [c[0] for c in coords_n222]
            lats = [c[1] for c in coords_n222]
            if all(-10 <= lon <= -6 for lon in lons) and all(36 <= lat <= 42 for lat in lats):
                print(f"   ✅ Coordinates within Portugal bounds")
            else:
                print(f"   ⚠️  Warning: Some coordinates outside expected bounds")
        else:
            print(f"   ❌ Failed: No coordinates returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Test 2: N2 (Portugal's Route 66 - very long road)
    print("🧪 Test 2: N2 (Chaves → Faro) - This may take longer...")
    print("-" * 70)
    try:
        coords_n2 = get_road_from_osm("N 2")
        if coords_n2:
            print(f"   ✅ Success: {len(coords_n2)} coordinates")
            print(f"   📍 Start: {coords_n2[0]}")
            print(f"   📍 End: {coords_n2[-1]}")

            # Validate coordinates
            lons = [c[0] for c in coords_n2]
            lats = [c[1] for c in coords_n2]
            if all(-10 <= lon <= -6 for lon in lons) and all(36 <= lat <= 42 for lat in lats):
                print(f"   ✅ Coordinates within Portugal bounds")
            else:
                print(f"   ⚠️  Warning: Some coordinates outside expected bounds")
        else:
            print(f"   ❌ Failed: No coordinates returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Test 3: Invalid road (error handling)
    print("🧪 Test 3: Error Handling (Invalid Road)")
    print("-" * 70)
    try:
        coords_invalid = get_road_from_osm("INVALID_ROAD_999")
        if not coords_invalid:
            print(f"   ✅ Correctly handled non-existent road (returned empty list)")
        else:
            print(f"   ⚠️  Unexpected: Found coordinates for invalid road")
    except Exception as e:
        print(f"   ✅ Correctly raised exception: {type(e).__name__}")

    print("\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("=" * 70)
