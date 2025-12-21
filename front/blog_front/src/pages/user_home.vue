<script setup>
import { onMounted, ref, computed, nextTick, watch } from 'vue'
import { useRoute } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { useRouter } from 'vue-router'
import Logout from '../components/Logout.vue'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import apiClient from '../lib/api.js'
import axios from 'axios'

const route = useRoute()
const targetUserId = ref(null)
const targetUser = ref(null)
const userLoading = ref(false)
const userError = ref(null)

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

// 当前用户头像URL
const currentUserAvatar = ref(defaultAvatar)
const currentUserAvatarLoading = ref(false)

// 目标用户头像URL
const targetUserAvatar = ref(defaultAvatar)
const targetUserAvatarLoading = ref(false)

const authStore = useAuthStore()
const {
  user,
  isAuthenticated,
  tokenExpired,
  username,
  userId,
  registeredTime,
  avatar,
  bgColor,
  bgPattern,
  cornerRadius,
  followCount,
  articleCount,
  likedArticleCount,
  followerCount
} = storeToRefs(authStore)
const { loading, fetchUserInfo } = useUserInfo()
const router = useRouter()
const isLoading = ref(true)
const layoutReady = ref(false)
const showPageLoading = computed(() => loading.value || isLoading.value || !layoutReady.value)

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}

// 获取目标用户信息
const fetchTargetUser = async (userId) => {
  if (!userId) {
    userError.value = '用户ID不存在'
    return
  }

  userLoading.value = true
  userError.value = null
  targetUser.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${userId}/`)
    if (response.data?.success) {
      targetUser.value = response.data.data.user
      // 获取目标用户头像
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

// 获取当前用户头像
const fetchCurrentUserAvatar = async () => {
  if (isAuthenticated.value && user.value && avatar.value) {
    currentUserAvatarLoading.value = true
    currentUserAvatar.value = await getUserAvatarUrl(userId.value, avatar.value)
    currentUserAvatarLoading.value = false
  } else {
    currentUserAvatar.value = defaultAvatar
  }
}

// 监听路由参数变化
watch(() => route.params.userId, (newUserId) => {
  if (newUserId) {
    targetUserId.value = parseInt(newUserId)
    fetchTargetUser(targetUserId.value)
  } else {
    // 如果没有路由参数，清空目标用户信息
    targetUser.value = null
    userError.value = null
  }
})
// 页面挂载时刷新用户信息（确保数据最新）
// 注意：应用启动时已自动获取，这里作为刷新机制
onMounted(async () => {
  authStore.syncFromLocalStorage()

  // 从路由参数获取目标用户ID
  if (route.params.userId) {
    targetUserId.value = parseInt(route.params.userId)
    await fetchTargetUser(targetUserId.value)
  } else {
    // 如果没有路由参数，显示当前登录用户的信息
    // 等待认证信息加载完成
  }

  if (tokenExpired.value) {
    // token已过期，等待路由守卫处理
    isLoading.value = false
    await markLayoutReady()
    return
  }

  const accessToken = localStorage.getItem('access_token')

  if (!accessToken) {
    // 游客模式：没有 token，直接结束 loading
    isLoading.value = false
    await markLayoutReady()
    return
  }

  try {
    await fetchUserInfo()
    // 获取当前用户头像
    await fetchCurrentUserAvatar()
  } catch (error) {
    // 如果是token过期错误，不显示错误消息，让路由守卫处理
    if (error.message !== 'TOKEN_EXPIRED') {
      // 其他错误可以在这里处理
    }
  } finally {
    isLoading.value = false
    await markLayoutReady()
  }
})

// 监听用户信息变化，更新头像
watch([isAuthenticated, userId, avatar], async () => {
  if (isAuthenticated.value) {
    await fetchCurrentUserAvatar()
  }
})
</script>

<template>
  <FullScreenLoading :visible="showPageLoading" />
  <div v-if="showPageLoading">
  </div>
  <div v-else>

    <div class="common-layout">
      <el-container>
        <el-header style="padding: 0">
          <Head />
        </el-header>
        <el-container>
          <el-aside style="height: 570px;width: 200px;" class="user-aside">
            <!-- 优先显示目标用户信息（查看别人的主页） -->
            <template v-if="targetUser">
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
            <!-- 显示当前登录用户信息（自己的主页） -->
            <template v-else-if="isAuthenticated && user">
              <div class="avatar-container">
                <el-skeleton :loading="currentUserAvatarLoading" animated>
                  <template #template>
                    <el-skeleton-item variant="circle" style="width: 120px; height: 120px;" />
                  </template>
                  <template #default>
                    <img 
                      :src="currentUserAvatar" 
                      alt="用户头像" 
                      class="user-avatar"
                      @error="currentUserAvatar = defaultAvatar"
                    />
                  </template>
                </el-skeleton>
              </div>
              <div class="stats-row">
                <span class="stat-item">
                  <span class="stat-label">关注</span>
                  <span class="stat-value">{{ followCount }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-label">喜欢</span>
                  <span class="stat-value">{{ likedArticleCount }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-label">文章</span>
                  <span class="stat-value">{{ articleCount }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-label">粉丝</span>
                  <span class="stat-value">{{ followerCount }}</span>
                </span>
              </div>
              <div class="register-time">
                注册时间：{{ registeredTime }}
              </div>
            </template>
            <!-- 游客模式 -->
            <template v-else>
              <div class="avatar-container">
                <img 
                  src="/default_head.png" 
                  alt="默认头像" 
                  class="user-avatar"
                />
              </div>
              <div class="guest-message">
                <p>欢迎，游客！</p>
                <p>您当前以访客身份浏览</p>
              </div>
            </template>
          </el-aside>
          <el-main style="min-height: 570px;">
            <div v-if="userLoading" class="user-loading">加载中...</div>
            <div v-else-if="userError" class="user-error">{{ userError }}</div>
            <div v-else-if="targetUser" class="user-info">
              <h2>用户名：{{ targetUser.username }}</h2>
              <p>用户ID：{{ targetUser.id }}</p>
              <p>注册时间：{{ targetUser.registered_time }}</p>
            </div>
            <div v-else-if="isAuthenticated && user" class="user-info">
              <h2>用户名：{{ username }}</h2>
              <p>用户ID：{{ userId }}</p>
              <p>注册时间：{{ registeredTime }}</p>
              <Logout />
            </div>
            <div v-else class="user-info">
              <p>请先登录</p>
            </div>
          </el-main>
          <el-aside style="height: 570px;width: 200px;"></el-aside>
        </el-container>
        <el-footer style="padding: 0">
          <Footer />
        </el-footer>
      </el-container>
    </div>
  </div>
</template>
<style scoped>
.el-aside {
  background-color: #00000000;
}

.el-main {
  background-color: #00000000;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
  border: 1px solid var(--el-border-color-light);
  margin-top: 10px;
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
}
.user-aside {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
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

.guest-message {
  text-align: center;
  color: #909399;
}

.guest-message p {
  margin: 10px 0;
}

.user-loading,
.user-error {
  text-align: center;
  padding: 40px;
}

.user-error {
  color: #f56c6c;
}

.user-info {
  padding: 20px;
}

.user-info h2 {
  margin-bottom: 15px;
}

.user-info p {
  margin: 10px 0;
}
</style>

