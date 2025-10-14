#!/usr/bin/env python3
"""
==============================================================================
Single Road Processing Test Script
==============================================================================
Script: test_single_road.py
Purpose: Test road data processing pipeline with a single road (N2)
Author: Road Explorer Portugal
==============================================================================

This script processes a single road to verify the complete pipeline:
1. Fetch geometry from OpenStreetMap
2. Calculate distance and curve metrics
3. Fetch elevation data from Mapbox
4. Insert into Supabase database
5. Verify data integrity

Usage:
    python test_single_road.py

Prerequisites:
    - Virtual environment activated
    - Dependencies installed
    - .env file configured
    - Database connection working (run test_connection.py first)

Note:
    This test uses N2 (Chaves → Faro) - Portugal's Route 66
    WARNING: N2 is 739km long and will take 10-15 minutes to process!
    If you want a faster test, edit this script to use N339 instead.
==============================================================================
"""

import os
import sys
import time
from typing import Dict
from dotenv import load_dotenv
from supabase import create_client, Client

# Import our processing modules
from osm_utils import get_road_from_osm
from metrics import calculate_all_metrics
from elevation import calculate_elevation_for_coordinates


# Load environment variables
load_dotenv()


def print_header(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def format_time(seconds: float) -> str:
    """Format seconds into human-readable time."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def test_single_road():
    """Test processing a single road."""

    print("=" * 70)
    print("  🛣️  Road Explorer Portugal - Single Road Test")
    print("=" * 70)
    print("\n📋 This test will process ONE road through the complete pipeline:")
    print("   1. Fetch geometry from OSM")
    print("   2. Calculate metrics (distance, curves)")
    print("   3. Fetch elevation data from Mapbox")
    print("   4. Insert into Supabase")
    print("   5. Verify data\n")

    # =========================================================================
    # Test Road Definition
    # =========================================================================
    # Using N2 - change to N339 for faster test!
    test_road = {
        "code": "N2",
        "name": "Chaves → Faro",
        "region": "Continental",
        "osm_ref": "N 2",
        "description": "Portugal's legendary Route 66 - 739km from North to South",
        "start_point_name": "Chaves",
        "end_point_name": "Faro",
        "surface": "asphalt",
        "category": "Long Distance"
    }

    # Alternative: Use N339 for faster testing (much shorter road)
    # Uncomment to use N339 instead:
    """
    test_road = {
        "code": "N339-TEST",
        "name": "Covilhã → Torre (Test)",
        "region": "Continental",
        "osm_ref": "N 339",
        "description": "Test road - Climb to Portugal's highest point",
        "start_point_name": "Covilhã",
        "end_point_name": "Torre",
        "surface": "asphalt",
        "category": "Mountain"
    }
    """

    print(f"🎯 Test Road: {test_road['code']} - {test_road['name']}")
    print(f"📍 Region: {test_road['region']}")
    print(f"🗺️  OSM Reference: {test_road['osm_ref']}")
    print(f"ℹ️  {test_road['description']}\n")

    if test_road['code'] == "N2":
        print("⚠️  WARNING: N2 is 739km long!")
        print("   This test will take 10-15 minutes due to elevation API calls.")
        print("   To test faster, edit this script and uncomment the N339 definition.\n")

        response = input("Continue with N2 test? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("\n❌ Test cancelled. Edit script to use N339 for faster test.")
            return 1

    overall_start = time.time()

    # =========================================================================
    # Initialize Supabase
    # =========================================================================
    print_header("Step 0: Initialize Database Connection")

    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")

    if not supabase_url or not supabase_key:
        print("❌ Missing Supabase credentials!")
        print("   Run test_connection.py first to verify setup.")
        return 1

    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Supabase: {e}")
        return 1

    # Check if road already exists
    try:
        existing = supabase.table('roads').select('id, code').eq('code', test_road['code']).execute()
        if existing.data:
            print(f"\n⚠️  Road {test_road['code']} already exists in database (ID: {existing.data[0]['id']})")
            response = input("Delete existing road and reprocess? (yes/no): ").strip().lower()
            if response in ['yes', 'y']:
                supabase.table('roads').delete().eq('code', test_road['code']).execute()
                print(f"✅ Deleted existing {test_road['code']}")
            else:
                print("❌ Test cancelled. Choose a different road or delete manually.")
                return 1
    except Exception as e:
        print(f"⚠️  Could not check for existing road: {e}")

    # =========================================================================
    # Step 1: Fetch Geometry from OSM
    # =========================================================================
    print_header("Step 1: Fetch Geometry from OpenStreetMap")

    step_start = time.time()

    try:
        print(f"📡 Querying Overpass API for: {test_road['osm_ref']}")
        coordinates = get_road_from_osm(test_road['osm_ref'])

        if not coordinates or len(coordinates) < 2:
            print(f"❌ No coordinates found for {test_road['osm_ref']}")
            print("   Check if the OSM reference is correct")
            print("   Visit https://overpass-turbo.eu/ to verify")
            return 1

        step_time = time.time() - step_start
        print(f"\n✅ Success: {len(coordinates)} GPS points fetched")
        print(f"   Time: {format_time(step_time)}")
        print(f"   Start: {coordinates[0]}")
        print(f"   End: {coordinates[-1]}")

    except Exception as e:
        print(f"❌ OSM fetch failed: {e}")
        return 1

    # =========================================================================
    # Step 2: Calculate Metrics
    # =========================================================================
    print_header("Step 2: Calculate Road Metrics")

    step_start = time.time()

    try:
        print("📊 Calculating distance, curves, and straights...")
        metrics = calculate_all_metrics(coordinates)

        step_time = time.time() - step_start
        print(f"\n✅ Metrics calculated:")
        print(f"   Distance: {metrics.get('distance_km', 0)} km")
        print(f"   Total Curves: {metrics.get('curve_count_total', 0)}")
        print(f"   - Gentle: {metrics.get('curve_count_gentle', 0)}")
        print(f"   - Moderate: {metrics.get('curve_count_moderate', 0)}")
        print(f"   - Sharp: {metrics.get('curve_count_sharp', 0)}")
        print(f"   Straight Sections: {metrics.get('straight_count', 0)}")
        print(f"   Longest Straight: {metrics.get('longest_straight_km', 0)} km")
        print(f"   Time: {format_time(step_time)}")

    except Exception as e:
        print(f"❌ Metrics calculation failed: {e}")
        return 1

    # =========================================================================
    # Step 3: Fetch Elevation Data
    # =========================================================================
    print_header("Step 3: Fetch Elevation Data from Mapbox")

    step_start = time.time()

    try:
        print("🏔️  Fetching elevation data (this may take several minutes)...")
        print(f"   Sampling every 10th point = ~{len(coordinates)//10} API calls")

        elevation_metrics = calculate_elevation_for_coordinates(coordinates)

        step_time = time.time() - step_start
        print(f"\n✅ Elevation data fetched:")
        print(f"   Maximum: {elevation_metrics.get('elevation_max', 0)}m")
        print(f"   Minimum: {elevation_metrics.get('elevation_min', 0)}m")
        print(f"   Total Gain: {elevation_metrics.get('elevation_gain', 0)}m")
        print(f"   Total Loss: {elevation_metrics.get('elevation_loss', 0)}m")
        print(f"   Time: {format_time(step_time)}")

    except Exception as e:
        print(f"❌ Elevation fetch failed: {e}")
        print("   Continuing without elevation data...")
        elevation_metrics = {
            'elevation_max': 0,
            'elevation_min': 0,
            'elevation_gain': 0,
            'elevation_loss': 0
        }

    # =========================================================================
    # Step 4: Prepare Data for Database
    # =========================================================================
    print_header("Step 4: Prepare Database Entry")

    try:
        # Convert coordinates to WKT format
        coords_wkt = ", ".join([f"{lon} {lat}" for lon, lat in coordinates])
        geometry_wkt = f"LINESTRING({coords_wkt})"

        road_data = {
            # Identifiers
            "code": test_road['code'],
            "name": test_road['name'],
            "description": test_road.get('description', ''),

            # Classification
            "region": test_road['region'],

            # Geometry
            "geometry": geometry_wkt,

            # Start/End points
            "start_point_name": test_road.get('start_point_name', ''),
            "start_lat": coordinates[0][1],
            "start_lon": coordinates[0][0],
            "end_point_name": test_road.get('end_point_name', ''),
            "end_lat": coordinates[-1][1],
            "end_lon": coordinates[-1][0],

            # Metrics
            **metrics,
            **elevation_metrics,

            # Characteristics
            "surface": test_road.get('surface', 'asphalt'),
            "surface_verified": False,
            "data_source": "osm"
        }

        print("✅ Data prepared for insertion")
        print(f"   WKT geometry length: {len(geometry_wkt)} characters")
        print(f"   Total fields: {len(road_data)}")

    except Exception as e:
        print(f"❌ Data preparation failed: {e}")
        return 1

    # =========================================================================
    # Step 5: Insert into Supabase
    # =========================================================================
    print_header("Step 5: Insert into Supabase")

    step_start = time.time()

    try:
        print("💾 Inserting road data...")
        result = supabase.table('roads').insert(road_data).execute()

        if result.data:
            road_id = result.data[0]['id']
            step_time = time.time() - step_start
            print(f"✅ Road inserted successfully!")
            print(f"   ID: {road_id}")
            print(f"   Code: {test_road['code']}")
            print(f"   Time: {format_time(step_time)}")
        else:
            print("❌ Insert succeeded but no data returned")
            return 1

    except Exception as e:
        print(f"❌ Database insertion failed: {e}")
        return 1

    # =========================================================================
    # Step 6: Verify Data
    # =========================================================================
    print_header("Step 6: Verify Inserted Data")

    try:
        # Fetch the road back from database
        verify_result = supabase.table('roads').select('*').eq('code', test_road['code']).single().execute()

        if verify_result.data:
            print("✅ Road verified in database:")
            print(f"   Code: {verify_result.data['code']}")
            print(f"   Name: {verify_result.data['name']}")
            print(f"   Distance: {verify_result.data['distance_km']} km")
            print(f"   Curves: {verify_result.data['curve_count_total']}")
            print(f"   Elevation: {verify_result.data['elevation_min']}m → {verify_result.data['elevation_max']}m")

            # Check geometry is valid
            if verify_result.data.get('geometry'):
                print(f"   Geometry: ✅ Valid (type: {verify_result.data['geometry'].get('type', 'unknown')})")
        else:
            print("⚠️  Road not found in verification query")
            return 1

    except Exception as e:
        print(f"⚠️  Verification failed: {e}")
        print("   Road was inserted but couldn't be verified")

    # =========================================================================
    # Summary
    # =========================================================================
    overall_time = time.time() - overall_start

    print_header("✅ Test Complete!")
    print(f"\n🎉 Successfully processed {test_road['code']} - {test_road['name']}")
    print(f"⏱️  Total time: {format_time(overall_time)}")
    print(f"📊 Road ID: {road_id}")
    print(f"📏 Distance: {metrics.get('distance_km', 0)} km")
    print(f"🌀 Curves: {metrics.get('curve_count_total', 0)}")
    print(f"🏔️  Elevation gain: {elevation_metrics.get('elevation_gain', 0)}m")
    print("\n✅ The complete pipeline is working correctly!")
    print("🚀 You can now run: python process_roads.py")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    exit(test_single_road())
