/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './app/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        sage: {
          50: '#f7f9f5',
          100: '#eef3eb',
          200: '#dde7d6',
          300: '#ccdbc2',
          400: '#8b9a7c',
          500: '#6b8a69',
          600: '#4a7c59',
          700: '#2d5a3d',
          800: '#1a4d2e',
          900: '#0d3620',
        },
        cream: {
          50: '#fefdfb',
          100: '#faf8f3',
          200: '#f5f1e8',
          300: '#ece5d7',
          400: '#dfc9b0',
          500: '#d4c5a9',
          600: '#c4b5a0',
          700: '#9e8a6f',
          800: '#7a6b57',
          900: '#5a5244',
        },
        rose: {
          500: '#c1566c',
          600: '#a0465a',
        },
      },
      fontFamily: {
        serif: ['Georgia', 'Garamond', 'serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        fadeIn: 'fadeIn 0.6s ease-in-out',
        slideUp: 'slideUp 0.6s ease-out',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        'soft': '0 4px 12px rgba(0, 0, 0, 0.08)',
        'hover': '0 6px 16px rgba(0, 0, 0, 0.12)',
      },
    },
  },
  plugins: [],
}
