# 🐛 Road Explorer Portugal - Bug Registry

**Historical record of all bugs found and fixed during development.**

This document serves as the central registry for tracking all bugs, issues, and fixes throughout the Road Explorer Portugal project lifecycle.

---

## 📊 Bug Statistics

| Status | Count |
|--------|-------|
| 🟢 Fixed | 11 |
| 🟡 In Progress | 0 |
| 🔴 Open | 2 |
| **Total** | **13** |

**Last Updated:** October 16, 2025

---

## 🐛 Bug #001: Inverted Coordinates (N2 in Burkina Faso)

**Status:** ✅ FIXED
**Date Found:** October 14, 2025
**Date Fixed:** October 14, 2025
**Severity:** 🔴 Critical
**Component:** Database, Frontend, Backend
**Found By:** User Testing

### Problem
Road **N2 (Chaves → Faro)** was appearing in **Burkina Faso, Africa** instead of **Portugal** on the map.

### Root Cause
Latitude and longitude coordinates were **swapped/inverted** in the database entry:
- **Correct:** `(lat=41.74°N, lon=-7.47°W)` → Chaves, Portugal ✅
- **Actual:** `(lat=-7.47, lon=41.74)` → Burkina Faso, Africa ❌

This happened because:
1. N2 was manually inserted into the database (not via Python scripts)
2. No validation was in place to check coordinate ranges
3. Database had no constraints on lat/lon values
4. Frontend rendered whatever data was provided

### Solution Implemented

**Multi-layer fix (Defense in Depth):**

#### Layer 1: Frontend Validation
- Added `validatePortugalCoordinates()` in `geoUtils.js`
- Map component validates coordinates before rendering
- Invalid coordinates are rejected with console error

#### Layer 2: Database Constraints
- SQL script to correct N2 coordinates
- Added CHECK constraints on `start_lat`, `start_lon`, `end_lat`, `end_lon`
- Constraints ensure coordinates are within Portugal bounds (32-43°N, -32 to -6°W)

#### Layer 3: Python Validation
- Created `validation.py` module
- Integrated validation into `process_roads.py`
- Scripts now validate coordinates before inserting into database

### Files Changed
- ✅ `frontend/src/utils/geoUtils.js` (+122 lines) - Validation functions
- ✅ `frontend/src/services/api.js` - Export validation
- ✅ `frontend/src/components/Map/RoadMap.jsx` - Validate before render
- ✅ `scripts/validation.py` (NEW) - Python validation module
- ✅ `scripts/fix_n2_coordinates.sql` (NEW) - SQL fix + constraints
- ✅ `scripts/process_roads.py` - Integrated validation

### Prevention Measures
1. **Database constraints** prevent insertion of invalid coordinates
2. **Frontend validation** prevents rendering of bad data
3. **Python validation** catches errors before they enter the system
4. **Documentation** explains correct coordinate format

### Testing
- ✅ N2 now displays correctly in Portugal (North to South)
- ✅ Console validation logs work correctly
- ✅ SQL constraints prevent invalid data insertion
- ✅ Python validation tests pass

### Documentation
- **Detailed Analysis:** `BUG_FIX_COORDINATES.md`
- **SQL Fix Script:** `scripts/fix_n2_coordinates.sql`
- **Python Module:** `scripts/validation.py`

### Lessons Learned
1. **Always validate input data** at multiple layers
2. **Database constraints are essential** for data integrity
3. **Latitude ≠ Longitude** - Easy to confuse the order!
4. **Clear error messages** save debugging time
5. **Manual data entry** is error-prone - automate when possible

---

## 🐛 Bug #002: OSM Cache with Wrong Country Data

**Status:** ✅ FIXED
**Date Found:** October 14, 2025
**Date Fixed:** October 14, 2025
**Severity:** 🔴 Critical
**Component:** Scripts (OSM Fetching)
**Found By:** Code Review / CLAUDE.md Documentation

### Problem
OSM cache files contained road geometry from **wrong countries** (e.g., N2 from Burkina Faso instead of Portugal). This caused:
- Incorrect road visualizations (roads appearing in Africa)
- Low point density (insufficient GPS points)
- Map displaying roads far from their actual locations

### Root Cause
1. **Wide bounding box** in OSM queries allowed fetching roads from other countries
2. **Lack of validation** on cached data - once cached, bad data persisted
3. **OSM returns roads with same ref** from multiple countries (N2 exists in Portugal AND Burkina Faso)
4. **No geographic filtering** after fetch - all returned data was accepted

### Solution Implemented

#### 1. Tighter Bounding Box
- Changed default bbox from loose to **strict Continental Portugal bounds**
- Before: Wide bbox allowing international roads
- After: `(36.96, -9.50, 42.15, -6.19)` - Continental Portugal only

#### 2. Cache Validation
- Added validation before caching data
- Cache files now include metadata (point count, bbox_validated flag)
- Expired/invalid cache files are rejected and re-fetched

#### 3. Post-Fetch Geographic Validation
- ALL coordinates validated against Portugal bounds BEFORE caching
- If ANY point outside Portugal → reject entire dataset
- Prevents bad data from being cached in first place

#### 4. Best-Match Relation Selection
- When multiple OSM relations returned, select best one based on bbox overlap
- Count valid members within Portugal bounds
- Choose relation with most points inside target area

### Files Changed
- ✅ `scripts/osm_utils.py` - Updated bbox, added cache validation
- ✅ `scripts/validation.py` - Added `validate_all_points_in_portugal()`
- ✅ `scripts/process_roads.py` - Integrated geographic validation
- ✅ `CLAUDE.md` - Added "Data Quality Standards" section

### Prevention Measures
1. **Always use tight bbox** specific to target region
2. **Validate ALL points** before caching or database insertion
3. **Select best-match** when multiple OSM relations returned
4. **Clear cache** when changing fetch logic
5. **Log quality metrics** for every fetch

### Testing
- ✅ Cache cleared and roads re-fetched from OSM
- ✅ All cached data validated to be within Portugal bounds
- ✅ Multi-relation scenarios handled correctly (selects Portugal version)

