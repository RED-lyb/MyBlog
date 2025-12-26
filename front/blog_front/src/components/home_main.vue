<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import page_number from "./page_number.vue"
import FullScreenLoading from '../pages/FullScreenLoading.vue'
import apiClient from '../lib/api.js'
import axios from 'axios'
import { storeToRefs } from 'pinia'
import { usePaginationStore } from '../stores/pagination.js'

const router = useRouter()

// 文章列表数据
const articles = ref([])
const loading = ref(false)
const error = ref(null)

// 使用分页 store
const paginationStore = usePaginationStore()
const { currentPage, pageSize } = storeToRefs(paginationStore)

// 容器引用
const containerRef = ref(null)
const articlesListRef = ref(null)
let resizeObserver = null
let resizeTimer = null

// 标记是否已经初始化完成
const isInitialized = ref(false)

// 测量实际的文章高度
const measureArticleHeight = () => {
  if (!articlesListRef.value) return null
  
  // 获取第一个文章项
  const firstArticle = articlesListRef.value.querySelector('.article-item')
  if (!firstArticle) return null
  
  // 获取文章项的实际高度（包括 padding）
  const articleHeight = firstArticle.offsetHeight
  
  // articles-list 的 gap 是 10px
  const gap = 10
  
  // 总高度 = 文章高度 + gap
  return articleHeight + gap
}

// 计算每页显示数量（根据容器高度和实际文章高度）
const calculatePageSize = () => {
  if (!containerRef.value) return
  
  const container = containerRef.value
  const containerHeight = container.offsetHeight || container.clientHeight
  
  // 如果高度异常，跳过计算
  if (containerHeight < 100) return
  
  // 测量实际的文章高度
  const articleItemHeight = measureArticleHeight()
  
  // 如果无法测量（文章列表为空），使用默认值
  if (!articleItemHeight) {
    // 使用默认值 140px
    const defaultHeight = 140
    const paginationHeight = 50
    const containerPadding = 10
    const availableHeight = containerHeight - paginationHeight - containerPadding
    let calculatedSize = Math.floor(availableHeight / defaultHeight)
    calculatedSize = Math.max(4, Math.min(20, calculatedSize))
    if (calculatedSize !== pageSize.value) {
      paginationStore.setPageSize(calculatedSize)
    }
    return
  }
  console.log('articleItemHeight', articleItemHeight)
  // 分页组件高度约 40px，加上 padding-top 10px
  const paginationHeight = 50
  
  // 容器 padding: top 10px, bottom 0px
  const containerPadding = 10
  
  // 可用高度 = 容器高度 - 分页组件高度 - 容器 padding
  const availableHeight = containerHeight - paginationHeight - containerPadding
  
  // 计算能显示多少篇文章
  let calculatedSize = Math.floor(availableHeight / articleItemHeight)
  
  // 设置最小值为 4，最大值为 20
  calculatedSize = Math.max(4, Math.min(20, calculatedSize))
  
  // 只有当计算出的值与当前值不同时才更新，避免不必要的重新请求
  if (calculatedSize !== pageSize.value) {
    paginationStore.setPageSize(calculatedSize)
  }
}

// 默认头像
const defaultAvatar = '/default_head.png'

// 构建头像URL
const buildAvatarUrl = (userId, avatar) => {
  if (!userId || !avatar) return defaultAvatar
  const baseUrl = import.meta.env?.VITE_API_FILE_URL || import.meta.env?.VITE_API_URL || ''
  const avatarFileName = `${userId}${avatar}`
  if (!baseUrl) return `/api/static/user_heads/${avatarFileName}`
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`
  return `${normalizedBase}static/user_heads/${avatarFileName}`
}

// 获取用户头像
const fetchUserAvatar = async (article) => {
  if (!article.author_id || !article.author_avatar) {
    article.display_avatar = defaultAvatar
    article.avatar_loading = false
    return
  }
  
  article.avatar_loading = true
  const avatarFileName = `${article.author_id}${article.author_avatar}`
  
  try {
    const { data } = await axios.get(`${import.meta.env.VITE_API_URL}home/avatar/`, {
      params: {
        file_name: avatarFileName
      }
    })
    if (data?.success && data?.data?.avatar_url) {
      article.display_avatar = data.data.avatar_url
    } else {
      article.display_avatar = buildAvatarUrl(article.author_id, article.author_avatar)
    }
  } catch (error) {
    console.error('获取头像失败', error)
    article.display_avatar = buildAvatarUrl(article.author_id, article.author_avatar)
  } finally {
    article.avatar_loading = false
  }
}

// 获取文章摘要（从内容中提取纯文本，限制长度）
const getArticleSummary = (content, maxLength = 150) => {
  if (!content) return ''
  // 移除HTML标签
  const text = content.replace(/<[^>]*>/g, '').trim()
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 获取所有文章
const fetchArticles = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}article/list/`, {
      params: {
        page: currentPage.value,
        page_size: pageSize.value
      }
    })
    if (response.data?.success) {
      const data = response.data.data
      articles.value = data.articles || []
      
      // 更新总记录数到 store
      paginationStore.setTotal(data.total || 0)
      
      // 为每篇文章初始化头像相关属性并获取头像
      articles.value.forEach(article => {
        article.display_avatar = defaultAvatar
        article.avatar_loading = true
        fetchUserAvatar(article)
      })
      
      // 等待 DOM 更新后重新计算 pageSize（使用实际文章高度）
      await nextTick()
      // 延迟一下确保文章完全渲染（包括头像加载）
      setTimeout(() => {
        calculatePageSize()
      }, 300)
    } else {
      error.value = response.data?.error || '获取文章列表失败'
    }
  } catch (err) {
    error.value = err.message || '请求失败'
    console.error('获取文章列表错误:', err)
  } finally {
    loading.value = false
  }
}

