"""
Geographic Validation Module for Road Explorer Portugal

Validates coordinates and road data before inserting into the database.
Prevents common data entry errors like inverted lat/lon coordinates.
"""


# Portugal geographic bounds (includes all territories)
PORTUGAL_BOUNDS = {
    'lat': (32, 43),   # Latitude: 32-43°N (Continental + Islands)
    'lon': (-32, -6)   # Longitude: -32 to -6°W (Açores to Mainland)
}


def validate_portugal_coordinates(lat, lon, location_name="Unknown"):
    """
    Validate if coordinates are within Portugal's geographic bounds.

    Args:
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)
        location_name (str): Name of location for error messages

    Returns:
        tuple: (is_valid: bool, error_message: str or None)

    Examples:
        >>> validate_portugal_coordinates(41.74, -7.47, "Chaves")
        (True, None)

        >>> validate_portugal_coordinates(-7.47, 41.74, "Chaves")
        (False, "Chaves: Coordinates (-7.47, 41.74) are outside Portugal...")

        >>> validate_portugal_coordinates(48.85, 2.35, "Paris")
        (False, "Paris: Coordinates (48.85, 2.35) are outside Portugal...")
    """
    # Check if values are numbers
    if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
        return (False, f"{location_name}: Coordinates must be numbers (got lat={type(lat)}, lon={type(lon)})")

    # Check latitude range (general)
    if lat < -90 or lat > 90:
        return (False, f"{location_name}: Latitude {lat} is invalid (must be between -90 and 90)")

    # Check longitude range (general)
    if lon < -180 or lon > 180:
        return (False, f"{location_name}: Longitude {lon} is invalid (must be between -180 and 180)")

    # Check Portugal bounds
    lat_min, lat_max = PORTUGAL_BOUNDS['lat']
    lon_min, lon_max = PORTUGAL_BOUNDS['lon']

    if not (lat_min <= lat <= lat_max):
        return (
            False,
            f"{location_name}: Latitude {lat} is outside Portugal bounds "
            f"({lat_min}° to {lat_max}°N). "
            f"Are lat/lon swapped?"
        )

    if not (lon_min <= lon <= lon_max):
        return (
            False,
            f"{location_name}: Longitude {lon} is outside Portugal bounds "
            f"({lon_min}° to {lon_max}°W). "
            f"Are lat/lon swapped?"
        )

    return (True, None)


