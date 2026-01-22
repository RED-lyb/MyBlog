<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import apiClient from '../lib/api.js'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const props = defineProps({
  articleId: {
    type: [String, Number],
    required: true
  }
})

const comments = ref([])
const loading = ref(false)
const error = ref(null)

// 用户认证
const authStore = useAuthStore()
const { isAuthenticated, userId } = storeToRefs(authStore)

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
const getUserAvatarUrl = async (userId, avatar) => {
  if (!userId || !avatar) return defaultAvatar
  
  const avatarFileName = `${userId}${avatar}`
  
  try {
    const { data } = await axios.get(`${import.meta.env.VITE_API_URL}home/avatar/`, {
      params: {
        file_name: avatarFileName
      }
    })
    if (data?.success && data?.data?.avatar_url) {
      return data.data.avatar_url
    } else {
      return buildAvatarUrl(userId, avatar)
    }
  } catch (error) {
    console.error('获取头像失败', error)
    return buildAvatarUrl(userId, avatar)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取评论列表
const fetchComments = async () => {
  if (!props.articleId) {
    comments.value = []
    return
  }

  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}article/${props.articleId}/comments/`)
    if (response.data?.success) {
      comments.value = response.data.data.comments || []
      
      // 为每条评论获取头像
      for (const comment of comments.value) {
        comment.display_avatar = defaultAvatar
        comment.avatar_loading = true
        if (comment.user_avatar) {
          comment.display_avatar = await getUserAvatarUrl(comment.user_id, comment.user_avatar)
        }
        comment.avatar_loading = false
      }
    } else {
      error.value = response.data?.error || '获取评论列表失败'
    }
  } catch (err) {
    error.value = err.message || '请求失败'
    console.error('获取评论列表错误:', err)
  } finally {
    loading.value = false
  }
}

// 监听articleId变化
watch(() => props.articleId, () => {
  fetchComments()
}, { immediate: true })

// 组件挂载时获取评论列表
onMounted(() => {
  fetchComments()
})

// 检查是否是自己的评论
const isMyComment = (comment) => {
  return isAuthenticated.value && userId.value && comment.user_id === userId.value
}

// 删除评论
const handleDeleteComment = (comment) => {
  ElMessageBox.confirm(
    '确定要删除这条评论吗？',
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.delete(
        `${import.meta.env.VITE_API_URL}article/${props.articleId}/comments/${comment.id}/delete/`
      )
      
      if (response.data?.success) {
        ElMessage.success('评论删除成功')
        // 刷新评论列表
        await fetchComments()
      } else {
        ElMessage.error(response.data?.error || '删除失败')
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message || '删除失败'
      ElMessage.error(errorMsg)
      console.error('删除评论错误:', err)
    }
  }).catch(() => {
    // 用户取消删除
  })
}

// 暴露刷新方法供父组件调用
defineExpose({
  refresh: fetchComments
})
</script>

<template>
  <div class="comment-list-container">
    <div v-if="loading" class="comment-loading">加载中...</div>
    <div v-else-if="error" class="comment-error">{{ error }}</div>
    <div v-else-if="comments.length === 0" class="comment-empty">暂无评论</div>
    <div v-else class="comment-list">
      <div 
        v-for="comment in comments" 
        :key="comment.id" 
        class="comment-item"
      >
        <div class="comment-header">
          <el-skeleton :loading="comment.avatar_loading" animated
            style="display: flex;align-items: center;justify-content: center;width: 32px;height: 32px;">
            <template #template>
              <el-skeleton-item variant="circle" style="width: 32px;height: 32px;" />
            </template>
            <template #default>
              <el-avatar :size="32" :src="comment.display_avatar || defaultAvatar" />
            </template>
          </el-skeleton>
          <div class="comment-user-info">
            <div class="comment-user-name">{{ comment.user_name }}</div>
            <div class="comment-time">{{ formatDate(comment.created_at) }}</div>
          </div>
        </div>
        <div class="comment-content-wrapper">
          <div class="comment-content">{{ comment.content }}</div>
          <div v-if="isMyComment(comment)" class="comment-actions">
            <span class="comment-delete" @click="handleDeleteComment(comment)">删除</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.comment-list-container {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.comment-loading,
.comment-error,
.comment-empty {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.comment-error {
  color: #f56c6c;
}

.comment-list {
  display: flex;
  flex-direction: column;
}

.comment-item {
  padding: 12px 0;
  border-bottom: 1px solid var(--el-border-color-light);
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.comment-user-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.comment-user-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.comment-content-wrapper {
  position: relative;
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  word-wrap: break-word;
  white-space: pre-wrap;
  padding-right: 50px;
}

.comment-actions {
  position: absolute;
  right: 0;
  bottom: 0;
}

.comment-delete {
  font-size: 12px;
  color: var(--el-color-danger);
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s;
}

.comment-delete:hover {
  opacity: 0.8;
  text-decoration: underline;
}
</style>

