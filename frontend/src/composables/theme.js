import { ref } from 'vue'

const THEME_KEY = 'pg_theme'
const theme = ref('dark')

// 랜딩·로그인은 다크 고정 페이지 — 라이트 설정을 잠시 해제(설정 자체는 보존)
const DARK_ONLY_PATHS = ['/', '/auth']
let suspended = false

function apply() {
  document.documentElement.classList.toggle('light', !suspended && theme.value === 'light')
}

export function initTheme() {
  theme.value = localStorage.getItem(THEME_KEY) === 'light' ? 'light' : 'dark'
  suspended = DARK_ONLY_PATHS.includes(window.location.pathname)
  apply()
}

/** 라우터에서 호출: 다크 고정 라우트 여부에 따라 light 클래스를 껐다 켠다 */
export function suspendLightTheme(on) {
  suspended = on
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
