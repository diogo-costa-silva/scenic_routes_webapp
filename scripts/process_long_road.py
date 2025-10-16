#!/usr/bin/env python3
"""
==============================================================================
Long Road Processing Module
==============================================================================
Module: process_long_road.py
Purpose: Process very long roads (>100km) using waypoints strategy
Author: Road Explorer Portugal
==============================================================================

Strategy:
1. Load waypoints from JSON (10-15 cities along the road)
2. Process each section (waypoint_i → waypoint_i+1) independently
3. Each section uses hybrid_strategy (OSM → validate → Map Matching fallback)
4. Merge all successful sections into single geometry
5. Validate final quality

Benefits:
- Handles roads >100km that timeout on single OSM query
- Avoids "1000+ disconnected segments" problem
- Each section is validated independently
- Reuses existing hybrid_strategy code (no new APIs)
==============================================================================
"""

import os
import json
from typing import List, Tuple, Dict, Optional
from pathlib import Path
from dataclasses import dataclass

# Import our modules
from hybrid_strategy import get_road_geometry_hybrid, GeometryResult
from validation import get_quality_report
from metrics import calculate_total_distance


# ==============================================================================
# Helper Functions
# ==============================================================================

def load_waypoints(waypoints_file: str) -> Dict:
    """
    Load waypoints from JSON file.

    Args:
        waypoints_file: Path to waypoints JSON file (e.g., "n2_waypoints.json")

    Returns:
        Dict with 'waypoints' list and metadata

    Raises:
        FileNotFoundError: If waypoints file doesn't exist
        ValueError: If waypoints data is invalid
    """
    file_path = Path(__file__).parent / waypoints_file

    if not file_path.exists():
        raise FileNotFoundError(f"Waypoints file not found: {waypoints_file}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate structure
    if 'waypoints' not in data or not isinstance(data['waypoints'], list):
        raise ValueError(f"Invalid waypoints file: missing 'waypoints' list")

    if len(data['waypoints']) < 2:
        raise ValueError(f"Need at least 2 waypoints, got {len(data['waypoints'])}")

    print(f"📍 Loaded {len(data['waypoints'])} waypoints from {waypoints_file}")
    print(f"   Road: {data.get('road_name', 'Unknown')}")
    print(f"   Expected distance: {data.get('total_distance_km', 0):.0f} km")

    return data


def calculate_section_bbox(waypoint1: Dict, waypoint2: Dict, buffer: float = 0.15) -> Tuple[float, float, float, float]:
    """
    Calculate bounding box for a section between two waypoints.

    Adds buffer around the direct line between waypoints to ensure we capture
    the actual road (which may not be perfectly straight).

    Args:
        waypoint1: Dict with 'lat' and 'lon' keys
        waypoint2: Dict with 'lat' and 'lon' keys
        buffer: Buffer in degrees (default: 0.15° ≈ 15km)

    Returns:
        Tuple: (south, west, north, east) bounding box

    Example:
        >>> wp1 = {"lat": 41.74, "lon": -7.47}
        >>> wp2 = {"lat": 41.30, "lon": -7.74}
        >>> bbox = calculate_section_bbox(wp1, wp2, buffer=0.15)
        >>> bbox
        (41.15, -7.89, 41.89, -7.32)
    """
    lat1, lon1 = waypoint1['lat'], waypoint1['lon']
    lat2, lon2 = waypoint2['lat'], waypoint2['lon']

    # Calculate min/max with buffer
    south = min(lat1, lat2) - buffer
    north = max(lat1, lat2) + buffer
    west = min(lon1, lon2) - buffer
    east = max(lon1, lon2) + buffer

    return (south, west, north, east)


def merge_section_coordinates(sections: List[GeometryResult]) -> List[Tuple[float, float]]:
    """
    Merge coordinates from multiple sections into a single path.

    Removes duplicate points at section boundaries to avoid artifacts.

    Args:
        sections: List of GeometryResult objects (already validated)

    Returns:
        List of (lon, lat) tuples representing the complete road

    Example:
        >>> section1.coordinates = [(0, 0), (1, 1), (2, 2)]
        >>> section2.coordinates = [(2, 2), (3, 3), (4, 4)]
        >>> merge_section_coordinates([section1, section2])
        [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]
    """
    if not sections:
        return []

    merged = []

    for i, section in enumerate(sections):
        coords = section.coordinates

        if i == 0:
            # First section: add all points
            merged.extend(coords)
        else:
            # Subsequent sections: skip first point if it duplicates last
            # (sections should connect at waypoints)
            if merged and coords and merged[-1] == coords[0]:
                merged.extend(coords[1:])
            else:
                # No overlap - add all points
                merged.extend(coords)

    print(f"   🔗 Merged {len(sections)} sections into {len(merged)} points")

    return merged


# ==============================================================================
# Main Processing Function
# ==============================================================================

def process_road_with_waypoints(
    road_info: Dict,
    waypoints_file: str,
    mapbox_token: Optional[str] = None
) -> Optional[GeometryResult]:
    """
    Process a long road using waypoints strategy.

    Divides road into sections based on waypoints, processes each section
    independently with hybrid strategy, then merges successful sections.

    Args:
        road_info: Road definition dict (from roads_data.json)
        waypoints_file: Path to waypoints JSON (e.g., "n2_waypoints.json")
        mapbox_token: Mapbox API token for Map Matching fallback (optional)

    Returns:
        GeometryResult with merged coordinates and quality metrics, or None if failed

    Example:
        >>> road_info = {
        ...     'code': 'N2',
        ...     'osm_ref': 'EN 2',
        ...     'expected_distance_km': 739.0
        ... }
        >>> result = process_road_with_waypoints(
        ...     road_info, "n2_waypoints.json", "pk.xxx"
        ... )
        >>> if result:
        ...     print(f"Distance: {result.distance_km}km")
        Distance: 739km
    """
    road_code = road_info.get('code', 'UNKNOWN')
    road_ref = road_info.get('osm_ref', road_code)
    expected_distance_km = road_info.get('expected_distance_km', 0)

    print(f"\n{'='*70}")
    print(f"🗺️  WAYPOINTS STRATEGY: {road_code}")
    print(f"{'='*70}")

    # Step 1: Load waypoints
    try:
        waypoints_data = load_waypoints(waypoints_file)
        waypoints = waypoints_data['waypoints']
    except Exception as e:
        print(f"❌ Failed to load waypoints: {e}")
        return None

    # Step 2: Process each section
    sections = []
    failed_sections = []
    total_sections = len(waypoints) - 1

    print(f"\n📍 Processing {total_sections} sections...")
    print(f"{'='*70}")

    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i + 1]

        section_name = f"{wp1['name']} → {wp2['name']}"
        section_num = i + 1

        print(f"\n🔹 Section {section_num}/{total_sections}: {section_name}")
        print(f"   From: {wp1['lat']:.4f}, {wp1['lon']:.4f}")
        print(f"   To:   {wp2['lat']:.4f}, {wp2['lon']:.4f}")

        # Calculate bbox for this section
        bbox = calculate_section_bbox(wp1, wp2, buffer=0.15)
        print(f"   BBox: S={bbox[0]:.2f}, W={bbox[1]:.2f}, N={bbox[2]:.2f}, E={bbox[3]:.2f}")

        # Estimate section distance (straight line)
        from geopy.distance import geodesic
        straight_distance = geodesic(
            (wp1['lat'], wp1['lon']),
            (wp2['lat'], wp2['lon'])
        ).kilometers
        expected_section_distance = straight_distance * 1.3  # Roads are ~30% longer than straight line

        print(f"   Expected distance: {expected_section_distance:.1f} km")

        # Try to process this section with hybrid strategy
        try:
            section_result = get_road_geometry_hybrid(
                road_ref=road_ref,
                bbox=bbox,
                expected_distance_km=expected_section_distance,
                mapbox_token=mapbox_token
            )

            if section_result:
                print(f"   ✅ Section SUCCESS")
                print(f"      Source: {section_result.source}")
                print(f"      Points: {section_result.point_count}")
                print(f"      Distance: {section_result.distance_km:.2f} km")
                print(f"      Density: {section_result.density:.2f} pts/km")
                print(f"      Quality: {section_result.quality_report['quality']}")

                sections.append(section_result)
            else:
                print(f"   ❌ Section FAILED: Quality check failed")
                failed_sections.append(section_name)

        except Exception as e:
            print(f"   ❌ Section FAILED: {e}")
            failed_sections.append(section_name)

    # Step 3: Check if we have enough successful sections
    success_rate = len(sections) / total_sections
    print(f"\n{'='*70}")
    print(f"📊 Section Processing Results:")
    print(f"   ✅ Successful: {len(sections)}/{total_sections} ({success_rate*100:.0f}%)")
    print(f"   ❌ Failed: {len(failed_sections)}/{total_sections}")
    print(f"{'='*70}")

    if success_rate < 0.70:
        print(f"\n❌ REJECTED: Only {success_rate*100:.0f}% sections successful (need ≥70%)")
        print(f"   Failed sections:")
        for section_name in failed_sections:
            print(f"   • {section_name}")
        print(f"\n   Better NO road than BAD road")
        return None

    if not sections:
        print(f"\n❌ REJECTED: No sections processed successfully")
        return None

    # Step 4: Merge sections
    print(f"\n🔗 Merging {len(sections)} sections...")
    merged_coords = merge_section_coordinates(sections)

    if not merged_coords or len(merged_coords) < 100:
        print(f"❌ REJECTED: Only {len(merged_coords)} points after merge (need ≥100)")
        return None

    # Step 5: Calculate final metrics
    print(f"\n📊 Calculating final metrics...")
    final_distance = calculate_total_distance(merged_coords)
    final_density = len(merged_coords) / final_distance if final_distance > 0 else 0

    print(f"   Total points: {len(merged_coords)}")
    print(f"   Total distance: {final_distance:.2f} km")
    print(f"   Final density: {final_density:.2f} pts/km")

    # Step 6: Final quality validation
    road_info_with_coords = {**road_info, 'coordinates': merged_coords}
    final_quality = get_quality_report(road_info_with_coords, merged_coords, final_distance)

    print(f"\n📋 Final Quality Report:")
    print(f"   Quality: {final_quality['quality']}")
    print(f"   Density valid: {final_quality['density_valid']}")
    print(f"   Geography valid: {final_quality['geo_valid']}")

    if final_quality['quality'] == 'REJECTED':
        print(f"\n❌ REJECTED: Final quality check failed")
        for msg in final_quality['messages']:
            print(f"   • {msg}")
        return None

    # Step 7: Build final GeometryResult
    # Determine predominant source
    sources = [s.source for s in sections]
    osm_count = sources.count('osm_recursive')
    mapbox_count = sources.count('mapbox_matching')

    if osm_count > mapbox_count:
        final_source = 'osm_recursive_sections'
    elif mapbox_count > osm_count:
        final_source = 'mapbox_matching_sections'
    else:
        final_source = 'mixed_sections'

    print(f"\n✅ FINAL RESULT:")
    print(f"   Source: {final_source}")
    print(f"   Sections: {osm_count} OSM + {mapbox_count} Map Matching")
    print(f"   Quality: {final_quality['quality']}")

    result = GeometryResult(
        coordinates=merged_coords,
        source=final_source,
        quality_report=final_quality,
        point_count=len(merged_coords),
        density=final_density,
        distance_km=final_distance,
        cached=False
    )

    return result


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    print("=" * 70)
    print("Long Road Processing - Test Suite")
    print("=" * 70)

    # Load environment
    load_dotenv()
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

    # Test: N2 with 2-3 sections only (limited test)
    print("\n🧪 Test: N2 (Limited - First 3 waypoints only)")
    print("-" * 70)

    # Simulated road_info
    road_info = {
        'code': 'N2_TEST',
        'osm_ref': 'EN 2',
        'expected_distance_km': 120.0  # Just for first 2 sections
    }

    # This would need a modified n2_waypoints.json with only 3 waypoints
    # For now, just show the concept
    print("To run: Modify n2_waypoints.json to have only 3 waypoints")
    print("Then: python process_long_road.py")

    print("\n" + "=" * 70)
    print("✅ Module loaded successfully!")
    print("=" * 70)
