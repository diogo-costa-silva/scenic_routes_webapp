#!/usr/bin/env python3
"""
Fetch Road Geometry using Mapbox Directions API with Waypoints

This script reads road definitions from roads_data.json and uses the Mapbox
Directions API with intermediate waypoints to ensure the route follows the
actual road path, not just the shortest route between endpoints.

Author: Road Explorer Portugal
"""

import os
import json
import requests
from pathlib import Path
from math import radians, sin, cos, sqrt, atan2
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')
ROADS_DATA_FILE = Path(__file__).parent / "roads_data.json"


def haversine(lon1, lat1, lon2, lat2):
    """Calculate distance between two points in km."""
    R = 6371
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c


def calculate_total_distance(coords):
    """Calculate total distance along path."""
    if len(coords) < 2:
        return 0.0
    total = 0.0
    for i in range(len(coords) - 1):
        lon1, lat1 = coords[i]
        lon2, lat2 = coords[i + 1]
        total += haversine(lon1, lat1, lon2, lat2)
    return total


def fetch_route_with_waypoints(waypoints, mapbox_token):
    """
    Fetch route from Mapbox Directions API using multiple waypoints.

    Args:
        waypoints: List of dicts with 'lat' and 'lon' keys
        mapbox_token: Mapbox API token

    Returns:
        tuple: (coordinates list, distance_km, route_info dict)

    Raises:
        Exception: If API request fails
    """
    if not waypoints or len(waypoints) < 2:
        raise ValueError("Need at least 2 waypoints")

    if len(waypoints) > 25:
        raise ValueError("Mapbox supports maximum 25 waypoints")

    # Build coordinates string: "lon1,lat1;lon2,lat2;..."
    coords_str = ";".join([f"{wp['lon']},{wp['lat']}" for wp in waypoints])

    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coords_str}"

    params = {
        'access_token': mapbox_token,
        'geometries': 'geojson',
        'overview': 'full',  # Full geometry (all points)
        'steps': 'false'
    }

    print(f"   API request with {len(waypoints)} waypoints...")
    print(f"   URL: {url[:100]}...")

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if data.get('code') != 'Ok':
        raise Exception(f"Mapbox API error: {data.get('code')} - {data.get('message')}")

    routes = data.get('routes', [])
    if not routes:
        raise Exception("No routes found")

    route = routes[0]
    geometry = route['geometry']
    coords = geometry['coordinates']

    route_info = {
        'distance_m': route['distance'],
        'duration_s': route['duration'],
        'waypoints_used': len(waypoints)
    }

    our_distance = calculate_total_distance(coords)

    return coords, our_distance, route_info


def process_road(road_code):
    """
    Process a single road by code, fetching geometry with waypoints.

    Args:
        road_code: Road code (e.g., "N222")

    Returns:
        dict: Road data with coordinates
    """
    print("=" * 70)
    print(f"Processing: {road_code}")
    print("=" * 70)

    # Load roads data
    if not ROADS_DATA_FILE.exists():
        raise FileNotFoundError(f"roads_data.json not found at {ROADS_DATA_FILE}")

    with open(ROADS_DATA_FILE, 'r') as f:
        roads_data = json.load(f)

    # Find the road
    road_info = None
    for road in roads_data:
        if road['code'] == road_code:
            road_info = road
            break

    if not road_info:
        raise ValueError(f"Road {road_code} not found in roads_data.json")

    print(f"Name: {road_info['name']}")
    print(f"Description: {road_info.get('description', 'N/A')}")

    # Check if road has waypoints
    waypoints = road_info.get('waypoints', [])

    if not waypoints:
        print("\nWARNING: No waypoints defined for this road")
        print("Using start/end points only (less accurate)")

        # Fallback to start/end
        waypoints = [
            {"lat": 41.164, "lon": -7.788, "name": road_info['start_point_name']},
            {"lat": 41.178, "lon": -7.548, "name": road_info['end_point_name']}
        ]

    print(f"\nWaypoints: {len(waypoints)}")
    for i, wp in enumerate(waypoints):
        print(f"   {i+1}. {wp.get('name', 'Unnamed')} ({wp['lat']}, {wp['lon']})")

    # Fetch route from Mapbox
    print(f"\nFetching route from Mapbox Directions API...")

    if not MAPBOX_TOKEN:
        raise ValueError("MAPBOX_TOKEN not set in .env")

    coords, distance_km, route_info = fetch_route_with_waypoints(waypoints, MAPBOX_TOKEN)

    print(f"\nRoute fetched successfully!")
    print(f"   Points: {len(coords)}")
    print(f"   Distance (Mapbox): {route_info['distance_m'] / 1000:.2f} km")
    print(f"   Distance (calculated): {distance_km:.2f} km")
    print(f"   Duration: {route_info['duration_s'] / 60:.0f} minutes")

    density = len(coords) / distance_km if distance_km > 0 else 0
    print(f"   Density: {density:.2f} points/km")

    # Quality check
    if density < 2.0:
        print(f"   WARNING: Density below 2.0 points/km")
    elif density >= 3.0:
        print(f"   EXCELLENT geometry quality")
    else:
        print(f"   GOOD geometry quality")

    # Validate endpoints
    start_lon, start_lat = coords[0]
    end_lon, end_lat = coords[-1]

    first_wp = waypoints[0]
    last_wp = waypoints[-1]

    start_dist = haversine(start_lon, start_lat, first_wp['lon'], first_wp['lat'])
    end_dist = haversine(end_lon, end_lat, last_wp['lon'], last_wp['lat'])

    print(f"\nEndpoint validation:")
    print(f"   Start distance from first waypoint: {start_dist:.2f} km")
    print(f"   End distance from last waypoint: {end_dist:.2f} km")

    # Build output data
    output_data = {
        'code': road_info['code'],
        'name': road_info['name'],
        'region': road_info['region'],
        'description': road_info.get('description', ''),
        'point_count': len(coords),
        'distance_km': round(distance_km, 2),
        'density': round(density, 2),
        'start_lat': start_lat,
        'start_lon': start_lon,
        'end_lat': end_lat,
        'end_lon': end_lon,
        'start_point_name': road_info.get('start_point_name', ''),
        'end_point_name': road_info.get('end_point_name', ''),
        'surface': road_info.get('surface', 'asphalt'),
        'data_source': 'mapbox_waypoints',
        'waypoints_used': len(waypoints),
        'coordinates': coords
    }

    return output_data


