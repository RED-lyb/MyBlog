<script setup>
import { onMounted, ref, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Folder, Document, Download, Delete, Upload, Plus, ArrowLeft, UploadFilled } from '@element-plus/icons-vue'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import { showGuestDialog } from '../lib/guestDialog.js'
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

// 文件列表相关
const currentPath = ref('')
const directories = ref([])
const files = ref([])
const loadingFiles = ref(false)
const uploadDialogVisible = ref(false)
const uploadFileList = ref([])
const mkdirDialogVisible = ref(false)
const newDirName = ref('')

const apiUrl = import.meta.env.VITE_API_URL

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}

// 格式化日期
const formatDate = (timestamp) => {
  if (!timestamp) return '-'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

// 获取文件列表
const fetchFileList = async (path = '') => {
  loadingFiles.value = true
  try {
    const response = await apiClient.get(`${apiUrl}network_disk/list/`, {
      params: { path }
    })
    if (response.data?.success) {
      currentPath.value = response.data.data.current_path
      directories.value = response.data.data.directories
      files.value = response.data.data.files
    } else {
      ElMessage.error(response.data?.error || '获取文件列表失败')
    }
  } catch (error) {
    console.error('获取文件列表错误:', error)
    ElMessage.error('获取文件列表失败')
  } finally {
    loadingFiles.value = false
  }
}

// 进入目录
const enterDirectory = (dirName) => {
  const newPath = currentPath.value 
    ? `${currentPath.value}/${dirName}` 
    : dirName
  fetchFileList(newPath)
}

// 返回上级目录
const goToParent = () => {
  if (!currentPath.value) return
  const pathParts = currentPath.value.split('/').filter(p => p)
  pathParts.pop()
  const newPath = pathParts.join('/')
  fetchFileList(newPath)
}

// 返回根目录
const goToRoot = () => {
  fetchFileList('')
}

// 获取完整路径
const getFullPath = (name) => {
  return currentPath.value ? `${currentPath.value}/${name}` : name
}

// 下载文件
const downloadFile = async (fileName) => {
  try {
    const filePath = getFullPath(fileName)
    const url = `${apiUrl}network_disk/download/${encodeURIComponent(filePath)}`
    const response = await apiClient.get(url, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response.data])
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(link.href)
    
    ElMessage.success('下载成功')
  } catch (error) {
    console.error('下载文件错误:', error)
    ElMessage.error('下载失败')
  }
}

// 删除文件或目录
const deleteItem = async (item) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除${item.is_directory ? '目录' : '文件'} "${item.name}" 吗？${item.is_directory ? '（目录下的所有文件将被删除）' : ''}`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const itemPath = getFullPath(item.name)
    const response = await apiClient.delete(`${apiUrl}network_disk/delete/${encodeURIComponent(itemPath)}`)
    
    if (response.data?.success) {
      ElMessage.success('删除成功')
      fetchFileList(currentPath.value)
    } else {
      ElMessage.error(response.data?.error || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除错误:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 上传文件
const handleUpload = async () => {
  if (uploadFileList.value.length === 0) {
    ElMessage.warning('请选择要上传的文件')
    return
  }
  
  try {
    const formData = new FormData()
    formData.append('file', uploadFileList.value[0].raw)
    formData.append('path', currentPath.value)
    
    const response = await apiClient.post(`${apiUrl}network_disk/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data?.success) {
      ElMessage.success('上传成功')
      uploadDialogVisible.value = false
      uploadFileList.value = []
      fetchFileList(currentPath.value)
    } else {
      ElMessage.error(response.data?.error || '上传失败')
    }
  } catch (error) {
    console.error('上传错误:', error)
    ElMessage.error('上传失败')
  }
}

// 创建目录
const createDirectory = async () => {
  if (!newDirName.value.trim()) {
    ElMessage.warning('请输入目录名')
    return
  }
  
  try {
    const response = await apiClient.post(`${apiUrl}network_disk/mkdir/`, {
      name: newDirName.value.trim(),
      path: currentPath.value
    })
    
    if (response.data?.success) {
      ElMessage.success('目录创建成功')
      mkdirDialogVisible.value = false
      newDirName.value = ''
      fetchFileList(currentPath.value)
    } else {
      ElMessage.error(response.data?.error || '创建目录失败')
    }
  } catch (error) {
    console.error('创建目录错误:', error)
    ElMessage.error('创建目录失败')
  }
}

// 获取路径面包屑
const breadcrumbs = computed(() => {
  const parts = currentPath.value ? currentPath.value.split('/').filter(p => p) : []
  return [
    { name: '根目录', path: '' },
    ...parts.map((part, index) => ({
      name: part,
      path: parts.slice(0, index + 1).join('/')
    }))
  ]
})

// 跳转到指定路径
const navigateToPath = (path) => {
  fetchFileList(path)
}

onMounted(async () => {
  authStore.syncFromLocalStorage()

  if (tokenExpired.value) {
    isLoading.value = false
    await markLayoutReady()
    return
  }

  const accessToken = localStorage.getItem('access_token')

  if (!accessToken) {
    isLoading.value = false
    await markLayoutReady()
    if (!isAuthenticated.value) {
      await nextTick()
      showGuestDialog(router, '/home')
    }
    return
  }

  try {
    await fetchUserInfo()
    // 获取文件列表
    await fetchFileList()
  } catch (error) {
    if (error.message !== 'TOKEN_EXPIRED') {
      // 其他错误处理
    }
  } finally {
    isLoading.value = false
    if (!isAuthenticated.value && !tokenExpired.value) {
      await markLayoutReady()
      await nextTick()
      showGuestDialog(router, '/home')
    } else {
      await markLayoutReady()
    }
  }
})
</script>

