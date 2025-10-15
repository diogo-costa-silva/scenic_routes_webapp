-- ============================================================================
-- Migration: Update data_source for Hybrid Strategy
-- ============================================================================
-- Description: Aligns data_source field with new hybrid geometry strategy
-- Date: 2025-10-15
-- Related: PRD.md, ARCHITECTURE.md (Hybrid Strategy)
-- ============================================================================

-- ============================================================================
-- Step 1: Update DEFAULT value for data_source column
-- ============================================================================
-- Change default from 'osm' to 'hybrid' to match new strategy

ALTER TABLE roads
ALTER COLUMN data_source SET DEFAULT 'hybrid';

-- ============================================================================
-- Step 2: Update existing roads with old data_source values
-- ============================================================================
-- Map old values to new hybrid strategy values:
--   'osm' → 'osm_recursive' (new OSM recursive query method)
--   'mapbox_directions' → 'mapbox_matching' (WRONG API, needs re-processing)
--   'manual' → keep as 'manual'
--   'gps_trace' → keep as 'gps_trace'

-- Update generic 'osm' to 'osm_recursive'
UPDATE roads
SET data_source = 'osm_recursive'
WHERE data_source = 'osm';

-- Mark old 'mapbox_directions' roads for re-processing
-- Note: These roads used the WRONG API and likely have detours
-- They should be re-processed using the hybrid strategy
UPDATE roads
SET data_source = 'mapbox_directions_deprecated'
WHERE data_source = 'mapbox_directions';

-- ============================================================================
-- Step 3: Add comment to explain deprecated value
-- ============================================================================
COMMENT ON COLUMN roads.data_source IS
'Data source for road geometry. Valid values:
 - osm_recursive: OpenStreetMap recursive query (primary method)
 - mapbox_matching: Mapbox Map Matching API (fallback)
 - hybrid: Mixed/unknown source
 - manual: Manually entered data
 - gps_trace: GPS trace data
 - mapbox_directions_deprecated: OLD API (causes detours, re-process needed)';

-- ============================================================================
-- Verification Queries
-- ============================================================================
-- Check updated values
-- SELECT code, name, data_source FROM roads ORDER BY data_source;

-- Count by data_source
-- SELECT data_source, COUNT(*) as count FROM roads GROUP BY data_source;

-- Find roads needing re-processing
-- SELECT code, name FROM roads WHERE data_source = 'mapbox_directions_deprecated';

-- ============================================================================
-- Post-Migration Actions Required
-- ============================================================================
-- [ ] Re-process all roads marked 'mapbox_directions_deprecated'
-- [ ] These roads likely have detours (e.g., N222 through Peso da Régua)
-- [ ] Run: python process_roads.py --reprocess-deprecated
-- [ ] After re-processing, verify geometries are correct on map

-- ============================================================================
-- End of Migration
-- ============================================================================
