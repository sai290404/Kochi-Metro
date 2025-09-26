/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'metro-blue': '#1e40af',
        'metro-green': '#059669',
        'metro-orange': '#ea580c',
        'metro-red': '#dc2626',
        'metro-gray': '#6b7280'
      }
    },
  },
  plugins: [],
}
