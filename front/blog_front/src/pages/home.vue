<script setup>
import { onMounted, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessageBox } from 'element-plus'
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
    return
  }

  const accessToken = localStorage.getItem('access_token')

  if (!accessToken) {
    // 游客模式：没有 token，直接结束 loading，并提示
    isLoading.value = false
    if (!isAuthenticated.value) {
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
    // 只有在不是过期状态且未认证时才显示游客提示
    if (!isAuthenticated.value && !tokenExpired.value) {
      guest_info_show()
    }
  }
})
</script>

<template>
  <FullScreenLoading :visible="isLoading" />
  <div v-if="loading">
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
            <Logout />
          </el-main>
          <el-aside width="200px">Aside</el-aside>
        </el-container>
        <el-footer style="padding: 0">
          <Footer />
        </el-footer>
      </el-container>
    </div>
  </div>
  <!--    <div>-->
  <!--        <h1>目前正处于测试部署状态，还未正式部署相关内容</h1>-->

  <!--        <div v-if="loading">-->
  <!--            <p>加载中...</p>-->
  <!--        </div>-->

  <!--        <div v-else>-->
  <!--            <div v-if="authState.isAuthenticated && authState.user">-->

  <!--                <Logout />-->
  <!--            </div>-->

  <!--            <div v-else>-->
  <!--                <h2>访客模式</h2>-->
  <!--                <p>您当前以访客身份访问，请登录以获得完整功能</p>-->
  <!--            </div>-->

  <!--        </div>-->
  <!--    </div>-->
</template>
<style scoped>
.el-aside {
  background-color: #2effc1;
}

.el-main {
  background-color: #fbaf00;
}
</style>