<script setup>
import { ref, onMounted, watch } from 'vue'
import { Loading } from '@element-plus/icons-vue'
import apiClient from '../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

// Props
const props = defineProps({
  selectedHistory: {
    type: Object,
    default: null
  }
})

// 更新历史数据
const historyList = ref([])
const selectedHistory = ref(null)
const loadingHistory = ref(false)

// 监听外部传入的selectedHistory
watch(() => props.selectedHistory, (newVal) => {
  selectedHistory.value = newVal
}, { immediate: true })

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
}

// 暴露方法供父组件调用
defineExpose({
  fetchHistory,
  historyList,
  selectedHistory,
  selectHistory,
  loadingHistory
})

onMounted(() => {
  fetchHistory()
})
</script>

<template>
  <div v-if="selectedHistory" class="history-content">
    <div class="content-header">
      <h1>更新历史</h1>
    </div>

    <div class="content-body">
      <pre class="content-text">{{ selectedHistory.update_content }}</pre>
    </div>
  </div>
  <div v-else class="empty-content">
    <p>暂无更新历史</p>
  </div>
</template>

<style scoped>
.history-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-header {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.content-header h1 {
  margin: 0;
  color: var(--el-text-color-primary);
}

.content-body {
  flex: 1;
  overflow-y: auto;
}

.content-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 15px;
  line-height: 1.8;
  color: var(--el-text-color-primary);
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.empty-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--el-text-color-secondary);
  font-size: 16px;
}
</style>

