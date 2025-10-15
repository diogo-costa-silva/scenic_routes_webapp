#!/usr/bin/env python3
"""
==============================================================================
Hybrid Road Geometry Strategy - Orchestrator
==============================================================================
Module: hybrid_strategy.py
Purpose: Orchestrate OSM → Validate → Map Matching → Cache decision flow
Author: Road Explorer Portugal
==============================================================================

THE SOLUTION TO N222 DETOUR PROBLEM

Hybrid Strategy Flow:
1. Check cache (30-day) → Return if hit
2. Try OSM Overpass recursive query (FREE)
3. Validate quality (density, bounds, distance)
   ├─ GOOD (≥2.0 pts/km) → Use OSM (70% roads)
   └─ POOR → Mapbox Map Matching fallback (30% roads)
4. Cache result (30 days)

Expected Results:
- 70% roads from OSM (FREE)
- 30% roads from Map Matching (within free tier)
- Monthly cost: $0
- N222 accuracy: ✅ CORRECT (no detour)

==============================================================================
"""

import os
import json
import time
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict
from pathlib import Path
from datetime import datetime, timedelta
from geopy.distance import geodesic

# Import our modules
from osm_utils import get_road_from_osm
from mapbox_matching import batch_map_matching, validate_coordinates_for_matching
from validation import (
    validate_geometry_density,
    validate_all_points_in_portugal,
    get_quality_report,
    print_quality_report
)


# ==============================================================================
# Configuration
# ==============================================================================

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_MAX_AGE_DAYS = 30

# Quality thresholds
MIN_DENSITY = 2.0  # points/km
MIN_POINTS = 100
DISTANCE_TOLERANCE = 0.20  # ±20%


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class GeometryResult:
    """
    Result container for road geometry with quality metrics.

    Attributes:
        coordinates: List of (lon, lat) tuples
        source: Data source ('osm_recursive' or 'mapbox_matching')
        quality_report: Quality validation report dict
        point_count: Total number of GPS points
        density: Points per kilometer
        distance_km: Total road distance in kilometers
        cached: Whether result came from cache
    """
    coordinates: List[Tuple[float, float]]
    source: str
    quality_report: Dict
    point_count: int
    density: float
    distance_km: float
    cached: bool = False


# ==============================================================================
# Cache Functions
# ==============================================================================

def _check_cache(road_ref: str) -> Optional[GeometryResult]:
    """
    Check if cached geometry exists and is fresh.

    Args:
        road_ref: Road reference (e.g., "N 222")

    Returns:
        GeometryResult if cache hit and fresh, None otherwise
    """
    if not CACHE_DIR.exists():
        return None

    # Normalize road_ref for filename
    cache_filename = road_ref.replace(" ", "_").replace("/", "_") + ".json"
    cache_file = CACHE_DIR / cache_filename

    if not cache_file.exists():
        return None

    try:
        # Load cache data
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)

        # Check age
        cached_at_str = cache_data.get('cached_at')
        if cached_at_str:
            cached_at = datetime.fromisoformat(cached_at_str)
            age = datetime.now() - cached_at
            age_days = age.days

            if age_days > CACHE_MAX_AGE_DAYS:
                print(f"   💾 Cache expired ({age_days}d old), re-fetching...")
                return None

            # Cache is fresh - reconstruct GeometryResult
            coordinates = [tuple(coord) for coord in cache_data['coordinates']]

            result = GeometryResult(
                coordinates=coordinates,
                source=cache_data['source'],
                quality_report=cache_data['quality_report'],
                point_count=cache_data['point_count'],
                density=cache_data['density'],
                distance_km=cache_data['distance_km'],
                cached=True
            )

            print(f"   💾 Cache HIT: {road_ref} ({age_days}d old)")
            print(f"      Source: {result.source}, Density: {result.density:.2f} pts/km")

            return result

    except Exception as e:
        print(f"   ⚠️  Cache read error: {e}")
        return None

    return None


def _save_cache(road_ref: str, result: GeometryResult) -> None:
    """
    Save geometry result to cache.

    Args:
        road_ref: Road reference
        result: GeometryResult to cache
    """
    try:
        # Create cache directory if doesn't exist
        CACHE_DIR.mkdir(exist_ok=True)

        # Normalize road_ref for filename
        cache_filename = road_ref.replace(" ", "_").replace("/", "_") + ".json"
        cache_file = CACHE_DIR / cache_filename

        # Prepare cache data
        cache_data = {
            'road_ref': road_ref,
            'coordinates': result.coordinates,
            'source': result.source,
            'quality_report': result.quality_report,
            'point_count': result.point_count,
            'density': result.density,
            'distance_km': result.distance_km,
            'cached_at': datetime.now().isoformat()
        }

        # Save to file
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

        print(f"   💾 Cached: {road_ref} ({result.source}, {result.density:.2f} pts/km)")

    except Exception as e:
        print(f"   ⚠️  Cache save error: {e}")


