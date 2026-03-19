/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#e8edf5',
          100: '#c5d0e6',
          200: '#9fb1d5',
          300: '#7892c4',
          400: '#5b7ab7',
          500: '#3e62aa',
          600: '#375a9f',
          700: '#2d4f91',
          800: '#1a365d',
          900: '#0f2240',
        },
        accent: {
          300: '#fcd089',
          400: '#f9b94d',
          500: '#f6a623',
          600: '#e08f0a',
        },
        industrial: {
          50: '#f5f6f8',
          100: '#e2e5ea',
          200: '#c8cdd6',
          300: '#a4acb9',
          400: '#7d8797',
          500: '#626c7c',
          600: '#4e5664',
          700: '#3d4452',
          800: '#2a2f3a',
          900: '#1a1d24',
          950: '#12141a',
        },
        severity: {
          low: '#22c55e',
          medium: '#eab308',
          high: '#f97316',
          critical: '#ef4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
