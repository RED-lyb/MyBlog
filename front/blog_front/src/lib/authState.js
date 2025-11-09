import { reactive, watch, ref } from 'vue'
import { useAuthStore } from '../stores/user_info.js'
import apiClient from './api.js'

// 提供一个可直接使用的 reactive 用户态对象，供页面使用
export function useAuthState() {
  const auth = useAuthStore()
  // 根据本地缓存初始化一次
  auth.syncFromLocalStorage()

  const state = reactive({
    user: auth.user,
    isAuthenticated: auth.isAuthenticated,
  })

  // 监听 store 更新，保持同步
  watch(
    () => [auth.user, auth.isAuthenticated],
    ([u, a]) => {
      state.user = u
      state.isAuthenticated = a
    },
    { immediate: true }
  )

  return state
}

// 封装获取用户信息的逻辑（调用全局 /api/user/info/ 接口并同步到 Pinia）
export function useUserInfo() {
  const auth = useAuthStore()
  const loading = ref(false)
  const error = ref(null)

  const fetchUserInfo = async () => {
    try {
      loading.value = true
      error.value = null
      const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/info/`)
      
      // 处理用户信息并同步到 Pinia
      if (response.data.success && response.data.data) {
        if (response.data.data.is_authenticated && response.data.data.user) {
          auth.setUser(response.data.data.user)
        } else {
          auth.clear()
        }
      } else {
        auth.clear()
      }
      
      return response.data
    } catch (err) {
      // 检查是否是登录过期错误
      if (err.message === '登录已过期，请重新登录') {
        // 不要清除用户信息，让路由守卫处理过期状态
        // api.js 的拦截器已经调用了 setTokenExpired()，保留了用户信息
        throw new Error('TOKEN_EXPIRED')
      }
      error.value = err.response?.data || err.message
      // 只有在非过期错误时才清除用户信息
      if (!auth.tokenExpired) {
        auth.clear()
      }
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    fetchUserInfo
  }
}

// 应用启动时自动初始化用户信息（如果已登录）
// 注意：这个函数可能不是必需的，因为路由守卫和页面组件都会处理用户信息获取
// 如果移除此函数，需要在路由守卫中确保状态正确初始化
export function initUserInfo() {
  const auth = useAuthStore()
  
  // 先同步localStorage中的状态
  auth.syncFromLocalStorage()
  
  // 如果本地有 access_token，尝试获取用户信息
  const token = localStorage.getItem('access_token')
  const expiredFlag = localStorage.getItem('token_expired')
  
  if (token) {
    const { fetchUserInfo } = useUserInfo()
    // 静默获取，不显示错误（如果 token 过期，会在后续请求中处理）
    fetchUserInfo().then(() => {
      // 用户信息获取成功
    }).catch((error) => {
      // 如果是token过期错误，触发路由守卫处理
      if (error.message === 'TOKEN_EXPIRED') {
        // 不需要特殊处理，路由守卫会处理这种情况
        return
      }
      // 获取失败，可能是 token 已过期
    })
  } else {
    // 没有 token
    if (expiredFlag === 'true' && auth.tokenExpired) {
      // 如果已标记为过期，不要清空用户信息，保留过期状态让路由守卫处理
      return
    } else {
      // 没有 token 且未过期，清空用户信息（真正的游客状态）
      auth.clear()
    }
  }
}