<template>
  <div class="feedback-manage-container">
    <div class="page-header">
      <h1 class="page-title">反馈管理</h1>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-select v-model="filters.issue_type" placeholder="问题类型" clearable style="width: 150px; margin-right: 12px;"
          @change="handleFilter">
          <el-option label="使用错误" value="使用错误" />
          <el-option label="功能建议" value="功能建议" />
        </el-select>
        <el-select v-model="filters.is_resolved" placeholder="解决状态" clearable style="width: 150px; margin-right: 12px;"
          @change="handleFilter">
          <el-option label="未解决" value="未解决" />
          <el-option label="已解决" value="已解决" />
          <el-option label="未采纳" value="未采纳" />
        </el-select>
        <el-button plain @click="resetFilters">重置</el-button>
      </div>
      <div class="filter-right" v-if="selectedFeedbacks.length > 0">
        <el-button type="danger" plain @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
    </div>

    <!-- 反馈表格 -->
    <el-table v-loading="loading" :data="feedbackList" stripe table-layout="auto" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="username" label="用户" width="120" align="center">
        <template #default="{ row }">
          {{ row.username || '匿名用户' }}
        </template>
      </el-table-column>
      <el-table-column prop="issue_type" label="问题类型" width="120" align="center" />
      <el-table-column prop="description" label="问题描述" min-width="300" align="center" show-overflow-tooltip>
        <template #default="{ row }">
          <span class="description-link" @click="showDescriptionDialog(row)">{{ row.description }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="提交时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column prop="is_resolved" label="解决状态" width="120" align="center">
        <template #default="{ row }">

          <el-tag :type="getStatusType(row.is_resolved)">

            <div class="inline-grid *:[grid-area:1/1]" v-if="row.is_resolved === '未解决'">
              <div class="dsi-status dsi-status-error animate-ping"></div>
              <div class="dsi-status dsi-status-error"></div>
            </div>
            <div class="inline-grid *:[grid-area:1/1]" v-else-if="row.is_resolved === '已解决'">
              <div class="dsi-status dsi-status-success animate-ping"></div>
              <div class="dsi-status dsi-status-success"></div>
            </div>
            <div class="inline-grid *:[grid-area:1/1]" v-else-if="row.is_resolved === '未采纳'">
              <div class="dsi-status dsi-status-warning animate-ping"></div>
              <div class="dsi-status dsi-status-warning"></div>
            </div>
            {{ row.is_resolved }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="resolved_at" label="处理时间" width="180" align="center">
        <template #default="{ row }">
          {{ row.resolved_at ? formatDateTime(row.resolved_at) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center">
        <template #default="{ row }">
          <el-button link type="primary" plain @click="handleEditStatus(row)">
            <el-icon>
              <Edit />
            </el-icon>
            编辑状态
          </el-button>
          <el-button link type="danger" plain @click="handleDelete(row)">
            <el-icon>
              <Delete />
            </el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 问题描述对话框 -->
    <el-dialog v-model="descriptionDialogVisible" title="问题描述详情" width="600px" :close-on-click-modal="false">
      <div class="description-content">
        <pre>{{ currentDescription }}</pre>
      </div>
      <template #footer>
        <el-button type="primary" plain @click="descriptionDialogVisible = false">确定</el-button>
      </template>
    </el-dialog>

    <!-- 编辑状态对话框 -->
    <el-dialog v-model="statusDialogVisible" title="编辑反馈状态" width="500px" :close-on-click-modal="false">
      <el-form label-width="100px">
        <el-form-item label="解决状态">
          <el-select v-model="statusFormData.is_resolved" placeholder="请选择状态" style="width: 100%">
            <el-option label="未解决" value="未解决" />
            <el-option label="已解决" value="已解决" />
            <el-option label="未采纳" value="未采纳" />
          </el-select>
        </el-form-item>
        <el-form-item label="作者回复">
          <el-input 
            v-model="statusFormData.author_reply" 
            type="textarea" 
            :rows="4" 
            placeholder="可输入反馈回复"
            maxlength="1000"
            show-word-limit
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" plain @click="handleSubmitStatus" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Delete } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

const loading = ref(false)
const feedbackList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedFeedbacks = ref([])

const filters = ref({
  issue_type: '',
  is_resolved: ''
})

const statusDialogVisible = ref(false)
const submitting = ref(false)
const statusFormData = ref({
  id: null,
  is_resolved: '',
  author_reply: ''
})

const descriptionDialogVisible = ref(false)
const currentDescription = ref('')

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const getStatusType = (status) => {
  const statusMap = {
    '未解决': 'danger',
    '已解决': 'success',
    '未采纳': 'warning'
  }
  return statusMap[status] || 'info'
}

const fetchFeedbacks = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (filters.value.issue_type) {
      params.issue_type = filters.value.issue_type
    }
    if (filters.value.is_resolved) {
      params.is_resolved = filters.value.is_resolved
    }

    const response = await apiClient.get(`${apiUrl}feedback/admin/list/`, { params })

    if (response.data.success) {
      feedbackList.value = response.data.data.feedbacks || []
      total.value = response.data.data.total || 0
    } else {
      ElMessage.error(response.data.error || '获取反馈列表失败')
    }
  } catch (error) {
    console.error('获取反馈列表错误:', error)
    ElMessage.error('获取反馈列表失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  fetchFeedbacks()
}

const resetFilters = () => {
  filters.value = {
    issue_type: '',
    is_resolved: ''
  }
  currentPage.value = 1
  fetchFeedbacks()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchFeedbacks()
}

const handlePageChange = () => {
  fetchFeedbacks()
}

const handleEditStatus = (row) => {
  statusFormData.value = {
    id: row.id,
    is_resolved: row.is_resolved,
    author_reply: row.author_reply || ''
  }
  statusDialogVisible.value = true
}

const handleSubmitStatus = async () => {
  if (!statusFormData.value.is_resolved) {
    ElMessage.warning('请选择状态')
    return
  }

  submitting.value = true
  try {
    // 处理 author_reply：空字符串或只有空格时设置为 null
    let authorReply = statusFormData.value.author_reply
    if (authorReply && typeof authorReply === 'string') {
      authorReply = authorReply.trim()
      if (!authorReply) {
        authorReply = null
      }
    } else if (!authorReply) {
      authorReply = null
    }
    
    const response = await apiClient.put(
      `${apiUrl}feedback/admin/${statusFormData.value.id}/update-status/`,
      { 
        is_resolved: statusFormData.value.is_resolved,
        author_reply: authorReply
      }
    )

    if (response.data.success) {
      ElMessage.success('状态更新成功')
      statusDialogVisible.value = false
      await fetchFeedbacks()
    } else {
      ElMessage.error(response.data.error || '更新失败')
    }
  } catch (error) {
    console.error('更新状态错误:', error)
    ElMessage.error('更新失败')
  } finally {
    submitting.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedFeedbacks.value = selection
}

const showDescriptionDialog = (row) => {
  currentDescription.value = row.description
  descriptionDialogVisible.value = true
}

const handleDelete = (row) => {
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
      const response = await apiClient.delete(`${apiUrl}feedback/admin/${row.id}/delete/`)

      if (response.data.success) {
        ElMessage.success('删除成功')
        await fetchFeedbacks()
      } else {
        ElMessage.error(response.data.error || '删除失败')
      }
    } catch (error) {
      console.error('删除反馈错误:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => { })
}

const handleBatchDelete = () => {
  if (selectedFeedbacks.value.length === 0) {
    ElMessage.warning('请选择要删除的反馈')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedFeedbacks.value.length} 条反馈吗？`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      let successCount = 0
      let failCount = 0
      
      for (const feedback of selectedFeedbacks.value) {
        try {
          const response = await apiClient.delete(`${apiUrl}feedback/admin/${feedback.id}/delete/`)
          if (response.data.success) {
            successCount++
          } else {
            failCount++
          }
        } catch (error) {
          failCount++
        }
      }
      
      if (failCount === 0) {
        ElMessage.success(`成功删除 ${successCount} 条反馈`)
      } else {
        ElMessage.warning(`成功删除 ${successCount} 条反馈，失败 ${failCount} 条`)
      }
      
      selectedFeedbacks.value = []
      await fetchFeedbacks()
    } catch (error) {
      console.error('批量删除反馈错误:', error)
      ElMessage.error('批量删除失败')
    }
  }).catch(() => { })
}

onMounted(() => {
  fetchFeedbacks()
})
</script>

<style scoped>
.feedback-manage-container {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: var(--el-text-color-primary);
}

.filter-bar {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-left {
  display: flex;
  align-items: center;
}

.filter-right {
  display: flex;
  justify-content: flex-end;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.description-link {
  color: var(--el-color-primary);
  cursor: pointer;
  text-decoration: underline;
}

.description-link:hover {
  color: var(--el-color-primary-light-3);
}

/* 确保省略号也有链接样式 */
.el-table__cell .description-link {
  color: var(--el-color-primary) !important;
}

.el-table__cell .description-link:hover {
  color: var(--el-color-primary-light-3) !important;
}

/* 覆盖Element Plus表格单元格的省略号样式 */
.el-table__cell:has(.description-link) {
  color: var(--el-color-primary);
}

.el-table__cell:has(.description-link) .el-tooltip__trigger {
  color: var(--el-color-primary);
}

.description-content {
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
  background-color: var(--el-bg-color-page);
  border-radius: 4px;
}

.description-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  color: var(--el-text-color-primary);
}
</style>
