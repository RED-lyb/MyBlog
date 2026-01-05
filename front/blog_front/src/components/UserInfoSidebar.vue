<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import apiClient from '../lib/api.js'
import axios from 'axios'
import { ElMessage } from 'element-plus'

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

const emit = defineEmits(['edit-profile'])

const authStore = useAuthStore()
const { userId: currentUserId, isAuthenticated } = storeToRefs(authStore)
const router = useRouter()

// 判断是否是自己的主页
const isOwnProfile = computed(() => {
  return isAuthenticated.value && currentUserId.value && props.userId && currentUserId.value === props.userId
})

// 关注状态
const isFollowing = ref(false)
const followLoading = ref(false)

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
  if (!userId || userId === null || userId === undefined) {
    targetUser.value = null
    userLoading.value = false
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

// 检查关注状态
const checkFollowStatus = async () => {
  if (!isAuthenticated.value || !props.userId || isOwnProfile.value) {
    isFollowing.value = false
    return
  }
  
  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${props.userId}/follow-status/`)
    if (response.data?.success) {
      isFollowing.value = response.data.data.is_following
    }
  } catch (error) {
    console.error('检查关注状态失败:', error)
    isFollowing.value = false
  }
}

// 切换关注状态
const handleToggleFollow = async () => {
  if (!isAuthenticated.value || !props.userId || followLoading.value) {
    return
  }
  
  followLoading.value = true
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/${props.userId}/follow/`)
    if (response.data?.success) {
      isFollowing.value = response.data.data.is_following
      ElMessage.success(response.data.message)
      // 刷新用户信息以更新关注数
      await fetchUser(props.userId)
    } else {
      ElMessage.error(response.data?.error || '操作失败')
    }
  } catch (error) {
    console.error('关注操作失败:', error)
    ElMessage.error(error.response?.data?.error || '操作失败')
  } finally {
    followLoading.value = false
  }
}

// 编辑资料
const handleEditProfile = () => {
  if (props.userId) {
    router.push(`/user_home/${props.userId}/edit`)
  }
}

// 监听 userId 变化
watch(() => props.userId, async (newUserId) => {
  if (newUserId) {
    await fetchUser(newUserId)
    await checkFollowStatus()
  } else {
    targetUser.value = null
    userError.value = null
    isFollowing.value = false
  }
}, { immediate: true })

// 监听认证状态变化
watch(() => isAuthenticated.value, () => {
  if (props.userId) {
    checkFollowStatus()
  }
})

onMounted(async () => {
  if (props.userId) {
    await fetchUser(props.userId)
    await checkFollowStatus()
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
        <router-link 
          :to="`/user_home/${targetUser.id}/following`"
          class="stat-item stat-link"
        >
          <span class="stat-label">关注</span>
          <span class="stat-value">{{ targetUser.follow_count || 0 }}</span>
        </router-link>
        <router-link 
          :to="`/user_home/${targetUser.id}/followers`"
          class="stat-item stat-link"
        >
          <span class="stat-label">粉丝</span>
          <span class="stat-value">{{ targetUser.follower_count || 0 }}</span>
        </router-link>
        <router-link 
          :to="`/user_home/${targetUser.id}/liked-articles`"
          class="stat-item stat-link"
        >
          <span class="stat-label">喜欢</span>
          <span class="stat-value">{{ targetUser.liked_article_count || 0 }}</span>
        </router-link>
        <router-link 
          :to="`/user_home/${targetUser.id}/articles`"
          class="stat-item stat-link"
        >
          <span class="stat-label">文章</span>
          <span class="stat-value">{{ targetUser.article_count || 0 }}</span>
        </router-link>
      </div>
      <!-- 操作按钮区域 -->
      <div class="action-buttons">
        <!-- 如果是自己的主页，显示编辑资料按钮 -->
        <button
          v-if="isOwnProfile"
          class="dsi-btn dsi-btn-warning dsi-btn-outline"
          @click="handleEditProfile"
        >
          编辑资料
        </button>
        <!-- 如果是别人的主页，显示关注/取消关注按钮 -->
        <button
          v-else-if="isAuthenticated"
          :class="['dsi-btn', isFollowing ? 'dsi-btn-outline' : 'dsi-btn-warning']"
          :disabled="followLoading"
          @click="handleToggleFollow"
        >
          {{ followLoading ? '处理中...' : (isFollowing ? '取消关注' : '关注') }}
        </button>
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

.stat-link {
  text-decoration: none;
  color: inherit;
  transition: all 0.3s;
}

.stat-link:hover {
  transform: scale(1.05);
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
}

.action-buttons {
  width: 100%;
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.action-buttons .dsi-btn {
  padding: 8px 20px;
  font-size: 14px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-buttons .dsi-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

