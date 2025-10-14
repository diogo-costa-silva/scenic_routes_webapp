#!/usr/bin/env python3
"""
==============================================================================
Road Metrics Calculation Functions
==============================================================================
Module: metrics.py
Purpose: Calculate distance, curves, straights, and other road metrics
Author: Road Explorer Portugal
==============================================================================
"""

from geopy.distance import geodesic
import math
from typing import List, Tuple, Dict, Optional


# ==============================================================================
# Distance Calculations
# ==============================================================================

def calculate_total_distance(coordinates: List[Tuple[float, float]]) -> float:
    """
    Calculate total distance following GPS coordinates using geodesic formula.

    This function accounts for Earth's curvature by using the geodesic distance
    calculation (ellipsoidal distance), which is more accurate than simple
    haversine for distances over a few kilometers.

    Args:
        coordinates (list): List of (lon, lat) tuples

    Returns:
        float: Distance in kilometers, rounded to 2 decimal places

    Example:
        >>> coords = [(-8.0, 39.5), (-8.01, 39.51)]
        >>> distance = calculate_total_distance(coords)
        >>> print(f"{distance} km")
        1.56 km

    Note:
        - Requires at least 2 coordinates
        - Returns 0.0 for invalid input
        - Coordinates format: (longitude, latitude)
    """

    if not coordinates or len(coordinates) < 2:
        return 0.0

    total_distance = 0.0

    # Sum distances between consecutive GPS points
    for i in range(len(coordinates) - 1):
        # Convert (lon, lat) to (lat, lon) for geopy
        point1 = (coordinates[i][1], coordinates[i][0])
        point2 = (coordinates[i+1][1], coordinates[i+1][0])

        # Calculate geodesic distance
        distance = geodesic(point1, point2).kilometers
        total_distance += distance

    return round(total_distance, 2)


# ==============================================================================
# Bearing and Direction Calculations
# ==============================================================================