<template>
  <FullScreenLoading :visible="showPageLoading" />
  <div v-if="showPageLoading"></div>
  <div v-else>
    <div class="common-layout">
      <el-container>
        <el-header style="padding: 0">
          <Head />
        </el-header>
        <el-container>
          <el-main class="network-disk-main">
            <div class="network-disk-container">
              <div class="disk-header">
                <h1>流动网盘</h1>
                <div class="header-actions">
                  <el-button type="primary" :icon="Plus" @click="mkdirDialogVisible = true">新建文件夹</el-button>
                  <el-button type="success" :icon="Upload" @click="uploadDialogVisible = true">上传文件</el-button>
                </div>
              </div>

              <!-- 路径导航 -->
              <div class="breadcrumb-container">
                <el-breadcrumb separator="/">
                  <el-breadcrumb-item 
                    v-for="crumb in breadcrumbs" 
                    :key="crumb.path"
                    @click="navigateToPath(crumb.path)"
                    :class="{ 'is-link': crumb.path !== currentPath }"
                  >
                    {{ crumb.name }}
                  </el-breadcrumb-item>
                </el-breadcrumb>
                <el-button 
                  v-if="currentPath" 
                  :icon="ArrowLeft" 
                  size="small" 
                  @click="goToParent"
                  style="margin-left: 10px"
                >
                  返回上级
                </el-button>
              </div>

              <!-- 文件列表 -->
              <div class="file-list-container">
                <el-table 
                  :data="[...directories, ...files]" 
                  v-loading="loadingFiles"
                  style="width: 100%"
                  stripe
                  @row-dblclick="(row) => row.is_directory && enterDirectory(row.name)"
                >
                  <el-table-column prop="name" label="名称" min-width="300">
                    <template #default="{ row }">
                      <div class="file-name-cell">
                        <el-icon v-if="row.is_directory" class="file-icon folder-icon">
                          <Folder />
                        </el-icon>
                        <el-icon v-else class="file-icon file-icon-default">
                          <Document />
                        </el-icon>
                        <span>{{ row.name }}</span>
                      </div>
                    </template>
                  </el-table-column>
                  <el-table-column prop="size_formatted" label="大小" width="120" align="right">
                    <template #default="{ row }">
                      {{ row.is_directory ? '-' : row.size_formatted }}
                    </template>
                  </el-table-column>
                  <el-table-column label="修改时间" width="180">
                    <template #default="{ row }">
                      {{ formatDate(row.modified_time) }}
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="180" fixed="right">
                    <template #default="{ row }">
                      <el-button 
                        v-if="!row.is_directory"
                        type="primary" 
                        size="small" 
                        :icon="Download"
                        @click="downloadFile(row.name)"
                      >
                        下载
                      </el-button>
                      <el-button 
                        type="danger" 
                        size="small" 
                        :icon="Delete"
                        @click="deleteItem(row)"
                      >
                        删除
                      </el-button>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </div>
          </el-main>
        </el-container>
        <el-footer style="padding: 0">
          <Footer />
        </el-footer>
      </el-container>
    </div>

    <!-- 上传文件对话框 -->
    <el-dialog v-model="uploadDialogVisible" title="上传文件" width="500px">
      <el-upload
        :auto-upload="false"
        :on-change="(file) => uploadFileList = [file]"
        :file-list="uploadFileList"
        :limit="1"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
      </el-upload>
      <template #footer>
        <el-button @click="uploadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpload">确定</el-button>
      </template>
    </el-dialog>

    <!-- 创建目录对话框 -->
    <el-dialog v-model="mkdirDialogVisible" title="新建文件夹" width="400px">
      <el-input 
        v-model="newDirName" 
        placeholder="请输入文件夹名称"
        @keyup.enter="createDirectory"
      />
      <template #footer>
        <el-button @click="mkdirDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="createDirectory">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.network-disk-main {
  min-height: calc(100vh - 120px);
  padding: 20px;
  background-color: var(--el-bg-color-page);
}

.network-disk-container {
  max-width: 1400px;
  margin: 0 auto;
}

.disk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.disk-header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.breadcrumb-container {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background-color: var(--el-bg-color);
  border-radius: 4px;
}

.breadcrumb-container .el-breadcrumb-item {
  cursor: pointer;
}

.breadcrumb-container .el-breadcrumb-item.is-link {
  color: var(--el-color-primary);
}

.breadcrumb-container .el-breadcrumb-item.is-link:hover {
  text-decoration: underline;
}

.file-list-container {
  background-color: var(--el-bg-color);
  border-radius: 4px;
  padding: 10px;
}

.file-name-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 20px;
}

.folder-icon {
  color: var(--el-color-warning);
}

.file-icon-default {
  color: var(--el-color-info);
}

.el-table {
  --el-table-border-color: var(--el-border-color-lighter);
}

.el-table :deep(.el-table__row) {
  cursor: pointer;
}

.el-table :deep(.el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}
</style>
