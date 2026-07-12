import { defineStore } from 'pinia'
import api, {
  clearTokens,
  getRefreshToken,
  refreshTokens,
  setAccessToken,
  setRefreshToken,
} from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null, // access는 메모리에만 (localStorage 금지)
    sessionChecked: false,
  }),
  getters: {
    isLoggedIn: (s) => !!s.accessToken,
  },
  actions: {
    _setTokens(access, refresh) {
      this.accessToken = access
      setAccessToken(access)
      if (refresh !== undefined) setRefreshToken(refresh)
    },
    async ensureSession() {
      if (this.sessionChecked || this.accessToken) return
      this.sessionChecked = true
      if (!getRefreshToken()) return
      try {
        const data = await refreshTokens()
        this.accessToken = data.access_token
        await this.fetchMe()
      } catch {
        clearTokens()
      }
    },
    async signup(payload) {
      await api.post('/auth/signup', payload)
      await this.login({ email: payload.email, password: payload.password })
    },
    async login(payload) {
      const { data } = await api.post('/auth/login', payload)
      this._setTokens(data.access_token, data.refresh_token)
      await this.fetchMe()
    },
    async fetchMe() {
      const { data } = await api.get('/users/me')
      this.user = data
    },
    async updateProfile(payload) {
      const { data } = await api.patch('/users/me', payload)
      this.user = data
    },
    async logout() {
      const refresh = getRefreshToken()
      if (refresh) {
        try {
          await api.post('/auth/logout', { refresh_token: refresh })
        } catch {
          /* revoke 실패해도 로컬은 정리 */
        }
      }
      this.accessToken = null
      this.user = null
      clearTokens()
    },
  },
})
