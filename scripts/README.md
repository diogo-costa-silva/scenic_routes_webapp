# 🐍 Python Data Processing Scripts

This directory contains Python scripts for processing road data and populating the Supabase database.

## ⚠️ Prerequisites

### 1. UV Package Manager (MANDATORY)

**This project REQUIRES [UV](https://github.com/astral-sh/uv)** - an extremely fast Python package installer written in Rust.

#### Install UV

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Via Homebrew (macOS):**
```bash
brew install uv
```

#### Verify Installation
```bash
uv --version
# Should output: uv 0.x.x
```

### 2. Python 3.11+

UV will handle Python versions, but ensure you have Python 3.11 or higher available:
```bash
python --version
# or
python3 --version
```

---

## 🚀 Quick Start

### Step 1: Setup Virtual Environment

```bash
# Navigate to scripts directory
cd scripts/

# Create virtual environment with UV
uv venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Your prompt should now show: (.venv)
```

### Step 2: Install Dependencies

```bash
# Install all dependencies with UV (MUCH faster than pip!)
uv pip install -r requirements.txt

# Verify installation
python -c "import requests, geopy, supabase; print('✅ All packages installed')"
```

### Step 3: Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Add your API keys:
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key_here
MAPBOX_TOKEN=pk.your_mapbox_token_here
```

⚠️ **Important:** Use the **SERVICE ROLE KEY** from Supabase, not the anon key!

---

## 📁 File Structure

```
scripts/
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .env                    # Your credentials (DO NOT COMMIT)
│
├── schema.sql              # Database schema (run in Supabase)
├── test_data.sql           # Sample data for testing
│
├── roads_data.json         # Road definitions for processing
│
├── osm_utils.py            # OSM data fetching
├── metrics.py              # Distance/curve calculations
├── elevation.py            # Elevation data from Mapbox
└── process_roads.py        # Main processing script
```

---

## 🗄️ Database Setup

### 1. Create Supabase Project

1. Go to [supabase.com](https://app.supabase.com/)
2. Create a new project
3. Wait for database to initialize (~2 minutes)

### 2. Run Schema Script

1. In Supabase dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire contents of `schema.sql`
4. Paste and click **Run**
5. Verify: Check **Table Editor** → should see `roads` table

### 3. (Optional) Add Test Data

1. In SQL Editor, create a new query
2. Copy contents of `test_data.sql`
3. Paste and click **Run**
4. Verify: `SELECT * FROM roads` should show 3 sample roads

### 4. Get API Credentials

1. Go to **Settings** → **API**
2. Copy:
   - **URL** → `SUPABASE_URL`
   - **service_role** key (NOT anon!) → `SUPABASE_KEY`
3. Add to `.env` file

---

## 🛠️ Usage

### Test Database Connection

**IMPORTANT:** Always test your connection first!

```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Run connection test
python test_connection.py
```

This comprehensive test verifies:
- ✅ Environment variables configured
- ✅ Supabase connection works
- ✅ PostGIS extension enabled
- ✅ Roads table accessible
- ✅ Geometry functions work (ST_AsText, ST_GeomFromText)
- ✅ Region filtering works

**Expected Output:**
```
==================================================================
  🧪 Road Explorer Portugal - Database Connection Test
==================================================================

==================================================================
  1. Testing Environment Variables
==================================================================
✅ SUPABASE_URL configured
✅ SUPABASE_KEY configured
✅ MAPBOX_TOKEN configured

==================================================================
  2. Testing Supabase Connection
==================================================================
✅ Supabase client created

[... more tests ...]

📊 Tests passed: 7/7
🎉 All tests passed! Your Supabase setup is working correctly.
```

### Process Roads

```bash
# After connection test passes
python process_roads.py
```

**Current Status:** ⚠️ Scripts are **placeholder implementations**
- Structure is complete
- Ready for implementation
- TODOs marked in each file

### Test Individual Modules

```bash
# Test OSM utilities
python osm_utils.py

# Test metrics calculator
python metrics.py

# Test elevation fetcher
python elevation.py
```

---

## 📝 Editing Road Definitions

Edit `roads_data.json` to add/modify roads:

```json
[
  {
    "code": "N222",
    "name": "Peso da Régua → Pinhão",
    "region": "Continental",
    "osm_ref": "N 222",
    "description": "Beautiful Douro Valley road",
    "start_point_name": "Peso da Régua",
    "end_point_name": "Pinhão",
    "surface": "asphalt",
    "category": "River Valley"
  }
]
```

**Required fields:**
- `code` - Road code (e.g., "N222")
- `name` - Road name with start → end
- `region` - "Continental", "Madeira", or "Açores"
- `osm_ref` - OSM reference tag (usually with space: "N 222")

**Optional fields:**
- `description` - Brief description
- `start_point_name` / `end_point_name` - Location names
- `surface` - "asphalt", "gravel", "mixed"
- `category` - "Serra", "Costa", "Montanha", etc.

---

## 🔧 Common UV Commands

```bash
# Create virtual environment
uv venv

# Install package
uv pip install package-name

# Install from requirements.txt
uv pip install -r requirements.txt

# Update all packages
uv pip install -U -r requirements.txt

# List installed packages
uv pip list

# Uninstall package
uv pip uninstall package-name

# Generate requirements.txt from installed packages
uv pip freeze > requirements.txt
```

---

## 🐛 Troubleshooting

### UV not found after installation

**Solution:**
```bash
# Restart terminal or reload shell config
source ~/.bashrc  # or ~/.zshrc

# Or use absolute path
~/.cargo/bin/uv --version
```

### Virtual environment won't activate

**Solution:**
```bash
# Make sure you're in scripts/ directory
cd scripts/

# Use absolute path
source "$(pwd)/.venv/bin/activate"

# Windows: Check execution policy
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Missing Supabase credentials

**Solution:**
```bash
# Check if .env exists
ls -la .env

# If not, copy template
cp .env.example .env

# Edit with your credentials
nano .env
```

### Import errors

**Solution:**
```bash
# Reinstall dependencies
uv pip install -r requirements.txt

# Verify packages
python -c "import requests; import geopy; import supabase"
```

---

## 🚦 Next Steps

1. ✅ Complete this setup guide
2. ⏳ Implement OSM data fetching in `osm_utils.py`
3. ⏳ Implement metrics calculation in `metrics.py`
4. ⏳ Implement elevation fetching in `elevation.py`
5. ⏳ Complete `process_roads.py` integration
6. ⏳ Process 25-30 roads for MVP
7. ⏳ Validate data in Supabase

---

## 📚 Additional Resources

- **UV Documentation:** https://github.com/astral-sh/uv
- **Supabase Docs:** https://supabase.com/docs
- **PostGIS Functions:** https://postgis.net/docs/
- **Mapbox Tilequery API:** https://docs.mapbox.com/api/maps/tilequery/
- **Overpass API:** https://wiki.openstreetmap.org/wiki/Overpass_API

---

## ✅ Checklist

Before running scripts, ensure:

- [ ] UV installed and working (`uv --version`)
- [ ] Virtual environment created (`uv venv`)
- [ ] Virtual environment activated (see `(.venv)` in prompt)
- [ ] Dependencies installed (`uv pip install -r requirements.txt`)
- [ ] `.env` file created with real credentials
- [ ] Supabase project created
- [ ] Database schema applied (`schema.sql`)
- [ ] Test data loaded (optional, `test_data.sql`)

---

## 🏔️ Handling Long Roads

### N2 (Portugal's Route 66) - Special Case

**N2 is 739km long** and requires special handling:

#### Automatic Segmentation
- Overpass API times out on single query for very long roads
- Solution: Automatic 4-segment fetch (implemented in `osm_utils.py`)
- Each segment processed separately, then merged intelligently

#### Expected Behavior
```
📡 Fetching road data for: N 2
   ⚠️  Timeout occurred - road may be very long (>100km)
   🔄 Falling back to segmentation strategy...
   🔄 Using segmentation strategy (4 segments)...
   📍 Processing segment 1/4...
      ✅ Found 580 points in segment 1
   📍 Processing segment 2/4...
      ✅ Found 590 points in segment 2
   [...]
   🔗 Merging 4 segments...
   ✅ Segmentation complete: 2321 total points
```

#### Processing Time
- **N2**: ~5-7 minutes total
  - OSM fetch (4 segments): ~3-4 minutes
  - Elevation calculation: ~2-3 minutes
- **Normal roads (<100km)**: 30-90 seconds

---

## 💾 Cache System

### Purpose
- **Avoid re-fetching** OSM data for roads that rarely change
- **Respect API rate limits** during development/testing
- **Speed up processing**: Cache hit = instant (10ms vs 30s)

### Location
```
scripts/cache/
├── .gitignore          # All cache files ignored by git
├── N_2.json           # N2: 2,321 GPS points
├── N_222.json         # N222: cached coordinates
└── N_339.json         # N339: cached coordinates
```

### Cache Expiry
- **Default**: 30 days
- After 30 days, data is automatically re-fetched from OSM
- Manual invalidation: `rm cache/ROAD_NAME.json`

### Cache Format (JSON)
```json
[
  [-7.924515, 40.6417689],
  [-7.924234, 40.6418123],
  ...
]
```

### Manual Cache Management
```bash
# Clear all cache
rm cache/*.json

# Clear specific road
rm cache/N_222.json

# View cache
cat cache/N_2.json | head -n 5
```

---

## 🌍 OSM Query Strategy

### Multi-Tier Fallback
1. **Check cache** (instant if available)
2. **Query OSM** (works for most roads)
3. **Automatic segmentation** (fallback for timeouts)

### Bbox Filtering
- Portugal bbox: `(37.0, -9.5, 42.2, -6.2)` (south, west, north, east)
- Filters international roads with same reference
- Example: "N 2" exists in multiple countries, bbox selects Portugal's instance

### Relation vs Ways
- **Major roads** (N2, N222): Stored as OSM relations ✅
- **Minor roads**: May be individual ways
- Query tries both, prefers relations

---

## 📊 Performance Notes

### API Usage
**OpenStreetMap Overpass**:
- Free, unlimited (with rate limiting)
- 1-second delay between requests (respectful)
- Cache avoids repeated queries

**Mapbox Tilequery**:
- Free tier: 100,000 requests/month
- Sampling: Every 10th point (10x reduction)
- Typical road: 100-300 API calls

### Processing Estimates
| Road Length | GPS Points | OSM Time | Elevation Time | Total |
|------------|-----------|----------|---------------|-------|
| 20-50km | ~1,000 | 10-30s | 5-10s | ~30-60s |
| 50-200km | ~3,000 | 30-60s | 15-30s | ~1-3min |
| 700km+ | ~2,300 | 3-4min | 2-3min | ~5-7min |

---

## 🔍 Troubleshooting

### "Rate limited by Overpass API"
**Cause**: Too many queries in short time
**Solution**:
- Wait 5-10 minutes
- Use cached data (won't hit API)
- Increase `RATE_LIMIT_DELAY` in `osm_utils.py`

### "No coordinates found for road"
**Possible causes**:
1. Wrong OSM reference format
   - Try: "N 222", "EN 222", "N222"
2. Road not in OpenStreetMap database
3. Bbox doesn't include road location

**Debug**:
```python
from osm_utils import get_road_from_osm
coords = get_road_from_osm("N 222")  # Try variations
```

### "Timeout occurred"
**Expected for long roads** (>100km)
- Automatic segmentation will trigger
- Not an error, just slower processing

---

**Ready to process roads? Run:** `python process_roads.py`
