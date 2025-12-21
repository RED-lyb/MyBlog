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
import { showGuestDialog } from '../lib/guestDialog.js'

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
    // 游客模式：没有 token，直接结束 loading，并显示游客提示
    isLoading.value = false
    await markLayoutReady()
    if (!isAuthenticated.value) {
      // 延迟显示弹窗，确保页面已渲染完成
      await nextTick()
      showGuestDialog(router, '/home')
    }
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
    // 只有在不是过期状态且未认证时才显示游客提示
    if (!isAuthenticated.value && !tokenExpired.value) {
      await markLayoutReady()
      await nextTick()
      showGuestDialog(router, '/home')
    } else {
      await markLayoutReady()
    }
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
          <el-aside style="height: 570px;width: 200px;">
          </el-aside>
          <el-main style="min-height: 570px;">
            <h1>趣味游戏</h1>
            <p>这里是趣味游戏的内容区域</p>
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
</style>