def validate_road_coordinates(road_info):
    """
    Validate all coordinates for a road before processing.

    Args:
        road_info (dict): Dictionary with road information:
            - code: Road code (e.g., "N222")
            - start_point_name: Name of start point
            - end_point_name: Name of end point
            - coordinates: List of (lon, lat) tuples (from OSM)

    Returns:
        tuple: (is_valid: bool, errors: list of str)

    Example:
        >>> road = {
        ...     'code': 'N222',
        ...     'coordinates': [(-7.7880, 41.1640), (-7.7850, 41.1650)]
        ... }
        >>> validate_road_coordinates(road)
        (True, [])
    """
    errors = []
    code = road_info.get('code', 'Unknown')

    # Validate start point (if coordinates provided)
    coordinates = road_info.get('coordinates', [])
    if coordinates and len(coordinates) > 0:
        start_lon, start_lat = coordinates[0]
        start_name = road_info.get('start_point_name', 'Start point')

        is_valid, error_msg = validate_portugal_coordinates(
            start_lat, start_lon,
            f"{code} - {start_name}"
        )
        if not is_valid:
            errors.append(error_msg)

    # Validate end point (if coordinates provided)
    if coordinates and len(coordinates) > 1:
        end_lon, end_lat = coordinates[-1]
        end_name = road_info.get('end_point_name', 'End point')

        is_valid, error_msg = validate_portugal_coordinates(
            end_lat, end_lon,
            f"{code} - {end_name}"
        )
        if not is_valid:
            errors.append(error_msg)

    # Validate a few intermediate points (sample every 10th point)
    if coordinates and len(coordinates) > 2:
        sample_interval = max(1, len(coordinates) // 10)
        for i in range(1, len(coordinates) - 1, sample_interval):
            lon, lat = coordinates[i]
            is_valid, error_msg = validate_portugal_coordinates(
                lat, lon,
                f"{code} - Point {i}"
            )
            if not is_valid:
                errors.append(error_msg)
                # Don't spam too many errors
                if len(errors) >= 5:
                    errors.append(f"{code}: Too many coordinate errors, stopping validation...")
                    break

    return (len(errors) == 0, errors)


def validate_wkt_geometry(wkt_string):
    """
    Basic validation of WKT LINESTRING format.

    Args:
        wkt_string (str): WKT geometry string

    Returns:
        tuple: (is_valid: bool, error_message: str or None)

    Example:
        >>> validate_wkt_geometry("LINESTRING(-7.7880 41.1640, -7.7850 41.1650)")
        (True, None)
    """
    if not isinstance(wkt_string, str):
        return (False, "WKT must be a string")

    if not wkt_string.startswith('LINESTRING('):
        return (False, "WKT must start with 'LINESTRING('")

    if not wkt_string.endswith(')'):
        return (False, "WKT must end with ')'")

    # Extract coordinates part
    coords_part = wkt_string.replace('LINESTRING(', '').replace(')', '')
    coord_pairs = coords_part.split(',')

    if len(coord_pairs) < 2:
        return (False, "LINESTRING must have at least 2 coordinate pairs")

    # Validate each coordinate pair
    for i, pair in enumerate(coord_pairs):
        parts = pair.strip().split()
        if len(parts) != 2:
            return (False, f"Coordinate pair {i} is invalid: '{pair}' (expected 'lon lat')")

        try:
            lon = float(parts[0])
            lat = float(parts[1])

            # Basic range check
            if lat < -90 or lat > 90:
                return (False, f"Latitude {lat} in pair {i} is out of range")
            if lon < -180 or lon > 180:
                return (False, f"Longitude {lon} in pair {i} is out of range")

        except ValueError:
            return (False, f"Coordinate pair {i} has non-numeric values: '{pair}'")

    return (True, None)


def validate_geometry_density(coordinates, distance_km, road_code="Unknown"):
    """
    Validate that geometry has sufficient point density.

    Minimum acceptable density: 2.0 points/km
    - < 1.0 points/km: REJECTED (critically insufficient)
    - < 2.0 points/km: POOR QUALITY (insufficient)
    - >= 2.0 points/km: GOOD (acceptable)
    - >= 3.0 points/km: EXCELLENT (high quality)

    Args:
        coordinates (list): List of (lon, lat) tuples
        distance_km (float): Total road distance in kilometers
        road_code (str): Road code for error messages

    Returns:
        tuple: (is_valid: bool, density: float, message: str)

    Examples:
        >>> coords = [(-7.788, 41.164), (-7.785, 41.165), (-7.782, 41.166)]
        >>> validate_geometry_density(coords, 1.0, "N222")
        (True, 3.0, "N222: Density 3.00 points/km - EXCELLENT")

        >>> coords = [(-7.788, 41.164), (-7.785, 41.165)]  # Only 2 points
        >>> validate_geometry_density(coords, 10.0, "N2")
        (False, 0.2, "N2: Density 0.20 < 1.0 points/km - REJECTED")
    """
    if not coordinates or distance_km <= 0:
        return (False, 0.0, f"{road_code}: Invalid coordinates or distance")

    point_count = len(coordinates)
    density = point_count / distance_km

    # Critical: Less than 1 point/km
    if density < 1.0:
        return (
            False,
            density,
            f"{road_code}: Density {density:.2f} < 1.0 points/km - REJECTED (critically insufficient)"
        )

    # Poor quality: Less than 2 points/km
    elif density < 2.0:
        return (
            False,
            density,
            f"{road_code}: Density {density:.2f} < 2.0 points/km - POOR QUALITY (insufficient)"
        )

    # Excellent: 3 or more points/km
    elif density >= 3.0:
        return (
            True,
            density,
            f"{road_code}: Density {density:.2f} points/km - EXCELLENT"
        )

    # Good: 2-3 points/km
    else:
        return (
            True,
            density,
            f"{road_code}: Density {density:.2f} points/km - GOOD"
        )


def validate_all_points_in_portugal(coordinates, road_code="Unknown"):
    """
    Validate that ALL coordinate points are within Portugal's geographic bounds.

    Even a single point outside Portugal bounds will cause rejection.
    This prevents common issues like OSM returning roads from other countries
    with the same reference (e.g., N2 from Burkina Faso instead of Portugal).

    Args:
        coordinates (list): List of (lon, lat) tuples
        road_code (str): Road code for error messages

    Returns:
        tuple: (is_valid: bool, errors: list of str)

    Examples:
        >>> coords = [(-7.788, 41.164), (-7.785, 41.165)]  # Portugal
        >>> validate_all_points_in_portugal(coords, "N222")
        (True, [])

        >>> coords = [(-1.531, 12.368)]  # Burkina Faso
        >>> validate_all_points_in_portugal(coords, "N2")
        (False, ['Point 0: (12.368, -1.531) outside Portugal bounds...'])
    """
    errors = []
    lat_min, lat_max = PORTUGAL_BOUNDS['lat']
    lon_min, lon_max = PORTUGAL_BOUNDS['lon']

    for i, (lon, lat) in enumerate(coordinates):
        # Check if point is outside Portugal bounds
        if not (lat_min <= lat <= lat_max and lon_min <= lon <= lon_max):
            errors.append(
                f"Point {i}: ({lat:.4f}, {lon:.4f}) outside Portugal bounds "
                f"(lat: {lat_min}-{lat_max}°N, lon: {lon_min}-{lon_max}°W)"
            )

            # Don't spam too many errors - stop after 10
            if len(errors) >= 10:
                remaining = len(coordinates) - i - 1
                if remaining > 0:
                    errors.append(f"... ({remaining} more points not checked to avoid spam)")
                break

    return (len(errors) == 0, errors)


def get_quality_report(road_info, coordinates, distance_km):
    """
    Generate comprehensive quality report for a road.

    Combines all validation checks into a single quality report with
    an overall quality grade: EXCELLENT, GOOD, or REJECTED.

    Args:
        road_info (dict): Road information dict with 'code' and other metadata
        coordinates (list): List of (lon, lat) tuples
        distance_km (float): Total road distance in kilometers

    Returns:
        dict: Quality report with metrics and validation results
            - point_count: Number of GPS points
            - distance_km: Road distance
            - density: Points per kilometer
            - density_valid: Boolean, True if density acceptable
            - geo_valid: Boolean, True if all points in Portugal
            - geo_errors: List of geographic validation errors
            - quality: Overall quality grade (EXCELLENT/GOOD/REJECTED)
            - messages: List of all validation messages

    Example:
        >>> road = {'code': 'N222', 'name': 'Peso da Régua → Pinhão'}
        >>> coords = [...]  # 542 points
        >>> report = get_quality_report(road, coords, 27.0)
        >>> print(report['quality'])
        'EXCELLENT'
        >>> print(report['density'])
        20.07
    """
    road_code = road_info.get('code', 'Unknown')
    point_count = len(coordinates)

    # Validate density
    density_valid, density, density_msg = validate_geometry_density(
        coordinates, distance_km, road_code
    )

    # Validate geography
    geo_valid, geo_errors = validate_all_points_in_portugal(
        coordinates, road_code
    )

    # Determine overall quality
    if not density_valid or not geo_valid:
        quality = "REJECTED"
    elif density >= 3.0:
        quality = "EXCELLENT"
    else:
        quality = "GOOD"

    # Compile all messages
    messages = [density_msg]
    if geo_errors:
        messages.extend(geo_errors)

    return {
        'road_code': road_code,
        'point_count': point_count,
        'distance_km': distance_km,
        'density': density,
        'density_valid': density_valid,
        'geo_valid': geo_valid,
        'geo_errors': geo_errors,
        'quality': quality,
        'messages': messages
    }


def print_quality_report(quality_report):
    """
    Print a formatted quality report to console.

    Args:
        quality_report (dict): Quality report from get_quality_report()
    """
    print(f"\n{'='*70}")
    print(f"📊 QUALITY REPORT: {quality_report['road_code']}")
    print(f"{'='*70}")
    print(f"📍 Points: {quality_report['point_count']}")
    print(f"📏 Distance: {quality_report['distance_km']:.2f} km")
    print(f"📊 Density: {quality_report['density']:.2f} points/km")

    # Quality indicator with emoji
    quality = quality_report['quality']
    if quality == "EXCELLENT":
        quality_emoji = "✅ 🌟"
    elif quality == "GOOD":
        quality_emoji = "✅"
    else:
        quality_emoji = "❌"

    print(f"🎯 Quality: {quality_emoji} {quality}")
    print(f"{'='*70}")

    # Print validation messages
    if quality_report['messages']:
        print("\nValidation Details:")
        for msg in quality_report['messages']:
            if "REJECTED" in msg or "outside Portugal" in msg:
                print(f"  ❌ {msg}")
            elif "POOR" in msg:
                print(f"  ⚠️  {msg}")
            else:
                print(f"  ✅ {msg}")

    print(f"{'='*70}\n")


if __name__ == "__main__":
    # Run tests
    print("Running validation tests...")
    print()

    # Test 1: Valid Portugal coordinates
    print("Test 1: Valid coordinates (Chaves)")
    valid, error = validate_portugal_coordinates(41.74, -7.47, "Chaves")
    print(f"  Result: {'✅ PASS' if valid else '❌ FAIL'}")
    if error:
        print(f"  Error: {error}")
    print()

    # Test 2: Inverted coordinates (common bug!)
    print("Test 2: Inverted coordinates (lat/lon swapped)")
    valid, error = validate_portugal_coordinates(-7.47, 41.74, "Chaves (inverted)")
    print(f"  Result: {'❌ FAIL (expected)' if not valid else '✅ PASS (unexpected!)'}")
    if error:
        print(f"  Error: {error}")
    print()

    # Test 3: Coordinates outside Portugal
    print("Test 3: Coordinates outside Portugal (Paris)")
    valid, error = validate_portugal_coordinates(48.85, 2.35, "Paris")
    print(f"  Result: {'❌ FAIL (expected)' if not valid else '✅ PASS (unexpected!)'}")
    if error:
        print(f"  Error: {error}")
    print()

    # Test 4: Valid road coordinates
    print("Test 4: Valid road coordinates")
    road = {
        'code': 'N222',
        'coordinates': [(-7.7880, 41.1640), (-7.7850, 41.1650), (-7.7820, 41.1665)]
    }
    valid, errors = validate_road_coordinates(road)
    print(f"  Result: {'✅ PASS' if valid else '❌ FAIL'}")
    if errors:
        for err in errors:
            print(f"  Error: {err}")
    print()

    # Test 5: WKT validation
    print("Test 5: Valid WKT string")
    wkt = "LINESTRING(-7.7880 41.1640, -7.7850 41.1650)"
    valid, error = validate_wkt_geometry(wkt)
    print(f"  Result: {'✅ PASS' if valid else '❌ FAIL'}")
    if error:
        print(f"  Error: {error}")
    print()

    print("All tests completed!")
