#!/usr/bin/env python3
"""
==============================================================================
Road Data Processing Script
==============================================================================
Script: process_roads.py
Purpose: Main script to process road data and populate Supabase database
Author: Road Explorer Portugal
==============================================================================

Usage:
    python process_roads.py

Prerequisites:
    1. UV installed (uv --version)
    2. Virtual environment created (uv venv)
    3. Dependencies installed (uv pip install -r requirements.txt)
    4. .env file configured with API keys

Flow:
    1. Load road definitions from roads_data.json
    2. For each road:
       a. Fetch geometry from OSM
       b. Calculate distance and curves
       c. Fetch elevation data
       d. Insert into Supabase
    3. Report results
==============================================================================
"""

import os
import json
import time
from typing import Dict, List, Optional, Callable, Any
from dotenv import load_dotenv
from supabase import create_client, Client

# Import our modules
from osm_utils import get_road_from_osm
from metrics import calculate_all_metrics
from elevation import calculate_elevation_for_coordinates


# ==============================================================================
# Retry Logic Configuration
# ==============================================================================

MAX_RETRIES = 3
RETRY_DELAY_BASE = 2  # seconds (exponential backoff: 2s, 4s, 8s)


def retry_with_backoff(func: Callable, *args, **kwargs) -> Any:
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        *args, **kwargs: Arguments to pass to function

    Returns:
        Result of function call

    Raises:
        Last exception if all retries fail
    """
    for attempt in range(MAX_RETRIES):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                # Last attempt failed
                raise

            delay = RETRY_DELAY_BASE * (2 ** attempt)
            print(f"   ⚠️  Attempt {attempt + 1} failed: {e}")
            print(f"   🔄 Retrying in {delay}s...")
            time.sleep(delay)


# Load environment variables
load_dotenv()


# ==============================================================================
# Configuration
# ==============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ROADS_DATA_FILE = "roads_data.json"


# ==============================================================================
# Initialize Supabase Client
# ==============================================================================

def init_supabase() -> Client:
    """
    Initialize and return Supabase client.

    Returns:
        Client: Supabase client instance

    Raises:
        ValueError: If credentials are missing
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "❌ Missing Supabase credentials!\n"
            "   Please set SUPABASE_URL and SUPABASE_KEY in .env file"
        )

    print("📡 Connecting to Supabase...")
    print(f"   URL: {SUPABASE_URL}")

    return create_client(SUPABASE_URL, SUPABASE_KEY)


# ==============================================================================
# Data Loading
# ==============================================================================

def load_roads_data() -> List[Dict]:
    """
    Load road definitions from roads_data.json.

    Returns:
        List[Dict]: List of road definitions

    Raises:
        FileNotFoundError: If roads_data.json doesn't exist
    """
    print(f"\n📂 Loading road definitions from {ROADS_DATA_FILE}...")

    if not os.path.exists(ROADS_DATA_FILE):
        raise FileNotFoundError(
            f"❌ {ROADS_DATA_FILE} not found!\n"
            f"   Please create this file with road definitions"
        )

    with open(ROADS_DATA_FILE, 'r', encoding='utf-8') as f:
        roads_data = json.load(f)

    print(f"✅ Loaded {len(roads_data)} road definitions")
    return roads_data


# ==============================================================================
# Road Processing
# ==============================================================================

def check_road_exists(supabase: Client, code: str) -> Optional[int]:
    """
    Check if a road already exists in the database.

    Args:
        supabase: Supabase client
        code: Road code to check

    Returns:
        Road ID if exists, None otherwise
    """
    try:
        result = supabase.table('roads').select('id').eq('code', code).execute()
        if result.data:
            return result.data[0]['id']
        return None
    except Exception as e:
        print(f"   ⚠️  Warning: Could not check for existing road: {e}")
        return None


