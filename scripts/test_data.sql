-- ============================================================================
-- Road Explorer Portugal - Test Data
-- ============================================================================
-- Description: Sample road data for testing database setup
-- Usage: Run this after schema.sql to populate test data
-- ============================================================================

-- ============================================================================
-- Sample Road 1: N222 (Peso da Régua → Pinhão)
-- ============================================================================
-- One of Europe's most beautiful roads through the Douro Valley

INSERT INTO roads (
    code,
    name,
    description,
    region,
    geometry,
    start_point_name,
    start_lat,
    start_lon,
    end_point_name,
    end_lat,
    end_lon,
    distance_km,
    elevation_max,
    elevation_min,
    elevation_gain,
    elevation_loss,
    curve_count_total,
    curve_count_gentle,
    curve_count_moderate,
    curve_count_sharp,
    straight_count,
    longest_straight_km,
    surface,
    surface_verified,
    data_source
) VALUES (
    'N222',
    'Peso da Régua → Pinhão',
    'One of the most beautiful roads in Europe, winding through the Douro Valley with stunning vineyard views',
    'Continental',
    ST_GeomFromText('LINESTRING(-7.7880 41.1640, -7.7850 41.1650, -7.7820 41.1665, -7.7785 41.1682, -7.7750 41.1698, -7.7710 41.1715, -7.7670 41.1730, -7.7625 41.1748, -7.7580 41.1765)', 4326),
    'Peso da Régua',
    41.1640,
    -7.7880,
    'Pinhão',
    41.1765,
    -7.7580,
    27.30,
    523,
    89,
    434,
    380,
    147,
    82,
    54,
    11,
    23,
    1.20,
    'asphalt',
    true,
    'osm'
);

-- ============================================================================
-- Sample Road 2: N339 (Covilhã → Torre)
-- ============================================================================
-- Climb to Portugal's highest point in Serra da Estrela

INSERT INTO roads (
    code,
    name,
    description,
    region,
    geometry,
    start_point_name,
    start_lat,
    start_lon,
    end_point_name,
    end_lat,
    end_lon,
    distance_km,
    elevation_max,
    elevation_min,
    elevation_gain,
    elevation_loss,
    curve_count_total,
    curve_count_gentle,
    curve_count_moderate,
    curve_count_sharp,
    straight_count,
    longest_straight_km,
    surface,
    surface_verified,
    data_source
) VALUES (
    'N339',
    'Covilhã → Torre',
    'Climb to Portugal''s highest point at 1993m altitude in Serra da Estrela',
    'Continental',
    ST_GeomFromText('LINESTRING(-7.5000 40.2830, -7.5050 40.2900, -7.5100 40.2970, -7.5160 40.3040, -7.5220 40.3115, -7.5285 40.3195, -7.5350 40.3270)', 4326),
    'Covilhã',
    40.2830,
    -7.5000,
    'Torre',
    40.3270,
    -7.5350,
    18.50,
    1993,
    675,
    1318,
    0,
    89,
    45,
    32,
    12,
    15,
    0.85,
    'asphalt',
    true,
    'osm'
);

-- ============================================================================
-- Sample Road 3: N247 (Cascais → Ericeira) - Coastal Section
-- ============================================================================
-- Beautiful Atlantic coastal road

INSERT INTO roads (
    code,
    name,
    description,
    region,
    geometry,
    start_point_name,
    start_lat,
    start_lon,
    end_point_name,
    end_lat,
    end_lon,
    distance_km,
    elevation_max,
    elevation_min,
    elevation_gain,
    elevation_loss,
    curve_count_total,
    curve_count_gentle,
    curve_count_moderate,
    curve_count_sharp,
    straight_count,
    longest_straight_km,
    surface,
    surface_verified,
    data_source
) VALUES (
    'N247',
    'Cascais → Ericeira',
    'Stunning Atlantic coastal road with ocean views and charming fishing villages',
    'Continental',
    ST_GeomFromText('LINESTRING(-9.4200 38.6970, -9.4250 38.7050, -9.4300 38.7135, -9.4360 38.7225, -9.4420 38.7315, -9.4485 38.7410, -9.4550 38.7500)', 4326),
    'Cascais',
    38.6970,
    -9.4200,
    'Ericeira',
    38.7500,
    -9.4550,
    45.20,
    156,
    5,
    892,
    915,
    203,
    128,
    61,
    14,
    42,
    2.80,
    'asphalt',
    false,
    'osm'
);

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check inserted roads
-- SELECT code, name, region, distance_km, curve_count_total FROM roads;

-- Check roads list view
-- SELECT * FROM roads_list;

-- Verify geometry is valid
-- SELECT code, ST_IsValid(geometry) as is_valid FROM roads;

-- Get road count by region
-- SELECT region, COUNT(*) as road_count FROM roads GROUP BY region;

-- ============================================================================
-- End of Test Data
-- ============================================================================
