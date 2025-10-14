# Architecture Decisions - Road Explorer Portugal

**Document Purpose**: Record key architectural decisions made during development
**Last Updated**: 2025-10-14

---

## Table of Contents

1. [OSM Data Fetching Strategy](#1-osm-data-fetching-strategy)
2. [Caching System](#2-caching-system)
3. [Long Roads Handling](#3-long-roads-handling)
4. [Bbox Filtering for International Roads](#4-bbox-filtering-for-international-roads)

---

## 1. OSM Data Fetching Strategy

### Decision
Use OpenStreetMap Overpass API with a 3-tier fallback strategy:
1. Check local cache (instant)
2. Try normal Overpass query (works for most roads)
3. Fallback to automatic segmentation on timeout (handles long roads)

### Context
- Portugal has ~50-80 roads to process (MVP scope)
- OSM Overpass API is free but has query time limits
- Some roads (like N2: 739km) timeout with single query
- Need reliable, maintainable solution without over-engineering

### Alternatives Considered

#### ❌ Geofabrik OSM Extracts + Local Processing
**Pros**: No API limits, full control, fast repeated processing
**Cons**: Overkill for <100 roads, complex setup, large downloads, maintenance burden
**Verdict**: TOO COMPLEX for project scope

#### ❌ Commercial OSM APIs
**Pros**: Higher limits, better SLAs
**Cons**: Costs money, vendor lock-in
**Verdict**: Unnecessary - free tier sufficient

#### ✅ Overpass API + Cache + Segmentation
**Pros**: Simple, free, handles all road types, maintainable
**Cons**: Initial processing slower (~1-2min per road)
**Verdict**: PERFECT fit for project scope

### Implementation Details

**Query Strategy**:
```python
# 1. Initial query: Relations first (major roads), then ways
relation["ref"="N 222"]["highway"](bbox);
way["ref"="N 222"]["highway"](bbox);

# 2. Alternative formats if no results
relation["ref"="EN 222"]["highway"](bbox);  # Portuguese format
relation["ref"="EN222"]["highway"](bbox);   # No space
```

**Why Relations First**:
- Major roads (N2, N222) stored as OSM relations
- Relations contain ordered list of way members
- Single relation = complete road geometry
- Avoids fragmentation issues with individual ways

### Consequences

**Positive**:
- ✅ Simple implementation (~300 lines)
- ✅ Works for all road types
- ✅ Zero cost
- ✅ Easy to maintain
- ✅ Respects API rate limits

**Negative**:
- ⏱️ Initial processing: 1-3min per road
- 🔄 Re-runs without cache hit API limits
- 📊 Requires monitoring of Overpass API status

---

## 2. Caching System

### Decision
Use simple JSON file-based caching with 30-day expiry.

### Context
- Road geometries rarely change (months/years between updates)
- Re-fetching same road wastes API quota
- Need to avoid rate limiting during development/testing
- Team size: 1 developer → simple solution preferred

### Implementation

```
scripts/cache/
├── .gitignore          # Ignore all cache files
├── N_2.json           # 2,321 GPS points, 728km
├── N_222.json         # Cached coordinates
└── N_339.json
```

**Cache Structure**:
```json
[
  [-7.924515, 40.6417689],
  [-7.924234, 40.6418123],
  ...
]
```

**Cache Lifecycle**:
1. **Check**: On `get_road_from_osm()`, check cache first
2. **Age**: If cache >30 days old, re-fetch
3. **Save**: After successful fetch, save to cache
4. **Invalidate**: Manual deletion if road updated in OSM

### Alternatives Considered

#### ❌ Database Caching
**Pros**: Centralized, queryable
**Cons**: Extra complexity, overkill for 50-80 files
**Verdict**: Too complex

#### ❌ Redis/Memcached
**Pros**: Fast, distributed
**Cons**: Extra dependency, infrastructure overhead
**Verdict**: Unnecessary for single developer

#### ✅ JSON Files
**Pros**: Simple, human-readable, no dependencies, easy debugging
**Cons**: Slower than DB (but fast enough - <10ms read)
**Verdict**: Perfect for scope

### Consequences

**Positive**:
- ✅ Zero dependencies
- ✅ Easy to inspect (`cat cache/N_2.json`)
- ✅ Easy to invalidate (`rm cache/N_2.json`)
- ✅ Git-ignored (no repo bloat)
- ✅ Works offline after first fetch

**Negative**:
- 📦 Cache files ~100-500KB each (~50MB total for all roads)
- 🔄 No automatic invalidation when OSM data changes

---

## 3. Long Roads Handling

### Decision
Implement automatic geographic segmentation for roads that timeout.

### Context
- N2 (739km, Portugal's Route 66) times out with single Overpass query
- Overpass timeout limit: 120 seconds
- Long roads have too many way members for single query

### Problem Example: N2
- **Length**: 739km (Chaves → Faro)
- **Way Members**: 97 ways in relation
- **GPS Points**: ~2,300 points
- **Single Query**: Times out after 120s

### Solution: Automatic Segmentation

```python
if query_timeout:
    # Divide bbox into N vertical segments
    segments = _divide_bbox_vertical(bbox, NUM_SEGMENTS=4)

    # Fetch each segment separately (60s timeout each)
    for segment_bbox in segments:
        coords = fetch_single_segment(road_ref, segment_bbox, timeout=60)
        all_coords.append(coords)

    # Merge intelligently
    merged = merge_way_segments(all_coords)
```

**Why 4 Segments**:
- N2 spans ~5° latitude (37° to 42°)
- Each segment: ~1.25° latitude (~139km)
- 60s timeout per segment: sufficient for ~150km roads
- Total time: 4 segments × 60s = ~4 minutes

### Alternatives Considered

#### ❌ Increase Timeout to 300s
**Pros**: Simple
**Cons**: Overpass API rejects timeouts >180s
**Verdict**: Not possible

#### ❌ Manual Road Splitting
**Pros**: Full control
**Cons**: Manual work for each long road, error-prone
**Verdict**: Not maintainable

#### ✅ Automatic Segmentation
**Pros**: Works automatically, no manual intervention, handles any length
**Cons**: Slightly slower (4min vs theoretical 2min)
**Verdict**: Best solution

### Consequences

**Positive**:
- ✅ Handles roads of any length
- ✅ Automatic (no manual intervention)
- ✅ Fallback only triggers on timeout (fast roads unaffected)

**Negative**:
- ⏱️ Longer processing time for very long roads (N2: ~4min)
- 🔀 Requires intelligent segment merging

---

## 4. Bbox Filtering for International Roads

### Decision
Filter OSM relations by bounding box to select only Portuguese roads.

### Context
- Multiple countries have roads with same reference (e.g., "N 2")
- OSM returns ALL matching relations globally without bbox filtering
- Need to select only the Portuguese instance

### Problem Discovered: N2 Multiple Matches

Query `relation["ref"="N 2"]["highway"]` returned:
1. **Relation 410047**: Kreisstraße N 2 (Germany) - 1.81 km
2. **Relation 555692**: N 2 (Romania?) - 81.91 km
3. **Relation 4187060**: N 2 (Portugal) - 728.47 km ✅ CORRECT
4. **Relation 4828569**: N 2 (other) - 5,225.73 km

Without filtering, all 4 were merged → 63,018 km ❌

### Solution: Bbox-based Relation Selection

```python
def extract_coordinates_from_response(data, bbox):
    relations = [e for e in data['elements'] if e['type'] == 'relation']

    if len(relations) > 1 and bbox:
        # Select relation with most members within bbox
        best_relation = None
        best_member_count = 0

        for relation in relations:
            valid_members = count_members_within_bbox(relation, bbox)
            if valid_members > best_member_count:
                best_member_count = valid_members
                best_relation = relation

        return best_relation  # Only the Portuguese one
```

**Portugal Bounding Box**:
```python
bbox = (37.0, -9.5, 42.2, -6.2)  # (south, west, north, east)
# Covers Continental Portugal only
```

### Alternatives Considered

#### ❌ Query by Relation ID
**Pros**: Exact match, no ambiguity
**Cons**: Requires manual mapping (road_ref → relation_id), not maintainable
**Verdict**: Not scalable

#### ❌ Filter by Country Tag
**Pros**: Semantic filtering
**Cons**: Not all relations have country tag, inconsistent
**Verdict**: Unreliable

#### ✅ Bbox Filtering
**Pros**: Geographic filter, works universally, deterministic
**Cons**: Requires knowing Portugal bbox (trivial)
**Verdict**: Robust solution

### Consequences

**Positive**:
- ✅ Correctly selects Portuguese roads
- ✅ Works for all road types
- ✅ No manual mapping needed
- ✅ Geographically intuitive

**Negative**:
- 🌍 Border roads might match multiple countries (rare)
- 📊 Requires counting members (slight performance cost)

---

## Summary Table

| Decision | Choice | Rationale | Status |
|----------|--------|-----------|--------|
| Data Source | OSM Overpass API | Free, comprehensive, maintained | ✅ Implemented |
| Caching | JSON files (30-day) | Simple, no dependencies, sufficient | ✅ Implemented |
| Long Roads | Auto-segmentation | Handles any length, automatic | ✅ Implemented |
| Bbox Filtering | Member counting | Robust, no manual mapping | ✅ Implemented |
| Query Strategy | Relations-first | Major roads are relations | ✅ Implemented |

---

## Future Considerations

### When to Revisit

1. **If processing >500 roads**: Consider Geofabrik + local processing
2. **If OSM data changes frequently**: Add webhook-based cache invalidation
3. **If team grows >3 developers**: Consider centralized cache (DB/Redis)
4. **If API rate limiting becomes issue**: Implement exponential backoff

### Monitoring

- Track Overpass API success rate
- Monitor average processing time per road
- Watch for segmentation fallback frequency
- Check cache hit rate

---

**Document Maintainer**: Claude Code
**Review Schedule**: After adding Madeira/Açores roads (~Q1 2026)
