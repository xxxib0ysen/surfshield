import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    userInfo: {
      token: localStorage.getItem('token') || '',
      user: JSON.parse(localStorage.getItem('user') || 'null'),
      permissions: JSON.parse(localStorage.getItem('permissions') || '[]')
    }
  }),

  actions: {
    init() {
      this.userInfo.token = localStorage.getItem('token') || ''
      this.userInfo.user = JSON.parse(localStorage.getItem('user') || 'null')
      this.userInfo.permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
    },
    setUserInfo({ token, user, permissions }) {
      this.userInfo = { token, user, permissions }
      localStorage.setItem('token', token)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('permissions', JSON.stringify(permissions))
    },

    logout() {
      this.userInfo = {
        token: '',
        user: null,
        permissions: []
      }
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('permissions')
    }
  }
})
