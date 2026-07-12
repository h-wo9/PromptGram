// 무료 cross-domain 호스팅(FE/BE 서브도메인 분리)에서는 httpOnly third-party cookie가
// 차단되므로 localStorage + 짧은 access + refresh rotation 채택.
// 커스텀 도메인으로 same-site가 되면 httpOnly cookie 방식으로 전환 가능.
import axios from 'axios'

const REFRESH_KEY = 'pg_refresh_token'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

let accessToken = null

export function setAccessToken(token) {
  accessToken = token
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_KEY)
}

export function setRefreshToken(token) {
  if (token) localStorage.setItem(REFRESH_KEY, token)
  else localStorage.removeItem(REFRESH_KEY)
}

export function clearTokens() {
  accessToken = null
  setRefreshToken(null)
}

api.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

let refreshPromise = null

// rotation: 저장된 refresh로 새 pair를 받아 양쪽 저장소를 교체 (동시 401은 single-flight)
export async function refreshTokens() {
  const refresh = getRefreshToken()
  if (!refresh) throw new Error('no refresh token')
  refreshPromise ??= api
    .post('/auth/refresh', { refresh_token: refresh })
    .finally(() => {
      refreshPromise = null
    })
  const { data } = await refreshPromise
  accessToken = data.access_token
  setRefreshToken(data.refresh_token)
  return data
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retried && !original.url.includes('/auth/')) {
      original._retried = true
      try {
        await refreshTokens()
        return api(original)
      } catch {
        clearTokens()
        if (window.location.pathname !== '/') window.location.assign('/')
      }
    }
    return Promise.reject(error)
  }
)

export default api
