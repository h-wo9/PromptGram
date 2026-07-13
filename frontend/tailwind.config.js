import plugin from 'tailwindcss/plugin'

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        night: '#0A0A0A',
        day: '#F5F7FB',
        accent: '#0070F3',
      },
      fontFamily: {
        sans: [
          'Pretendard Variable',
          'Pretendard',
          '-apple-system',
          'BlinkMacSystemFont',
          'system-ui',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [
    // 라이트 모드: html.light 하위에서만 적용되는 variant (다크가 기본)
    plugin(({ addVariant }) => addVariant('light', ':is(.light &)')),
  ],
}
