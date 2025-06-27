module.exports = {
  content: [
    './templates/**/*.html',
    './static/js/**/*.js',
    './app.py',
  ],
  safelist: [
    'bg-green-500',
    'bg-red-500',
    'text-green-500',
    'text-red-500',
    'hover:text-green-500',
    'hover:bg-green-600',
    'hover:bg-green-700',
    'hover:text-green-700',
    // Agrega aquí más clases si usas dinámicas en Jinja2
  ],
  theme: {
    extend: {},
  },
  plugins: [],
} 