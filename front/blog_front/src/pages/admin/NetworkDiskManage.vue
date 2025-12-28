<template>
  <div class="network-disk-manage-container">
    <div class="page-header">
      <h1 class="page-title">网盘管理</h1>
      <div class="storage-info">
        <span>总存储: {{ storageInfo.total_size_gb }} GB</span>
        <span>文件数: {{ storageInfo.file_count }}</span>
      </div>
    </div>
    
    <!-- 文件表格 -->
    <el-table
      v-loading="loading"
      :data="files"
      stripe
      style="width: 100%"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="path" label="文件路径" min-width="300" show-overflow-tooltip />
      <el-table-column prop="name" label="文件名" width="200" show-overflow-tooltip />
      <el-table-column prop="username" label="所属用户" width="120" />
      <el-table-column prop="size_mb" label="大小(MB)" width="120">
        <template #default="{ row }">
          {{ row.size_mb.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="modified_time" label="修改时间" width="180">
        <template #default="{ row }">
          {{ formatDate(row.modified_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click="handleDelete(row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 批量操作 -->
    <div v-if="selectedFiles.length > 0" class="batch-actions">
      <el-button type="danger" @click="handleBatchDelete">
        <el-icon><Delete /></el-icon>
        批量删除 ({{ selectedFiles.length }})
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

const loading = ref(false)
const files = ref([])
const selectedFiles = ref([])
const storageInfo = ref({
  total_size_gb: 0,
  file_count: 0
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const fetchFiles = async () => {
  loading.value = true
  try {
    const response = await apiClient.get(`${apiUrl}admin/network-files/`)
    
    if (response.data.success) {
      files.value = response.data.data.files
      storageInfo.value = {
        total_size_gb: response.data.data.total_size_gb,
        file_count: response.data.data.file_count
      }
    } else {
      ElMessage.error(response.data.error || '获取文件列表失败')
    }
  } catch (error) {
    console.error('获取文件列表错误:', error)
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const handleSelectionChange = (selection) => {
  selectedFiles.value = selection
}

const handleDelete = (row) => {
  ElMessageBox.confirm(
    `确定要删除文件"${row.name}"吗？此操作不可恢复！`,
    '确认删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await apiClient.delete(`${apiUrl}admin/network-files/delete/`, {
        data: { path: row.path }
      })
      
      if (response.data.success) {
        ElMessage.success('文件删除成功')
        fetchFiles()
      } else {
        ElMessage.error(response.data.error || '删除文件失败')
      }
    } catch (error) {
      console.error('删除文件错误:', error)
      ElMessage.error('删除文件失败')
    }
  }).catch(() => {})
}

const handleBatchDelete = () => {
  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedFiles.value.length} 个文件吗？此操作不可恢复！`,
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
      
      for (const file of selectedFiles.value) {
        try {
          const response = await apiClient.delete(`${apiUrl}admin/network-files/delete/`, {
            data: { path: file.path }
          })
          
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
        ElMessage.success(`成功删除 ${successCount} 个文件`)
      } else {
        ElMessage.warning(`成功删除 ${successCount} 个文件，失败 ${failCount} 个`)
      }
      
      fetchFiles()
    } catch (error) {
      console.error('批量删除文件错误:', error)
      ElMessage.error('批量删除文件失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchFiles()
})
</script>

<style scoped>
.network-disk-manage-container {
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

.storage-info {
  display: flex;
  gap: 20px;
  color: var(--el-text-color-regular);
}

.batch-actions {
  margin-top: 20px;
  padding: 16px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
}
</style>

