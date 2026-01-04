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
import { showGuestDialog } from '../lib/guestDialog.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete, Loading } from '@element-plus/icons-vue'
import apiClient from '../lib/api.js'

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

const apiUrl = import.meta.env.VITE_API_URL

// 当前选中的面板类型
const selectedPanel = ref('intro') // 'intro', 'error', 'suggestion'
const feedbackList = ref([])
const loadingFeedback = ref(false)

// 编辑对话框
const editDialogVisible = ref(false)
const editSubmitting = ref(false)
const editFormData = ref({
  id: null,
  issue_type: '',
  description: ''
})

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 获取状态标签类型
const getStatusType = (status) => {
  const statusMap = {
    '未解决': 'info',
    '已解决': 'success',
    '未采纳': 'warning'
  }
  return statusMap[status] || 'info'
}

// 选择面板
const selectPanel = (panelType) => {
  selectedPanel.value = panelType
  if (panelType === 'error' || panelType === 'suggestion') {
    fetchFeedbackList(panelType === 'error' ? '使用错误' : '功能建议')
  }
}

// 获取反馈列表
const fetchFeedbackList = async (issueType = '') => {
  loadingFeedback.value = true
  try {
    const params = {}
    if (issueType) {
      params.issue_type = issueType
    }
    
    const response = await apiClient.get(`${apiUrl}feedback/list/`, { params })
    
    if (response.data.success) {
      feedbackList.value = response.data.data.feedbacks || []
    } else {
      console.error('获取反馈列表失败:', response.data.error)
    }
  } catch (error) {
    console.error('获取反馈列表失败:', error)
  } finally {
    loadingFeedback.value = false
  }
}

// 检查是否是自己的反馈
const isMyFeedback = (feedback) => {
  return isAuthenticated.value && userId.value && feedback.user_id === userId.value
}

// 提供给FeedbackButton组件的刷新函数
const refreshFeedbackList = () => {
  if (selectedPanel.value === 'error') {
    fetchFeedbackList('使用错误')
  } else if (selectedPanel.value === 'suggestion') {
    fetchFeedbackList('功能建议')
  }
}

provide('refreshFeedbackList', refreshFeedbackList)

// 编辑反馈
const handleEdit = (feedback) => {
  editFormData.value = {
    id: feedback.id,
    issue_type: feedback.issue_type,
    description: feedback.description
  }
  editDialogVisible.value = true
}

// 提交编辑
const handleEditSubmit = async () => {
  if (!editFormData.value.description.trim()) {
    ElMessage.warning('问题描述不能为空')
    return
  }

  editSubmitting.value = true
  try {
    const response = await apiClient.put(
      `${apiUrl}feedback/${editFormData.value.id}/update/`,
      {
        issue_type: editFormData.value.issue_type,
        description: editFormData.value.description
      }
    )
    
    if (response.data.success) {
      ElMessage.success('反馈更新成功')
      editDialogVisible.value = false
      // 刷新列表
      if (selectedPanel.value === 'error') {
        fetchFeedbackList('使用错误')
      } else if (selectedPanel.value === 'suggestion') {
        fetchFeedbackList('功能建议')
      }
    } else {
      ElMessage.error(response.data.error || '更新失败')
    }
  } catch (error) {
    console.error('更新反馈错误:', error)
    ElMessage.error('更新失败')
  } finally {
    editSubmitting.value = false
  }
}