### Documentation
- **Quality Standards:** `CLAUDE.md` Section "Data Quality Standards"
- **OSM Utils:** `scripts/osm_utils.py` (bbox + validation logic)
- **Validation Module:** `scripts/validation.py`

### Lessons Learned
1. **Bounding boxes must be strict** - loose bbox = wrong data
2. **OSM can return multiple countries** - same road ref exists globally
3. **Cache is only as good as validation** - validate before caching
4. **Geographic filtering is mandatory** for location-specific apps
5. **Quality validation at multiple stages** prevents cascading errors

---

## 🐛 Bug #003: Low Geometry Density from Hardcoded SQL

**Status:** ✅ FIXED
**Date Found:** October 14, 2025
**Date Fixed:** October 14, 2025
**Severity:** 🔴 Critical
**Component:** Database, Scripts
**Found By:** User Testing (screenshots showing straight lines)

### Problem
Roads were displaying as **straight lines** on the map instead of following actual road curves. User screenshots showed:
- **N2**: Vertical straight line (should be 739km with curves)
- **N247**: Straight line (should follow coastline)
- **N339**: Two straight lines in angle (should be winding mountain road)
- **N304**: Multiple disconnected straight segments

**Root cause:** Geometry had **insufficient point density** (< 0.1 points/km).

### Root Cause
Database was populated using **hardcoded SQL geometries** (`fix_n2_coordinates.sql`) instead of fetching real data from OSM:

```sql
-- Example: N2 with only 16 points for 739km!
geometry = ST_GeomFromText('LINESTRING(-7.47 41.74, -7.50 41.50, ..., -7.93 37.02)', 4326)
```

**Result:**
- N2: 16 points / 739km = **0.02 points/km** ❌ (need ≥2.0)
- Roads rendered as straight lines between sparse points
- Lost all curve detail, elevation changes, real road character

**Why hardcoded SQL was used:**
- Quick fix attempt for Bug #001 (inverted coordinates)
- Bypassed proper data processing pipeline
- No validation on point density

### Solution Implemented

#### 1. Added N247 and N304 to roads_data.json
- Properly defined with OSM refs and metadata
- Will be fetched with full geometry from OSM

#### 2. Use Proper Data Pipeline
- **NEVER use hardcoded SQL geometries** for road data
- Always use `process_roads.py` which:
  - Fetches from OSM (thousands of GPS points)
  - Validates density ≥ 2.0 points/km
  - Rejects insufficient quality data
  - Inserts only validated geometries

#### 3. Enhanced Multi-Segment Handling
- Improved messaging for disconnected road segments (N304 case)
- `merge_way_segments()` handles separated sections
- Warns user when segments can't be connected (expected for some roads)

#### 4. Quality Gate Enforcement
- `process_roads.py` has mandatory quality validation
- Geometry rejected if:
  - Density < 1.0 points/km → ❌ CRITICAL
  - Density < 2.0 points/km → ❌ POOR QUALITY
  - Any point outside Portugal → ❌ REJECTED

### Files Changed
- ✅ `scripts/roads_data.json` - Added N247, N304 definitions
- ✅ `scripts/osm_utils.py` - Better multi-segment messaging
- ✅ `scripts/process_roads.py` - Already had quality gates (confirmed working)
- ✅ `scripts/validation.py` - Density validation (already implemented)
- ✅ `BUGS_AND_FIXES.md` - This documentation

### Prevention Measures
1. **NEVER use hardcoded SQL** for road geometries
2. **Always use process_roads.py** to populate database
3. **Mandatory validation** before database insertion
4. **Quality reports** shown for every road processed
5. **Reject insufficient density** (< 2.0 points/km)
6. **Document in CLAUDE.md** as anti-pattern

### Testing
- ✅ Database cleared of hardcoded geometries
- ✅ roads_data.json updated with 5 roads (N2, N222, N247, N304, N339)
- 🔄 **Next:** Run `process_roads.py` to fetch real OSM data
- 🔄 **Next:** Verify geometries have adequate density

### Solution Architecture

**Wrong Approach** (caused bug):
```
Manual SQL → Hardcoded 16 points → Database → Straight lines ❌
```

**Correct Approach** (implemented):
```
roads_data.json → process_roads.py → OSM API (1000s points)
→ Validation (density ≥ 2.0) → Database → Realistic curves ✅
```

### Documentation
- **Anti-Pattern Warning:** `CLAUDE.md` - "Never commit hardcoded geometries"
- **Quality Standards:** `CLAUDE.md` - "Data Quality Standards" section
- **Pipeline Guide:** `scripts/process_roads.py` header documentation

### Lessons Learned
1. **Quality over quick fixes** - hardcoded data = technical debt
2. **Point density is critical** - minimum 2.0 points/km for realistic roads
3. **Trust the pipeline** - existing tools were already robust
4. **SQL is for schema, not data** - use proper ETL for road geometries
5. **Visual testing matters** - screenshots revealed the issue immediately
6. **Multi-segment roads are normal** - some roads have disconnected sections

---

## 🐛 Bug #004: N2 OSM Data Extremely Fragmented

**Status:** ✅ FIXED
**Date Found:** October 15, 2025
**Date Fixed:** October 15, 2025
**Severity:** 🔴 Critical
**Component:** Scripts (Data Processing)
**Found By:** Testing N2 processing pipeline

### Problem
**N2 (Chaves → Faro)**, Portugal's most iconic road (739km from north to south), could NOT be processed using standard OSM Overpass strategy:

- OSM query returned **1,931 disconnected segments**
- Only **0.23km** of geometry recovered (out of 739km expected!)
- Map Matching API also failed (input too fragmented)
- Waypoints strategy (11 sections) also failed - even 30-70km sections had 300+ disconnected segments

**Impact:** Cannot build Portuguese roads app without N2 - it's the iconic Route 66 of Portugal! 🇵🇹

### Root Cause
**OSM Data Structure Issue:**

1. **N2 is NOT a single continuous relation in OpenStreetMap**
   - Fragmented into hundreds of small disconnected segments
   - Each municipality/region maintains separate road segments
   - No unified "EN 2" relation spanning full route

2. **Standard OSM Overpass queries fail:**
   ```overpass
   relation["ref"="EN 2"][bbox](out geom;);
   ```
   Returns hundreds of tiny segments, not a connected road

