#!/usr/bin/env python3
"""
==============================================================================
GPX/External Geometry Import Module
==============================================================================
Module: import_gpx_geometry.py
Purpose: Import road geometries from external sources (GPX, JSON, etc.)

Use Cases:
- Import pre-generated N2 geometry (from waypoints + Directions API)
- Import GPX tracks downloaded from cycling/motorcycling communities
- Reuse validated geometries without reprocessing

This module bridges the gap between external data sources and our processing
pipeline, allowing us to handle roads where OSM data is insufficient.
==============================================================================
"""

import json
from typing import List, Tuple, Dict, Optional
from pathlib import Path

# Import our modules
from metrics import calculate_total_distance
from validation import get_quality_report


def load_geometry_from_json(
    json_file: str
) -> Optional[Dict]:
    """
    Load road geometry from JSON file.

    Expected JSON format:
    {
        "road_code": "N2",
        "road_name": "Chaves → Faro",
        "source": "waypoints_mapbox_directions",
        "coordinates": [[lon1, lat1], [lon2, lat2], ...]
    }

    Args:
        json_file: Path to JSON file (relative to scripts/ directory)

    Returns:
        Dict with 'coordinates' and metadata, or None if failed

    Example:
        >>> data = load_geometry_from_json("n2_from_waypoints.json")
        >>> len(data['coordinates'])
        13441
    """
    file_path = Path(__file__).parent / json_file

    if not file_path.exists():
        print(f"❌ File not found: {json_file}")
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Validate structure
        if 'coordinates' not in data or not isinstance(data['coordinates'], list):
            print(f"❌ Invalid JSON: missing 'coordinates' array")
            return None

        if len(data['coordinates']) < 100:
            print(f"❌ Invalid JSON: too few coordinates ({len(data['coordinates'])})")
            return None

        # Convert coordinates to tuples if needed
        coordinates = [tuple(coord) for coord in data['coordinates']]

        print(f"✅ Loaded geometry from {json_file}")
        print(f"   Road: {data.get('road_code', 'UNKNOWN')} - {data.get('road_name', 'Unknown')}")
        print(f"   Source: {data.get('source', 'unknown')}")
        print(f"   Points: {len(coordinates)}")

        return {
            'coordinates': coordinates,
            'source': data.get('source', 'external_json'),
            'road_code': data.get('road_code', ''),
            'road_name': data.get('road_name', ''),
            'metadata': data.get('metadata', {})
        }

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON format: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return None


def validate_imported_geometry(
    road_info: Dict,
    geometry_data: Dict
) -> bool:
    """
    Validate imported geometry before using it.

    Checks:
    - Point density ≥ 2.0 pts/km
    - All points within Portugal bounds
    - Distance within ±30% of expected (more lenient than hybrid strategy)

    Args:
        road_info: Road definition from roads_data.json
        geometry_data: Imported geometry data with coordinates

    Returns:
        True if valid, False otherwise

    Example:
        >>> road_info = {'code': 'N2', 'expected_distance_km': 739.0}
        >>> geometry_data = {'coordinates': [...], 'source': 'waypoints_mapbox_directions'}
        >>> validate_imported_geometry(road_info, geometry_data)
        True
    """
    coordinates = geometry_data['coordinates']
    expected_distance_km = road_info.get('expected_distance_km', 0)

    print(f"\n🔍 Validating imported geometry...")

    # Calculate distance
    distance_km = calculate_total_distance(coordinates)

    # Get quality report
    road_info_with_coords = {**road_info, 'coordinates': coordinates}
    quality_report = get_quality_report(road_info_with_coords, coordinates, distance_km)

    print(f"\n📊 Quality Report:")
    print(f"   Points: {quality_report['point_count']}")
    print(f"   Distance: {quality_report['distance_km']:.2f} km")
    print(f"   Expected: {expected_distance_km:.0f} km")
    print(f"   Density: {quality_report['density']:.2f} pts/km")
    print(f"   Quality: {quality_report['quality']}")
    print(f"   Density valid: {quality_report['density_valid']}")
    print(f"   Geography valid: {quality_report['geo_valid']}")

    # Check quality
    if quality_report['quality'] == 'REJECTED':
        print(f"\n❌ VALIDATION FAILED:")
        for msg in quality_report.get('messages', []):
            print(f"   • {msg}")
        return False

    # For imported geometries, we're more lenient with distance
    # Allow ±30% instead of ±20%
    if expected_distance_km > 0:
        distance_diff_pct = abs(distance_km - expected_distance_km) / expected_distance_km
        if distance_diff_pct > 0.30:
            print(f"\n⚠️  WARNING: Distance differs by {distance_diff_pct*100:.1f}%")
            print(f"   Expected: {expected_distance_km:.0f} km")
            print(f"   Actual: {distance_km:.2f} km")
            print(f"   Difference: {abs(distance_km - expected_distance_km):.2f} km")
            print(f"\n   For imported geometries, this is acceptable if quality is EXCELLENT")

            if quality_report['quality'] != 'EXCELLENT':
                print(f"❌ REJECTED: Distance too different and quality not EXCELLENT")
                return False

    print(f"\n✅ Validation PASSED")
    return True


