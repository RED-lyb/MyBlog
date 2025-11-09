import axios from 'axios'
import { useAuthStore } from '../stores/user_info.js'

// 创建axios实例，全局设置 withCredentials 确保所有请求都能发送 Cookie
const apiClient = axios.create({
  withCredentials: true
})

/**
 * 检查 token 是否过期
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

/**
 * 清除所有认证信息（不跳转页面）
 */
function clearAuthInfo() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_info')
  try {
    const auth = useAuthStore()
    auth.clear()
  } catch (_) {}
}

/**
 * 设置token过期状态（刷新失败时调用）
 * 不清除用户信息，保留用于显示过期提示
 */
function setTokenExpired() {
  localStorage.removeItem('access_token')
  // 保留user_info，不清除，用于显示过期提示
  try {
    const auth = useAuthStore()
    auth.setTokenExpired()
  } catch (_) {}
}

// 请求拦截器 - 自动添加Authorization头
apiClient.interceptors.request.use(
  async (config) => {
    const url = config.url || ''
    const accessToken = localStorage.getItem('access_token')
    
    // 如果是刷新 token 的请求，不添加 access_token，也不检查过期
    // refresh_token 通过 Cookie 自动发送
    if (url.includes('auth/refresh')) {
      return config
    }
    
    // 如果是登录/退出请求，也不检查 access_token
    if (url.includes('auth/logout') || url.includes('login')) {
      return config
    }
    
    if (accessToken) {
      // 检查 token 是否过期
      if (isTokenExpired(accessToken)) {
        
        try {
          // 尝试使用 refresh_token 刷新 access_token
          const refreshResponse = await axios.post(
            `${import.meta.env.VITE_API_URL}auth/refresh/`,
            {},
            { withCredentials: true }
          )
          
          if (refreshResponse.data?.success) {
            const newAccessToken = refreshResponse.data.data.access_token
            localStorage.setItem('access_token', newAccessToken)
            localStorage.setItem('user_info', JSON.stringify(refreshResponse.data.data.user))
            try {
              const auth = useAuthStore()
              auth.setUser(refreshResponse.data.data.user)
            } catch (_) {}
            
            // 使用新 token 添加到请求头
            config.headers.Authorization = `Bearer ${newAccessToken}`
            return config
          } else {
            throw new Error('刷新 token 返回失败')
          }
        } catch (refreshError) {
          // 刷新失败，设置过期状态（不清除用户信息）
          setTokenExpired()
          // 返回一个会被拒绝的 Promise，让调用方处理
          return Promise.reject(new Error('登录已过期，请重新登录'))
        }
      } else {
        // Token 有效，添加到请求头
        config.headers.Authorization = `Bearer ${accessToken}`
      }
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理token过期
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // 如果是401错误且不是刷新token请求，且尚未重试过
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        // 使用HttpOnly Cookie自动携带刷新令牌
        const refreshResponse = await axios.post(
          `${import.meta.env.VITE_API_URL}auth/refresh/`,
          {},
          { withCredentials: true }
        )

        if (refreshResponse.data?.success) {
          const newAccessToken = refreshResponse.data.data.access_token
          localStorage.setItem('access_token', newAccessToken)
          localStorage.setItem('user_info', JSON.stringify(refreshResponse.data.data.user))
          try {
            const auth = useAuthStore()
            auth.setUser(refreshResponse.data.data.user)
          } catch (_) {}
          
          // 重新发送原始请求
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`
          return apiClient(originalRequest)
        } else {
          throw new Error('刷新 token 返回失败')
        }
      } catch (refreshError) {
        // 刷新失败，设置过期状态（不清除用户信息）
        setTokenExpired()
        
        // 返回一个友好的错误，避免原始错误继续传播
        return Promise.reject(new Error('登录已过期，请重新登录'))
      }
    }
    
    // 如果是刷新 token 的请求失败（401或400），设置过期状态
    if (error.config?.url?.includes('auth/refresh') && 
        (error.response?.status === 401 || error.response?.status === 400)) {
      setTokenExpired()
    }
    
    return Promise.reject(error)
  }
)

export default apiClient