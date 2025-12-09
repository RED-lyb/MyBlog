<script setup>
import { onMounted, ref, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { useRouter } from 'vue-router'
import Logout from '../components/Logout.vue'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'

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
// 页面挂载时刷新用户信息（确保数据最新）
// 注意：应用启动时已自动获取，这里作为刷新机制
onMounted(async () => {
  authStore.syncFromLocalStorage()

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
            <h1>关于作者</h1>
            <p>这里是关于作者的内容区域</p>
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
</style>

