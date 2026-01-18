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
import HistoryMain from '../components/history_main.vue'
import { Loading } from '@element-plus/icons-vue'
import apiClient from '../lib/api.js'

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
  bgPattern
} = storeToRefs(authStore)
const { loading, fetchUserInfo } = useUserInfo()
const router = useRouter()
const isLoading = ref(true)
const layoutReady = ref(false)
const showPageLoading = computed(() => loading.value || isLoading.value || !layoutReady.value)

const apiUrl = import.meta.env.VITE_API_URL

// 更新历史数据
const historyList = ref([])
const selectedHistory = ref(null)
const loadingHistory = ref(false)
const historyMainRef = ref(null)

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}

// 格式化日期（仅日期部分）
const formatDate = (dateString) => {
  if (!dateString) return '-'
  // 如果已经是 YYYY-MM-DD 格式，直接返回
  if (typeof dateString === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(dateString)) {
    return dateString
  }
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 获取更新历史列表
const fetchHistory = async () => {
  loadingHistory.value = true
  try {
    const response = await apiClient.get(`${apiUrl}history/list/`)
    if (response.data.success) {
      historyList.value = response.data.data.history || []
      // 默认选中第一条
      if (historyList.value.length > 0 && !selectedHistory.value) {
        selectedHistory.value = historyList.value[0]
        if (historyMainRef.value) {
          historyMainRef.value.selectHistory(selectedHistory.value)
        }
      }
    } else {
      console.error('获取更新历史失败:', response.data.error)
    }
  } catch (error) {
    console.error('获取更新历史失败:', error)
  } finally {
    loadingHistory.value = false
  }
}

// 选择更新历史
const selectHistory = (history) => {
  selectedHistory.value = history
  if (historyMainRef.value) {
    historyMainRef.value.selectHistory(history)
  }
}

// 页面挂载时刷新用户信息（确保数据最新）
onMounted(async () => {
  authStore.syncFromLocalStorage()

  if (tokenExpired.value) {
    // token已过期，等待路由守卫处理
    isLoading.value = false
    await markLayoutReady()
    await fetchHistory()
    return
  }

  const accessToken = localStorage.getItem('access_token')

  if (!accessToken) {
    // 游客模式：没有 token，直接结束 loading
    isLoading.value = false
    await markLayoutReady()
    await fetchHistory()
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
    await fetchHistory()
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
          <el-aside>
            <!-- 时间列表 -->
            <div class="history-list">
              <div 
                v-for="history in historyList" 
                :key="history.id"
                class="history-item"
                :class="{ active: selectedHistory && selectedHistory.id === history.id }"
                @click="selectHistory(history)"
              >
                <div class="history-date">{{ formatDate(history.update_time) }}</div>
              </div>
              <div v-if="historyList.length === 0 && !loadingHistory" class="empty-history">
                暂无更新历史
              </div>
              <div v-if="loadingHistory" class="loading-history">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>加载中...</span>
              </div>
            </div>
          </el-aside>
          <el-main>
            <HistoryMain ref="historyMainRef" :selected-history="selectedHistory" />
          </el-main>
          <el-aside></el-aside>
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
  overflow-y: auto;
  padding: 10px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  padding: 12px 15px;
  background-color: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.history-item:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.history-item.active {
  border-color: var(--el-color-primary);
  background-color: var(--el-color-primary-light-9);
}

.history-date {
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.empty-history,
.loading-history {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
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

</style>
