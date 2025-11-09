import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

// 用户信息 
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const wasLoggedIn = ref(false) // 标记用户当前会话是否登录过
  const tokenExpired = ref(false) // 标记token是否真正过期（刷新失败）

  const username = computed(() => user.value?.username || '')
  const userId = computed(() => user.value?.id || null)

  function setUser(nextUser) {
    user.value = nextUser
    isAuthenticated.value = !!nextUser
    tokenExpired.value = false // 登录成功时清除过期状态
    localStorage.removeItem('token_expired') // 清除过期标记
    if (nextUser) {
      wasLoggedIn.value = true // 标记当前会话登录过
    }
  }

  function clear() {
    user.value = null
    isAuthenticated.value = false
    // 注意：不清除wasLoggedIn和tokenExpired，保持当前会话登录过的状态和过期状态
  }

  function setTokenExpired() {
    // 设置token过期状态（刷新失败时调用）
    tokenExpired.value = true
    isAuthenticated.value = false
    // 在localStorage中标记过期状态，以便页面刷新后恢复
    localStorage.setItem('token_expired', 'true')
    // 不清除user和wasLoggedIn，保留用户信息用于显示
  }

  function resetLoginState() {
    // 完全重置登录状态（用于用户主动退出登录）
    user.value = null
    isAuthenticated.value = false
    wasLoggedIn.value = false // 重置会话登录状态
    tokenExpired.value = false // 重置过期状态
    localStorage.removeItem('token_expired') // 清除过期标记
  }

  function syncFromLocalStorage() {
    try {
      const raw = localStorage.getItem('user_info')
      const accessToken = localStorage.getItem('access_token')
      const expiredFlag = localStorage.getItem('token_expired')
      
      // 如果标记为过期，恢复过期状态（即使有accessToken也要恢复，因为token可能已过期）
      if (expiredFlag === 'true' && raw) {
        try {
          const parsed = JSON.parse(raw)
          user.value = parsed
          isAuthenticated.value = false
          tokenExpired.value = true
          wasLoggedIn.value = true
        } catch (_) {
          // 解析失败
        }
        return
      }
      
      // 如果没有过期标记，且有用户信息，正常恢复
      if (raw) {
        const parsed = JSON.parse(raw)
        setUser(parsed)
      }
      // 不再检查持久化的登录状态
    } catch (_) {
      // 解析失败
    }
  }

  return { 
    user, 
    isAuthenticated, 
    wasLoggedIn, // 导出状态
    tokenExpired, // 导出过期状态
    username, 
    userId, 
    setUser, 
    clear, 
    setTokenExpired, // 导出设置过期状态的方法
    resetLoginState,
    syncFromLocalStorage
  }
})