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

const route = useRoute()
const targetUserId = ref(null)
const targetUser = ref(null)
const userLoading = ref(false)
const userError = ref(null)

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
  cornerRadius
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
          <el-aside width="200px">
            <template v-if="isAuthenticated && user">
              <h2>欢迎回来，{{ username }}！</h2>
              <p>用户ID: {{ userId }}</p>
              <p>注册时间: {{ registeredTime }}</p>
              <p>头像: {{ avatar || '暂未设置' }}</p>
              <p>背景色: {{ bgColor || '默认' }}</p>
              <p>背景样式: {{ bgPattern || '默认' }}</p>
              <p>卡片圆角: {{ cornerRadius || '默认' }}</p>
            </template>
            <template v-else>
              <h2>欢迎，游客！</h2>
              <p>您当前以访客身份浏览</p>
            </template>
          </el-aside>
          <el-main style="height: 600px">
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
          <el-aside width="200px">Aside</el-aside>
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
  background-color: #2effc1;
}

.el-main {
  background-color: #fbaf00;
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

