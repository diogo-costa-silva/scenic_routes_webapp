-- ============================================================================
-- Road Explorer Portugal - Database Schema
-- ============================================================================
-- Description: Complete schema for roads table with PostGIS geometry support
-- Version: 1.0
-- Database: PostgreSQL + PostGIS (Supabase)
-- ============================================================================

-- Enable PostGIS extension (required for geometry types)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ============================================================================
-- Main Table: roads
-- ============================================================================
-- Stores all motorcycle road data including geometry, metrics, and metadata

CREATE TABLE IF NOT EXISTS roads (
    -- ========================================================================
    -- Identifiers
    -- ========================================================================
    id SERIAL PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,                   -- e.g., "N222", "N2", "EM567"
    name VARCHAR(200) NOT NULL,                         -- e.g., "Peso da Régua → Pinhão"
    description TEXT,                                   -- Brief description of the road

    -- ========================================================================
    -- Classification
    -- ========================================================================
    region VARCHAR(20) NOT NULL                         -- "Continental", "Madeira", "Açores"
        CHECK (region IN ('Continental', 'Madeira', 'Açores')),
    category VARCHAR(50),                               -- "Serra", "Costa", "Montanha", etc (future use)

    -- ========================================================================
    -- Geometry (PostGIS)
    -- ========================================================================
    geometry GEOMETRY(LINESTRING, 4326) NOT NULL,       -- GPS coordinates (WGS84, SRID 4326)

    -- ========================================================================
    -- Start and End Points
    -- ========================================================================
    start_point_name VARCHAR(100),                      -- e.g., "Covilhã"
    start_lat DECIMAL(10, 7) NOT NULL,
    start_lon DECIMAL(10, 7) NOT NULL,
    end_point_name VARCHAR(100),                        -- e.g., "Torre"
    end_lat DECIMAL(10, 7) NOT NULL,
    end_lon DECIMAL(10, 7) NOT NULL,

    -- ========================================================================
    -- Metrics: Distance
    -- ========================================================================
    distance_km DECIMAL(10, 2) NOT NULL,                -- Total distance in kilometers

    -- ========================================================================
    -- Metrics: Elevation
    -- ========================================================================
    elevation_max INTEGER,                              -- Maximum altitude (meters)
    elevation_min INTEGER,                              -- Minimum altitude (meters)
    elevation_gain INTEGER,                             -- Total elevation gain (meters)
    elevation_loss INTEGER,                             -- Total elevation loss (meters)

    -- ========================================================================
    -- Metrics: Curves and Straights
    -- ========================================================================
    curve_count_total INTEGER,                          -- Total number of curves
    curve_count_gentle INTEGER,                         -- Gentle curves (20-45°)
    curve_count_moderate INTEGER,                       -- Moderate curves (45-90°)
    curve_count_sharp INTEGER,                          -- Sharp curves (>90°)
    straight_count INTEGER,                             -- Number of straight sections
    longest_straight_km DECIMAL(10, 2),                 -- Longest straight section (km)

    -- ========================================================================
    -- Road Characteristics
    -- ========================================================================
    surface VARCHAR(50) DEFAULT 'asphalt',              -- "asphalt", "gravel", "unpaved", "mixed"
    surface_verified BOOLEAN DEFAULT FALSE,             -- Manually validated?
    road_condition VARCHAR(50),                         -- "excellent", "good", "fair", "poor" (future)

    -- ========================================================================
    -- Metadata
    -- ========================================================================
    data_source VARCHAR(50) DEFAULT 'hybrid',           -- "osm_recursive", "mapbox_matching", "hybrid"
    last_validated_at TIMESTAMP,                        -- Last manual validation
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- ========================================================================
    -- Constraints
    -- ========================================================================
    CONSTRAINT check_lat_start CHECK (start_lat BETWEEN -90 AND 90),
    CONSTRAINT check_lon_start CHECK (start_lon BETWEEN -180 AND 180),
    CONSTRAINT check_lat_end CHECK (end_lat BETWEEN -90 AND 90),
    CONSTRAINT check_lon_end CHECK (end_lon BETWEEN -180 AND 180),
    CONSTRAINT check_distance CHECK (distance_km > 0),
    CONSTRAINT check_elevation_logic CHECK (
        elevation_max IS NULL OR
        elevation_min IS NULL OR
        elevation_max >= elevation_min
    )
);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

-- B-tree index on region for filtering
CREATE INDEX IF NOT EXISTS idx_roads_region ON roads(region);

-- B-tree index on code for quick lookups
CREATE INDEX IF NOT EXISTS idx_roads_code ON roads(code);

-- Spatial index on geometry (GIST) for geospatial queries
CREATE INDEX IF NOT EXISTS idx_roads_geometry ON roads USING GIST(geometry);

-- Composite index for common queries (region + created_at)
CREATE INDEX IF NOT EXISTS idx_roads_region_created ON roads(region, created_at DESC);

-- ============================================================================
-- View: roads_list (Simplified API Response)
-- ============================================================================
-- Returns essential data for listing roads in the frontend sidebar

CREATE OR REPLACE VIEW roads_list AS
SELECT
    id,
    code,
    name,
    region,
    distance_km,
    elevation_max,
    curve_count_total,
    start_point_name,
    end_point_name,
    surface,
    created_at
FROM roads
ORDER BY region, code;

-- ============================================================================
-- Row Level Security (RLS) Policies
-- ============================================================================
-- Enable RLS on roads table
ALTER TABLE roads ENABLE ROW LEVEL SECURITY;

-- Policy: Allow anonymous read access (public SELECT)
CREATE POLICY "Allow public read access" ON roads
    FOR SELECT
    USING (true);

-- Policy: Allow authenticated users to insert (for future admin features)
-- Note: This will be used later when authentication is implemented
-- CREATE POLICY "Allow authenticated insert" ON roads
--     FOR INSERT
--     WITH CHECK (auth.role() = 'authenticated');

-- ============================================================================
-- Helper Functions
-- ============================================================================

-- Function: Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger: Auto-update updated_at on row modification
CREATE TRIGGER update_roads_updated_at
    BEFORE UPDATE ON roads
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Comments (Documentation)
-- ============================================================================

COMMENT ON TABLE roads IS 'Stores motorcycle road data for Road Explorer Portugal';
COMMENT ON COLUMN roads.geometry IS 'PostGIS LineString with SRID 4326 (WGS84)';
COMMENT ON COLUMN roads.region IS 'Geographic region: Continental, Madeira, or Açores';
COMMENT ON COLUMN roads.curve_count_total IS 'Total curves detected via bearing analysis';
COMMENT ON COLUMN roads.surface IS 'Road surface type, defaults to asphalt';
COMMENT ON COLUMN roads.data_source IS 'Source of road data: osm, manual, or gps_trace';

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Run these queries to verify the schema was created correctly:

-- Check if PostGIS is enabled
-- SELECT PostGIS_version();

-- Check table structure
-- \d roads

-- Check indexes
-- \di

-- Check RLS policies
-- \dp roads

-- Test view
-- SELECT * FROM roads_list LIMIT 5;

-- ============================================================================
-- End of Schema
-- ============================================================================
