#!/usr/bin/env python3
"""
==============================================================================
N2 Geometry Generator from Waypoints
==============================================================================
Script: generate_n2_from_waypoints.py
Purpose: Generate N2 road geometry using waypoints + Map Matching API

Strategy:
1. Load 11 waypoints from n2_waypoints.json
2. Densify waypoints (add intermediate points every ~10-15km)
3. Process with Map Matching API (in batches if needed)
4. Validate quality (distance ~739km, density ≥2.0 pts/km)
5. Save as JSON for import into process_roads.py

Why this approach:
- All free GPX sources require login/registration
- We already have validated waypoints along N2
- Map Matching will align to actual roads (not straight lines)
- Generates high-quality geometry without external dependencies
==============================================================================
"""

import os
import json
from typing import List, Tuple, Dict
from pathlib import Path
from geopy.distance import geodesic
from dotenv import load_dotenv

# Import our modules
from mapbox_directions import mapbox_directions
from metrics import calculate_total_distance
from validation import get_quality_report

load_dotenv()
MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")


def load_waypoints(waypoints_file: str = "n2_waypoints.json") -> Dict:
    """Load waypoints from JSON file."""
    file_path = Path(__file__).parent / waypoints_file

    if not file_path.exists():
        raise FileNotFoundError(f"Waypoints file not found: {waypoints_file}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return data


def densify_waypoints(
    waypoints: List[Dict],
    target_spacing_km: float = 10.0
) -> List[Tuple[float, float]]:
    """
    Densify waypoints by adding intermediate points along straight lines.

    This creates a denser set of input points for Map Matching to work with.
    Map Matching will then align these to actual roads.

    Args:
        waypoints: List of waypoint dicts with 'lat' and 'lon' keys
        target_spacing_km: Target distance between points (default: 10km)

    Returns:
        List of (lon, lat) tuples with densified points
    """
    densified = []

    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i + 1]

        point1 = (wp1['lat'], wp1['lon'])
        point2 = (wp2['lat'], wp2['lon'])

        # Calculate distance between waypoints
        distance_km = geodesic(point1, point2).kilometers

        # Calculate number of intermediate points needed
        num_intermediates = max(1, int(distance_km / target_spacing_km))

        print(f"  {wp1['name']} → {wp2['name']}: {distance_km:.1f}km, "
              f"adding {num_intermediates} intermediate points")

        # Add first waypoint (lon, lat format for Mapbox)
        densified.append((wp1['lon'], wp1['lat']))

        # Add intermediate points (linear interpolation)
        for j in range(1, num_intermediates):
            fraction = j / num_intermediates

            lat = wp1['lat'] + fraction * (wp2['lat'] - wp1['lat'])
            lon = wp1['lon'] + fraction * (wp2['lon'] - wp1['lon'])

            densified.append((lon, lat))

    # Add final waypoint
    final_wp = waypoints[-1]
    densified.append((final_wp['lon'], final_wp['lat']))

    return densified


def process_n2_section_by_section(
    waypoints: List[Dict],
    mapbox_token: str
) -> Tuple[List[Tuple[float, float]], Dict]:
    """
    Process N2 by generating routes for each section (waypoint_i → waypoint_i+1).

    Uses Directions API to generate route geometry between waypoints.

    NOTE: Directions API optimizes for speed/distance, which may cause detours.
    For N2, this is acceptable as OSM data is too fragmented and no free GPX
    sources are available without registration.

    Args:
        waypoints: List of waypoint dicts with 'lat' and 'lon'
        mapbox_token: Mapbox API token

    Returns:
        Tuple of (merged_coordinates, metadata)
    """
    print(f"\n🗺️  Processing {len(waypoints)-1} sections with Directions API...")

    all_sections = []
    failed_sections = []
    total_sections = len(waypoints) - 1

    for i in range(len(waypoints) - 1):
        wp1 = waypoints[i]
        wp2 = waypoints[i + 1]

        section_name = f"{wp1['name']} → {wp2['name']}"
        section_num = i + 1

        print(f"\n🔹 Section {section_num}/{total_sections}: {section_name}")

        # Just use the 2 waypoints (start, end)
        # Directions API will generate the detailed route
        section_coords = [
            (wp1['lon'], wp1['lat']),
            (wp2['lon'], wp2['lat'])
        ]

        try:
            route_coords = mapbox_directions(section_coords, mapbox_token)

            if not route_coords or len(route_coords) < 10:
                print(f"   ❌ FAILED: Directions API returned too few points")
                failed_sections.append(section_name)
                continue

            matched_coords = route_coords

            distance_km = calculate_total_distance(matched_coords)
            density = len(matched_coords) / distance_km if distance_km > 0 else 0

            print(f"   ✅ SUCCESS")
            print(f"      Points: {len(matched_coords)}")
            print(f"      Distance: {distance_km:.2f} km")
            print(f"      Density: {density:.2f} pts/km")

            all_sections.append({
                'name': section_name,
                'coordinates': matched_coords,
                'distance_km': distance_km
            })

        except Exception as e:
            print(f"   ❌ FAILED: {e}")
            failed_sections.append(section_name)

    # Check if we have enough successful sections
    success_rate = len(all_sections) / total_sections

    print(f"\n{'='*70}")
    print(f"📊 Section Processing Results:")
    print(f"   ✅ Successful: {len(all_sections)}/{total_sections} ({success_rate*100:.0f}%)")
    print(f"   ❌ Failed: {len(failed_sections)}/{total_sections}")
    print(f"{'='*70}")

    if success_rate < 0.70:
        print(f"\n❌ REJECTED: Only {success_rate*100:.0f}% sections successful (need ≥70%)")
        if failed_sections:
            print(f"   Failed sections:")
            for section_name in failed_sections:
                print(f"   • {section_name}")
        raise ValueError("Too many sections failed")

    if not all_sections:
        raise ValueError("No sections processed successfully")

    # Merge sections (remove duplicate points at boundaries)
    print(f"\n🔗 Merging {len(all_sections)} sections...")
    merged_coords = []

    for i, section in enumerate(all_sections):
        coords = section['coordinates']

        if i == 0:
            # First section: add all points
            merged_coords.extend(coords)
        else:
            # Skip first point if it duplicates last point
            if merged_coords and coords and merged_coords[-1] == coords[0]:
                merged_coords.extend(coords[1:])
            else:
                merged_coords.extend(coords)

    total_distance = sum(s['distance_km'] for s in all_sections)

    print(f"   🔗 Merged into {len(merged_coords)} total points")
    print(f"   📏 Total distance: {total_distance:.2f} km")

    return merged_coords, {
        'sections_successful': len(all_sections),
        'sections_failed': len(failed_sections),
        'sections_total': total_sections,
        'output_points': len(merged_coords),
        'distance_km': total_distance
    }


