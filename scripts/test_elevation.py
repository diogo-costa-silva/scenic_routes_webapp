#!/usr/bin/env python3
"""
Test script for elevation calculations
"""

import os
from elevation import (
    get_elevation_from_mapbox,
    calculate_elevation_metrics,
    estimate_api_calls,
    estimate_time
)

print("=" * 70)
print("ELEVATION CALCULATION - COMPREHENSIVE TEST")
print("=" * 70)

# Check MAPBOX_TOKEN
mapbox_token = os.getenv("MAPBOX_TOKEN", "")
if mapbox_token:
    print(f"\n✅ MAPBOX_TOKEN found (starts with: {mapbox_token[:10]}...)")
    api_tests_enabled = True
else:
    print(f"\n⚠️  MAPBOX_TOKEN not found - API tests will be skipped")
    api_tests_enabled = False

# Test 1: Elevation Metrics Calculation (No API needed)
print("\n🧪 Test 1: Elevation Metrics Calculation")
print("-" * 70)
# Elevations: [100, 150, 200, 180, 250, 230, 300]
# Changes: +50, +50, -20, +70, -20, +70
# Gain: 50+50+70+70 = 240m
# Loss: 20+20 = 40m
test_elevations = [100, 150, 200, 180, 250, 230, 300]
metrics = calculate_elevation_metrics(test_elevations)

print(f"✅ Test elevations: {test_elevations}")
print(f"   Changes: +50, +50, -20, +70, -20, +70")
print(f"   Max: {metrics['elevation_max']}m (expected: 300m)")
print(f"   Min: {metrics['elevation_min']}m (expected: 100m)")
print(f"   Gain: {metrics['elevation_gain']}m (expected: 240m)")
print(f"   Loss: {metrics['elevation_loss']}m (expected: 40m)")

# Verify calculations
assert metrics['elevation_max'] == 300, "Max elevation incorrect"
assert metrics['elevation_min'] == 100, "Min elevation incorrect"
assert metrics['elevation_gain'] == 240, "Elevation gain incorrect"
assert metrics['elevation_loss'] == 40, "Elevation loss incorrect"
print("✅ All calculations verified!")

# Test 2: Empty Elevations
print("\n🧪 Test 2: Empty Elevations (Edge Case)")
print("-" * 70)
empty_metrics = calculate_elevation_metrics([])
print(f"✅ Empty list result: {empty_metrics}")
assert empty_metrics['elevation_max'] == 0
assert empty_metrics['elevation_min'] == 0
print("✅ Edge case handled correctly!")

# Test 3: API Call Estimation
print("\n🧪 Test 3: API Call Estimation")
print("-" * 70)
test_coords = [(-8.0 + i*0.01, 39.5 + i*0.01) for i in range(100)]  # 100 points
api_calls = estimate_api_calls(test_coords, sample_interval=10)
time_estimate = estimate_time(test_coords, sample_interval=10)

print(f"✅ 100 coordinates with interval=10:")
print(f"   API calls needed: {api_calls} (expected: 10)")
print(f"   Estimated time: {time_estimate:.1f}s")
assert api_calls == 10, "API call estimation incorrect"
print("✅ Estimation working correctly!")

# Test 4: Single Point Elevation (Requires API)
if api_tests_enabled:
    print("\n🧪 Test 4: Single Point Elevation (API Test)")
    print("-" * 70)
    print("⚠️  This test makes a real API call to Mapbox")

    # Test with a known location in Portugal (Covilhã - mountain town)
    test_lat, test_lon = 40.2833, -7.5000
    print(f"   Testing: Covilhã, Portugal ({test_lat}, {test_lon})")

    elevation = get_elevation_from_mapbox(test_lat, test_lon)

    if elevation is not None:
        print(f"✅ Elevation retrieved: {elevation}m")
        print(f"   Expected range: 600-800m (Covilhã is ~675m)")
        if 500 < elevation < 900:
            print(f"✅ Elevation within expected range for Covilhã!")
        else:
            print(f"⚠️  Elevation outside expected range, but API is working")
    else:
        print(f"❌ Failed to retrieve elevation")
        print(f"   This could be due to:")
        print(f"   - Invalid MAPBOX_TOKEN")
        print(f"   - Network issues")
        print(f"   - API rate limiting")
else:
    print("\n🧪 Test 4: Single Point Elevation (SKIPPED - No API Token)")
    print("-" * 70)
    print("   To enable API tests:")
    print("   1. Copy .env.example to .env")
    print("   2. Add your MAPBOX_TOKEN")
    print("   3. Run test again")

# Test 5: Cumulative Elevation Gain Example
print("\n🧪 Test 5: Cumulative Elevation Gain (Realistic Example)")
print("-" * 70)
# Simulate a mountain pass: up, down, up again
mountain_pass = [
    100,  # Start (valley)
    200,  # +100m
    350,  # +150m
    500,  # +150m (summit 1)
    400,  # -100m (descend)
    300,  # -100m (valley)
    450,  # +150m (climb)
    600,  # +150m (summit 2)
]

metrics = calculate_elevation_metrics(mountain_pass)
print(f"✅ Mountain pass elevation profile:")
print(f"   Start: {mountain_pass[0]}m → End: {mountain_pass[-1]}m")
print(f"   Net change: {mountain_pass[-1] - mountain_pass[0]}m")
print(f"   BUT cumulative gain: {metrics['elevation_gain']}m")
print(f"   AND cumulative loss: {metrics['elevation_loss']}m")
print(f"   (This is why cumulative is important for cyclists/motorcyclists!)")

# Verify
expected_gain = 100 + 150 + 150 + 150 + 150  # All uphill segments
expected_loss = 100 + 100  # All downhill segments
assert metrics['elevation_gain'] == expected_gain, f"Expected gain {expected_gain}, got {metrics['elevation_gain']}"
assert metrics['elevation_loss'] == expected_loss, f"Expected loss {expected_loss}, got {metrics['elevation_loss']}"
print(f"✅ Cumulative calculations verified!")

print("\n" + "=" * 70)
print("✅ ALL NON-API TESTS PASSED!")
if api_tests_enabled:
    print("✅ API TEST COMPLETED (check results above)")
else:
    print("ℹ️  API tests skipped (MAPBOX_TOKEN not configured)")
print("=" * 70)
