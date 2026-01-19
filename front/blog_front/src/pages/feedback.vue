<script setup>
import { onMounted, ref, computed, nextTick, provide } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { useRouter } from 'vue-router'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import FeedbackButton from '../components/FeedbackButton.vue'
import FeedbackMain from '../components/feedback_main.vue'
import { showGuestDialog } from '../lib/guestDialog.js'

const authStore = useAuthStore()
const {
  user,
  isAuthenticated,
  tokenExpired,
  username,
  userId
} = storeToRefs(authStore)
const { loading, fetchUserInfo } = useUserInfo()
const router = useRouter()
const isLoading = ref(true)
const layoutReady = ref(false)
const showPageLoading = computed(() => loading.value || isLoading.value || !layoutReady.value)

// 当前选中的面板类型
const selectedPanel = ref('intro') // 'intro', 'error', 'suggestion'
const feedbackMainRef = ref(null)

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}

// 选择面板
const selectPanel = (panelType) => {
  selectedPanel.value = panelType
  if (feedbackMainRef.value) {
    feedbackMainRef.value.selectPanel(panelType)
  }
}

// 提供给FeedbackButton组件的刷新函数
const refreshFeedbackList = () => {
  if (feedbackMainRef.value) {
    if (selectedPanel.value === 'error') {
      feedbackMainRef.value.fetchFeedbackList('使用错误')
    } else if (selectedPanel.value === 'suggestion') {
      feedbackMainRef.value.fetchFeedbackList('功能建议')
    }
  }
}

provide('refreshFeedbackList', refreshFeedbackList)

// 页面挂载时刷新用户信息（确保数据最新）
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
          <el-aside style="padding: 10px;">
            <!-- 选择面板 -->
            <div class="panel-list">
              <div class="panel-item" :class="{ active: selectedPanel === 'intro' }" @click="selectPanel('intro')">
                <span>反馈介绍</span>
              </div>
              <div class="panel-item" :class="{ active: selectedPanel === 'error' }" @click="selectPanel('error')">
                <span>使用错误</span>
              </div>
              <div class="panel-item" :class="{ active: selectedPanel === 'suggestion' }"
                @click="selectPanel('suggestion')">
                <span>功能建议</span>
              </div>
            </div>
          </el-aside>
          <el-main>
            <FeedbackMain ref="feedbackMainRef" v-model:selected-panel="selectedPanel" />
          </el-main>
          <el-aside>
            <FeedbackButton />
          </el-aside>
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
  width: 230px;
  position: sticky;
  top: 60px;
  align-self: flex-start;
  height: calc(100vh - 165px);
}

.el-main {
  background-color: #00000000;
  min-height: max(570px, calc(100vh - 165px));
  padding: 20px 20px 20px 20px;
  border: 1px solid var(--el-border-color-light);
  margin-top: 10px;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}

.panel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-item {
  padding: 15px 20px;
  background-color: rgba(245, 245, 245, 0.1);;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.panel-item:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-item.active {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

</style>
