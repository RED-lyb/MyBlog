<template>
  <div class="history-manage-container">
    <div class="page-header">
      <h1 class="page-title">更新历史管理</h1>
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建更新历史
      </el-button>
    </div>
    
    <!-- 更新历史表格 -->
    <el-table
      v-loading="loading"
      :data="historyList"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="update_time" label="更新日期" width="150">
        <template #default="{ row }">
          {{ formatDate(row.update_time) }}
        </template>
      </el-table-column>
      <el-table-column prop="update_content" label="更新内容" min-width="300" show-overflow-tooltip />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="handleEdit(row)">
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button link type="danger" @click="handleDelete(row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
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
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
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
    const response = await apiClient.get(`${apiUrl}history/admin/list/`)
    
    if (response.data.success) {
      historyList.value = response.data.data.history || []
    } else {
      ElMessage.error(response.data.error || '获取更新历史列表失败')
    }
  } catch (error) {
    console.error('获取更新历史列表错误:', error)
    ElMessage.error('获取更新历史列表失败')
  } finally {
    loading.value = false
  }
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
        fetchHistory()
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
        fetchHistory()
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
        fetchHistory()
      } else {
        ElMessage.error(response.data.error || '删除失败')
      }
    } catch (error) {
      console.error('删除更新历史错误:', error)
      ElMessage.error('删除失败')
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
</style>

