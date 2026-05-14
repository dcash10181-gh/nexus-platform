/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        nexus: {
          bg:      '#08080f',
          surface: '#0f0f1a',
          card:    '#141420',
          border:  '#1e1e2e',
          cyan:    '#00d4ff',
          'cyan-dim': '#00a3c4',
          magenta: '#ff0080',
          amber:   '#ffb347',
          green:   '#00ff9d',
          muted:   '#6b7280',
          text:    '#e2e8f0',
          subtext: '#94a3b8',
        },
      },
      fontFamily: {
        display: ['"Syne"', 'sans-serif'],
        body:    ['"DM Sans"', 'sans-serif'],
        mono:    ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'fade-up':    'fadeUp 0.5s ease forwards',
        'glow-pulse': 'glowPulse 3s ease-in-out infinite',
        'scan-line':  'scanLine 8s linear infinite',
      },
      keyframes: {
        fadeUp: {
          from: { opacity: 0, transform: 'translateY(16px)' },
          to:   { opacity: 1, transform: 'translateY(0)' },
        },
        glowPulse: {
          '0%, 100%': { opacity: 0.6 },
          '50%':      { opacity: 1 },
        },
        scanLine: {
          '0%':   { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100vh)' },
        },
      },
      backdropBlur: { xs: '2px' },
    },
  },
  plugins: [],
}
