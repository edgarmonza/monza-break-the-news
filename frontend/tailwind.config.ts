import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'var(--font-inter)', 'sans-serif'],
      },
      colors: {
        'navy-dark': '#0A1628',
        'navy-medium': '#1A2B45',
        'navy-light': '#2A3B55',
        'cyan': {
          DEFAULT: '#00E5CC',
          hover: '#00FFF0',
        },
        'magenta': '#FF006B',
        'purple-accent': '#9D4EDD',
        'gray-light': '#A8B2C0',
        'gray-medium': '#6B7A8F',
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.4s ease-out",
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "float": "float 3s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        pulseGlow: {
          "0%, 100%": { boxShadow: "0 0 20px rgba(0, 229, 204, 0.5)" },
          "50%": { boxShadow: "0 0 40px rgba(0, 229, 204, 0.8)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
    },
  },
  plugins: [],
};
export default config;