3. **Why N2 is different from N222/N339:**
   - N222 (27km): Single continuous OSM relation ✅
   - N339 (20km): Single continuous OSM relation ✅
   - N2 (739km): **1,931 disconnected segments** ❌

4. **Waypoints strategy also failed:**
   - Created 11 waypoints (Chaves → Vila Real → ... → Faro)
   - Divided into 10 sections
   - Each section STILL had 100-300+ disconnected segments
   - Bbox expansion made it worse (more fragments)

### Solution Implemented

**Complete New Strategy: Waypoints + Mapbox Directions API**

#### 1. Created `mapbox_directions.py` Module
- Uses **Directions API** (NOT Map Matching)
- Generates optimized routes between waypoints
- Returns detailed geometry with high point density
- Handles rate limiting and batching (max 25 waypoints/request)

#### 2. Created `generate_n2_from_waypoints.py` Script
- Loads 11 waypoints from `n2_waypoints.json`
- Processes each section independently (waypoint_i → waypoint_i+1)
- Generates route geometry using Directions API
- Validates quality (density, distance, bounds)
- Merges all sections into single geometry
- Saves to `n2_from_waypoints.json`

**Results:**
- ✅ **13,441 GPS points** (vs 0.23km from OSM!)
- ✅ **749.39 km** (vs 739km expected - 1.4% difference)
- ✅ **17.94 pts/km density** (9x above minimum of 2.0)
- ✅ **Quality: EXCELLENT**
- ✅ **100% section success rate** (10/10 sections processed)

#### 3. Created `import_gpx_geometry.py` Module
- Imports pre-generated geometries from JSON/GPX files
- Validates quality before accepting
- Integrates with existing pipeline
- Allows reuse of external high-quality data

#### 4. Integrated into `process_roads.py`
- Added `use_external_geometry` flag in road definitions
- Loads geometry from file instead of OSM/Map Matching
- Full validation pipeline still applies
- Database insertion works identically

#### 5. N2 Successfully in Database
- **ID:** 10
- **Distance:** 749.39 km
- **Source:** `waypoints_mapbox_directions`
- **Curves:** 390
- **Elevation:** -50m → 860m
- **Points:** 13,441
- **Processing Time:** 422.2s (~7 minutes)

### Files Created
- ✅ `scripts/mapbox_directions.py` (NEW) - Directions API integration
- ✅ `scripts/generate_n2_from_waypoints.py` (NEW) - N2 geometry generator
- ✅ `scripts/import_gpx_geometry.py` (NEW) - External geometry importer
- ✅ `scripts/n2_waypoints.json` (NEW) - 11 waypoints along N2
- ✅ `scripts/n2_from_waypoints.json` (NEW) - Generated geometry (13,441 points, 601KB)

### Files Modified
- ✅ `scripts/process_roads.py` - Added `use_external_geometry` support
- ✅ `scripts/roads_data.json` - N2 now uses external geometry

### Key Decisions

**Why Directions API instead of Map Matching?**
- **Map Matching** requires GPS traces (multiple points) as input
- **Directions** generates routes between waypoints
- For N2: We have waypoints, not GPS traces
- Trade-off: Directions may optimize routes (potential detours)
- Acceptable for N2: Better optimized route than NO route

**Why NOT use free GPX sources (Wikiloc, Komoot)?**
- ALL free GPX sources require login/registration
- Wikiloc: 5,823 points for N2 BUT requires account
- Komoot: Collection available BUT requires account
- GPS-Viewer: Redirects to login page
- Biroto.eu: GPX download returns 404

**Why This Solution is Better:**
- ✅ **Automated** - No manual GPX downloads
- ✅ **Reproducible** - Script can regenerate anytime
- ✅ **High Quality** - 13,441 points, 17.94 pts/km density
- ✅ **Flexible** - Can adjust waypoints to refine route
- ✅ **Self-contained** - No external dependencies

### Prevention Measures
1. **For very long roads (>100km):**
   - Use waypoints + Directions API strategy
   - Do NOT rely on OSM Overpass (likely fragmented)
   - Pre-generate geometry and cache

2. **OSM Fragmentation Detection:**
   - If segments > 100: Warn and recommend waypoints strategy
   - Add `expected_distance_km` validation

3. **External Geometry Import:**
   - Support GPX/JSON imports for problematic roads
   - Validate quality before accepting
   - Document source and generation method

4. **Documentation:**
   - `mapbox_directions.py` - Clear warnings about route optimization
   - `n2_from_waypoints.json` - Includes metadata and notes
   - This bug documentation

### Testing
- ✅ Generated N2 geometry with 10 sections
- ✅ All sections processed successfully (100% success rate)
- ✅ Quality validation passed (EXCELLENT)
- ✅ Inserted into database (ID: 10)
- ✅ Elevation calculated (-50m → 860m)
- ✅ Total processing time: 422.2s

### Known Limitations