def save_n2_geometry(
    coordinates: List[Tuple[float, float]],
    metadata: Dict,
    output_file: str = "n2_from_waypoints.json"
) -> None:
    """Save N2 geometry to JSON file."""
    data = {
        'road_code': 'N2',
        'road_name': 'Chaves → Faro',
        'source': 'waypoints_mapbox_directions',
        'generated_at': '2025-10-15',
        'metadata': metadata,
        'coordinates': coordinates,
        'note': 'Generated using Directions API - may have route optimizations'
    }

    output_path = Path(__file__).parent / output_file

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Saved to {output_file}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("🛣️  N2 Geometry Generator from Waypoints")
    print("=" * 70)

    if not MAPBOX_TOKEN:
        print("❌ Error: MAPBOX_TOKEN not found in .env")
        print("   Please set MAPBOX_TOKEN in scripts/.env")
        return 1

    try:
        # Step 1: Load waypoints
        print("\n📍 Step 1: Loading waypoints...")
        waypoints_data = load_waypoints()
        waypoints = waypoints_data['waypoints']
        expected_distance = waypoints_data.get('total_distance_km', 739.0)

        print(f"✅ Loaded {len(waypoints)} waypoints")
        print(f"   Expected distance: {expected_distance:.0f} km")

        # Step 2: Process sections with Directions
        print("\n🗺️  Step 2: Processing sections with Directions API...")
        print(f"   Strategy: Generate route for each section (waypoint_i → waypoint_i+1)")
        print(f"   Sections: {len(waypoints) - 1}")
        print(f"   ⚠️  Note: Directions may optimize routes (potential detours)")

        matched_coords, metadata = process_n2_section_by_section(
            waypoints,
            MAPBOX_TOKEN
        )

        # Step 3: Validate quality
        print("\n🔍 Step 3: Validating quality...")

        road_info = {
            'code': 'N2',
            'name': 'Chaves → Faro',
            'expected_distance_km': expected_distance,
            'coordinates': matched_coords
        }

        distance_km = metadata['distance_km']
        quality_report = get_quality_report(road_info, matched_coords, distance_km)

        print(f"\n📊 Quality Report:")
        print(f"   Points: {quality_report['point_count']}")
        print(f"   Distance: {quality_report['distance_km']:.2f} km")
        print(f"   Density: {quality_report['density']:.2f} pts/km")
        print(f"   Quality: {quality_report['quality']}")
        print(f"   Density valid: {quality_report['density_valid']}")
        print(f"   Geography valid: {quality_report['geo_valid']}")

        if quality_report['quality'] == 'REJECTED':
            print(f"\n❌ REJECTED: Quality check failed")
            for msg in quality_report.get('messages', []):
                print(f"   • {msg}")
            return 1

        # Step 4: Save result
        print("\n💾 Step 4: Saving geometry...")

        save_n2_geometry(matched_coords, metadata)

        print("\n" + "=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"N2 geometry generated successfully:")
        print(f"  • {len(matched_coords)} GPS points")
        print(f"  • {distance_km:.2f} km total distance")
        print(f"  • {len(matched_coords) / distance_km:.2f} pts/km density")
        print(f"  • Quality: {quality_report['quality']}")
        print(f"\nNext steps:")
        print(f"  1. Review n2_from_waypoints.json")
        print(f"  2. Update roads_data.json to use this geometry")
        print(f"  3. Test with process_roads.py")
        print("=" * 70)

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
