<script setup>
import { onMounted, ref, computed, nextTick, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Upload, Plus, UploadFilled } from '@element-plus/icons-vue'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import UserInfoSidebar from '../components/UserInfoSidebar.vue'
import apiClient from '../lib/api.js'

const authStore = useAuthStore()
const {
  isAuthenticated,
  username,
  userId
} = storeToRefs(authStore)
const router = useRouter()
const route = useRoute()
const isLoading = ref(false)
const layoutReady = ref(false)
const showPageLoading = computed(() => isLoading.value || !layoutReady.value)

// 文件列表相关
const currentPath = ref('')
const pathParts = ref([])
const pathUsernames = ref([])
const currentOwnerId = ref(null)
const currentOwnerUsername = ref(null)
const canWrite = ref(false)
const canDelete = ref(false)
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

// 从 URL 获取路径
const getPathFromRoute = () => {
  const pathParam = route.params.path
  if (!pathParam) return ''
  if (Array.isArray(pathParam)) {
    return pathParam.filter(p => p).join('/')
  }
  return pathParam || ''
}

// 更新 URL（使用 push 以支持浏览器返回键）
const updateUrl = (path) => {
  const pathArray = path ? path.split('/').filter(p => p) : []
  router.push({
    name: 'network_disk',
    params: pathArray.length > 0 ? { path: pathArray } : {}
  }).catch(() => {}) // 忽略重复导航错误
}

// 检查路径是否为文件
const checkIfFile = async (path) => {
  try {
    // 尝试获取文件列表，如果失败可能是文件
    const response = await apiClient.get(`${apiUrl}network_disk/list/`, {
      params: { path }
    })
    return false // 是目录
  } catch (error) {
    // 如果返回404，可能是文件，尝试下载
    if (error.response?.status === 404) {
      return true // 可能是文件
    }
    return false
  }
}

// 获取文件列表
const fetchFileList = async (path = null) => {
  // 如果未指定路径，从 URL 获取
  const targetPath = path !== null ? path : getPathFromRoute()
  
  loadingFiles.value = true
  try {
    const response = await apiClient.get(`${apiUrl}network_disk/list/`, {
      params: { path: targetPath }
    })
    if (response.data?.success) {
      currentPath.value = response.data.data.current_path
      pathParts.value = response.data.data.path_parts || []
      pathUsernames.value = response.data.data.path_usernames || []
      currentOwnerId.value = response.data.data.current_owner_id
      currentOwnerUsername.value = response.data.data.current_owner_username
      canWrite.value = response.data.data.can_write || false
      canDelete.value = response.data.data.can_delete || false
      directories.value = response.data.data.directories
      files.value = response.data.data.files
    } else {
      // 路径不存在，重定向到根目录
      ElMessage.error(response.data?.error || '文件路径不存在')
      router.push({ name: 'network_disk' })
    }
  } catch (error) {
    console.error('获取文件列表错误:', error)
    // 如果是404，可能是文件，抛出错误让路由监听处理
    if (error.response?.status === 404 && targetPath) {
      throw error // 重新抛出，让路由监听处理下载
    }
    // 其他错误，重定向到根目录
    ElMessage.error('文件路径不存在')
    router.push({ name: 'network_disk' })
    throw error // 重新抛出，让路由监听知道失败了
  } finally {
    loadingFiles.value = false
  }
}

// 进入目录（单击）
const enterDirectory = (dirName) => {
  // 如果是根目录，dirName 可能是用户名，需要转换为用户ID
  if (!currentPath.value && directories.value.length > 0) {
    const dir = directories.value.find(d => (d.display_name || d.name) === dirName)
    if (dir && dir.user_id) {
      // 使用用户ID作为路径
      updateUrl(String(dir.user_id))
      return
    }
    // 如果找不到，尝试使用 name（可能是用户ID）
    const dirById = directories.value.find(d => d.name === dirName)
    if (dirById) {
      updateUrl(dirById.name)
      return
    }
  }
  
  // 非根目录，直接拼接路径
  const newPath = currentPath.value 
    ? `${currentPath.value}/${dirName}` 
    : dirName
  updateUrl(newPath)
  // fetchFileList 会由路由监听触发
}

// 获取完整路径
const getFullPath = (name) => {
  return currentPath.value ? `${currentPath.value}/${name}` : name
}

// 获取文件下载 URL
const getFileDownloadUrl = (fileName) => {
  const filePath = getFullPath(fileName)
  return `${apiUrl}network_disk/download/${encodeURIComponent(filePath)}`
}

