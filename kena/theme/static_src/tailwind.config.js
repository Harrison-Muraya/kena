/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../templates/**/*.html",
    "../../templates/**/*.html",
    "../../**/templates/**/*.html",
  ],
  theme: {
    extend: {
      colors: {
        'kena-blue': '#0066cc',
        'kena-dark': '#1a1a2e',
        'kena-purple': '#16213e',
        'kena-gold': '#ffd700',
      },
    },
  },
  plugins: [],
}
