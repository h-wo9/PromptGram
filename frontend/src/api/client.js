import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  withCredentials: true,
})

let accessToken = null

export function setAccessToken(token) {
  accessToken = token
}

api.interceptors.request.use((config) => {
  if (accessToken) config.headers.Authorization = `Bearer ${accessToken}`
  return config
})

let refreshPromise = null

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retried && !original.url.includes('/auth/')) {
      original._retried = true
      try {
        refreshPromise ??= api.post('/auth/refresh').finally(() => {
          refreshPromise = null
        })
        const { data } = await refreshPromise
        setAccessToken(data.access_token)
        return api(original)
      } catch {
        setAccessToken(null)
      }
    }
    return Promise.reject(error)
  }
)

export default api
