<template>
  <div class="history-manage-container">
    <div class="page-header">
      <h1 class="page-title">更新历史管理</h1>
      <el-button type="primary" plain @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建更新历史
      </el-button>
    </div>
    
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="起始日期"
          end-placeholder="截止日期"
          value-format="YYYY-MM-DD"
          style="width: 300px; margin-right: 12px;"
          @change="handleDateFilter"
        />
        <el-button plain @click="resetDateFilter">重置</el-button>
      </div>
      <div class="filter-right" v-if="selectedHistories.length > 0">
        <el-button type="danger" plain @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
    </div>
    
    <!-- 更新历史表格 -->
    <el-table
      v-loading="loading"
      :data="historyList"
      stripe
      table-layout="auto"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="80" align="center" />
      <el-table-column prop="update_time" label="更新日期" width="150" align="center">
        <template #default="{ row }">
          {{ formatDate(row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="update_content" label="更新内容" min-width="300" align="center" show-overflow-tooltip />
      <el-table-column label="操作" width="180" align="center">
        <template #default="{ row }">
          <el-button link type="primary" plain @click="handleEdit(row)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button link type="danger" plain @click="handleDelete(row)">
            <el-icon><Delete /></el-icon>
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
    
    <!-- 编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="更新内容" prop="update_content">
          <el-input
            v-model="formData.update_content"
            type="textarea"
            :rows="10"
            placeholder="请输入更新内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" plain @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

const loading = ref(false)
const historyList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedHistories = ref([])
const dateRange = ref(null)

// 缓存所有历史数据，避免重复请求
const allHistoryCache = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新建更新历史')
const submitting = ref(false)
const formRef = ref(null)
const formData = ref({
  id: null,
  update_content: ''
})

const formRules = {
  update_content: [
    { required: true, message: '请输入更新内容', trigger: 'blur' }
  ]
}

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

const fetchHistory = async () => {
  loading.value = true
  try {
    // 如果没有缓存，先获取所有数据
    if (allHistoryCache.value.length === 0) {
      const response = await apiClient.get(`${apiUrl}history/admin/list/`)
      
      if (response.data.success) {
        allHistoryCache.value = response.data.data.history || []
      } else {
        ElMessage.error(response.data.error || '获取更新历史列表失败')
        loading.value = false
        return
      }
    }
    
    // 应用日期筛选
    let filteredHistory = allHistoryCache.value
    if (dateRange.value && dateRange.value.length === 2) {
      const startDate = new Date(dateRange.value[0])
      const endDate = new Date(dateRange.value[1])
      endDate.setHours(23, 59, 59, 999) // 包含结束日期的一整天
      
      filteredHistory = allHistoryCache.value.filter(item => {
        const itemDate = new Date(item.update_time)
        return itemDate >= startDate && itemDate <= endDate
      })
    }
    
    // 前端分页
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    historyList.value = filteredHistory.slice(start, end)
    total.value = filteredHistory.length
  } catch (error) {
    console.error('获取更新历史列表错误:', error)
    ElMessage.error('获取更新历史列表失败')
  } finally {
    loading.value = false
  }
}

const handleDateFilter = () => {
  currentPage.value = 1
  fetchHistory()
}

const resetDateFilter = () => {
  dateRange.value = null
  currentPage.value = 1
  fetchHistory()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchHistory()
}

const handlePageChange = () => {
  fetchHistory()
}

const handleSelectionChange = (selection) => {
  selectedHistories.value = selection
}

const handleCreate = () => {
  dialogTitle.value = '新建更新历史'
  formData.value = {
    id: null,
    update_content: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑更新历史'
  formData.value = {
    id: row.id,
    update_content: row.update_content
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  submitting.value = true
  try {
    if (formData.value.id) {
      // 更新更新历史
      const response = await apiClient.put(
        `${apiUrl}history/admin/${formData.value.id}/update/`,
        { update_content: formData.value.update_content }
      )
      
      if (response.data.success) {
        ElMessage.success('更新历史修改成功')
        dialogVisible.value = false
        // 清除缓存，重新获取数据
        allHistoryCache.value = []
        await fetchHistory()
      } else {
        ElMessage.error(response.data.error || '修改失败')
      }
    } else {
      // 创建更新历史
      const response = await apiClient.post(
        `${apiUrl}history/admin/create/`,
        { update_content: formData.value.update_content }
      )
      
      if (response.data.success) {
        ElMessage.success('更新历史创建成功')
        dialogVisible.value = false
        // 清除缓存，重新获取数据
        allHistoryCache.value = []
        await fetchHistory()
      } else {
        ElMessage.error(response.data.error || '创建失败')
      }
    }
  } catch (error) {
    console.error('提交更新历史错误:', error)
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除这条更新历史吗？`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.delete(`${apiUrl}history/admin/${row.id}/delete/`)
      
      if (response.data.success) {
        ElMessage.success('删除成功')
        // 清除缓存，重新获取数据
        allHistoryCache.value = []
        await fetchHistory()
      } else {
        ElMessage.error(response.data.error || '删除失败')
      }
    } catch (error) {
      console.error('删除更新历史错误:', error)
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedHistories.value.length === 0) {
    ElMessage.warning('请选择要删除的更新历史')
    return
  }
  
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedHistories.value.length} 条更新历史吗？`,
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
      
      for (const history of selectedHistories.value) {
        try {
          const response = await apiClient.delete(`${apiUrl}history/admin/${history.id}/delete/`)
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
        ElMessage.success(`成功删除 ${successCount} 条更新历史`)
      } else {
        ElMessage.warning(`成功删除 ${successCount} 条更新历史，失败 ${failCount} 条`)
      }
      
      selectedHistories.value = []
      // 清除缓存，重新获取数据
      allHistoryCache.value = []
      await fetchHistory()
    } catch (error) {
      console.error('批量删除更新历史错误:', error)
      ElMessage.error('批量删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.history-manage-container {
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
</style>

