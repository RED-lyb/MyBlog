<script setup>
import { ref, onMounted, watch, onUnmounted, nextTick, inject } from 'vue'
import { useRouter } from 'vue-router'
import page_number from "./page_number.vue"
import FullScreenLoading from '../pages/FullScreenLoading.vue'
import apiClient from '../lib/api.js'
import axios from 'axios'
import { storeToRefs } from 'pinia'
import { usePaginationStore } from '../stores/pagination.js'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessage } from 'element-plus'
import { Star, ChatLineRound, View, Calendar } from '@element-plus/icons-vue'
import c from 'highlight.js/lib/languages/c'

// 从父组件获取筛选和排序参数
const searchFilters = inject('searchFilters', ref({
  author_id: '',
  author_name: '',
  title: '',
  start_date: '',
  end_date: ''
}))

const sortOptions = inject('sortOptions', ref({
  sort_by: 'published_at',
  sort_order: 'desc'
}))

const router = useRouter()
const authStore = useAuthStore()
const { isAuthenticated, userId } = storeToRefs(authStore)

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

// 等待布局稳定后再测量（避免 height:100% 尚未解析导致偏小）
const waitForLayout = () => new Promise((resolve) => {
  requestAnimationFrame(() => requestAnimationFrame(resolve))
})

// 根据 layout.css 变量估算主容器高度（height:100% 未就绪时的回退）
const getFallbackContainerHeight = () => {
  const styles = getComputedStyle(document.documentElement)
  const bodyOffset = parseFloat(styles.getPropertyValue('--layout-body-offset')) || 213
  const extra = parseFloat(styles.getPropertyValue('--layout-main-content-extra')) || 0
  return window.innerHeight - bodyOffset + extra
}

// 计算每页显示数量（根据容器高度和实际文章高度）
const calculatePageSize = () => {
  if (!containerRef.value) return

  const container = containerRef.value
  let containerHeight = container.clientHeight
  if (containerHeight < 200) {
    containerHeight = getFallbackContainerHeight()
  }

  const headerEl = container.querySelector('.content-header')
  const headerHeight = headerEl?.offsetHeight ?? 0

  const articleItemHeight = measureArticleHeight()
  const itemHeight = articleItemHeight || 140

  const paginationHeight = 50
  const listPadding = 10
  const availableHeight = containerHeight - headerHeight - paginationHeight - listPadding

  if (availableHeight < itemHeight) return

  let calculatedSize = Math.floor(availableHeight / itemHeight)
  calculatedSize = Math.max(3, Math.min(20, calculatedSize))

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

// 构建文章列表请求参数
const buildListParams = () => {
  const params = {
    page: currentPage.value,
    page_size: pageSize.value,
    sort_by: sortOptions.value.sort_by,
    sort_order: sortOptions.value.sort_order
  }

  if (searchFilters.value.author_id) params.author_id = searchFilters.value.author_id
  if (searchFilters.value.author_name) params.author_name = searchFilters.value.author_name
  if (searchFilters.value.title) params.title = searchFilters.value.title
  if (searchFilters.value.start_date) params.start_date = searchFilters.value.start_date
  if (searchFilters.value.end_date) params.end_date = searchFilters.value.end_date

  return params
}

// 应用文章列表响应数据
const applyArticlesResponse = (data) => {
  articles.value = data.articles || []
  paginationStore.setTotal(data.total || 0)

  articles.value.forEach((article) => {
    article.display_avatar = defaultAvatar
    article.avatar_loading = true
    article.is_liked = false
    fetchUserAvatar(article)
  })

  if (isAuthenticated.value && userId.value) {
    articles.value.forEach(async (article) => {
      try {
        const response = await apiClient.get(`${import.meta.env.VITE_API_URL}article/${article.id}/like/status/`)
        if (response.data?.success) {
          article.is_liked = response.data.data.is_liked
        }
      } catch {
        // ignore
      }
    })
  }
}

// 获取所有文章
const fetchArticles = async (showLoading = true) => {
  if (showLoading) {
    loading.value = true
  }
  error.value = null
  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}article/list/`, {
      params: buildListParams()
    })
    if (response.data?.success) {
      applyArticlesResponse(response.data.data)
    } else {
      error.value = response.data?.error || '获取文章列表失败'
    }
  } catch (err) {
    error.value = err.message || '请求失败'
  } finally {
    if (showLoading) {
      loading.value = false
    }
  }
}

// 初始化：先算 pageSize，拉取列表，再用真实卡片高度校准并必要时重拉
const initializeArticles = async () => {
  loading.value = true
  isInitialized.value = false

  await waitForLayout()
  calculatePageSize()

  await fetchArticles(false)

  await nextTick()
  await waitForLayout()

  const sizeBeforeMeasure = pageSize.value
  calculatePageSize()

  if (pageSize.value !== sizeBeforeMeasure) {
    await fetchArticles(false)
  }

  isInitialized.value = true
  loading.value = false
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
watch(pageSize, async () => {
  // 只有在初始化完成后才重新获取，避免初始化时重复请求
  if (isInitialized.value) {
    // 不显示 loading，因为这是自动调整，用户不应该感知到加载过程
    await fetchArticles(false)
  }
})

// 监听筛选参数变化
watch(() => searchFilters.value, () => {
  if (isInitialized.value) {
    // 重置到第一页
    paginationStore.setCurrentPage(1)
    fetchArticles()
  }
}, { deep: true })

// 监听排序参数变化
watch(() => sortOptions.value, () => {
  if (isInitialized.value) {
    // 重置到第一页
    paginationStore.setCurrentPage(1)
    fetchArticles()
  }
}, { deep: true })

// 处理文章点击事件
const handleArticleClick = (article) => {
  // 跳转到文章详情页
  router.push(`/article/${article.id}`)
}

// 处理喜欢点击事件
const handleLikeClick = async (event, article) => {
  event.stopPropagation() // 阻止事件冒泡，避免触发文章点击
  
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}article/${article.id}/like/`)
    if (response.data?.success) {
      // 更新文章的喜欢状态和数量
      article.is_liked = response.data.data.is_liked
      // 重新获取文章列表以更新数量
      await fetchArticles(false)
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data?.error || '操作失败')
    }
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '操作失败')
  }
}


