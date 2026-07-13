import { ref } from 'vue'

const THEME_KEY = 'pg_theme'
const theme = ref('dark')

function apply() {
  document.documentElement.classList.toggle('light', theme.value === 'light')
}

export function initTheme() {
  theme.value = localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'
  apply()
}

export function useTheme() {
  function toggle() {
    theme.value = theme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem(THEME_KEY, theme.value)
    apply()
  }
  return { theme, toggle }
}
