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
import NetworkDiskMain from '../components/network_disk_main.vue'
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
const isDownloadingFile = ref(false) // 标记是否正在处理文件下载

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

// 处理进入目录（从组件接收）
const handleEnterDirectory = (row) => {
  if (row.is_directory) {
    if (!currentPath.value && row.user_id) {
      updateUrl(String(row.user_id))
    } else {
      const dirName = currentPath.value ? row.name : (row.user_id ? String(row.user_id) : row.name)
      enterDirectory(dirName)
    }
  }
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
  const filePath = getFullPath(fileName)
  const downloadUrl = getFileDownloadUrl(fileName)
  
  // 使用隐藏的 a 标签触发下载，避免页面跳转
  const link = document.createElement('a')
  link.href = downloadUrl
  link.style.display = 'none'
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  // 下载后不需要跳转，因为已经在正确的目录了
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

// 批量删除项目
const deleteItems = async (items) => {
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  
  try {
    let successCount = 0
    let failCount = 0
    
    // 逐个删除
    for (const item of items) {
      try {
        const itemPath = getFullPath(item.name)
        const response = await apiClient.delete(`${apiUrl}network_disk/delete/${encodeURIComponent(itemPath)}`)
        if (response.data?.success) {
          successCount++
        } else {
          failCount++
        }
      } catch (error) {
        failCount++
        console.error(`删除 ${item.name} 失败:`, error)
      }
    }
    
    if (failCount === 0) {
      ElMessage.success(`成功删除 ${successCount} 个项目`)
    } else if (successCount > 0) {
      ElMessage.warning(`成功删除 ${successCount} 个项目，${failCount} 个项目删除失败`)
    } else {
      ElMessage.error('删除失败')
    }
    
    fetchFileList() // 从 URL 读取路径
  } catch (error) {
    console.error('删除错误:', error)
    ElMessage.error('删除失败')
  }
}

// 编辑文件（占位函数，可以根据需要实现）
const editFile = (file) => {
  ElMessage.info(`编辑文件功能待实现: ${file.name}`)
}

// 递归查找第一个存在的父目录
const findValidParentPath = async (filePath) => {
  const pathParts = filePath.split('/').filter(p => p)
  
  // 从完整路径开始，逐步向上查找
  for (let i = pathParts.length; i > 0; i--) {
    const testPath = pathParts.slice(0, i).join('/')
    
    try {
      const response = await apiClient.get(`${apiUrl}network_disk/list/`, {
        params: { path: testPath }
      })
      if (response.data?.success) {
        return testPath // 找到有效的目录
      }
    } catch (error) {
      // 继续尝试上一级
      continue
    }
  }
  
  // 如果都找不到，返回根目录
  return ''
}

// 触发文件下载并跳转到父路径
const triggerFileDownload = async (filePath, isFileNotFound = false) => {
  const downloadUrl = `${apiUrl}network_disk/download/${encodeURIComponent(filePath)}`
  
  // 如果文件不存在，递归查找第一个有效的父目录
  if (isFileNotFound) {
    const validPath = await findValidParentPath(filePath)
    
    // 确保标记已重置，让路由监听能够正常处理
    isDownloadingFile.value = false
    
    // 更新URL到有效路径，这会触发路由监听并加载数据
    updateUrl(validPath)
    
    // 显示提示
    ElMessage.warning('文件不存在，已跳转到可访问的目录')
    return
  }
  
  // 文件存在，正常下载
  // 获取父路径（文件的上一层目录）
  const pathParts = filePath.split('/').filter(p => p)
  let parentPath = ''
  if (pathParts.length > 1) {
    pathParts.pop() // 移除文件名，获取父目录
    parentPath = pathParts.join('/')
  }
  
  // 使用隐藏的 a 标签触发下载，避免页面跳转
  const link = document.createElement('a')
  link.href = downloadUrl
  link.style.display = 'none'
  link.download = '' // 让浏览器使用服务器返回的文件名
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  // 延迟更新URL到父路径，确保下载已开始
  setTimeout(() => {
    // 先重置标记，让路由监听能够正常处理
    isDownloadingFile.value = false
    
    // 然后更新URL，这会触发路由监听并加载数据
    if (parentPath) {
      updateUrl(parentPath)
    } else {
      // 如果路径只有文件名，返回根目录
      router.push({ name: 'network_disk' })
    }
  }, 200)
}

// 检查文件是否存在（静默检查，不显示错误信息，不触发下载）
const checkFileExists = async (filePath) => {
  try {
    // 使用 fetch API 静默检查文件是否存在
    // 使用 Range 请求只获取第一个字节，避免下载整个文件
    const downloadUrl = `${apiUrl}network_disk/download/${encodeURIComponent(filePath)}`
    const response = await fetch(downloadUrl, {
      method: 'GET',
      headers: {
        'Range': 'bytes=0-0' // 只请求第一个字节
      },
      credentials: 'include'
    })
    
    // 如果状态码是 404，说明文件不存在
    if (response.status === 404) {
      // 读取响应内容以避免显示 JSON，但不使用它
      try {
        const text = await response.text()
        // 如果响应是 JSON 错误信息，解析它但不显示
        try {
          JSON.parse(text)
        } catch (e) {
          // 不是 JSON，忽略
        }
      } catch (e) {
        // 忽略读取错误
      }
      return false
    }
    
    // 206 表示部分内容（Range 请求成功），200 表示完整内容，都说明文件存在
    // 读取响应内容以避免显示，但不使用它
    if (response.status === 200 || response.status === 206) {
      try {
        await response.blob()
      } catch (e) {
        // 忽略读取错误
      }
      return true
    }
    
    return false
  } catch (error) {
    // 网络错误或其他错误，返回 false
    return false
  }
}

// 监听路由变化
watch(() => route.params.path, async () => {
  // 如果正在处理文件下载，跳过
  if (isDownloadingFile.value) {
    return
  }
  
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
        // 先尝试递归查找有效目录（避免暴露后端URL）
        const validPath = await findValidParentPath(path)
        
        // 如果找到的有效路径与当前路径不同，说明当前路径不存在或不是目录
        if (validPath !== path) {
          // 检查文件是否真的存在（静默检查，不显示错误信息）
          const fileExists = await checkFileExists(path)
          
          if (fileExists) {
            // 文件存在，正常下载（不暴露后端URL）
            await triggerFileDownload(path, false)
          } else {
            // 文件不存在，跳转到有效目录（不暴露后端URL）
            await triggerFileDownload(path, true)
          }
        } else {
          // 如果有效路径与当前路径相同，说明当前路径可能是有效的目录
          // 但 fetchFileList 失败了，这不应该发生
          // 为了安全，直接跳转到根目录
          ElMessage.warning('路径不存在，已跳转到根目录')
          router.push({ name: 'network_disk' })
        }
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
          <el-aside style="height: 570px;width: 200px;" v-if="currentOwnerId">
            <UserInfoSidebar :user-id="currentOwnerId" />
          </el-aside>
          <el-aside style="height: 570px;width: 200px;" v-else></el-aside>
          <el-main style="min-height: 570px;" class="network-disk-main">
            <NetworkDiskMain
              :directories="directories"
              :files="files"
              :loading-files="loadingFiles"
              :path-parts="pathParts"
              :path-usernames="pathUsernames"
              :current-path="currentPath"
              :can-delete="canDelete"
              :is-authenticated="isAuthenticated"
              :current-owner-id="currentOwnerId"
              :user-id="userId"
              @navigate-to-path="updateUrl"
              @enter-directory="handleEnterDirectory"
              @download-file="downloadFile"
              @delete-items="deleteItems"
              @edit-file="editFile"
            />
          </el-main>
          <el-aside style="height: 580px;width: 200px;">
            <div class="disk-header">
              <div class="header-actions" v-if="canWrite && isAuthenticated">
                <el-button type="primary" :icon="Plus" @click="mkdirDialogVisible = true" style="width: 100%; margin-bottom: 10px;">新建文件夹</el-button>
                <el-button type="success" :icon="Upload" @click="uploadDialogVisible = true" style="width: 100%;">上传文件</el-button>
              </div>
              <div v-else-if="!isAuthenticated" class="header-tip">
                <el-text type="info">访客模式：只能浏览和下载</el-text>
              </div>
              <div v-else class="header-tip">
                <el-text type="info">当前目录只读</el-text>
              </div>
            </div>
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
  padding: 10px 20px 20px 20px;
  border: 1px solid var(--el-border-color-light);
  margin-top: 10px;
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
}

.network-disk-container {
  max-width: 1400px;
  margin: 0 auto;
}

.disk-header {
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.header-tip {
  display: flex;
  align-items: center;
  padding: 10px;
}
</style>
