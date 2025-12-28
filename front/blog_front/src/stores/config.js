import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useConfigStore = defineStore('config', () => {
  const config = ref({
    author_id: 1,
    author: '',
    blog_name: '',
    github_link: '',
    gitee_link: '',
    bilibili_link: ''
  })
  const loading = ref(false)
  const loaded = ref(false)

  // 从localStorage恢复配置
  function syncFromLocalStorage() {
    try {
      const saved = localStorage.getItem('app_config')
      if (saved) {
        const parsed = JSON.parse(saved)
        config.value = { ...config.value, ...parsed }
        loaded.value = true
      }
    } catch (error) {
      console.error('恢复配置失败:', error)
    }
  }

  // 持久化配置到localStorage
  function persistConfig() {
    try {
      localStorage.setItem('app_config', JSON.stringify(config.value))
    } catch (error) {
      console.error('保存配置失败:', error)
    }
  }

  // 加载配置文件
  async function loadConfig() {
    if (loaded.value) return // 避免重复加载
    
    loading.value = true
    try {
      // 先从localStorage恢复
      syncFromLocalStorage()
      
      // 然后从配置文件加载（覆盖localStorage的值）
      const response = await fetch('/config.json')
      if (response.ok) {
        const data = await response.json()
        config.value = { ...config.value, ...data }
        persistConfig() // 保存到localStorage
        loaded.value = true
      } else {
        console.warn('配置文件加载失败，使用默认配置')
        loaded.value = true
      }
    } catch (error) {
      console.error('加载配置失败:', error)
      loaded.value = true // 即使失败也标记为已加载，避免重复请求
    } finally {
      loading.value = false
    }
  }

  return {
    config,
    loading,
    loaded,
    loadConfig,
    syncFromLocalStorage,
    persistConfig
  }
})

