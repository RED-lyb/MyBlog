<script setup>
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '../lib/api.js'
import axios from 'axios'

const props = defineProps({
  userId: {
    type: Number,
    default: null
  },
  username: {
    type: String,
    default: null
  }
})

const targetUser = ref(null)
const userLoading = ref(false)
const userError = ref(null)
const targetUserAvatar = ref('/default_head.png')
const targetUserAvatarLoading = ref(false)

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

// 获取用户头像URL
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

// 获取用户信息
const fetchUser = async (userId) => {
  if (!userId) {
    targetUser.value = null
    return
  }

  userLoading.value = true
  userError.value = null
  targetUser.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${userId}/`)
    if (response.data?.success) {
      targetUser.value = response.data.data.user
      // 获取用户头像
      if (targetUser.value.avatar) {
        targetUserAvatarLoading.value = true
        targetUserAvatar.value = await getUserAvatarUrl(targetUser.value.id, targetUser.value.avatar)
        targetUserAvatarLoading.value = false
      } else {
        targetUserAvatar.value = defaultAvatar
      }
    } else {
      userError.value = response.data?.error || '获取用户信息失败'
    }
  } catch (err) {
    if (err.response?.status === 404) {
      userError.value = '用户不存在'
    } else {
      userError.value = err.message || '请求失败'
    }
    console.error('获取用户信息错误:', err)
  } finally {
    userLoading.value = false
  }
}

// 监听 userId 变化
watch(() => props.userId, (newUserId) => {
  if (newUserId) {
    fetchUser(newUserId)
  } else {
    targetUser.value = null
    userError.value = null
  }
}, { immediate: true })

onMounted(() => {
  if (props.userId) {
    fetchUser(props.userId)
  }
})
</script>

<template>
  <div class="user-info-sidebar">
    <div v-if="userLoading" class="user-loading">加载中...</div>
    <div v-else-if="userError" class="user-error">{{ userError }}</div>
    <template v-else-if="targetUser">
      <div class="avatar-container">
        <el-skeleton :loading="targetUserAvatarLoading" animated>
          <template #template>
            <el-skeleton-item variant="circle" style="width: 120px; height: 120px;" />
          </template>
          <template #default>
            <img 
              :src="targetUserAvatar" 
              alt="用户头像" 
              class="user-avatar"
              @error="targetUserAvatar = defaultAvatar"
            />
          </template>
        </el-skeleton>
      </div>
      <div class="stats-row">
        <span class="stat-item">
          <span class="stat-label">关注</span>
          <span class="stat-value">{{ targetUser.follow_count || 0 }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">喜欢</span>
          <span class="stat-value">{{ targetUser.liked_article_count || 0 }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">文章</span>
          <span class="stat-value">{{ targetUser.article_count || 0 }}</span>
        </span>
        <span class="stat-item">
          <span class="stat-label">粉丝</span>
          <span class="stat-value">{{ targetUser.follower_count || 0 }}</span>
        </span>
      </div>
      <div class="register-time">
        注册时间：{{ targetUser.registered_time }}
      </div>
    </template>
  </div>
</template>

<style scoped>
.user-info-sidebar {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.avatar-container {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.user-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e4e7ed;
}

.stats-row {
  width: 100%;
  display: flex;
  justify-content: space-around;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px 0;
  border-top: 1px solid #e4e7ed;
  border-bottom: 1px solid #e4e7ed;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
}

.register-time {
  width: 100%;
  text-align: center;
  font-size: 12px;
  color: #909399;
  padding-top: 10px;
}

.user-loading,
.user-error {
  text-align: center;
  padding: 40px;
}

.user-error {
  color: #f56c6c;
}
</style>

