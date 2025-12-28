import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

const sanitizeUser = (rawUser) => {
  if (!rawUser || typeof rawUser !== 'object') {
    return null
  }

  return {
    id: rawUser.id ?? '',
    username: rawUser.username ?? '',
    registered_time: rawUser.registered_time ?? rawUser.registeredTime ?? '',
    avatar: rawUser.avatar ?? '',
    bg_color: rawUser.bg_color ?? '',
    bg_pattern: rawUser.bg_pattern ?? '',
    corner_radius: rawUser.corner_radius ?? '',
    follow_count: rawUser.follow_count ?? 0,
    article_count: rawUser.article_count ?? 0,
    liked_article_count: rawUser.liked_article_count ?? 0,
    follower_count: rawUser.follower_count ?? 0,
    is_admin: rawUser.is_admin ?? false
  }
}

const persistUserInfo = (userData) => {
  if (userData) {
    localStorage.setItem('user_info', JSON.stringify(userData))
  } else {
    localStorage.removeItem('user_info')
  }
}

// 用户信息 
export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isAuthenticated = ref(false)
  const wasLoggedIn = ref(false) // 标记用户当前会话是否登录过
  const tokenExpired = ref(false) // 标记token是否真正过期（刷新失败）
  
  const userId = computed(() => user.value?.id || null)
  const username = computed(() => user.value?.username || '')
  const registeredTime = computed(() => user.value?.registered_time || '')
  const avatar = computed(() => user.value?.avatar || '')
  const bgColor = computed(() => user.value?.bg_color || '')
  const bgPattern = computed(() => user.value?.bg_pattern || '')
  const cornerRadius = computed(() => user.value?.corner_radius || '')
  const followCount = computed(() => user.value?.follow_count || 0)
  const articleCount = computed(() => user.value?.article_count || 0)
  const likedArticleCount = computed(() => user.value?.liked_article_count || 0)
  const followerCount = computed(() => user.value?.follower_count || 0)
  const isAdmin = computed(() => user.value?.is_admin ?? false)


  function setUser(nextUser, options = {}) {
    const { persist = true, resetTokenExpired = true } = options
    const sanitized = sanitizeUser(nextUser)

    user.value = sanitized
    if (!tokenExpired.value || resetTokenExpired === true) {
      isAuthenticated.value = !!sanitized
    }

    if (sanitized) {
      wasLoggedIn.value = true // 标记当前会话登录过
      if (resetTokenExpired) {
        tokenExpired.value = false // 登录成功时清除过期状态
        localStorage.removeItem('token_expired') // 清除过期标记
      }
    } else if (resetTokenExpired) {
      tokenExpired.value = false
      localStorage.removeItem('token_expired')
    }

    if (persist) {
      persistUserInfo(sanitized)
    }
  }

  function clear() {
    user.value = null
    isAuthenticated.value = false
    persistUserInfo(null)
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
    persistUserInfo(null)
    localStorage.removeItem('token_expired') // 清除过期标记
  }

  function syncFromLocalStorage() {
    try {
      const raw = localStorage.getItem('user_info')
      const expiredFlag = localStorage.getItem('token_expired') === 'true'
      
      if (raw) {
        const parsed = JSON.parse(raw)
        const sanitized = sanitizeUser(parsed)
        user.value = sanitized
        if (sanitized) {
          wasLoggedIn.value = true
        }
        isAuthenticated.value = expiredFlag ? false : !!sanitized
      } else {
        user.value = null
        isAuthenticated.value = false
      }

      tokenExpired.value = expiredFlag
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
    registeredTime,
    avatar,
    bgColor,
    bgPattern,
    cornerRadius,
    followCount,
    articleCount,
    likedArticleCount,
    followerCount,
    isAdmin,
    setUser, 
    clear, 
    setTokenExpired, // 导出设置过期状态的方法
    resetLoginState,
    syncFromLocalStorage
  }
})