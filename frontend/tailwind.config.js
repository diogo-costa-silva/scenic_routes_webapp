/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Brand colors
        primary: '#FF6B35',        // Orange vibrant - roads
        secondary: '#004E89',      // Dark blue - maps
        accent: '#10B981',         // Green - start point
        danger: '#EF4444',         // Red - end point

        // Region colors
        'region-continental': '#3B82F6',
        'region-madeira': '#F59E0B',
        'region-acores': '#8B5CF6',
      },
    },
  },
  plugins: [],
}
