<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '../lib/api.js'
import axios from 'axios'

const route = useRoute()
const article = ref(null)
const loading = ref(false)
const error = ref(null)

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
const fetchUserAvatar = async () => {
  if (!article.value?.author_id || !article.value?.author_avatar) {
    article.value.display_avatar = defaultAvatar
    article.value.avatar_loading = false
    return
  }
  
  article.value.avatar_loading = true
  const avatarFileName = `${article.value.author_id}${article.value.author_avatar}`
  
  try {
    const { data } = await axios.get(`${import.meta.env.VITE_API_URL}home/avatar/`, {
      params: {
        file_name: avatarFileName
      }
    })
    if (data?.success && data?.data?.avatar_url) {
      article.value.display_avatar = data.data.avatar_url
    } else {
      article.value.display_avatar = buildAvatarUrl(article.value.author_id, article.value.author_avatar)
    }
  } catch (error) {
    console.error('获取头像失败', error)
    article.value.display_avatar = buildAvatarUrl(article.value.author_id, article.value.author_avatar)
  } finally {
    article.value.avatar_loading = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取文章详情
const fetchArticleDetail = async () => {
  const articleId = route.params.id
  if (!articleId) {
    error.value = '文章ID不存在'
    return
  }

  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}article/${articleId}/`)
    if (response.data?.success) {
      article.value = response.data.data
      // 初始化头像相关属性
      article.value.display_avatar = defaultAvatar
      article.value.avatar_loading = true
      fetchUserAvatar()
    } else {
      error.value = response.data?.error || '获取文章详情失败'
    }
  } catch (err) {
    error.value = err.message || '请求失败'
    console.error('获取文章详情错误:', err)
  } finally {
    loading.value = false
  }
}

// 监听路由参数变化
watch(() => route.params.id, () => {
  fetchArticleDetail()
})

// 组件挂载时获取文章详情
onMounted(() => {
  fetchArticleDetail()
})
</script>

<template>
  <div class="article-main-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">错误: {{ error }}</div>
    <div v-else-if="article" class="article-detail">
      <!-- 文章标题 -->
      <h1 class="article-title">{{ article.title }}</h1>
      
      <!-- 作者信息 -->
      <div class="article-author">
        <el-skeleton :loading="article.avatar_loading" animated
          style="display: flex;align-items: center;justify-content: center;width: 40px;height: 40px;">
          <template #template>
            <el-skeleton-item variant="circle" style="width: 40px;height: 40px;" />
          </template>
          <template #default>
            <el-avatar :size="40" :src="article.display_avatar || defaultAvatar" />
          </template>
        </el-skeleton>
        <div class="author-info">
          <span class="author-name">{{ article.author_name }}</span>
          <span class="publish-time">发布时间：{{ formatDate(article.published_at) }}</span>
        </div>
      </div>
      
      <!-- 文章内容 -->
      <div class="article-content" v-html="article.content"></div>

      
      <!-- 文章统计信息 -->
      <div class="article-stats">
        <span class="stat-item">
          <el-icon><View /></el-icon>
          阅读 {{ article.view_count || 0 }}
        </span>
        <span class="stat-item">
          <el-icon><Star /></el-icon>
          喜欢 {{ article.love_count || 0 }}
        </span>
        <span class="stat-item">
          <el-icon><ChatLineRound /></el-icon>
          评论 {{ article.comment_count || 0 }}
        </span>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.article-main-container {
  width: 100%;
  height: 100%;
  padding: 20px;
  overflow-y: auto;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
}

.error {
  color: #f56c6c;
}

.article-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.article-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 20px;
  line-height: 1.4;
}

.article-author {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--el-border-color);
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.author-name {
  font-size: 16px;
  font-weight: 500;
}

.publish-time {
  font-size: 14px;
  color: #999;
}

.article-stats {
  display: flex;
  gap: 20px;
  padding: 20px 0 20px 0;

  border-bottom: 1px solid var(--el-border-color);
  border-top: 1px solid var(--el-border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #858585;
}

.article-content {
  line-height: 1.8;
  word-wrap: break-word;
  margin-bottom: 20px;
  margin-top: 20px;
}
</style>

