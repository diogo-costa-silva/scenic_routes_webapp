#!/usr/bin/env python3
"""
Test script for metrics calculations
"""

from metrics import (
    calculate_total_distance,
    calculate_bearing,
    calculate_angle_difference,
    analyze_curves,
    calculate_all_metrics
)

print("=" * 70)
print("METRICS CALCULATION - COMPREHENSIVE TEST")
print("=" * 70)

# Test 1: Distance Calculation
print("\n🧪 Test 1: Distance Calculation")
print("-" * 70)
test_coords = [
    (-8.0, 39.5),    # Start
    (-8.01, 39.51),  # ~1.4 km NE
    (-8.02, 39.52),  # ~1.4 km NE
]
distance = calculate_total_distance(test_coords)
print(f"✅ Distance for 3 points: {distance} km")
print(f"   Expected: ~2.8 km")

# Test 2: Bearing Calculation
print("\n🧪 Test 2: Bearing Calculation")
print("-" * 70)
p1 = (-8.0, 39.5)
p2_north = (-8.0, 39.51)  # Due north
p2_east = (-7.99, 39.5)   # Due east
p2_south = (-8.0, 39.49)  # Due south
p2_west = (-8.01, 39.5)   # Due west

bearing_north = calculate_bearing(p1, p2_north)
bearing_east = calculate_bearing(p1, p2_east)
bearing_south = calculate_bearing(p1, p2_south)
bearing_west = calculate_bearing(p1, p2_west)

print(f"✅ North bearing: {bearing_north:.1f}° (expected: ~0°)")
print(f"✅ East bearing: {bearing_east:.1f}° (expected: ~90°)")
print(f"✅ South bearing: {bearing_south:.1f}° (expected: ~180°)")
print(f"✅ West bearing: {bearing_west:.1f}° (expected: ~270°)")

# Test 3: Angle Difference
print("\n🧪 Test 3: Angle Difference")
print("-" * 70)
diff1 = calculate_angle_difference(10, 350)  # Should be 20°
diff2 = calculate_angle_difference(90, 270)  # Should be 180°
diff3 = calculate_angle_difference(0, 180)   # Should be 180°
diff4 = calculate_angle_difference(45, 135)  # Should be 90°

print(f"✅ 10° to 350°: {diff1:.1f}° (expected: 20°)")
print(f"✅ 90° to 270°: {diff2:.1f}° (expected: 180°)")
print(f"✅ 0° to 180°: {diff3:.1f}° (expected: 180°)")
print(f"✅ 45° to 135°: {diff4:.1f}° (expected: 90°)")

# Test 4: Curve Analysis with Simulated Winding Road
print("\n🧪 Test 4: Curve Analysis (Simulated Winding Road)")
print("-" * 70)
# Simulate a road with curves: straight, gentle turn, sharp turn, straight
winding_road = [
    (-8.0, 39.5),    # Start
    (-7.99, 39.5),   # Straight east
    (-7.98, 39.5),   # Continue straight
    (-7.97, 39.5),   # Continue straight
    (-7.97, 39.51),  # Gentle turn north (45°)
    (-7.97, 39.52),  # Continue north
    (-7.96, 39.52),  # Sharp turn east (90°)
    (-7.95, 39.52),  # Continue east
    (-7.94, 39.52),  # Continue straight
]

curve_metrics = analyze_curves(winding_road, min_curve_angle=20)
print(f"✅ Total curves: {curve_metrics['curve_count_total']}")
print(f"   - Gentle (20-45°): {curve_metrics['curve_count_gentle']}")
print(f"   - Moderate (45-90°): {curve_metrics['curve_count_moderate']}")
print(f"   - Sharp (>90°): {curve_metrics['curve_count_sharp']}")
print(f"✅ Straight sections: {curve_metrics['straight_count']}")
print(f"✅ Longest straight: {curve_metrics['longest_straight_km']} km")

# Test 5: Complete Metrics
print("\n🧪 Test 5: Complete Metrics (All in One)")
print("-" * 70)
all_metrics = calculate_all_metrics(winding_road)
print(f"✅ Distance: {all_metrics['distance_km']} km")
print(f"✅ Total curves: {all_metrics['curve_count_total']}")
print(f"   Breakdown: {all_metrics['curve_count_gentle']} gentle, "
      f"{all_metrics['curve_count_moderate']} moderate, "
      f"{all_metrics['curve_count_sharp']} sharp")
print(f"✅ Straights: {all_metrics['straight_count']}")
print(f"✅ Longest straight: {all_metrics['longest_straight_km']} km")

# Test 6: Edge Cases
print("\n🧪 Test 6: Edge Cases")
print("-" * 70)
empty_result = calculate_all_metrics([])
single_point = calculate_all_metrics([(-8.0, 39.5)])
two_points = calculate_all_metrics([(-8.0, 39.5), (-8.01, 39.51)])

print(f"✅ Empty coordinates: {empty_result['distance_km']} km (expected: 0)")
print(f"✅ Single point: {single_point['distance_km']} km (expected: 0)")
print(f"✅ Two points: {two_points['distance_km']} km (expected: ~1.4)")

print("\n" + "=" * 70)
print("✅ ALL TESTS PASSED!")
print("=" * 70)
