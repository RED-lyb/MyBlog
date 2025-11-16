import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessageBox } from 'element-plus'
import axios from 'axios'

/**
 * 检查 token 是否过期（从 api.js 复制，避免循环依赖）
 * @param {string} token - JWT token
 * @returns {boolean} - true 表示已过期或无效
 */
function isTokenExpired(token) {
  if (!token) return true
  
  try {
    // JWT token 格式: header.payload.signature
    const payload = JSON.parse(atob(token.split('.')[1]))
    const exp = payload.exp * 1000 // 转换为毫秒
    const now = Date.now()
    
    // 提前 5 秒判断为过期，避免边界情况
    return now >= (exp - 5000)
  } catch (e) {
    // 解析失败视为过期
    return true
  }
}

const routes=[
  {
    path: '/',
    name: 'index',
    component: () => import('../pages/index.vue'),
    meta:{
      title: '首页|L-BLOG'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../pages/login.vue'),
    meta:{
      title: '登录|L-BLOG'
    }
  },
  {
    path: '/home',
    name: 'home',
    component: () => import('../pages/home.vue'),
    meta:{
      title: '主页|L-BLOG'
    }
  },
  {
  path: '/develop',
  name: 'develop',
  component: () => import('../pages/develop.vue'),
  meta: {
    title: '开发中|L-BLOG'
  }
}
]
//创建路由器实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 检查认证状态并区分三种情况
function checkAuthStatus() {
  const authStore = useAuthStore()
  
  // 情况1: 登录状态（有用户信息且token有效）
  if (authStore.isAuthenticated && !authStore.tokenExpired) {
    return 'authenticated'
  }
  
  // 情况2: 登录过期状态（token真正过期，刷新失败）
  if (authStore.tokenExpired) {
    return 'expired'
  }
  
  // 情况3: 游客状态（当前会话未登录过）
  return 'guest'
}

router.beforeEach(async (to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }

  const authStore = useAuthStore()
  
  // 访问登录页时的处理
  if (to.path === '/login') {
    authStore.syncFromLocalStorage()
    
    // 如果已经登录且未过期，重定向到主页
    if (authStore.isAuthenticated && !authStore.tokenExpired) {
      return next('/home')
    } else {
      // 允许访问登录页（包括过期状态和游客状态）
      return next()
    }
  }
  
  // 对于其他页面，先同步localStorage状态
  authStore.syncFromLocalStorage()
  
  // 检查是否有token但可能已过期
  const accessToken = localStorage.getItem('access_token')
  const expiredFlag = localStorage.getItem('token_expired')
  const userInfo = localStorage.getItem('user_info')
  
  // 如果localStorage标记为过期，但store中未标记，直接设置过期状态
  if (expiredFlag === 'true' && !authStore.tokenExpired) {
    if (userInfo) {
      try {
        const parsed = JSON.parse(userInfo)
        authStore.user = parsed
        authStore.tokenExpired = true
        authStore.isAuthenticated = false
        authStore.wasLoggedIn = true
      } catch (_) {}
    }
  }
  
  // 如果有token但未标记为过期，检查token是否真的过期
  if (accessToken && !authStore.tokenExpired) {
    if (isTokenExpired(accessToken)) {
      // Token已过期，先尝试刷新，只有刷新失败时才设置过期状态
      try {
        const refreshResponse = await axios.post(
          `${import.meta.env.VITE_API_URL}auth/refresh/`,
          {},
          { 
            withCredentials: true,
            // 使用 validateStatus 让 400 不被视为错误，静默处理刷新失败
            validateStatus: (status) => status < 500
          }
        )
        
        if (refreshResponse.status === 200 && refreshResponse.data?.success) {
          // 刷新成功，更新token和用户信息
          const newAccessToken = refreshResponse.data.data.access_token
          localStorage.setItem('access_token', newAccessToken)
          localStorage.setItem('user_info', JSON.stringify(refreshResponse.data.data.user))
          authStore.setUser(refreshResponse.data.data.user)
          // 刷新成功，继续访问
          return next()
        } else {
          // 刷新失败（400或其他错误），设置过期状态
          throw new Error('刷新 token 返回失败')
        }
      } catch (refreshError) {
        // 刷新失败，设置过期状态（静默处理，不显示错误）
        if (userInfo) {
          try {
            // 先标记过期，这样syncFromLocalStorage会正确恢复状态
            localStorage.setItem('token_expired', 'true')
            // 使用store的方法设置过期状态
            authStore.setTokenExpired()
          } catch (_) {}
        }
      }
    }
  }
  
  // 再次同步状态，确保过期标记被正确应用
  authStore.syncFromLocalStorage()
  
  // 检查认证状态
  const authStatus = checkAuthStatus()
  
  // 只有在登录过期状态下才提示并跳转到登录页
  if (authStatus === 'expired') {
    try {
      // 显示确认框，提示用户登录已过期
      await ElMessageBox.confirm(
        '您的登录状态已过期，请重新登录以继续使用完整功能。',
        '登录过期',
        {
          confirmButtonText: '去登录',
          showCancelButton: false,
          type: 'warning',
          center: true,
        }
      )
      
      // 用户点击"去登录"按钮后，清除所有认证信息并跳转到登录页
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      localStorage.removeItem('token_expired')
      const authStore = useAuthStore()
      authStore.resetLoginState() // 完全重置登录状态
      return next('/login')
    } catch (error) {
      // 用户关闭了确认框，清除认证信息并允许以访客身份浏览
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      localStorage.removeItem('token_expired')
      const authStore = useAuthStore()
      authStore.resetLoginState() // 完全重置登录状态
      return next()
    }
  }
  
  // 其他情况（已认证或游客）都可以继续访问
  next()
})

export default router