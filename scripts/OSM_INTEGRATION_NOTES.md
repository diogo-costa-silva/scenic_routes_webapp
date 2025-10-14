# 🗺️ OpenStreetMap Integration - Implementation Notes

**Date:** October 14, 2025
**Status:** ✅ Implemented and Tested
**Module:** `osm_utils.py`

---

## 📋 Summary

Successfully implemented OpenStreetMap data fetching for Portuguese roads using the Overpass API. The implementation includes intelligent ref format conversion, segment merging, and comprehensive error handling.

---

## 🔑 Key Findings

### 1. **Portuguese Road Tagging in OSM**

Portuguese roads use **"EN" prefix** (Estrada Nacional) in OpenStreetMap, NOT "N":

| Real Life | OSM Tag |
|-----------|---------|
| N222      | **EN 222** |
| N2        | **EN 2** |
| N 222     | **EN 222** |

**Other Road Types:**
- **EM XXX** - Estrada Municipal (Municipal roads)
- **ER XXX** - Estrada Regional (Regional roads)

### 2. **Automatic Conversion**

The implementation automatically converts "N" to "EN":
- Input: `get_road_from_osm("N 222")`
- Tries: "N 222", "N222", "N-222"
- Falls back to: **"EN 222", "EN222", "EN-222"** ✅
- Result: Successfully finds the road

### 3. **Road Data Characteristics**

**EN 222 Example:**
- ✅ Found 7,849 coordinates
- ⚠️ 401 segments (highly fragmented)
- 📍 Covers multiple sections across Portugal
- 📏 Returns ALL EN 222 segments, not just Douro Valley section

**Why Fragmentation?**
- OSM roads are split at intersections
- Different segments have different properties
- Multiple "EN 222" designations may exist in different regions

---

## ✅ Implementation Features

### Core Functions

1. **`get_road_from_osm(road_ref, bbox=None)`**
   - Fetches road geometry from OSM
   - Auto-converts N→EN for Portuguese roads
   - Tries multiple ref formats automatically
   - Returns (longitude, latitude) coordinate list

2. **`query_overpass_api(query)`**
   - HTTP POST to Overpass API
   - 30-second timeout
   - Rate limiting (1 second delay)
   - Error handling (429, 504, timeouts)

3. **`extract_coordinates_from_response(data)`**
   - Parses OSM JSON response
   - Handles ways and relations
   - Extracts geometry coordinates

4. **`merge_way_segments(segments)`**
   - Intelligently connects road segments
   - Matches endpoints
   - Handles reversed segments
   - Warns about disconnected segments

5. **`validate_road_ref(road_ref)`**
   - Basic format validation
   - Non-empty check
   - Minimum length check

### Error Handling

✅ **Network Errors:**
- Connection failures
- Timeouts (30s)
- Rate limiting (429)
- Gateway timeouts (504)

✅ **Data Errors:**
- Road not found (returns empty list)
- Invalid JSON responses
- Missing geometry data

✅ **Edge Cases:**
- Invalid road references
- Empty responses
- Disconnected segments

---

## 📊 Test Results

### Test 1: N→EN Conversion ✅
```bash
Input: "N 222"
Result: Automatically tries "EN 222" → Success
Coordinates: 7,849 points
Status: ✅ PASSED
```

### Test 2: EN 222 Direct ✅
```bash
Input: "EN 222"
Result: Found immediately
Coordinates: 7,849 points
Bounds: Within Portugal (✅)
Status: ✅ PASSED
```

### Test 3: Error Handling ✅
```bash
Input: "INVALID_ROAD_999"
Result: Returns empty list (no exception)
Status: ✅ PASSED
```

---

## 🚨 Important Notes

### 1. **Bounding Box Requirement**

**Default:** Portugal bounds (36°N to 43°N, -10°W to -6°W)

For specific road sections, provide tighter bbox:
```python
# Douro Valley only
douro_bbox = (40.9, -8.0, 41.3, -7.4)
coords = get_road_from_osm("EN 222", bbox=douro_bbox)
```

### 2. **Multiple Road Sections**

Some road designations (e.g., EN 222) appear in multiple locations:
- **Solution:** Use regional bounding boxes
- **Alternative:** Filter coordinates by proximity to start/end points

### 3. **Segment Fragmentation**

OSM roads are split into many segments:
- Normal behavior at intersections
- Merging algorithm handles most cases
- Some disconnected segments may remain (warnings shown)

### 4. **Rate Limiting**

Overpass API guidelines:
- ✅ 1-second delay between requests (implemented)
- ✅ 30-second timeout (implemented)
- ⚠️ Avoid excessive parallel requests
- ⚠️ Respect fair use policy

---

## 📖 Usage Examples

### Basic Usage
```python
from osm_utils import get_road_from_osm

# Fetch N222 (automatically converts to EN 222)
coords = get_road_from_osm("N 222")
print(f"Found {len(coords)} coordinates")
# Output: Found 7849 coordinates
```

### With Custom Bounding Box
```python
# Only search in Douro Valley region
douro_bbox = (40.9, -8.0, 41.3, -7.4)
coords = get_road_from_osm("EN 222", bbox=douro_bbox)
```

### Error Handling
```python
try:
    coords = get_road_from_osm("N2")
    if coords:
        print(f"Success: {len(coords)} points")
    else:
        print("Road not found")
except Exception as e:
    print(f"Error: {e}")
```

---

## 🔄 Next Steps

### Immediate
1. ✅ Implement `metrics.py` (distance, curves calculation)
2. ✅ Implement `elevation.py` (Mapbox elevation data)
3. ✅ Complete `process_roads.py` (full pipeline)

### Integration
- Use `get_road_from_osm()` in data processing pipeline
- Add road sections to `roads_data.json` with specific bboxes
- Process 25-30 roads for MVP

### Optimization
- Consider caching frequently requested roads
- Add progress bars for long-running queries
- Implement batch processing for multiple roads

---

## 🐛 Known Limitations

1. **Global Road Names**
   - Returns ALL roads with matching designation
   - Solution: Use restrictive bounding boxes

2. **Segment Disconnection**
   - Some segments can't be automatically connected
   - Acceptable for most use cases
   - Manual review recommended for critical roads

3. **API Rate Limits**
   - Overpass API has fair use policy
   - Implement delays between requests
   - Consider local Overpass instance for heavy use

4. **Timeout on Very Long Roads**
   - EN 2 (739km) may timeout
   - Solution: Query by sections with smaller bboxes

---

## ✅ Success Criteria Met

- [x] Fetch road data from OSM ✅
- [x] Handle Portuguese road formats (N→EN) ✅
- [x] Try multiple ref variations ✅
- [x] Merge road segments ✅
- [x] Error handling ✅
- [x] Coordinate validation ✅
- [x] Rate limiting ✅
- [x] PEP 8 compliance ✅
- [x] Comprehensive docstrings ✅
- [x] Type hints ✅

---

## 📚 References

- **Overpass API:** https://overpass-api.de/
- **Overpass QL Guide:** https://wiki.openstreetmap.org/wiki/Overpass_API/Language_Guide
- **OSM Highway Tags:** https://wiki.openstreetmap.org/wiki/Key:highway
- **Portuguese Road Network:** https://wiki.openstreetmap.org/wiki/WikiProject_Portugal/Roads

---

**Implementation Complete!** ✅
Module ready for integration into data processing pipeline.