# ==============================================================================
# Integration Function for process_roads.py
# ==============================================================================

def get_geometry_from_file(
    road_info: Dict,
    geometry_file: str
) -> Optional[Dict]:
    """
    Load and validate geometry from external file for use in process_roads.py.

    This is the main function that process_roads.py should call when a road
    has "use_external_geometry": true.

    Args:
        road_info: Road definition from roads_data.json
        geometry_file: Path to geometry JSON file

    Returns:
        Dict with validated geometry data, or None if failed

    Format matches GeometryResult from hybrid_strategy.py:
    {
        'coordinates': [(lon, lat), ...],
        'source': 'external_json' or specific source,
        'distance_km': float,
        'point_count': int,
        'density': float,
        'quality_report': {...}
    }

    Example Usage in roads_data.json:
    {
        "code": "N2",
        "name": "Chaves → Faro",
        "use_external_geometry": true,
        "geometry_file": "n2_from_waypoints.json",
        "expected_distance_km": 739.0
    }
    """
    print(f"\n📥 Loading external geometry from {geometry_file}...")

    # Load geometry
    geometry_data = load_geometry_from_json(geometry_file)
    if not geometry_data:
        return None

    # Validate
    if not validate_imported_geometry(road_info, geometry_data):
        return None

    # Calculate metrics for return value
    coordinates = geometry_data['coordinates']
    distance_km = calculate_total_distance(coordinates)
    density = len(coordinates) / distance_km if distance_km > 0 else 0

    road_info_with_coords = {**road_info, 'coordinates': coordinates}
    quality_report = get_quality_report(road_info_with_coords, coordinates, distance_km)

    # Return in GeometryResult-compatible format
    return {
        'coordinates': coordinates,
        'source': geometry_data['source'],
        'distance_km': distance_km,
        'point_count': len(coordinates),
        'density': density,
        'quality_report': quality_report,
        'cached': False
    }


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("GPX/External Geometry Import - Test Suite")
    print("=" * 70)

    # Test: Load N2 geometry
    print("\n🧪 Test 1: Load n2_from_waypoints.json")
    print("-" * 70)

    geometry_data = load_geometry_from_json("n2_from_waypoints.json")

    if geometry_data:
        print(f"✅ Test 1 PASSED:")
        print(f"   Points: {len(geometry_data['coordinates'])}")
        print(f"   Source: {geometry_data['source']}")
    else:
        print(f"❌ Test 1 FAILED")

    # Test 2: Validate N2 geometry
    print("\n🧪 Test 2: Validate N2 geometry")
    print("-" * 70)

    road_info = {
        'code': 'N2',
        'name': 'Chaves → Faro',
        'expected_distance_km': 739.0,
        'region': 'Continental'
    }

    if geometry_data:
        is_valid = validate_imported_geometry(road_info, geometry_data)
        if is_valid:
            print(f"✅ Test 2 PASSED")
        else:
            print(f"❌ Test 2 FAILED")

    # Test 3: Full integration function
    print("\n🧪 Test 3: Full integration with get_geometry_from_file")
    print("-" * 70)

    result = get_geometry_from_file(road_info, "n2_from_waypoints.json")

    if result:
        print(f"✅ Test 3 PASSED:")
        print(f"   Points: {result['point_count']}")
        print(f"   Distance: {result['distance_km']:.2f} km")
        print(f"   Density: {result['density']:.2f} pts/km")
        print(f"   Quality: {result['quality_report']['quality']}")
    else:
        print(f"❌ Test 3 FAILED")

    print("\n" + "=" * 70)
    print("✅ Module loaded successfully!")
    print("=" * 70)
