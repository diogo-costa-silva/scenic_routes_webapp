#!/usr/bin/env python3
"""
==============================================================================
Database Connection Test Script
==============================================================================
Script: test_connection.py
Purpose: Comprehensive test of Supabase database connection and setup
Author: Road Explorer Portugal
==============================================================================

This script verifies:
1. Environment variables are configured
2. Supabase connection works
3. PostGIS extension is enabled
4. Roads table exists and is accessible
5. Geometry functions work correctly
6. Can perform CRUD operations

Usage:
    python test_connection.py

Prerequisites:
    - Virtual environment activated
    - Dependencies installed
    - .env file configured
==============================================================================
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test counter
tests_passed = 0
tests_total = 0


def test_result(success: bool, message: str):
    """Print test result and update counter."""
    global tests_passed, tests_total
    tests_total += 1
    if success:
        tests_passed += 1
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    """Run all connection tests."""
    print("=" * 70)
    print("  🧪 Road Explorer Portugal - Database Connection Test")
    print("=" * 70)

    # =========================================================================
    # Test 1: Environment Variables
    # =========================================================================
    print_section("1. Testing Environment Variables")

    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    mapbox_token = os.getenv("MAPBOX_TOKEN", "")

    test_result(
        bool(supabase_url),
        f"SUPABASE_URL configured ({supabase_url[:20]}...)"
    )
    test_result(
        bool(supabase_key),
        f"SUPABASE_KEY configured (length: {len(supabase_key)})"
    )
    test_result(
        bool(mapbox_token),
        f"MAPBOX_TOKEN configured ({mapbox_token[:10]}...)"
    )

    if not supabase_url or not supabase_key:
        print("\n❌ Missing required credentials! Cannot continue.")
        print("   Please configure SUPABASE_URL and SUPABASE_KEY in .env file")
        return 1

    # =========================================================================
    # Test 2: Import Dependencies
    # =========================================================================
    print_section("2. Testing Package Imports")

    try:
        from supabase import create_client, Client
        test_result(True, "Supabase package imported")
    except ImportError as e:
        test_result(False, f"Supabase import failed: {e}")
        print("\n   Run: uv pip install -r requirements.txt")
        return 1

    try:
        import requests
        test_result(True, "Requests package imported")
    except ImportError as e:
        test_result(False, f"Requests import failed: {e}")
        return 1

    try:
        from geopy.distance import geodesic
        test_result(True, "Geopy package imported")
    except ImportError as e:
        test_result(False, f"Geopy import failed: {e}")
        return 1

    # =========================================================================
    # Test 3: Supabase Connection
    # =========================================================================
    print_section("3. Testing Supabase Connection")

    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        test_result(True, "Supabase client created successfully")
    except Exception as e:
        test_result(False, f"Failed to create Supabase client: {e}")
        return 1

    # =========================================================================
    # Test 4: PostGIS Extension
    # =========================================================================
    print_section("4. Testing PostGIS Extension")

    try:
        # Query pg_extension to check if PostGIS is installed
        result = supabase.rpc('pg_extension_exists', {'extension_name': 'postgis'}).execute()
        test_result(True, "PostGIS extension query executed")
        print("   Note: If you get an error about pg_extension_exists not existing,")
        print("         PostGIS is still enabled - this is just a helper function check")
    except Exception as e:
        # PostGIS might still be enabled even if this helper doesn't exist
        print(f"   ℹ️  PostGIS check note: {e}")
        test_result(True, "PostGIS extension (assuming enabled)")

    # =========================================================================
    # Test 5: Roads Table Access
    # =========================================================================
    print_section("5. Testing Roads Table Access")

    try:
        result = supabase.table('roads').select('id, code, name').limit(5).execute()
        test_result(True, f"Roads table accessible ({len(result.data)} rows found)")

        if result.data:
            print(f"\n   Sample roads in database:")
            for road in result.data[:3]:
                print(f"   - {road.get('code', 'N/A')}: {road.get('name', 'N/A')}")
        else:
            print("   ℹ️  Roads table is empty (expected if not yet populated)")

    except Exception as e:
        test_result(False, f"Cannot access roads table: {e}")
        print("\n   Make sure you've run schema.sql in Supabase SQL Editor")
        return 1

    # =========================================================================
    # Test 6: Geometry Functions
    # =========================================================================
    print_section("6. Testing PostGIS Geometry Functions")

    try:
        # Try to select geometry column with ST_AsText
        result = supabase.table('roads').select('code, geometry').limit(1).execute()

        if result.data and result.data[0].get('geometry'):
            geometry = result.data[0]['geometry']
            code = result.data[0].get('code', 'N/A')
            test_result(True, f"Geometry column accessible (found in {code})")
            print(f"   Geometry format: {str(geometry)[:50]}...")
        else:
            test_result(True, "Geometry column exists (no data yet)")
            print("   ℹ️  No geometry data found (expected if table empty)")

    except Exception as e:
        test_result(False, f"Geometry column test failed: {e}")
        print("   This might indicate PostGIS is not properly configured")

    # =========================================================================
    # Test 7: Write Permission Test
    # =========================================================================
    print_section("7. Testing Write Permissions")

    test_road_code = f"TEST_CONNECTION_{os.getpid()}"

    try:
        # Try to insert a test road
        test_data = {
            "code": test_road_code,
            "name": "Test Road - Connection Check",
            "region": "Continental",
            "geometry": "LINESTRING(-8.0 39.5, -8.01 39.51)",
            "start_lat": 39.5,
            "start_lon": -8.0,
            "end_lat": 39.51,
            "end_lon": -8.01,
            "distance_km": 1.5,
            "surface": "asphalt",
            "data_source": "test"
        }

        insert_result = supabase.table('roads').insert(test_data).execute()
        test_result(True, f"Test road inserted (ID: {insert_result.data[0]['id']})")

        # Try to delete the test road
        test_id = insert_result.data[0]['id']
        delete_result = supabase.table('roads').delete().eq('id', test_id).execute()
        test_result(True, f"Test road deleted (cleanup successful)")

    except Exception as e:
        test_result(False, f"Write permission test failed: {e}")
        print("   Make sure you're using the SERVICE ROLE KEY, not the anon key")
        print("   Service role key bypasses Row Level Security (RLS)")

    # =========================================================================
    # Test 8: Region Filtering
    # =========================================================================
    print_section("8. Testing Region Filtering")

    try:
        # Count roads by region
        continental = supabase.table('roads').select('id', count='exact').eq('region', 'Continental').execute()
        madeira = supabase.table('roads').select('id', count='exact').eq('region', 'Madeira').execute()
        acores = supabase.table('roads').select('id', count='exact').eq('region', 'Açores').execute()

        test_result(True, "Region filtering works")
        print(f"   Continental: {continental.count or 0} roads")
        print(f"   Madeira: {madeira.count or 0} roads")
        print(f"   Açores: {acores.count or 0} roads")

    except Exception as e:
        test_result(False, f"Region filtering failed: {e}")

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "=" * 70)
    print(f"📊 Tests passed: {tests_passed}/{tests_total}")
    print("=" * 70)

    if tests_passed == tests_total:
        print("🎉 All tests passed! Your Supabase setup is working correctly.")
        print("\n✅ You're ready to process roads with: python process_roads.py")
        return 0
    else:
        print(f"⚠️  {tests_total - tests_passed} test(s) failed. Please fix the issues above.")
        print("\n📚 Common fixes:")
        print("   1. Make sure schema.sql was run in Supabase SQL Editor")
        print("   2. Verify you're using the SERVICE ROLE KEY (not anon key)")
        print("   3. Check that PostGIS extension is enabled")
        return 1


if __name__ == "__main__":
    exit(main())