def process_single_road(road_info: Dict, supabase: Client, skip_existing: bool = True) -> bool:
    """
    Process a single road: fetch data, calculate metrics, insert to database.

    Args:
        road_info (Dict): Road definition dictionary
        supabase (Client): Supabase client
        skip_existing (bool): Skip if road already exists (default: True)

    Returns:
        bool: True if successful, False otherwise
    """
    code = road_info.get('code', 'UNKNOWN')
    name = road_info.get('name', 'Unknown Road')

    print("\n" + "=" * 70)
    print(f"🛣️  Processing: {code} - {name}")
    print("=" * 70)

    try:
        # Step 0: Check if road already exists
        if skip_existing:
            existing_id = check_road_exists(supabase, code)
            if existing_id:
                print(f"⏭️  Road {code} already exists (ID: {existing_id}), skipping...")
                return True

        # Step 1: Fetch OSM data with retry
        print("\n📡 Step 1: Fetching geometry from OpenStreetMap...")
        osm_ref = road_info.get('osm_ref', code)
        coordinates = retry_with_backoff(get_road_from_osm, osm_ref)

        if not coordinates or len(coordinates) < 2:
            print(f"❌ Error: No coordinates found for {code}")
            return False

        print(f"✅ Found {len(coordinates)} GPS points")

        # Step 2: Calculate metrics
        print("\n📊 Step 2: Calculating metrics...")
        try:
            metrics = calculate_all_metrics(coordinates)
            print(f"✅ Distance: {metrics.get('distance_km', 0)} km")
            print(f"✅ Curves: {metrics.get('curve_count_total', 0)}")
        except Exception as e:
            print(f"❌ Error calculating metrics: {e}")
            return False

        # Step 3: Calculate elevation with retry
        print("\n🏔️  Step 3: Calculating elevation (this may take a while)...")
        try:
            elevation_metrics = retry_with_backoff(
                calculate_elevation_for_coordinates,
                coordinates
            )
            print(f"✅ Elevation: {elevation_metrics.get('elevation_min', 0)}m "
                  f"→ {elevation_metrics.get('elevation_max', 0)}m")
        except Exception as e:
            print(f"⚠️  Warning: Elevation calculation failed: {e}")
            print(f"   Continuing without elevation data...")
            elevation_metrics = {
                'elevation_max': 0,
                'elevation_min': 0,
                'elevation_gain': 0,
                'elevation_loss': 0
            }

        # Step 4: Prepare data for database
        print("\n💾 Step 4: Preparing database entry...")
        road_data = prepare_road_data(road_info, coordinates, metrics, elevation_metrics)

        # Step 5: Insert into Supabase with retry
        print("\n📥 Step 5: Inserting into database...")
        try:
            result = retry_with_backoff(
                lambda: supabase.table('roads').insert(road_data).execute()
            )

            road_id = result.data[0]['id'] if result.data else None
            print(f"✅ Successfully inserted {code} (ID: {road_id})")

            return True
        except Exception as e:
            print(f"❌ Database insertion failed after {MAX_RETRIES} attempts: {e}")
            return False

    except KeyboardInterrupt:
        print(f"\n\n⚠️  Processing interrupted by user for {code}")
        print(f"   You can resume processing by running the script again")
        print(f"   (Already processed roads will be skipped)")
        raise
    except Exception as e:
        print(f"❌ Error processing {code}: {e}")
        import traceback
        traceback.print_exc()
        return False


def prepare_road_data(
    road_info: Dict,
    coordinates: List,
    metrics: Dict,
    elevation_metrics: Dict
) -> Dict:
    """
    Prepare road data dictionary for database insertion.

    Args:
        road_info (Dict): Original road definition
        coordinates (List): GPS coordinates
        metrics (Dict): Calculated metrics
        elevation_metrics (Dict): Elevation metrics

    Returns:
        Dict: Complete road data ready for database
    """
    # Convert coordinates to WKT LINESTRING format
    coords_wkt = ", ".join([f"{lon} {lat}" for lon, lat in coordinates])
    geometry_wkt = f"LINESTRING({coords_wkt})"

    return {
        # Identifiers
        "code": road_info['code'],
        "name": road_info['name'],
        "description": road_info.get('description', ''),

        # Classification
        "region": road_info['region'],

        # Geometry
        "geometry": geometry_wkt,

        # Start/End points
        "start_point_name": road_info.get('start_point_name', ''),
        "start_lat": coordinates[0][1],
        "start_lon": coordinates[0][0],
        "end_point_name": road_info.get('end_point_name', ''),
        "end_lat": coordinates[-1][1],
        "end_lon": coordinates[-1][0],

        # Metrics
        **metrics,
        **elevation_metrics,

        # Characteristics
        "surface": road_info.get('surface', 'asphalt'),
        "surface_verified": False,
        "data_source": "osm"
    }


# ==============================================================================
# Main Execution
# ==============================================================================

def main():
    """Main execution function."""

    print("=" * 70)
    print("🚀 Road Explorer Portugal - Data Processing")
    print("=" * 70)

    try:
        # Initialize
        supabase = init_supabase()
        roads_data = load_roads_data()

        print(f"\n📊 Ready to process {len(roads_data)} roads")

        # Process each road
        success_count = 0
        fail_count = 0
        skipped_count = 0

        start_time = time.time()

        for i, road_info in enumerate(roads_data, 1):
            print(f"\n\n{'='*70}")
            print(f"Road {i}/{len(roads_data)}")
            print(f"{'='*70}")

            road_start_time = time.time()

            try:
                result = process_single_road(road_info, supabase, skip_existing=True)

                # Check if it was skipped or processed
                code = road_info.get('code', 'UNKNOWN')
                existing_id = check_road_exists(supabase, code)

                if result:
                    # Check if it existed before this run
                    if existing_id and i == 1:
                        skipped_count += 1
                    else:
                        success_count += 1
                else:
                    fail_count += 1

            except KeyboardInterrupt:
                print("\n\n⚠️  Processing interrupted by user!")
                print(f"   Processed: {success_count}")
                print(f"   Failed: {fail_count}")
                print(f"   Remaining: {len(roads_data) - i}")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                fail_count += 1

            road_time = time.time() - road_start_time
            print(f"\n⏱️  Road processed in {road_time:.1f}s")

            # Small delay between roads to be respectful to APIs
            if i < len(roads_data):
                print("\n⏳ Waiting 2 seconds before next road...")
                time.sleep(2)

        # Summary
        print("\n" + "=" * 70)
        print("📈 Processing Complete!")
        print("=" * 70)
        print(f"✅ Success: {success_count}")
        print(f"❌ Failed: {fail_count}")
        print(f"📊 Total: {len(roads_data)}")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