// 删除反馈
const handleDelete = (feedback) => {
  ElMessageBox.confirm(
    `确定要删除这条反馈吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.delete(`${apiUrl}feedback/${feedback.id}/delete/`)
      
      if (response.data.success) {
        ElMessage.success('删除成功')
        // 刷新列表
        if (selectedPanel.value === 'error') {
          fetchFeedbackList('使用错误')
        } else if (selectedPanel.value === 'suggestion') {
          fetchFeedbackList('功能建议')
        }
      } else {
        ElMessage.error(response.data.error || '删除失败')
      }
    } catch (error) {
      console.error('删除反馈错误:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

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
          <el-aside>
            <!-- 选择面板 -->
            <div class="panel-list">
              <div 
                class="panel-item"
                :class="{ active: selectedPanel === 'intro' }"
                @click="selectPanel('intro')"
              >
                <span>反馈介绍</span>
              </div>
              <div 
                class="panel-item"
                :class="{ active: selectedPanel === 'error' }"
                @click="selectPanel('error')"
              >
                <span>使用错误</span>
              </div>
              <div 
                class="panel-item"
                :class="{ active: selectedPanel === 'suggestion' }"
                @click="selectPanel('suggestion')"
              >
                <span>功能建议</span>
              </div>
            </div>
          </el-aside>
          <el-main>
            <!-- 反馈介绍 -->
            <div v-if="selectedPanel === 'intro'" class="feedback-content">
              <h1>意见反馈</h1>
              <p class="feedback-description">
                欢迎您提出宝贵的意见和建议！我们非常重视您的反馈，会认真对待每一条反馈。
              </p>
              <div class="feedback-info">
                <el-card shadow="hover">
                  <template #header>
                    <div class="card-header">
                      <span>反馈说明</span>
                    </div>
                  </template>
                  <div class="info-content">
                    <p><strong>问题类型：</strong></p>
                    <ul>
                      <li><strong>使用错误：</strong>在使用过程中遇到的问题、BUG等</li>
                      <li><strong>功能建议：</strong>对新功能的需求或改进建议</li>
                    </ul>
                    <p style="margin-top: 16px;"><strong>反馈流程：</strong></p>
                    <ol>
                      <li>点击右侧"反馈"按钮</li>
                      <li>选择问题类型</li>
                      <li>详细描述问题或建议</li>
                      <li>提交反馈</li>
                    </ol>
                    <p style="margin-top: 16px; color: var(--el-text-color-secondary);">
                      我们会尽快处理您的反馈，感谢您的支持！
                    </p>
                  </div>
                </el-card>
              </div>
            </div>
            
            <!-- 反馈列表 -->
            <div v-else class="feedback-list-content">
              <h1>{{ selectedPanel === 'error' ? '使用错误' : '功能建议' }}</h1>
              
              <div v-if="loadingFeedback" class="loading-feedback">
                <el-icon class="is-loading"><Loading /></el-icon>
                <span>加载中...</span>
              </div>
              
              <div v-else-if="feedbackList.length === 0" class="empty-feedback">
                暂无反馈
              </div>
              
              <div v-else class="feedback-items">
                <el-card 
                  v-for="feedback in feedbackList" 
                  :key="feedback.id"
                  shadow="hover"
                  class="feedback-item"
                >
                  <div class="feedback-header">
                    <div class="feedback-meta">
                      <span class="feedback-user">{{ feedback.username }}</span>
                      <el-tag :type="getStatusType(feedback.is_resolved)" size="small">
                        {{ feedback.is_resolved }}
                      </el-tag>
                      <span class="feedback-time">{{ formatDateTime(feedback.created_at) }}</span>
                    </div>
                    <div v-if="isMyFeedback(feedback)" class="feedback-actions">
                      <el-button 
                        :icon="Edit" 
                        size="small" 
                        text
                        @click="handleEdit(feedback)"
                      >
                        编辑
                      </el-button>
                      <el-button 
                        :icon="Delete" 
                        size="small" 
                        text
                        type="danger"
                        @click="handleDelete(feedback)"
                      >
                        删除
                      </el-button>
                    </div>
                  </div>
                  <div class="feedback-description">
                    <pre>{{ feedback.description }}</pre>
                  </div>
                  <div v-if="feedback.resolved_at" class="feedback-resolved">
                    <span class="resolved-label">处理时间：</span>
                    <span>{{ formatDateTime(feedback.resolved_at) }}</span>
                  </div>
                </el-card>
              </div>
            </div>
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

    <!-- 编辑对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑反馈"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form label-width="100px">
        <el-form-item label="问题类型">
          <el-select
            v-model="editFormData.issue_type"
            placeholder="请选择问题类型"
            style="width: 100%"
          >
            <el-option label="使用错误" value="使用错误" />
            <el-option label="功能建议" value="功能建议" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题描述">
          <el-input
            v-model="editFormData.description"
            type="textarea"
            :rows="8"
            placeholder="请详细描述您遇到的问题或建议"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleEditSubmit" :loading="editSubmitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.el-aside {
  background-color: #00000000;
  width: 300px;
  position: sticky;
  top: 60px;
  align-self: flex-start;
  height: calc(100vh - 165px);
  overflow-y: auto;
  padding: 10px;
}

.panel-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-item {
  padding: 15px 20px;
  background-color: var(--el-bg-color);
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

.el-main {
  background-color: #00000000;
  min-height: max(570px, calc(100vh - 165px));
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  margin-top: 10px;
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
}

.feedback-content {
  max-width: 800px;
  margin: 0 auto;
}

.feedback-content h1,
.feedback-list-content h1 {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
}

.feedback-description {
  font-size: 16px;
  color: var(--el-text-color-regular);
  margin-bottom: 30px;
  line-height: 1.6;
}

.feedback-info {
  margin-top: 30px;
}

.card-header {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.info-content {
  font-size: 14px;
  line-height: 1.8;
  color: var(--el-text-color-regular);
}

.info-content ul,
.info-content ol {
  margin: 8px 0;
  padding-left: 24px;
}

.info-content li {
  margin: 8px 0;
}

.feedback-list-content {
  max-width: 1000px;
  margin: 0 auto;
}

.loading-feedback,
.empty-feedback {
  text-align: center;
  padding: 60px 20px;
  color: var(--el-text-color-secondary);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.feedback-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 20px;
}

.feedback-item {
  margin-bottom: 0;
}

.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.feedback-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.feedback-user {
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.feedback-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.feedback-actions {
  display: flex;
  gap: 8px;
}

.feedback-description {
  margin: 12px 0;
}

.feedback-description pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.6;
  color: var(--el-text-color-regular);
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.feedback-resolved {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.resolved-label {
  font-weight: 500;
  margin-right: 4px;
}
</style>
