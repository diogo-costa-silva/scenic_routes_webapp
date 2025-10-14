# 🏍️ Road Explorer Portugal

An interactive web application showcasing the best motorcycle roads in Portugal with detailed metrics including curves, elevation, distance, and road surface quality.

## 🎯 Project Overview

**Road Explorer Portugal** helps motorcyclists discover and plan rides on spectacular Portuguese roads across Continental Portugal, Madeira, and the Azores. The app provides:

- Interactive map visualization of curated motorcycle routes
- Detailed metrics (curves, elevation gain, distance, road surface)
- GPX export for GPS navigation
- Direct integration with Google Maps
- Mobile-first responsive design

## 🛠️ Technology Stack

### Frontend
- **React 18+** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Mapbox GL JS** - Interactive maps
- **Supabase** - Backend and database

### Backend & Data
- **Supabase (PostgreSQL + PostGIS)** - Database with geospatial support
- **Python 3.11+** - Data processing scripts
- **OpenStreetMap** - Road geometry data
- **Mapbox Elevation API** - Elevation metrics

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and **UV** (for data processing scripts)
- Mapbox account (free tier)
- Supabase account (free tier)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd sr_v1
   ```

2. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   VITE_MAPBOX_TOKEN=pk.your_mapbox_token_here
   VITE_SUPABASE_URL=https://your-project.supabase.co
   VITE_SUPABASE_ANON_KEY=your_anon_key_here
   ```

   **How to get API keys:**
   - **Mapbox Token**: Sign up at [mapbox.com](https://account.mapbox.com/), create a new token with default public scopes
   - **Supabase**: Create a project at [supabase.com](https://app.supabase.com/), find credentials in Settings → API

4. **Start development server**
   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173`

## 🗄️ Database Setup

### 1. Install UV (Python Package Manager)

**UV is REQUIRED** for Python data processing scripts.

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Verify installation:**
```bash
uv --version
```

### 2. Create Supabase Project

1. Go to [supabase.com](https://app.supabase.com/) and create a new project
2. Wait for database initialization (~2 minutes)
3. Note your project URL and keys from **Settings → API**

### 3. Run Database Schema

1. Open **Supabase SQL Editor**
2. Copy the contents of `scripts/schema.sql`
3. Paste and click **Run**
4. Verify the `roads` table was created in **Table Editor**

### 4. (Optional) Load Test Data

To test with sample roads:

1. In Supabase SQL Editor, create a new query
2. Copy contents of `scripts/test_data.sql`
3. Paste and click **Run**
4. Verify: Run `SELECT * FROM roads` - should show 3 sample roads

### 5. Setup Python Environment

```bash
# Navigate to scripts directory
cd scripts/

# Create virtual environment with UV
uv venv

# Activate environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies (FAST with UV!)
uv pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env with your Supabase and Mapbox credentials
```

### 6. Process Road Data

```bash
# With virtual environment activated
python process_roads.py
```

**Note:** Python scripts are currently **placeholder implementations**. See [scripts/README.md](scripts/README.md) for full setup guide.

## 📁 Project Structure

```
sr_v1/
├── frontend/                    # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map/            # Map-related components
│   │   │   ├── Sidebar/        # Road list sidebar
│   │   │   ├── Details/        # Road details panel
│   │   │   └── UI/             # Reusable UI components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── utils/              # Helper functions
│   │   ├── services/           # API services (Supabase)
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env.example            # Environment variables template
│   └── package.json
│
├── scripts/                     # Python data processing scripts
│   ├── README.md               # Python setup guide
│   ├── schema.sql              # Database schema
│   ├── test_data.sql           # Sample data
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example            # Python env template
│   ├── roads_data.json         # Road definitions
│   ├── osm_utils.py            # OSM data fetching
│   ├── metrics.py              # Metrics calculation
│   ├── elevation.py            # Elevation data
│   └── process_roads.py        # Main processing script
│
├── docs/
│   └── PRD.md                  # Product Requirements Document
│
└── README.md                    # This file
```

## 🎨 Design System

### Colors
- **Primary**: `#FF6B35` (Orange) - Roads and primary actions
- **Secondary**: `#004E89` (Blue) - Headers and secondary elements
- **Accent**: `#10B981` (Green) - Start points
- **Danger**: `#EF4444` (Red) - End points

### Regions
- **Continental**: `#3B82F6` (Blue)
- **Madeira**: `#F59E0B` (Orange)
- **Azores**: `#8B5CF6` (Purple)

## 🗺️ Features (MVP 1.0)

- [x] Interactive Mapbox map centered on Portugal
- [x] Project foundation with React + Vite
- [x] Tailwind CSS design system
- [x] Supabase integration ready
- [x] Database schema with PostGIS
- [x] Python data processing scripts (placeholders)
- [ ] Road list sidebar with search
- [ ] Animated route visualization
- [ ] Detailed metrics panel
- [ ] GPX export functionality
- [ ] Google Maps integration
- [ ] Region filtering
- [ ] Mobile responsive design

## 🧪 Development

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Code Style

- All code, comments, and documentation in **English**
- Follow React best practices
- Use functional components with hooks
- Tailwind CSS for all styling
- Descriptive variable and function names

## 🚢 Deployment

The application is designed to be deployed on:
- **Frontend**: Vercel (recommended) or Netlify
- **Database**: Supabase (included in setup)

## 📚 Documentation

For detailed product requirements, architecture, and implementation guidelines, see:
- [PRD.md](docs/PRD.md) - Complete product requirements document
- [CLAUDE.md](CLAUDE.md) - Development guidelines and workflow

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome!

## 📄 License

This project is private and proprietary.

## 🎯 Roadmap

### MVP 1.0 (Current)
- Basic map visualization
- Road database integration
- Core metrics display

### MVP 1.5
- Photo galleries
- Social sharing

### MVP 2.0
- User authentication
- Reviews and comments
- Favorites system

### MVP 3.0
- Mobile app
- Offline navigation
- GPS tracking

---

**Built with ❤️ for the Portuguese motorcycling community**