// 组件挂载时获取文章列表
onMounted(async () => {
  paginationStore.syncFromLocalStorage()
  if (paginationStore.currentPage < 1) {
    paginationStore.setCurrentPage(1)
  }

  await nextTick()

  if (containerRef.value) {
    resizeObserver = new ResizeObserver(() => {
      if (resizeTimer) clearTimeout(resizeTimer)
      resizeTimer = setTimeout(() => {
        calculatePageSize()
      }, 200)
    })
    resizeObserver.observe(containerRef.value)
  }

  await initializeArticles()
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
    <div class="content-header">
        <h1>博客主页</h1>
      </div>
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
              <span 
                class="stat-item clickable" 
                :class="{ 'liked': article.is_liked }"
                @click.stop="handleLikeClick($event, article)"
                :title="article.is_liked ? '取消喜欢' : '喜欢'"
              >
                <el-icon :class="{ 'filled-star': article.is_liked }"><Star /></el-icon>
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
.content-header {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--el-border-color-light);
}
.home-main-container{
  height: 100%;
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
  background: rgba(245, 245, 245, 0.1);
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

.stat-item.clickable {
  cursor: pointer;
  transition: color 0.3s;
}

.stat-item.clickable:hover {
  color: var(--el-color-primary);
}

.stat-item.clickable:hover .el-icon {
  color: var(--el-color-primary);
}

.stat-item.clickable:hover .el-icon.filled-star {
  fill: var(--el-color-primary);
}

.stat-item.liked {
  color: var(--el-color-warning);
}

.stat-item.liked .el-icon {
  color: var(--el-color-warning);
}

.stat-item.liked .el-icon.filled-star {
  fill: var(--el-color-warning);
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
  padding-top: 15px;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: flex-end;
}
</style>