import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

// Note: StrictMode is disabled due to incompatibility with Mapbox GL JS
// React 18+ StrictMode causes double-mounting which breaks Mapbox initialization
// See CLAUDE.md troubleshooting section for details
createRoot(document.getElementById('root')).render(
  <App />
)
