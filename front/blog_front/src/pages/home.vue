<script setup>
import { onMounted, ref, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessageBox } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import Home_main from '../components/home_main.vue'
import CreateButton from '../components/CreateButton.vue'

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
const route = useRoute()
const isLoading = ref(true)
const layoutReady = ref(false)
const showPageLoading = computed(() => loading.value || isLoading.value || !layoutReady.value)

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}
const guest_info_show = () => {
  ElMessageBox.confirm(
    `您当前正在以游客身份访问，仅可进行博客文档内容阅读，<br/>
        无个人主页，无法撰写与上传内容，无法与其他用户进行互动，
        如需获得完整体验，请进行登录<br/>`,
    '游客须知',
    {
      dangerouslyUseHTMLString: true,
      cancelButtonText: '继续访问',
      confirmButtonText: '去登录',
      type: 'info',
      center: true,
    }
  )
    .then(() => {
      router.push({ path: '/login' })
    })
    .catch(() => {
    })
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
    // 只有从登录页的游客登录进入时才显示弹窗
    const shouldShowDialog = sessionStorage.getItem('show_guest_dialog') === 'true'
    if (!isAuthenticated.value && shouldShowDialog) {
      // 清除标记，确保只弹出一次
      sessionStorage.removeItem('show_guest_dialog')
      await nextTick()
      guest_info_show()
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
    // 只有在不是过期状态且未认证时，且从登录页的游客登录进入时才显示游客提示
    const shouldShowDialog = sessionStorage.getItem('show_guest_dialog') === 'true'
    if (!isAuthenticated.value && !tokenExpired.value && shouldShowDialog) {
      // 清除标记，确保只弹出一次
      sessionStorage.removeItem('show_guest_dialog')
      await markLayoutReady()
      await nextTick()
      guest_info_show()
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
          <el-aside style="width: 200px;">用于筛选</el-aside>
          <el-main style="min-height: 580px;">
            <Home_main />
          </el-main>
          <el-aside style="width: 200px;">
            <CreateButton />
          </el-aside>
        </el-container>
        <el-footer >
          <Footer />
        </el-footer>
      </el-container>
    </div>
  </div>
</template>
<style scoped>
.el-aside {
  background-color: #2effc100;
}

.el-main {
  background-color: #2effc100;
  padding-top: 0 !important;
  padding-bottom: 0 !important;
}
</style>