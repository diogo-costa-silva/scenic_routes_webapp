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

**Ready to process roads? Run:** `python process_roads.py`