// 下载文件（通过 URL 跳转）
const downloadFile = (fileName) => {
  const downloadUrl = getFileDownloadUrl(fileName)
  window.open(downloadUrl, '_blank')
}

// 删除文件或目录
const deleteItem = async (item) => {
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  
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
      fetchFileList() // 从 URL 读取路径
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
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  
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
      fetchFileList() // 从 URL 读取路径
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
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  
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
      fetchFileList() // 从 URL 读取路径
    } else {
      ElMessage.error(response.data?.error || '创建目录失败')
    }
  } catch (error) {
    console.error('创建目录错误:', error)
    ElMessage.error('创建目录失败')
  }
}

// 获取路径面包屑（显示用户名）
const breadcrumbs = computed(() => {
  const parts = pathParts.value.length > 0 ? pathParts.value : []
  const usernames = pathUsernames.value.length > 0 ? pathUsernames.value : []
  const crumbs = [
    { name: '根目录', path: '', isLast: parts.length === 0 }
  ]
  
  parts.forEach((part, index) => {
    const displayName = usernames[index] || part
    crumbs.push({
      name: displayName,
      path: parts.slice(0, index + 1).join('/'),
      isLast: index === parts.length - 1
    })
  })
  
  return crumbs
})

// 跳转到指定路径
const navigateToPath = (path) => {
  updateUrl(path)
  // fetchFileList 会由路由监听触发
}

// 监听路由变化
watch(() => route.params.path, async () => {
  const path = getPathFromRoute()
  
  if (path) {
    // 先尝试获取文件列表，如果失败（400/404），可能是文件，尝试下载
    try {
      await fetchFileList(path)
    } catch (error) {
      // 如果获取文件列表失败（400/404），尝试作为文件下载
      // 400 可能是因为路径是文件而不是目录
      // 404 可能是路径不存在或文件不存在
      if (error.response?.status === 400 || error.response?.status === 404) {
        const downloadUrl = `${apiUrl}network_disk/download/${encodeURIComponent(path)}`
        // 直接跳转到下载URL（浏览器会自动处理下载）
        window.location.href = downloadUrl
        return
      }
      // 其他错误，显示错误信息
      console.error('获取文件列表错误:', error)
      ElMessage.error('文件路径不存在')
      router.push({ name: 'network_disk' })
    }
  } else {
    // 路径为空，获取根目录文件列表
    await fetchFileList(path)
  }
}, { immediate: true })

// 确保用户文件夹存在
const ensureUserDirectory = async () => {
  if (isAuthenticated.value && userId.value) {
    try {
      // 通过访问用户目录来触发创建
      await apiClient.get(`${apiUrl}network_disk/list/`, {
        params: { path: String(userId.value) }
      })
    } catch (error) {
      // 忽略错误，目录会在后端自动创建
      console.log('确保用户目录:', error)
    }
  }
}

onMounted(async () => {
  authStore.syncFromLocalStorage()
  isLoading.value = false
  await markLayoutReady()
  
  // 如果用户已登录，确保用户文件夹存在
  await ensureUserDirectory()
  
  // 从 URL 获取路径并加载文件列表（路由监听会处理）
  const path = getPathFromRoute()
  await fetchFileList(path)
})
</script>

