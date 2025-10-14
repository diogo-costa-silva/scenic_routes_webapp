# 🏍️ Road Explorer Portugal - Frontend

Interactive web application showcasing the best motorcycle roads in Portugal with detailed metrics.

## 🚀 Tech Stack

- **React 19** - UI framework
- **Vite 7** - Build tool and dev server
- **Tailwind CSS v4** - CSS-first styling (Rust-powered)
- **Mapbox GL JS 3** - Interactive maps
- **Supabase** - Backend and database
- **React Map GL** - React wrapper for Mapbox

## 📦 Installation

```bash
# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Add your credentials to .env
# - VITE_MAPBOX_TOKEN (from https://account.mapbox.com/)
# - VITE_SUPABASE_URL (from Supabase project)
# - VITE_SUPABASE_ANON_KEY (from Supabase project)
```

## 🛠️ Development

```bash
# Start development server (http://localhost:5173)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

## 📁 Project Structure

```
frontend/
├── public/              # Static assets
│   ├── favicon.svg      # Motorcycle icon
│   └── site.webmanifest # PWA manifest
├── src/
│   ├── components/      # React components
│   │   └── Map/         # Map-related components
│   │       └── RoadMap.jsx
│   ├── services/        # API clients
│   │   └── api.js       # Supabase client & queries
│   ├── hooks/           # Custom React hooks (future)
│   ├── utils/           # Helper functions (future)
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # React entry point
│   └── index.css        # Global styles + Tailwind config
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind content paths
└── postcss.config.js    # PostCSS with Tailwind v4 plugin
```

## 🎨 Tailwind CSS v4 (CSS-First)

This project uses **Tailwind CSS v4**, which uses CSS for theme configuration instead of JavaScript:

```css
/* src/index.css */
@theme {
  --color-primary: #FF6B35;        /* Orange - roads */
  --color-secondary: #004E89;      /* Blue - maps */
  --color-accent: #10B981;         /* Green - start */
  --color-danger: #EF4444;         /* Red - end */
  --color-region-continental: #3B82F6;
  --color-region-madeira: #F59E0B;
  --color-region-acores: #8B5CF6;
}
```

Use custom colors in components:
```jsx
<div className="bg-primary text-white">
<button className="bg-region-continental">
```

## 🗺️ Mapbox Integration

The RoadMap component includes:
- ✅ Centered on Portugal (39.5°N, 8.0°W)
- ✅ Navigation controls (zoom, bearing)
- ✅ Comprehensive error handling (6 error types)
- ✅ Loading states with retry mechanism
- ✅ 10-second timeout protection

## 📡 Supabase API

API functions in `src/services/api.js`:

```javascript
// Fetch all roads
const { data, error } = await fetchRoads();

// Fetch single road by ID
const { data, error } = await fetchRoadById(roadId);

// Fetch roads by region
const { data, error } = await fetchRoadsByRegion('Continental');
```

## 🔧 Environment Variables

Required variables in `.env`:

```bash
VITE_MAPBOX_TOKEN=pk.xxxxx           # Mapbox public token
VITE_SUPABASE_URL=https://xxx.supabase.co
VITE_SUPABASE_ANON_KEY=xxxxx         # Supabase anonymous key
```

> **Note:** All frontend env vars must start with `VITE_` prefix.

## 🚦 Development Workflow

1. Make changes to components
2. Hot Module Replacement (HMR) updates browser instantly
3. Check browser console for errors
4. Test on different screen sizes (responsive)

## 📱 Responsive Design

- **Mobile-first** approach
- Breakpoints: `sm:` (640px), `md:` (768px), `lg:` (1024px), `xl:` (1280px)
- Tested on mobile, tablet, and desktop

## 🐛 Troubleshooting

### Map not loading
- Check `VITE_MAPBOX_TOKEN` is set correctly
- Token must be public (starts with `pk.`)
- Check browser console for API errors

### Supabase connection fails
- Verify `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`
- Check CORS settings in Supabase dashboard
- Ensure RLS policies allow anonymous reads

### Build errors
- Clear node_modules: `rm -rf node_modules && npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check Node.js version: `node --version` (v18+ required)

## 📚 Documentation

- [Project PRD](../docs/PRD.md) - Product requirements
- [Main README](../README.md) - Project overview
- [Mapbox GL JS Docs](https://docs.mapbox.com/mapbox-gl-js/)
- [Tailwind CSS v4 Docs](https://tailwindcss.com/docs)
- [Supabase Docs](https://supabase.com/docs)

## 📄 License

See root LICENSE file.
