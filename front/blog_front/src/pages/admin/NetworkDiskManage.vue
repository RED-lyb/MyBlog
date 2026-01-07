<template>
  <div class="network-disk-manage-container">
    <div class="page-header">
      <h1 class="page-title">网盘管理</h1>
      <div class="storage-info">
        <span>总存储: {{ storageInfo.total_size_gb }} GB</span>
        <span>文件数: {{ storageInfo.file_count }}</span>
      </div>
    </div>
    
    <!-- 筛选栏 -->
    <div class="filter-bar">
      <div class="filter-left">
        <el-input
          v-model="searchUsername"
          placeholder="搜索用户名"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          style="width: 300px; margin-right: 12px;"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" plain @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
      <div class="filter-right" v-if="selectedFiles.length > 0">
        <el-button type="danger" plain @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
    </div>

    <!-- 文件表格 -->
    <el-table
      v-loading="loading"
      :data="files"
      stripe
      table-layout="auto"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="path" label="文件路径" min-width="300" align="center" show-overflow-tooltip />
      <el-table-column prop="name" label="文件名" width="200" align="center" show-overflow-tooltip />
      <el-table-column prop="username" label="所属用户" width="120" align="center" />
      <el-table-column prop="size_mb" label="大小(MB)" width="120" align="center">
        <template #default="{ row }">
          {{ row.size_mb.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column prop="modified_time" label="修改时间" width="180" align="center">
        <template #default="{ row }">
          {{ formatDate(row.modified_time) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120" align="center">
        <template #default="{ row }">
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
    
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Search } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

const loading = ref(false)
const files = ref([])
const selectedFiles = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchUsername = ref('')
const storageInfo = ref({
  total_size_gb: 0,
  file_count: 0
})

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 缓存所有文件数据，避免重复请求
const allFilesCache = ref([])

const fetchFiles = async () => {
  loading.value = true
  try {
    // 如果没有缓存，先获取所有数据
    if (allFilesCache.value.length === 0) {
      const response = await apiClient.get(`${apiUrl}admin/network-files/`)
      
      if (response.data.success) {
        allFilesCache.value = response.data.data.files || []
        storageInfo.value = {
          total_size_gb: response.data.data.total_size_gb || 0,
          file_count: response.data.data.file_count || allFilesCache.value.length
        }
      } else {
        ElMessage.error(response.data.error || '获取文件列表失败')
        loading.value = false
        return
      }
    }
    
    // 应用用户名筛选
    let filteredFiles = allFilesCache.value
    if (searchUsername.value) {
      filteredFiles = allFilesCache.value.filter(file => 
        file.username && file.username.toLowerCase().includes(searchUsername.value.toLowerCase())
      )
    }
    
    // 前端分页
    const start = (currentPage.value - 1) * pageSize.value
    const end = start + pageSize.value
    files.value = filteredFiles.slice(start, end)
    total.value = filteredFiles.length
    
  } catch (error) {
    console.error('获取文件列表错误:', error)
    ElMessage.error('获取文件列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  // 搜索时不需要重新获取数据，直接使用缓存
  fetchFiles()
}

const handleSizeChange = () => {
  currentPage.value = 1
  fetchFiles()
}

const handlePageChange = () => {
  fetchFiles()
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
        // 清除缓存，重新获取数据
        allFilesCache.value = []
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
      
      // 清除缓存，重新获取数据
      allFilesCache.value = []
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