<template>
  <FullScreenLoading :visible="showPageLoading" />
  <div v-if="showPageLoading"></div>
  <div v-else>
    <div class="common-layout">
      <el-container>
        <el-header style="padding: 0;">
          <Head />
        </el-header>
        <el-container>
          <el-aside style="height: 580px;width: 200px;" v-if="currentOwnerId">
            <UserInfoSidebar :user-id="currentOwnerId" />
          </el-aside>
          <el-aside style="height: 580px;width: 200px;" v-else></el-aside>
          <el-main style="min-height: 580px;" class="network-disk-main">
            <div class="network-disk-container">
              <div class="disk-header">
                <h1>流动网盘</h1>
                <div class="header-actions" v-if="canWrite && isAuthenticated">
                  <el-button type="primary" :icon="Plus" @click="mkdirDialogVisible = true">新建文件夹</el-button>
                  <el-button type="success" :icon="Upload" @click="uploadDialogVisible = true">上传文件</el-button>
                </div>
                <div v-else-if="!isAuthenticated" class="header-tip">
                  <el-text type="info">访客模式：只能浏览和下载</el-text>
                </div>
                <div v-else class="header-tip">
                  <el-text type="info">当前目录只读</el-text>
                </div>
              </div>

              <!-- 路径导航 - DaisyUI 风格 -->
              <div class="dsi-breadcrumbs text-sm items-center gap-2" style="margin-bottom: 20px;">
                <ul>
                  <li v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
                    <a 
                      v-if="!crumb.isLast"
                      @click.prevent="navigateToPath(crumb.path)"
                      class="breadcrumb-link"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        class="h-4 w-4 stroke-current">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                      </svg>
                      {{ crumb.name }}
                    </a>
                    
                    <span v-else class="inline-flex items-center gap-2">
                      <!-- 当前打开的路径：显示打开的文件夹图标 -->
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 24 24"
                        class="h-4 w-4"
                        fill="none"
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-width="2">
                        <g>
                          <path d="M3 12V7.2c0-1.12 0-1.68.218-2.108a2 2 0 0 1 .874-.874C4.52 4 5.08 4 6.2 4h1.475c.489 0 .733 0 .963.055a2 2 0 0 1 .579.24c.201.123.374.296.72.642l.126.126c.346.346.519.519.72.642c.18.11.375.19.579.24c.23.055.474.055.963.055h.475c1.12 0 1.68 0 2.108.218a2 2 0 0 1 .874.874C16 7.52 16 8.08 16 9.2v.3"></path>
                          <path d="M4.7 20h10.92c.854 0 1.28 0 1.64-.146a2 2 0 0 0 .813-.604c.243-.303.366-.713.611-1.53l1.08-3.6c.419-1.397.628-2.095.477-2.648a2 2 0 0 0-.869-1.168C18.886 10 18.157 10 16.699 10h-5.318c-.854 0-1.281 0-1.642.146a2 2 0 0 0-.812.604c-.243.303-.366.712-.611 1.53l-1.948 6.494A1.72 1.72 0 0 1 4.72 20v0C3.77 20 3 19.23 3 18.28V11m8 4h5"></path>
                        </g>
                      </svg>
                      {{ crumb.name }}
                    </span>
                  </li>
                </ul>
              </div>

              <!-- 文件列表 -->
              <FullScreenLoading :visible="loadingFiles" />
              <div class="file-list-container" v-if="!loadingFiles">
                <el-table 
                  :data="[...directories, ...files]" 
                  style="width: 100%"
                  stripe
                >
                  <el-table-column prop="name" label="名称" min-width="300">
                    <template #default="{ row }">
                      <div class="file-name-cell">
                        <!-- 文件夹图标 -->
                        <svg
                          v-if="row.is_directory"
                          xmlns="http://www.w3.org/2000/svg"
                          fill="none"
                          viewBox="0 0 24 24"
                          class="h-4 w-4 stroke-current file-icon"
                          @click="enterDirectory(row.display_name || row.name)"
                          style="cursor: pointer;">
                          <path
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="2"
                            d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                        </svg>
                        <!-- 文件图标 -->
                        <svg
                          v-else
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 24 24"
                          class="file-icon file-icon-default">
                          <g fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="2">
                            <path stroke-linecap="round" d="M4 4v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8.342a2 2 0 0 0-.602-1.43l-4.44-4.342A2 2 0 0 0 13.56 2H6a2 2 0 0 0-2 2m5 9h6m-6 4h3"></path>
                            <path d="M14 2v4a2 2 0 0 0 2 2h4"></path>
                          </g>
                        </svg>
                        <!-- 文件夹名称（可点击进入） -->
                        <span 
                          v-if="row.is_directory"
                          @click="enterDirectory(currentPath ? row.name : (row.user_id ? String(row.user_id) : row.name))"
                          class="file-name-link"
                          style="cursor: pointer;">
                          {{ row.display_name || row.name }}
                        </span>
                        <!-- 文件名称（可点击下载） -->
                        <a
                          v-else
                          :href="getFileDownloadUrl(row.name)"
                          @click.prevent="downloadFile(row.name)"
                          class="file-name-link">
                          {{ row.name }}
                        </a>
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
                        v-if="canDelete && isAuthenticated"
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
              <div v-else class="file-list-container">
                <div style="text-align: center; padding: 40px;">加载中...</div>
              </div>
            </div>
          </el-main>
          <el-aside style="height: 580px;width: 200px;"> 
          </el-aside>
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

.header-tip {
  display: flex;
  align-items: center;
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
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.file-name-link {
  color: var(--el-text-color-regular);
  text-decoration: none;
}

.file-name-link:hover {
  color: #EF5710;
  text-decoration: underline;
}

.el-table {
  --el-table-border-color: var(--el-border-color-lighter);
}

.el-table :deep(.el-table__row) {
  cursor: default;
}

.el-table :deep(.el-table__row:hover) {
  background-color: var(--el-fill-color-light);
}
</style>