def save_road_data(road_data):
    """Save road data to JSON and WKT files."""
    code = road_data['code']
    output_dir = Path(__file__).parent

    # Save JSON
    json_file = output_dir / f"{code}_waypoints_route.json"
    with open(json_file, 'w') as f:
        json.dump(road_data, f, indent=2)
    print(f"\nSaved JSON to: {json_file}")

    # Save WKT
    coords = road_data['coordinates']
    wkt_coords = ", ".join([f"{lon} {lat}" for lon, lat in coords])
    wkt_geometry = f"LINESTRING({wkt_coords})"

    wkt_file = output_dir / f"{code}_waypoints_route.wkt"
    with open(wkt_file, 'w') as f:
        f.write(wkt_geometry)
    print(f"Saved WKT to: {wkt_file}")

    return json_file, wkt_file


def generate_sql(road_data, sql_file):
    """Generate SQL UPDATE statement."""
    code = road_data['code']

    # Read WKT
    wkt_file = Path(__file__).parent / f"{code}_waypoints_route.wkt"
    with open(wkt_file, 'r') as f:
        wkt = f.read()

    sql = f'''-- Update {code} geometry with Mapbox route using waypoints
-- This ensures the route follows the actual road path
-- Route calculated with {road_data['waypoints_used']} waypoints
-- Distance: {road_data['distance_km']} km, Points: {road_data['point_count']}

UPDATE roads
SET
  geometry = ST_GeomFromText('{wkt}', 4326),
  start_lat = {road_data['start_lat']},
  start_lon = {road_data['start_lon']},
  end_lat = {road_data['end_lat']},
  end_lon = {road_data['end_lon']},
  distance_km = {road_data['distance_km']},
  data_source = 'mapbox_waypoints'
WHERE code = '{code}';

-- Verify the update
SELECT
  code,
  name,
  distance_km,
  ST_NumPoints(geometry) as point_count,
  data_source
FROM roads
WHERE code = '{code}';
'''

    with open(sql_file, 'w') as f:
        f.write(sql)

    print(f"Saved SQL to: {sql_file}")


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fetch_road_with_waypoints.py <ROAD_CODE>")
        print("Example: python fetch_road_with_waypoints.py N222")
        return 1

    road_code = sys.argv[1].upper()

    try:
        # Process road
        road_data = process_road(road_code)

        # Save files
        json_file, wkt_file = save_road_data(road_data)

        # Generate SQL
        sql_file = Path(__file__).parent / f"update_{road_code}_waypoints.sql"
        generate_sql(road_data, sql_file)

        # Summary
        print(f"\n{'='*70}")
        print(f"SUCCESS - {road_code} processed with waypoints")
        print(f"{'='*70}")
        print(f"Final:")
        print(f"   Points: {road_data['point_count']}")
        print(f"   Distance: {road_data['distance_km']} km")
        print(f"   Quality: {'EXCELLENT' if road_data['density'] >= 3.0 else 'GOOD' if road_data['density'] >= 2.0 else 'POOR'}")
        print(f"   Waypoints used: {road_data['waypoints_used']}")
        print(f"")
        print(f"Files created:")
        print(f"   * {json_file.name}")
        print(f"   * {wkt_file.name}")
        print(f"   * {sql_file.name}")
        print(f"")
        print(f"Next: Run SQL script to update database")
        print(f"{'='*70}")

        return 0

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