// 监听页码变化，重新获取文章并滚动到顶部
watch(currentPage, () => {
  fetchArticles()
  // 滚动到容器顶部
  if (containerRef.value) {
    containerRef.value.scrollTop = 0
  }
})

// 监听每页数量变化，重新获取文章（当容器高度变化导致 pageSize 改变时）
watch(pageSize, () => {
  // 只有在初始化完成后才重新获取，避免初始化时重复请求
  if (isInitialized.value) {
    fetchArticles()
  }
})

// 处理文章点击事件
const handleArticleClick = (article) => {
  // 跳转到文章详情页
  router.push(`/article/${article.id}`)
}

// 组件挂载时获取文章列表
onMounted(async () => {
  // 从 localStorage 恢复分页状态（如果不存在则默认为第1页）
  paginationStore.syncFromLocalStorage()
  // 确保当前页码至少为1
  if (paginationStore.currentPage < 1) {
    paginationStore.setCurrentPage(1)
  }
  
  // 等待 DOM 渲染完成
  await nextTick()
  
  // 使用 ResizeObserver 监听容器尺寸变化（包括高度和宽度）
  if (containerRef.value) {
    // 使用防抖，避免频繁计算
    resizeObserver = new ResizeObserver(() => {
      // 清除之前的定时器
      if (resizeTimer) {
        clearTimeout(resizeTimer)
      }
      // 延迟 200ms 后再计算，避免频繁触发
      resizeTimer = setTimeout(() => {
        calculatePageSize()
      }, 200)
    })
    resizeObserver.observe(containerRef.value)
  }
  
  // 获取文章列表
  await fetchArticles()
  
  // 标记初始化完成
  isInitialized.value = true
})

// 组件卸载时清理 ResizeObserver 和定时器
onUnmounted(() => {
  if (resizeTimer) {
    clearTimeout(resizeTimer)
    resizeTimer = null
  }
  if (resizeObserver && containerRef.value) {
    resizeObserver.unobserve(containerRef.value)
    resizeObserver.disconnect()
    resizeObserver = null
  }
})
</script>
<template>
  <div class="home-main-container" ref="containerRef">
    <!-- 全屏加载动画 -->
    <FullScreenLoading :visible="loading" />
    
    <!-- 文章列表区域 -->
      <div v-if="error" class="error">错误: {{ error }}</div>
      <div v-else class="articles-list" ref="articlesListRef">
        <div 
          v-for="article in articles" 
          :key="article.id" 
          class="article-item"
          @click="handleArticleClick(article)"
        >
          <div class="article-body">
            <div class="article-main">
              <div class="author-info">
                <el-skeleton :loading="article.avatar_loading" animated
                  style="display: flex;align-items: center;justify-content: center;width: 15px;height: 15px;">
                  <template #template>
                    <el-skeleton-item variant="circle" style="width: 15px;height: 15px;" />
                  </template>
                  <template #default>
                    <el-avatar :size="15" :src="article.display_avatar || defaultAvatar" />
                  </template>
                </el-skeleton>
                <span class="author-name">{{ article.author_name }}</span>
              </div>
              <h3 class="article-title">{{ article.title }}</h3>
              <div class="article-summary">{{ getArticleSummary(article.content) }}</div>
              <span class="stat-date">
                <el-icon><Calendar /></el-icon>
                发布时间：{{ formatDate(article.published_at) }}
              </span>
            </div>
            <div class="article-stats">
              <span class="stat-item">
                <el-icon><View /></el-icon>
                阅读{{ article.view_count || 0 }}
              </span>
              <span class="stat-item">
                <el-icon><Star /></el-icon>
                喜欢{{ article.love_count || 0 }}
              </span>
              <span class="stat-item">
                <el-icon><ChatLineRound /></el-icon>
                评论{{ article.comment_count || 0 }}
              </span>

          </div>
        </div>
      </div>
    </div>

    <!-- 分页组件 -->
    <div class="page-number-container">
      <page_number />
    </div>
  </div>
</template>
<style scoped>
.home-main-container {
  position: relative;
  width: 100%;
  height: 100%;
  padding-top: 10px;
  padding-left: 20px;
  padding-right: 20px;
  padding-bottom: 0px;
  overflow-y: auto;
}

.error,
.empty {
  text-align: center;
  padding: 40px;
}

.error {
  color: #f56c6c;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.article-item {
  padding: 12px 20px 12px 20px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.article-item:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.article-body {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: center;
}

.article-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
  overflow: hidden;
}

.author-info {
  display: flex;
  align-items: center;
  gap: 5px;
}

.author-name {
  font-size: 13px;
}

.article-title {
  margin: 0;
  font-size: 17px;
  font-weight: bolder;
  line-height: 1.3;
}

.article-summary {
  color: #8a8a8a;
  font-size: 13px;
  margin-bottom: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
  width: 100%;
}

.article-stats {
  display: flex;
  flex-direction: column;
  gap: 7px;
  align-items: flex-end;
  justify-content: center;
  flex-shrink: 0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 15px;
  color: #999;
}

.stat-item i {
  font-size: 13px;
}
.stat-date {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  color: #999;
}
.page-number-container {
  padding-top: 10px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}
</style>