# ==============================================================================
# Distance Calculation
# ==============================================================================

def _calculate_distance(coordinates: List[Tuple[float, float]]) -> float:
    """
    Calculate total distance of coordinate path in kilometers.

    Args:
        coordinates: List of (lon, lat) tuples

    Returns:
        Distance in kilometers
    """
    if len(coordinates) < 2:
        return 0.0

    total_distance = 0.0

    for i in range(len(coordinates) - 1):
        point1 = (coordinates[i][1], coordinates[i][0])  # (lat, lon)
        point2 = (coordinates[i + 1][1], coordinates[i + 1][0])
        distance = geodesic(point1, point2).kilometers
        total_distance += distance

    return total_distance


# ==============================================================================
# Main Hybrid Strategy Orchestrator
# ==============================================================================

def get_road_geometry_hybrid(
    road_ref: str,
    bbox: Tuple[float, float, float, float],
    expected_distance_km: float,
    mapbox_token: Optional[str] = None
) -> Optional[GeometryResult]:
    """
    Get road geometry using hybrid strategy.

    Decision Flow:
    1. Check cache (30-day) → Return if hit
    2. Try OSM Overpass query (FREE)
    3. Validate quality (density ≥2.0, bounds, distance)
       ├─ GOOD → Use OSM (cache + return)
       └─ POOR → Try Map Matching (if token provided)
    4. Validate Map Matching quality
       ├─ GOOD → Cache + return
       └─ POOR → Reject (return None)

    Args:
        road_ref: Road reference (e.g., "N 222")
        bbox: Bounding box (south, west, north, east)
        expected_distance_km: Expected road distance for validation
        mapbox_token: Mapbox API token (optional, for Map Matching fallback)

    Returns:
        GeometryResult with coordinates and quality metrics, or None if failed

    Example:
        >>> result = get_road_geometry_hybrid(
        ...     road_ref="N 222",
        ...     bbox=(40.9, -7.9, 41.2, -7.5),
        ...     expected_distance_km=27.0,
        ...     mapbox_token="pk.xxx"
        ... )
        >>> if result:
        ...     print(f"Source: {result.source}, Density: {result.density:.2f}")
        Source: osm_recursive, Density: 20.07
    """

    print(f"\n{'='*70}")
    print(f"🔄 HYBRID STRATEGY: {road_ref}")
    print(f"{'='*70}")

    # STEP 1: Check cache
    print(f"\n📍 Step 1: Checking cache...")
    cached_result = _check_cache(road_ref)
    if cached_result:
        print(f"✅ Using cached geometry ({cached_result.source})")
        return cached_result

    print(f"   💾 Cache MISS - fetching fresh data")

    # STEP 2: Try OSM Overpass query
    print(f"\n📍 Step 2: Fetching from OSM Overpass...")
    print(f"   Bounding box: S={bbox[0]}, W={bbox[1]}, N={bbox[2]}, E={bbox[3]}")

    osm_coords = get_road_from_osm(road_ref, bbox)

    if not osm_coords or len(osm_coords) < 2:
        print(f"❌ OSM query failed - no coordinates returned")
        print(f"   Road may not exist in OSM with ref='{road_ref}'")
        return None

    print(f"✅ OSM data: {len(osm_coords)} GPS points")

    # Calculate actual distance
    distance_km = _calculate_distance(osm_coords)
    print(f"   📏 Distance: {distance_km:.2f} km (expected: {expected_distance_km:.2f} km)")

    # STEP 3: Validate OSM quality
    print(f"\n📍 Step 3: Validating OSM quality...")

    road_info = {'code': road_ref}
    quality_report = get_quality_report(road_info, osm_coords, distance_km)

    # Print quality report
    print_quality_report(quality_report)

    # Check if quality meets minimum standards
    density = quality_report['density']
    geo_valid = quality_report['geo_valid']
    density_valid = quality_report['density_valid']

    # Distance validation
    distance_diff_pct = abs(distance_km - expected_distance_km) / expected_distance_km
    distance_valid = distance_diff_pct <= DISTANCE_TOLERANCE

    if not distance_valid:
        print(f"⚠️  Warning: Distance mismatch {distance_diff_pct*100:.1f}% "
              f"(tolerance: {DISTANCE_TOLERANCE*100:.0f}%)")

    # STEP 4a: If OSM quality is GOOD, use it
    if density_valid and geo_valid and distance_valid and len(osm_coords) >= MIN_POINTS:
        print(f"\n✅ OSM quality GOOD - using OSM geometry")
        print(f"   Source: osm_recursive")
        print(f"   Density: {density:.2f} pts/km")
        print(f"   Quality: {quality_report['quality']}")

        result = GeometryResult(
            coordinates=osm_coords,
            source='osm_recursive',
            quality_report=quality_report,
            point_count=len(osm_coords),
            density=density,
            distance_km=distance_km,
            cached=False
        )

        # Cache the result
        _save_cache(road_ref, result)

        return result

    # STEP 4b: OSM quality is POOR - try Map Matching fallback
    print(f"\n⚠️  OSM quality POOR:")
    if not density_valid:
        print(f"   • Density {density:.2f} < {MIN_DENSITY} pts/km")
    if not geo_valid:
        print(f"   • Some points outside Portugal bounds")
    if not distance_valid:
        print(f"   • Distance {distance_km:.2f}km differs {distance_diff_pct*100:.1f}% from expected {expected_distance_km}km")
    if len(osm_coords) < MIN_POINTS:
        print(f"   • Only {len(osm_coords)} points (minimum: {MIN_POINTS})")

    if not mapbox_token:
        print(f"\n❌ No Mapbox token provided - cannot refine with Map Matching")
        print(f"   Rejecting road {road_ref}")
        return None

    print(f"\n🗺️  Trying Map Matching API fallback...")

    # Pre-validate: Check for large coordinate gaps
    print(f"   🔍 Pre-validating coordinates...")
    coords_valid, warnings = validate_coordinates_for_matching(osm_coords)

    if warnings:
        for warning in warnings:
            print(f"      {warning}")

    if not coords_valid:
        print(f"\n❌ Pre-validation failed: Too many disconnected segments")
        print(f"   Map Matching would fail or produce poor results")
        print(f"   Rejecting road {road_ref}")
        return None

    print(f"   ✅ Pre-validation passed - proceeding with Map Matching")

    # Use Map Matching to refine
    matched_coords = batch_map_matching(osm_coords, mapbox_token)

    if not matched_coords or len(matched_coords) < 2:
        print(f"❌ Map Matching failed")
        return None

    # Recalculate distance and validate
    matched_distance_km = _calculate_distance(matched_coords)
    matched_quality_report = get_quality_report(
        road_info, matched_coords, matched_distance_km
    )

    print(f"\n📊 Map Matching Quality:")
    print_quality_report(matched_quality_report)

    matched_density = matched_quality_report['density']
    matched_geo_valid = matched_quality_report['geo_valid']
    matched_density_valid = matched_quality_report['density_valid']

    # Check if Map Matching improved quality
    if matched_density_valid and matched_geo_valid and len(matched_coords) >= MIN_POINTS:
        print(f"\n✅ Map Matching quality GOOD - using refined geometry")
        print(f"   Source: mapbox_matching")
        print(f"   Density: {matched_density:.2f} pts/km (was {density:.2f})")
        print(f"   Improvement: {matched_density/density:.1f}x")

        result = GeometryResult(
            coordinates=matched_coords,
            source='mapbox_matching',
            quality_report=matched_quality_report,
            point_count=len(matched_coords),
            density=matched_density,
            distance_km=matched_distance_km,
            cached=False
        )

        # Cache the result
        _save_cache(road_ref, result)

        return result

    else:
        print(f"\n❌ Map Matching quality still POOR - rejecting road")
        print(f"   Better NO road than BAD road")
        return None


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    print("=" * 70)
    print("Hybrid Strategy - Test Suite")
    print("=" * 70)

    # Load environment
    load_dotenv()
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN", "")

    # Test 1: N222 (Expected: OSM source with excellent quality)
    print("\n🧪 Test 1: N222 (Peso da Régua → Pinhão)")
    print("-" * 70)

    result = get_road_geometry_hybrid(
        road_ref="N 222",
        bbox=(40.9, -7.9, 41.2, -7.5),
        expected_distance_km=27.0,
        mapbox_token=MAPBOX_TOKEN if MAPBOX_TOKEN else None
    )

    if result:
        print(f"\n✅ Test 1 SUCCESS")
        print(f"   Source: {result.source}")
        print(f"   Points: {result.point_count}")
        print(f"   Density: {result.density:.2f} pts/km")
        print(f"   Quality: {result.quality_report['quality']}")
    else:
        print(f"\n❌ Test 1 FAILED: No result")

    print("\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("=" * 70)
