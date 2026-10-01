module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        serif: ['Playfair Display', 'ui-serif', 'Georgia', 'Cambria', 'serif'],
      },
    },
  },
  plugins: [
    require('daisyui')
  ],
  daisyui:{
    themes:['light','dark']
  }
}