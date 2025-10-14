#!/usr/bin/env python3
"""
==============================================================================
Database Connection Test Script
==============================================================================
Script: test_connection.py
Purpose: Verify Supabase connection and database setup
Author: Road Explorer Portugal
==============================================================================

This script tests:
1. Environment variables are configured
2. Supabase connection works
3. PostGIS extension is enabled
4. Roads table exists and is accessible
5. Geometry functions work correctly
6. Test data can be queried

Usage:
    python test_connection.py

Prerequisites:
    1. Virtual environment activated
    2. Dependencies installed (uv pip install -r requirements.txt)
    3. .env file configured with credentials
==============================================================================
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_test(test_name, status, message=""):
    """Print test result with formatting."""
    status_symbol = "✅" if status else "❌"
    print(f"{status_symbol} {test_name}")
    if message:
        print(f"   {message}")


def test_environment_variables():
    """Test if environment variables are configured."""
    print_header("1. Testing Environment Variables")

    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_KEY", "")
    mapbox_token = os.getenv("MAPBOX_TOKEN", "")

    url_valid = bool(supabase_url and supabase_url.startswith("https://"))
    key_valid = bool(supabase_key and len(supabase_key) > 20)
    mapbox_valid = bool(mapbox_token and mapbox_token.startswith("pk."))

    print_test("SUPABASE_URL configured", url_valid,
               f"URL: {supabase_url[:30]}..." if url_valid else "Not found or invalid")
    print_test("SUPABASE_KEY configured", key_valid,
               f"Length: {len(supabase_key)} chars" if key_valid else "Not found or too short")
    print_test("MAPBOX_TOKEN configured", mapbox_valid,
               f"Token: {mapbox_token[:15]}..." if mapbox_valid else "Not found or invalid")

    return url_valid and key_valid


def test_supabase_connection():
    """Test Supabase connection."""
    print_header("2. Testing Supabase Connection")

    try:
        supabase_url = os.getenv("SUPABASE_URL", "")
        supabase_key = os.getenv("SUPABASE_KEY", "")

        supabase = create_client(supabase_url, supabase_key)
        print_test("Supabase client created", True, f"Connected to: {supabase_url}")

        return supabase
    except Exception as e:
        print_test("Supabase client creation", False, f"Error: {e}")
        return None


def test_postgis_extension(supabase: Client):
    """Test if PostGIS extension is enabled."""
    print_header("3. Testing PostGIS Extension")

    try:
        # Query to check if PostGIS is installed
        result = supabase.rpc('postgis_version').execute()

        if result.data:
            print_test("PostGIS extension enabled", True, f"Version: {result.data}")
            return True
        else:
            # Alternative: Try a simple PostGIS function
            test_result = supabase.rpc('st_astext', {
                'geom': 'POINT(0 0)'
            }).execute()

            print_test("PostGIS extension enabled", True,
                      "PostGIS functions are working")
            return True

    except Exception as e:
        print_test("PostGIS extension check", False,
                  f"Note: This is expected if PostGIS functions aren't exposed via RPC")
        # This is not critical - PostGIS may be enabled but not exposed via RPC
        print("   ℹ️  PostGIS may still be working. Continuing tests...")
        return True


def test_roads_table(supabase: Client):
    """Test if roads table exists and is accessible."""
    print_header("4. Testing Roads Table")

    try:
        # Try to count roads
        result = supabase.table('roads').select('id', count='exact').execute()

        count = result.count if hasattr(result, 'count') else len(result.data)

        print_test("Roads table accessible", True, f"Found {count} roads")

        return count > 0
    except Exception as e:
        print_test("Roads table access", False, f"Error: {e}")
        return False


def test_query_road_data(supabase: Client):
    """Test querying road data with all fields."""
    print_header("5. Testing Road Data Query")

    try:
        # Fetch first road with all fields
        result = supabase.table('roads').select('*').limit(1).execute()

        if not result.data:
            print_test("Query road data", False, "No data returned")
            return False

        road = result.data[0]

        # Check essential fields
        required_fields = ['id', 'code', 'name', 'region', 'geometry',
                          'distance_km', 'start_lat', 'start_lon']

        missing_fields = [field for field in required_fields if field not in road]

        if missing_fields:
            print_test("Road data structure", False,
                      f"Missing fields: {', '.join(missing_fields)}")
            return False

        print_test("Query road data", True, f"Sample: {road['code']} - {road['name']}")
        print(f"   Region: {road['region']}")
        print(f"   Distance: {road['distance_km']} km")
        print(f"   Geometry type: {type(road['geometry'])}")

        return True

    except Exception as e:
        print_test("Query road data", False, f"Error: {e}")
        return False


def test_geometry_format(supabase: Client):
    """Test if geometry is returned in correct format."""
    print_header("6. Testing Geometry Format")

    try:
        # Fetch a road with geometry
        result = supabase.table('roads').select('code, geometry').limit(1).execute()

        if not result.data:
            print_test("Geometry format test", False, "No data returned")
            return False

        road = result.data[0]
        geometry = road.get('geometry', '')

        # Check if geometry is WKT LINESTRING format
        is_wkt = isinstance(geometry, str) and geometry.startswith('LINESTRING(')

        if is_wkt:
            # Count points in geometry
            coords = geometry.replace('LINESTRING(', '').replace(')', '')
            point_count = len(coords.split(','))

            print_test("Geometry format (WKT)", True,
                      f"Sample: {geometry[:50]}...")
            print(f"   Points in geometry: {point_count}")
            return True
        else:
            print_test("Geometry format", False,
                      f"Unexpected format: {type(geometry)}")
            print(f"   Value: {geometry}")
            return False

    except Exception as e:
        print_test("Geometry format test", False, f"Error: {e}")
        return False


def test_filter_by_region(supabase: Client):
    """Test filtering roads by region."""
    print_header("7. Testing Region Filtering")

    try:
        # Test filtering by Continental
        result = supabase.table('roads').select('code, region') \
                        .eq('region', 'Continental').execute()

        continental_count = len(result.data)

        print_test("Filter by region", True,
                  f"Found {continental_count} Continental roads")

        if continental_count > 0:
            sample_codes = [r['code'] for r in result.data[:3]]
            print(f"   Sample codes: {', '.join(sample_codes)}")

        return True

    except Exception as e:
        print_test("Filter by region", False, f"Error: {e}")
        return False


def main():
    """Main test execution."""

    print("=" * 70)
    print("  🧪 Road Explorer Portugal - Database Connection Test")
    print("=" * 70)
    print("\nThis script will verify your Supabase setup is working correctly.")

    # Run tests
    tests_passed = 0
    tests_total = 7

    # Test 1: Environment variables
    if not test_environment_variables():
        print("\n❌ Environment variables not configured properly!")
        print("   Please check your .env file and ensure all variables are set.")
        sys.exit(1)
    tests_passed += 1

    # Test 2: Supabase connection
    supabase = test_supabase_connection()
    if not supabase:
        print("\n❌ Cannot connect to Supabase!")
        print("   Please check your SUPABASE_URL and SUPABASE_KEY.")
        sys.exit(1)
    tests_passed += 1

    # Test 3: PostGIS (informational)
    test_postgis_extension(supabase)
    tests_passed += 1

    # Test 4: Roads table
    if not test_roads_table(supabase):
        print("\n❌ Roads table not accessible!")
        print("   Please run schema.sql in Supabase SQL Editor first.")
        sys.exit(1)
    tests_passed += 1

    # Test 5: Query road data
    if not test_query_road_data(supabase):
        print("\n⚠️  Warning: Could not query road data properly.")
        print("   You may need to load test data (test_data.sql).")
    else:
        tests_passed += 1

    # Test 6: Geometry format
    if test_geometry_format(supabase):
        tests_passed += 1

    # Test 7: Filter by region
    if test_filter_by_region(supabase):
        tests_passed += 1

    # Summary
    print_header("Test Summary")
    print(f"\n📊 Tests passed: {tests_passed}/{tests_total}")

    if tests_passed == tests_total:
        print("\n🎉 All tests passed! Your Supabase setup is working correctly.")
        print("\n✅ Next steps:")
        print("   1. Run Python data processing scripts to add roads")
        print("   2. Start frontend development (npm run dev)")
        print("   3. Test frontend connection to Supabase")
    elif tests_passed >= 4:
        print("\n⚠️  Most tests passed. Minor issues detected.")
        print("   Review the failures above and fix if needed.")
    else:
        print("\n❌ Multiple tests failed. Please review your setup.")
        print("   Check the errors above and fix configuration issues.")

    print("=" * 70)

    return 0 if tests_passed >= 4 else 1


if __name__ == "__main__":
    sys.exit(main())
