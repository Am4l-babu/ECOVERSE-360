/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        eco: {
          50:  "#edfcf2",
          100: "#d3f8df",
          200: "#aaf0c4",
          300: "#73e2a3",
          400: "#3acd7e",
          500: "#16b364",
          600: "#0a9150",
          700: "#087342",
          800: "#095c37",
          900: "#084c2e",
        },
        carbon: {
          50:  "#f8f6ff",
          100: "#f0ecfe",
          200: "#e3dcfd",
          300: "#cdc0fb",
          400: "#b49af7",
          500: "#9b70f1",
          600: "#8b4ee6",
          700: "#7c3dd2",
          800: "#6833b0",
          900: "#562c90",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
    },
  },
  plugins: [],
};
