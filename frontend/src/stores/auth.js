import { defineStore } from 'pinia'
import api from '@/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('campus_token') || '',
    user: JSON.parse(localStorage.getItem('campus_user') || 'null'),
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.token && state.user),
    isAdmin: (state) => ['admin', 'moderator'].includes(state.user?.role),
  },
  actions: {
    persist(data) {
      this.token = data.token
      this.user = data.user
      localStorage.setItem('campus_token', data.token)
      localStorage.setItem('campus_user', JSON.stringify(data.user))
    },
    async login(payload) {
      const data = await api.post('/auth/login', payload)
      this.persist(data)
      return data
    },
    async register(payload) {
      const data = await api.post('/auth/register', payload)
      this.persist(data)
      return data
    },
    async refresh() {
      if (!this.token) return
      try {
        this.user = await api.get('/auth/me')
        localStorage.setItem('campus_user', JSON.stringify(this.user))
      } catch {
        this.logout()
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('campus_token')
      localStorage.removeItem('campus_user')
    },
  },
})

