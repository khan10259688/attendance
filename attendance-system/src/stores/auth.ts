// stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import router from '../router'
import api from '../utils/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  // 增强计算属性
  const isLoggedIn = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  // 登录方法优化
  const login = async (credentials: { username: string; password: string }) => {
    try {
      const data = await api.post('/auth/login', credentials)
      console.log('login data: ', data)
      token.value = data.token
      user.value = data.user
      console.log("user: ", user.value)

      localStorage.setItem('token', data.token)
      localStorage.setItem('user', JSON.stringify(data.user))

      return {
        success: true,
        redirect: data.user.role === 'admin' ? '/report' : '/attendance'
      }
    } catch (error: any) {
      console.error('Login error:', error)
      throw new Error(error.response?.data?.message || '登录失败，请检查网络连接')
    }
  }

  // 退出登录优化
  const logout = () => {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    router.push('/login')
  }

  // 增强初始化方法
  const initialize = async () => {
    // 仅从本地存储恢复状态
    token.value = localStorage.getItem('token') || ''
    user.value = JSON.parse(localStorage.getItem('user') || 'null')
  }

  return {
    token,
    user,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    initialize
  }
})