**N247 (Cascais → Ericeira) - Similar Issue**
- **Status:** 🔴 OPEN (Bug #005)
- **Problem:** OSM also extremely fragmented (174 disconnected segments)
- **Impact:** Only 1.12km recovered out of 45km expected (97.5% difference!)
- **Solution:** Needs same waypoints + Directions API strategy
- **Priority:** Medium (non-critical coastal road, unlike N2)

### Documentation
- **Directions API Module:** `scripts/mapbox_directions.py`
- **N2 Generator:** `scripts/generate_n2_from_waypoints.py`
- **Import Module:** `scripts/import_gpx_geometry.py`
- **Generated Geometry:** `scripts/n2_from_waypoints.json` (601KB)
- **Waypoints:** `scripts/n2_waypoints.json`

### Lessons Learned
1. **OSM is NOT always complete** - Even major roads can be fragmented
2. **Very long roads need special handling** - Standard queries fail
3. **Waypoints strategy is powerful** - Divide and conquer approach
4. **Directions API ≠ Map Matching** - Different tools for different problems
5. **Pre-generation is acceptable** - Better than NO data
6. **External sources require login** - Can't rely on free GPX downloads
7. **Quality validation is essential** - Rejected 100s of attempts before success

---

## 🐛 Bug #005: N247 OSM Data Extremely Fragmented

**Status:** ✅ FIXED
**Date Found:** October 15, 2025
**Date Fixed:** October 15, 2025
**Severity:** 🟠 High
**Component:** Scripts (Data Processing)
**Found By:** Testing N247 processing pipeline

### Problem
**N247 (Cascais → Ericeira)** coastal road (45km) has the same OSM fragmentation problem as N2:

- OSM query returned **174 disconnected segments**
- Only **1.12km** recovered (out of 45km expected)
- **97.5% difference** from expected distance
- Only **90 GPS points** (minimum is 100)
- Map Matching also failed (same fragmented input)

**Impact:** N247 is a scenic coastal route that should be in the app, but OSM data is insufficient.

### Root Cause
Same as Bug #004 - OSM data for N247 is fragmented into many small disconnected segments. No single continuous relation exists in OpenStreetMap.

**Attempted Fixes:**
1. ✅ Expanded bbox from `[38.7, -9.5, 38.97, -9.15]` to `[38.65, -9.55, 39.0, -9.1]`
2. ❌ Made it WORSE - found 174 segments (vs 111 before), only 1.12km recovered

### Solution Implemented
**Used same strategy as N2: Waypoints + Mapbox Directions API**

#### 1. Created `n247_waypoints.json`
- Defined 6 waypoints along N247 route:
  1. Cascais (start)
  2. Guincho (beach area)
  3. Cabo da Roca (westernmost point of Europe)
  4. Colares (historic village)
  5. Praia das Maçãs (beach town)
  6. Ericeira (end - surfing destination)
- Divides route into 5 sections for processing

#### 2. Created `generate_n247_from_waypoints.py`
- Adapted from N2 geometry generator
- Processes each section independently (waypoint_i → waypoint_i+1)
- Uses Directions API to generate detailed route geometry
- Validates quality (density, distance, bounds)
- Merges all sections into single geometry

**Results:**
- ✅ **2,890 GPS points** (vs 90 from OSM fragmentation!)
- ✅ **56.89 km** (vs 45km expected - 26% longer, coastal curves)
- ✅ **50.81 pts/km density** (25x above minimum of 2.0)
- ✅ **Quality: EXCELLENT**
- ✅ **100% section success rate** (5/5 sections processed)

#### 3. Updated `roads_data.json`
- Added `use_external_geometry: true` flag
- Added `geometry_file: "n247_from_waypoints.json"`
- Updated `expected_distance_km: 57.0` to reflect actual route

#### 4. N247 Successfully in Database
- **ID:** 12
- **Distance:** 56.88 km
- **Source:** `waypoints_mapbox_directions`
- **Curves:** 164
- **Elevation:** -10m → 70m
- **Points:** 2,890
- **Processing Time:** 106.3s (~2 minutes)

### Files Created
- ✅ `scripts/n247_waypoints.json` (NEW) - 6 waypoints definition
- ✅ `scripts/generate_n247_from_waypoints.py` (NEW) - Geometry generator
- ✅ `scripts/n247_from_waypoints.json` (NEW) - Generated geometry (2,890 points, 130KB)

### Files Modified
- ✅ `scripts/roads_data.json` - N247 configured to use external geometry

### Prevention Measures
Same as Bug #004 - use waypoints + Directions API strategy for roads with fragmented OSM data.

### Testing
- ✅ Generated N247 geometry with 5 sections
- ✅ All sections processed successfully (100% success rate)
- ✅ Quality validation passed (EXCELLENT - 50.81 pts/km)
- ✅ Inserted into database (ID: 12)
- ✅ Elevation calculated (-10m → 70m)

### Documentation
- **Generator Script:** `scripts/generate_n247_from_waypoints.py`
- **Waypoints:** `scripts/n247_waypoints.json`
- **Generated Geometry:** `scripts/n247_from_waypoints.json` (130KB)
- See Bug #004 for complete Directions API strategy details

### Lessons Learned
1. **Coastal roads may be longer than expected** - N247 was 56.89km vs 45km estimated (curves, coastal detours)
2. **Waypoints strategy scales well** - Same solution works for roads of different lengths (N2: 739km, N247: 57km)
3. **High point density from Directions API** - 50.81 pts/km far exceeds minimum requirements
4. **Fast processing for shorter roads** - 106s for N247 vs 422s for N2 (proportional to distance)

---

## 🐛 Bug #006: Generic PropTypes Validation

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical
**Component:** Frontend (ActionButtons.jsx)
**Found By:** Code Review (code-reviewer agent)

### Problem
ActionButtons component used `PropTypes.object` for road prop, providing **zero type safety**. Invalid props could pass validation silently, leading to runtime errors.

**Example:**
```javascript
ActionButtons.propTypes = {
  road: PropTypes.object  // Too generic! ❌
};
```

**Why this is critical:**
- Any object passes validation, even `{foo: "bar"}`
- Missing required fields like `code` or `geometry` not detected
- Runtime errors when accessing undefined properties
- No IDE autocompletion or type hints

### Root Cause
Initial implementation used generic `PropTypes.object` as quick solution, without defining proper shape validation. This is a common anti-pattern in React development.

### Solution Implemented
Implemented detailed `PropTypes.shape()` validation with all required and optional fields:

```javascript
ActionButtons.propTypes = {
  road: PropTypes.shape({
    id: PropTypes.number.isRequired,
    code: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    geometry: PropTypes.oneOfType([
      PropTypes.string,  // WKT format from PostGIS
      PropTypes.object   // GeoJSON format
    ]).isRequired,
    start_lat: PropTypes.number,
    start_lon: PropTypes.number,
    distance_km: PropTypes.number,
    curve_count_total: PropTypes.number,
    surface: PropTypes.string,
    elevations: PropTypes.arrayOf(PropTypes.number),
  }),
};
```

**Improvements:**
- ✅ All required fields marked with `.isRequired`
- ✅ Geometry accepts both WKT string and GeoJSON object
- ✅ Optional fields explicitly defined
- ✅ Proper type checking for each field
- ✅ Better developer experience with IDE hints

### Files Changed
- ✅ `/frontend/src/components/Details/ActionButtons.jsx` (lines 162-175)

### Prevention Measures
1. **ESLint Rule:** Add `react/forbid-prop-types` to catch generic object/array props
2. **Code Review Checklist:** Verify PropTypes are specific, not generic
3. **TypeScript Migration (Future):** Consider migrating to TypeScript for compile-time type safety
4. **PropTypes Template:** Create reusable PropTypes shapes for common objects (road, marker, etc.)

### Testing
- ✅ Verified PropTypes validation catches invalid props
- ✅ IDE autocomplete now works correctly
- ✅ No console warnings with valid road objects
- ✅ Console warnings appear with invalid/missing fields

### Documentation
- Code comments explain WKT vs GeoJSON geometry formats
- PropTypes serve as inline documentation for component API

### Lessons Learned
1. **Generic PropTypes defeat the purpose** - Always define specific shapes
2. **PropTypes are self-documenting** - Clear shapes help other developers
3. **Early validation prevents runtime errors** - Catch issues in development, not production
4. **oneOfType is powerful** - Handles multiple valid formats elegantly

---

## 🐛 Bug #007: Memory Leak from Timeout Cleanup

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical
**Component:** Frontend (ActionButtons.jsx)
**Found By:** Code Review (code-reviewer agent)

### Problem
ActionButtons component set timeouts for feedback messages but did NOT clean them up on component unmount. This caused:
- **Memory leaks** - Timeouts continue after component unmounts
- **setState warnings** - "Can't perform a React state update on an unmounted component"
- **Unpredictable behavior** - Stale closures executing after unmount

**Problematic Code:**
```javascript
const showFeedback = (type, message) => {
  setFeedback({ type, message });
  setTimeout(() => {
    setFeedback(null);  // ❌ Runs even if component unmounts!
  }, 3000);
};
```

### Root Cause
1. **No refs for timeout IDs** - Timeouts created but not stored
2. **No cleanup on unmount** - Missing cleanup in useEffect return
3. **Multiple timeouts** - Both feedback and loading timeouts affected

### Solution Implemented
Added proper timeout cleanup with refs and useEffect:

```javascript
// 1. Create refs for timeout IDs
const feedbackTimeoutRef = useRef(null);
const loadingTimeoutRef = useRef(null);

// 2. Clear previous timeout before setting new one
const showFeedback = (type, message) => {
  setFeedback({ type, message });

  if (feedbackTimeoutRef.current) {
    clearTimeout(feedbackTimeoutRef.current);
  }

  feedbackTimeoutRef.current = setTimeout(() => {
    setFeedback(null);
    feedbackTimeoutRef.current = null;
  }, 3000);
};

// 3. Cleanup on unmount
useEffect(() => {
  return () => {
    if (feedbackTimeoutRef.current) clearTimeout(feedbackTimeoutRef.current);
    if (loadingTimeoutRef.current) clearTimeout(loadingTimeoutRef.current);
  };
}, []);
```

**Improvements:**
- ✅ Timeouts stored in refs (persist across renders)
- ✅ Clear previous timeout before setting new one (prevents overlapping)
- ✅ Cleanup on unmount (prevents memory leaks)
- ✅ No setState on unmounted component warnings

### Files Changed
- ✅ `/frontend/src/components/Details/ActionButtons.jsx` (lines 14-15, 21-33, 116-122)

### Prevention Measures
1. **ESLint Rule:** Enable `react-hooks/exhaustive-deps` to catch missing cleanup
2. **Code Review Checklist:** Verify all timeouts/intervals have cleanup
3. **useTimeout Hook (Future):** Create reusable hook that handles cleanup automatically
4. **Documentation:** Add comment explaining why refs are needed for timeouts

### Testing
- ✅ No console warnings when component unmounts
- ✅ Feedback messages clear correctly
- ✅ No memory leaks detected
- ✅ Multiple rapid button clicks handled correctly (timeouts reset)

### Documentation
- Code comments explain ref usage for timeout cleanup
- ESLint warnings would catch similar issues in other components

### Lessons Learned
1. **Always cleanup side effects** - Timeouts, intervals, subscriptions must be cleared
2. **Use refs for timeout IDs** - State doesn't persist correctly for cleanup
3. **Clear previous before setting new** - Prevents accumulation of pending timeouts
4. **Test component unmount** - Critical for catching memory leaks early

---

## 🐛 Bug #008: ESLint Error - Unused Variable (filteredRoads)

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical (Code Quality)
**Component:** Frontend (RoadList.jsx)
**Found By:** ESLint

### Problem
RoadList component destructured `filteredRoads` from useRoads hook but never used it, causing ESLint error:

```
'filteredRoads' is assigned a value but never used  no-unused-vars
```

### Root Cause
Component was refactored to use `groupedRoads` instead of `filteredRoads`, but the unused destructuring wasn't removed.

### Solution Implemented
Removed `filteredRoads` from destructuring statement:

```javascript
// Before:
const { loading, error, refetch, filteredRoads, groupedRoads, ... } = useRoads({...});

// After:
const { loading, error, refetch, groupedRoads, ... } = useRoads({...});
```

### Files Changed
- ✅ `/frontend/src/components/Sidebar/RoadList.jsx`

### Testing
- ✅ `npm run lint` passes with no errors
- ✅ Component functionality unchanged

---

## 🐛 Bug #009: ESLint Error - Unnecessary Regex Escape

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical (Code Quality)
**Component:** Frontend (gpxExport.js)
**Found By:** ESLint

### Problem
Unnecessary escape sequence in regex character class:

```javascript
const filename = `${road.code.replace(/[\/\\:*?"<>|]/g, '-')}.gpx`;
//                                            ↑ Unnecessary escape
```

**ESLint Error:**
```
Unnecessary escape character: \/  no-useless-escape
```

### Root Cause
Forward slash `/` does not need escaping inside character class `[...]` in JavaScript regex.

### Solution Implemented
Removed unnecessary backslash:

```javascript
const filename = `${road.code.replace(/[/\\:*?"<>|]/g, '-')}.gpx`;
```

### Files Changed
- ✅ `/frontend/src/utils/gpxExport.js` (line 219)

### Testing
- ✅ `npm run lint` passes
- ✅ Filename sanitization still works correctly

---

## 🐛 Bug #010: ESLint Error - Unused Catch Parameter

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical (Code Quality)
**Component:** Frontend (testConnection.js)
**Found By:** ESLint

### Problem
Catch block defined error parameter `_error` but never used it:

```javascript
} catch (_error) {
  // Error intentionally not used
  console.warn('⚠️  Geometry conversion test skipped (no data)');
}
```

**ESLint Error:**
```
'_error' is defined but never used  no-unused-vars
```

### Root Cause
Parameter prefixed with underscore to indicate "intentionally unused", but ESLint still flagged it. Better to omit the parameter entirely in JavaScript.

### Solution Implemented
Removed error parameter from catch block:

```javascript
} catch {
  // Test skipped if no data available
  console.warn('⚠️  Geometry conversion test skipped (no data)');
}
```

### Files Changed
- ✅ `/frontend/src/utils/testConnection.js` (line 108)

### Testing
- ✅ `npm run lint` passes
- ✅ Error handling unchanged

---

## 🐛 Bug #011: ESLint Error - Unused Variable (data)

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical (Code Quality)
**Component:** Frontend (testConnection.js)
**Found By:** ESLint

### Problem
`quickConnectionCheck` function destructured `data` from Supabase response but only used `error`:

```javascript
const { data, error } = await supabase.from('roads').select('count', {...});
// 'data' never used
```

### Root Cause
Function only needs to check if query succeeded (error is null), doesn't need the data itself.

### Solution Implemented
Removed `data` from destructuring:

```javascript
const { error } = await supabase.from('roads').select('count', {...});
```

### Files Changed
- ✅ `/frontend/src/utils/testConnection.js` (line 163)

### Testing
- ✅ `npm run lint` passes
- ✅ Connection check still works correctly

---

## 🐛 Bug #012: Missing Error Boundary Component

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical
**Component:** Frontend (App Architecture)
**Found By:** Code Review (code-reviewer agent)

### Problem
No React Error Boundary implemented. A single component error would crash the entire application with a white screen of death, providing zero user feedback.

**Consequences:**
- **Poor UX** - Users see blank white screen
- **No error info** - No way to know what went wrong
- **No recovery** - Users must manually refresh
- **Lost context** - Users lose their place in the app

### Root Cause
Initial MVP implementation didn't include error boundary. This is a common oversight in React apps.

### Solution Implemented
Created comprehensive ErrorBoundary component (173 lines) with:

**Features:**
1. **Error Catching** - getDerivedStateFromError catches all rendering errors
2. **Error Logging** - componentDidCatch logs to console (can integrate with error service)
3. **Graceful Fallback UI** - Beautiful error screen instead of white screen
4. **Reload Functionality** - User can reload app with button click
5. **Development Mode Details** - Shows error details and component stack in development
6. **Production Ready** - Clean error message without exposing internals

**Implementation:**
```javascript
// ErrorBoundary.jsx (Class Component)
class ErrorBoundary extends Component {
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('🚨 Error caught by Error Boundary:', error);
    console.error('📍 Component stack trace:', errorInfo.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return <FallbackUI />;  // Beautiful error screen
    }
    return this.props.children;
  }
}

// App.jsx - Wrapped entire app
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### Files Created
- ✅ `/frontend/src/components/ErrorBoundary.jsx` (173 lines)

### Files Modified
- ✅ `/frontend/src/App.jsx` - Wrapped app in ErrorBoundary

### Prevention Measures
1. **Error boundaries at multiple levels** - Consider boundaries around major sections
2. **Error reporting service** - Integrate with Sentry/LogRocket in production
3. **Component error tests** - Test error scenarios in component tests
4. **PropTypes validation** - Prevents many runtime errors before they happen

### Testing
- ✅ Simulated component errors (throw new Error in render)
- ✅ Error boundary catches and displays fallback UI
- ✅ Reload button works correctly
- ✅ Development mode shows error details
- ✅ Production mode hides sensitive info

### Documentation
- Component has extensive JSDoc comments
- Error boundary limitations documented (doesn't catch event handlers, async code)

### Lessons Learned
1. **Error boundaries are essential** - No production app should ship without them
2. **Class components still needed** - Error boundaries must be class components
3. **Fallback UI matters** - Users need helpful feedback, not blank screens
4. **Error logging is crucial** - Need visibility into production errors

---

## 🐛 Bug #013: Debug Console.log Statements in Production

**Status:** ✅ FIXED
**Date Found:** October 16, 2025
**Date Fixed:** October 16, 2025
**Severity:** 🔴 Critical
**Component:** Frontend (Multiple Components)
**Found By:** Code Review (code-reviewer agent)

### Problem
Multiple debug `console.log` statements throughout the codebase:
- **App.jsx** - "Road selected" log
- **RoadMap.jsx** - 8 debug logs (initialization, markers, route drawing)

**Why this is critical:**
- **Performance** - Console logging has performance overhead
- **Security** - May expose internal state/data in production
- **User experience** - Console filled with development noise
- **Best practices** - Production code should be clean

### Root Cause
Debug logs added during development but not removed before production readiness.

### Solution Implemented
Removed ALL debug `console.log` statements while keeping `console.error` and `console.warn` for debugging:

**Removed from App.jsx:**
- Line 11: "Road selected" log

**Removed from RoadMap.jsx:**
- Lines 48-51: Map initialization logs
- Line 72: Map loaded success log
- Line 206: No road selected log
- Line 210: Drawing route log
- Line 255: Route coordinates count log
- Lines 298, 310: Marker added logs
- Line 322: Map fitted bounds log
- Line 332: Retry initialization log

**Kept for production debugging:**
- ✅ All `console.error()` statements
- ✅ All `console.warn()` statements
- ✅ Validation error logging

### Files Changed
- ✅ `/frontend/src/App.jsx` (line 11)
- ✅ `/frontend/src/components/Map/RoadMap.jsx` (8 locations)

### Prevention Measures
1. **ESLint Rule** - Add `no-console` rule with `warn` level
2. **Pre-commit Hook** - Block commits with console.log
3. **Build Step** - Strip console.logs in production builds
4. **Code Review** - Check for debug logs before merge

### Testing
- ✅ Console output clean (only errors/warnings)
- ✅ All functionality unchanged
- ✅ No visual difference in behavior

### Documentation
- CLAUDE.md updated with production-ready code standards

### Lessons Learned
1. **Remove debug logs before production** - Essential for clean codebase
2. **Use proper logging library** - Consider using debug package or logging service
3. **ESLint can prevent this** - Automated checks catch these issues
4. **Code review is critical** - Human eyes catch what linters miss

---

## 🐛 Bug #014: Search Functionality Not Filtering Roads

**Status:** 🔴 OPEN
**Date Found:** October 16, 2025
**Severity:** 🟡 Medium
**Component:** Frontend (Sidebar/Search)
**Found By:** Chrome DevTools MCP Testing

### Problem
Search input accepts text but does NOT filter the road list. When typing "N222":
- **Expected:** Road list shows only N222
- **Actual:** All 12 roads remain visible
- **Results count:** Shows "12 roads available" instead of "1 result"

**Impact:** Users cannot search for specific roads, significantly reducing usability.

### Root Cause
**Investigation Status:** In Progress

**Code Review Findings:**
- ✅ Sidebar.jsx correctly debounces search query (300ms delay)
- ✅ Sidebar.jsx passes `debouncedSearchQuery` to RoadList
- ✅ useRoads hook has correct filtering logic
- ✅ useRoads returns `filteredRoads` and `groupedRoads`
- ✅ RoadList receives `searchQuery` prop

**Likely Causes:**
1. SearchBox component not triggering onChange correctly
2. useDebouncedValue hook timing issue
3. Event propagation problem with controlled input

**Files to Investigate:**
- `/frontend/src/components/Sidebar/SearchBox.jsx` - Input onChange handler
- `/frontend/src/hooks/useDebouncedValue.js` - Debounce implementation

### Solution (Proposed)
**Step 1:** Read SearchBox.jsx to verify onChange implementation
**Step 2:** Add debug logging to trace state changes
**Step 3:** Test with direct state update (bypass debounce)
**Step 4:** Fix identified issue

### Testing
- ⏳ Manual testing in progress
- ⏳ Need to verify controlled input with value + onChange
- ⏳ Test debounce timing

### Documentation
- ⏳ To be updated after fix implemented

### Lessons Learned
- TBD after fix

---

## 🐛 Bug #015: aria-hidden Accessibility Warning

**Status:** 🔴 OPEN
**Date Found:** October 16, 2025
**Severity:** 🟢 Low
**Component:** Frontend (Sidebar)
**Found By:** Chrome DevTools Console

### Problem
Browser accessibility warning:
```
Blocked aria-hidden on an element because its descendant retained focus.
The focus must not be hidden from assistive technology users.
```

**Affected Elements:**
- **Focused element:** Search input
- **Ancestor with aria-hidden:** Sidebar nav

**Impact:** Screen reader users may not be able to access focused input, violating WCAG AA accessibility standards.

### Root Cause
**Location:** `/frontend/src/components/Sidebar/Sidebar.jsx` line 96

```javascript
aria-hidden={!isOpen && 'md:hidden'}
```

**Problem:** Expression returns:
- `false` when isOpen = true ✅
- `'md:hidden'` (string) when isOpen = false ❌ (string is truthy!)

The string `'md:hidden'` is treated as `true` by aria-hidden, hiding the sidebar from assistive technology even on desktop where it's visible.

### Solution (Proposed)
**Option 1: Fix Boolean Logic**
```javascript
aria-hidden={!isOpen} // Simple boolean
```

**Option 2: Use Inert Attribute (Better)**
```javascript
{...(!isOpen && { inert: '' })}
```

**Why inert is better:**
- Prevents keyboard navigation into hidden content
- Removes from accessibility tree
- Blocks pointer events
- Single attribute handles all concerns

### Testing
- ⏳ To be tested after fix

### Prevention Measures
1. Add ESLint rule to detect incorrect aria-hidden usage
2. Use inert attribute instead of aria-hidden for hiding sections
3. Add accessibility tests (aXe, Lighthouse)
4. Run automated accessibility audits regularly

### Documentation
- ⏳ To be updated after fix

### Lessons Learned
- TBD after fix

---

## 📝 How to Add New Bugs

When you find a bug, add a new section using this template:

```markdown
## 🐛 Bug #XXX: [Short Description]

**Status:** 🔴 Open / 🟡 In Progress / ✅ Fixed
**Date Found:** YYYY-MM-DD
**Date Fixed:** YYYY-MM-DD (if fixed)
**Severity:** 🔴 Critical / 🟠 High / 🟡 Medium / 🟢 Low
**Component:** Frontend / Backend / Database / Scripts / etc
**Found By:** User Testing / Code Review / Automated Tests / etc

### Problem
[Clear description of what's wrong and its impact]

### Root Cause
[Why it happened - technical analysis]

### Solution Implemented
[How it was fixed - technical details]

### Files Changed
- List of modified files with brief description

### Prevention Measures
[How to prevent this in the future]

### Testing
[How you verified the fix works]

### Documentation
[Links to related docs, scripts, or detailed analysis]

### Lessons Learned
[Key takeaways from this bug]
```

**Remember to update the statistics table at the top!**

---

## 🏷️ Bug Categories

### By Component
- **Frontend:** 0 bugs
- **Backend:** 0 bugs
- **Database:** 2 bugs (Bug #001, #003 - Both Fixed)
- **Scripts:** 4 bugs (Bug #002, #003, #004, #005 - All Fixed)
- **Infrastructure:** 0 bugs
- **UI/UX:** 0 bugs

### By Severity
- **🔴 Critical:** 4 (Bug #001, #002, #003, #004 - All Fixed)
- **🟠 High:** 1 (Bug #005 - Fixed)
- **🟡 Medium:** 0
- **🟢 Low:** 0

### By Status
- **✅ Fixed:** 5
- **🟡 In Progress:** 0
- **🔴 Open:** 0

---

## ✅ Key Lessons Learned

### 1. Data Validation (Bug #001)
- **Lesson:** Always validate geographic coordinates at multiple layers
- **Application:** Implement validation in frontend, backend, and database
- **Prevention:** Use type systems, constraints, and validation libraries

### 2. Coordinate Formats (Bug #001)
- **Lesson:** Latitude and longitude order varies by context
- **Application:** Document expected format clearly (WKT: lon lat, DB: lat lon)
- **Prevention:** Add validation functions with clear error messages

### 3. Database Constraints (Bug #001)
- **Lesson:** Database constraints prevent bad data at the source
- **Application:** Use CHECK constraints for valid ranges
- **Prevention:** Add constraints during schema design, not as afterthought

### 4. Manual Data Entry (Bug #001)
- **Lesson:** Manual data entry is error-prone
- **Application:** Automate data processing with scripts
- **Prevention:** Always validate manually entered data

### 5. Geographic Bounding Boxes (Bug #002)
- **Lesson:** Wide bounding boxes return unexpected data from other regions
- **Application:** Use strict, region-specific bounding boxes for OSM queries
- **Prevention:** Validate ALL coordinates are within expected geographic area

### 6. Point Density Requirements (Bug #003)
- **Lesson:** Geometry point density is critical for realistic visualization
- **Application:** Enforce minimum 2.0 points/km for road geometries
- **Prevention:** Never use hardcoded SQL geometries - always fetch from OSM

### 7. Proper Data Pipeline (Bug #003)
- **Lesson:** Quick fixes with hardcoded data create technical debt
- **Application:** Always use proper ETL pipeline (process_roads.py)
- **Prevention:** SQL is for schema, not for data - use scripts for ETL

---

## 🔍 Bug Investigation Checklist

When investigating a bug, follow this checklist:

- [ ] **Reproduce the bug** reliably
- [ ] **Document** the exact steps to reproduce
- [ ] **Identify** which component(s) are affected
- [ ] **Analyze** the root cause (not just symptoms)
- [ ] **Check** if similar bugs exist elsewhere
- [ ] **Design** a solution that prevents recurrence
- [ ] **Implement** fix with tests
- [ ] **Verify** fix works in all scenarios
- [ ] **Document** in this registry
- [ ] **Update** statistics and categories

---

## 🚨 Severity Guidelines

### 🔴 Critical
- App crashes or becomes unusable
- Data corruption or loss
- Security vulnerabilities
- Incorrect core functionality (e.g., wrong locations on map)

**Action:** Fix immediately, stop other work

### 🟠 High
- Major feature broken
- Poor performance affecting usability
- Data inconsistencies (non-critical)
- Workaround exists but difficult

**Action:** Fix within 1-2 days

### 🟡 Medium
- Minor feature broken
- UI/UX issues
- Non-critical functionality affected
- Easy workaround available

**Action:** Fix within 1 week

### 🟢 Low
- Cosmetic issues
- Nice-to-have improvements
- Documentation errors
- Minor inconsistencies

**Action:** Fix when convenient

---

## 📚 Related Documentation

- **Development Guidelines:** `CLAUDE.md`
- **Product Requirements:** `docs/PRD.md`
- **Bug #001 Detailed Analysis:** `BUG_FIX_COORDINATES.md`
- **Database Schema:** `scripts/schema.sql`
- **Python Scripts:** `scripts/README.md`

---

## 🎯 Bug Prevention Best Practices

### Before Committing Code
1. ✅ Run all validation checks
2. ✅ Test edge cases
3. ✅ Check console for errors/warnings
4. ✅ Verify data integrity
5. ✅ Update documentation if needed

### During Code Review
1. ✅ Look for missing validation
2. ✅ Check error handling
3. ✅ Verify input sanitization
4. ✅ Review database constraints
5. ✅ Test failure scenarios

### Database Changes
1. ✅ Always add constraints for valid ranges
2. ✅ Validate data before migration
3. ✅ Test rollback procedures
4. ✅ Document schema changes

### External API Integration
1. ✅ Validate all API responses
2. ✅ Handle rate limits gracefully
3. ✅ Add retry logic for transient failures
4. ✅ Log errors for debugging

---

## 📈 Bug Resolution Timeline

| Bug # | Component | Severity | Time to Fix |
|-------|-----------|----------|-------------|
| #001  | Database/Frontend | Critical | Same day |
| #002  | Scripts (OSM) | Critical | Same day |
| #003  | Database/Scripts | Critical | Same day |
| #004  | Scripts (N2 Processing) | Critical | Same day |
| #005  | Scripts (N247 Processing) | High | Same day |

**Average Resolution Time:**
- Critical: Same day ✅ (target: same day) - 4/4 bugs fixed
- High: Same day ✅ (target: 1-2 days) - 1/1 bug fixed
- Medium: N/A (target: 1 week)
- Low: N/A (target: flexible)

---

## 🔄 Continuous Improvement

### Process Improvements from Bugs

**Bug #001 → Process Change:**
- ✅ Added mandatory coordinate validation
- ✅ Created validation.py module for reuse
- ✅ Documented coordinate format expectations
- ✅ Added database constraints to schema

**Bug #002 → Process Change:**
- ✅ Implemented strict bounding boxes for OSM queries
- ✅ Added geographic validation before caching
- ✅ Improved relation selection (best-match algorithm)
- ✅ Enhanced cache validation with metadata

**Bug #003 → Process Change:**
- ✅ Enforced density validation (≥ 2.0 points/km)
- ✅ Documented anti-pattern (no hardcoded geometries)
- ✅ Added N247 and N304 to roads_data.json
- ✅ Improved multi-segment road handling

### Future Improvements
- [ ] Add automated coordinate validation tests
- [ ] Create pre-commit hooks for data validation
- [ ] Add visual bounding box on map (debug mode)
- [ ] Implement coordinate auto-correction suggestions
- [ ] Add quality dashboard showing density metrics
- [ ] Automated testing of OSM fetch quality

---

**Remember:** Every bug is a learning opportunity. Document it well! 🚀

---

**Maintained by:** Development Team
**Last Review:** October 14, 2025
**Next Review:** When next bug is found or fixed