def calculate_bearing(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """
    Calculate the bearing (forward azimuth) between two GPS points.

    Uses the forward azimuth formula to calculate the direction from point1
    to point2. The bearing represents the compass direction needed to travel
    from the first point to the second point.

    Args:
        point1 (Tuple[float, float]): First point (lon, lat)
        point2 (Tuple[float, float]): Second point (lon, lat)

    Returns:
        float: Bearing in degrees (0-360), where:
               - 0° = North
               - 90° = East
               - 180° = South
               - 270° = West

    Example:
        >>> p1 = (-8.0, 39.5)  # Starting point
        >>> p2 = (-7.9, 39.5)  # Point to the east
        >>> bearing = calculate_bearing(p1, p2)
        >>> print(f"{bearing}°")
        90.0°

    Note:
        - Uses spherical geometry (not flat Earth)
        - Accurate for distances up to several hundred kilometers
    """

    # Extract coordinates and convert to radians
    lon1, lat1 = math.radians(point1[0]), math.radians(point1[1])
    lon2, lat2 = math.radians(point2[0]), math.radians(point2[1])

    # Calculate difference in longitude
    dlon = lon2 - lon1

    # Forward azimuth formula
    x = math.sin(dlon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)

    initial_bearing = math.atan2(x, y)

    # Convert from radians to degrees
    initial_bearing = math.degrees(initial_bearing)

    # Normalize to 0-360 range
    bearing = (initial_bearing + 360) % 360

    return bearing


def calculate_angle_difference(bearing1: float, bearing2: float) -> float:
    """
    Calculate the smallest angle difference between two bearings.

    Handles the circular nature of bearings (e.g., the difference between
    359° and 1° is 2°, not 358°). Always returns the acute or right angle.

    Args:
        bearing1 (float): First bearing (degrees, 0-360)
        bearing2 (float): Second bearing (degrees, 0-360)

    Returns:
        float: Smallest angle difference (0-180 degrees)

    Example:
        >>> angle_diff = calculate_angle_difference(10, 350)
        >>> print(angle_diff)
        20.0

        >>> angle_diff = calculate_angle_difference(90, 270)
        >>> print(angle_diff)
        180.0

    Note:
        - Result is always positive
        - Result is always ≤ 180°
        - Handles wraparound at 0°/360°
    """

    # Calculate absolute difference
    diff = abs(bearing2 - bearing1)

    # If difference is > 180°, take the complementary angle
    # (the shorter way around the circle)
    if diff > 180:
        diff = 360 - diff

    return diff


# ==============================================================================
# Curve Analysis
# ==============================================================================

def analyze_curves(
    coordinates: List[Tuple[float, float]],
    min_curve_angle: float = 20.0
) -> Dict:
    """
    Analyze curves in a road by detecting direction changes.

    ALGORITHM EXPLANATION:
    =====================
    1. Calculate bearings between consecutive coordinate points
    2. Compare consecutive bearings to detect direction changes
    3. When angle change ≥ min_curve_angle, classify as curve:
       - Gentle: 20° ≤ angle < 45°
       - Moderate: 45° ≤ angle < 90°
       - Sharp: angle ≥ 90°
    4. Track straight sections (angle change < min_curve_angle)
    5. Calculate distance of each straight section
    6. Identify longest straight section

    Args:
        coordinates (List[Tuple[float, float]]): List of (lon, lat) tuples
        min_curve_angle (float): Minimum angle to consider a curve (default: 20°)

    Returns:
        Dict: Dictionary with curve statistics:
            - curve_count_total: Total number of curves
            - curve_count_gentle: Gentle curves (20-45°)
            - curve_count_moderate: Moderate curves (45-90°)
            - curve_count_sharp: Sharp curves (>90°)
            - straight_count: Number of straight sections
            - longest_straight_km: Length of longest straight (km)

    Example:
        >>> coords = [(-8.0, 39.5), (-8.01, 39.51), (-8.02, 39.50)]
        >>> metrics = analyze_curves(coords)
        >>> print(f"Total curves: {metrics['curve_count_total']}")
        Total curves: 1

    Note:
        - Requires at least 3 coordinates
        - Curve detection is based on bearing changes
        - Straight sections include gentle bends < min_curve_angle
    """

    # Validate input
    if not coordinates or len(coordinates) < 3:
        return {
            'curve_count_total': 0,
            'curve_count_gentle': 0,
            'curve_count_moderate': 0,
            'curve_count_sharp': 0,
            'straight_count': 0,
            'longest_straight_km': 0.0
        }

    # Initialize counters
    curves_gentle = 0    # 20-45°
    curves_moderate = 0  # 45-90°
    curves_sharp = 0     # >90°

    # Track straight sections
    straights = []
    current_straight_coords = [coordinates[0]]

    # Step 1: Calculate bearings between consecutive points
    bearings = []
    for i in range(len(coordinates) - 1):
        bearing = calculate_bearing(coordinates[i], coordinates[i+1])
        bearings.append(bearing)

    # Step 2: Analyze bearing changes to detect curves
    for i in range(len(bearings) - 1):
        # Calculate angle change between consecutive bearings
        angle_change = calculate_angle_difference(bearings[i], bearings[i+1])

        if angle_change >= min_curve_angle:
            # It's a curve - classify by severity
            if angle_change < 45:
                curves_gentle += 1
            elif angle_change < 90:
                curves_moderate += 1
            else:
                curves_sharp += 1

            # End current straight section
            if len(current_straight_coords) > 1:
                # Calculate distance of this straight section
                straight_distance = calculate_total_distance(current_straight_coords)
                if straight_distance > 0:
                    straights.append(straight_distance)

            # Start new straight section from next point
            current_straight_coords = [coordinates[i+1]]

        else:
            # It's part of a straight section
            current_straight_coords.append(coordinates[i+1])

    # Don't forget the last straight section
    if len(current_straight_coords) > 1:
        straight_distance = calculate_total_distance(current_straight_coords)
        if straight_distance > 0:
            straights.append(straight_distance)

    # Calculate summary statistics
    total_curves = curves_gentle + curves_moderate + curves_sharp
    longest_straight = round(max(straights), 2) if straights else 0.0

    return {
        'curve_count_total': total_curves,
        'curve_count_gentle': curves_gentle,
        'curve_count_moderate': curves_moderate,
        'curve_count_sharp': curves_sharp,
        'straight_count': len(straights),
        'longest_straight_km': longest_straight
    }


# ==============================================================================
# Straight Section Analysis
# ==============================================================================

def find_straight_sections(
    coordinates: List[Tuple[float, float]],
    max_angle_deviation: float = 5.0
) -> List[Dict]:
    """
    Find straight sections of road.

    Args:
        coordinates (List[Tuple[float, float]]): List of (lon, lat) tuples
        max_angle_deviation (float): Maximum bearing change for straight

    Returns:
        List[Dict]: List of straight sections with start/end indices and length
    """

    # Placeholder implementation
    print(f"🚧 [PLACEHOLDER] Would find straight sections")

    # TODO: Detect sections with minimal bearing change
    # Calculate length of each straight
    # Return list of straight sections

    return []


# ==============================================================================
# Complete Metrics Calculation
# ==============================================================================

def calculate_all_metrics(coordinates: List[Tuple[float, float]]) -> Dict:
    """
    Calculate all road metrics in one pass.

    Convenience function that combines distance and curve calculations
    into a single function call. This is the recommended way to get
    all metrics at once.

    Args:
        coordinates (List[Tuple[float, float]]): List of (lon, lat) tuples

    Returns:
        Dict: Complete metrics dictionary with all calculated values

    Example:
        >>> coords = get_road_coordinates("N222")
        >>> metrics = calculate_all_metrics(coords)
        >>> print(f"Distance: {metrics['distance_km']} km")
        Distance: 27.3 km
        >>> print(f"Curves: {metrics['curve_count_total']}")
        Curves: 147
    """

    if not coordinates or len(coordinates) < 2:
        return {
            'distance_km': 0.0,
            'curve_count_total': 0,
            'curve_count_gentle': 0,
            'curve_count_moderate': 0,
            'curve_count_sharp': 0,
            'straight_count': 0,
            'longest_straight_km': 0.0
        }

    # Calculate distance
    distance_km = calculate_total_distance(coordinates)

    # Calculate curves (includes straights)
    curve_metrics = analyze_curves(coordinates)

    # Combine all metrics
    return {
        'distance_km': distance_km,
        **curve_metrics
    }


# ==============================================================================
# Module Testing
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Metrics Calculator - Placeholder Test")
    print("=" * 70)

    # Test with sample coordinates
    test_coords = [
        (-8.0, 39.5),
        (-8.01, 39.51),
        (-8.02, 39.52),
    ]

    print(f"\nTesting with {len(test_coords)} sample points...")

    distance = calculate_total_distance(test_coords)
    print(f"Distance: {distance} km")

    curves = analyze_curves(test_coords)
    print(f"Curves: {curves}")

    print("\n✅ Module loaded successfully (placeholder mode)")
    print("ℹ️  Actual implementation coming soon!")
