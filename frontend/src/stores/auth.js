import { defineStore } from 'pinia'
import api, { setAccessToken } from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: null,
    sessionChecked: false,
  }),
  getters: {
    isLoggedIn: (s) => !!s.accessToken,
  },
  actions: {
    _setToken(token) {
      this.accessToken = token
      setAccessToken(token)
    },
    async ensureSession() {
      if (this.sessionChecked || this.accessToken) return
      this.sessionChecked = true
      try {
        const { data } = await api.post('/auth/refresh')
        this._setToken(data.access_token)
        await this.fetchMe()
      } catch {
        /* not logged in */
      }
    },
    async signup(payload) {
      await api.post('/auth/signup', payload)
      await this.login({ email: payload.email, password: payload.password })
    },
    async login(payload) {
      const { data } = await api.post('/auth/login', payload)
      this._setToken(data.access_token)
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
      try {
        await api.post('/auth/logout')
      } catch {
        /* ignore */
      }
      this._setToken(null)
      this.user = null
    },
  },
})
