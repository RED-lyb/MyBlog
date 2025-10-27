import axios from 'axios'

// 创建axios实例
const apiClient = axios.create()

// 请求拦截器 - 自动添加Authorization头
apiClient.interceptors.request.use(
  (config) => {
    const accessToken = localStorage.getItem('access_token')
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
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
    
    // 如果是401错误且不是刷新token请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          // 尝试刷新token
          const refreshResponse = await axios.post(`${import.meta.env.VITE_API_URL}auth/refresh/`, {
            refresh_token: refreshToken
          })
          
          if (refreshResponse.data.success) {
            // 更新token
            localStorage.setItem('access_token', refreshResponse.data.data.access_token)
            localStorage.setItem('user_info', JSON.stringify(refreshResponse.data.data.user))
            
            // 重新发送原始请求
            originalRequest.headers.Authorization = `Bearer ${refreshResponse.data.data.access_token}`
            return apiClient(originalRequest)
          }
        } catch (refreshError) {
          // 刷新失败，清除所有token并跳转到登录页
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user_info')
          
          // 跳转到登录页
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }
      } else {
        // 没有refresh token，清除所有token
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_info')
      }
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
