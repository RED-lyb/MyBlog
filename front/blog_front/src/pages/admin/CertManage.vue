<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../../lib/api.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, Delete, Refresh } from '@element-plus/icons-vue'

const apiUrl = import.meta.env.VITE_API_URL || ''

const loading = ref(false)
const uploading = ref(false)
const installing = ref(false)
const deleting = ref(false)
const status = ref({
  pending: false,
  filename: null,
  size: 0,
  uploaded_at: null,
})

const formatSize = (size) => {
  if (!size) return '0 B'
  if (size < 1024) return `${size} B`
  return `${(size / 1024).toFixed(1)} KB`
}

const fetchStatus = async () => {
  loading.value = true
  try {
    const res = await apiClient.get(`${apiUrl}admin/nginx-cert/`)
    if (res.data.success) {
      status.value = res.data.data
    } else {
      ElMessage.error(res.data.error || '读取证书状态失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '读取证书状态失败')
  } finally {
    loading.value = false
  }
}

const handleUpload = async ({ file }) => {
  const name = (file.name || '').toLowerCase()
  if (!name.endsWith('.zip')) {
    ElMessage.error('只接受 .zip 压缩包')
    return
  }
  uploading.value = true
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await apiClient.post(`${apiUrl}admin/nginx-cert/upload/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    if (res.data.success) {
      status.value = res.data.data
      ElMessage.success(res.data.message || '上传成功')
    } else {
      ElMessage.error(res.data.error || '上传失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '上传失败')
  } finally {
    uploading.value = false
  }
}

const handleDelete = async () => {
  try {
    await ElMessageBox.confirm('确定删除待安装的证书包？', '删除证书包', {
      type: 'warning',
    })
  } catch {
    return
  }
  deleting.value = true
  try {
    const res = await apiClient.post(`${apiUrl}admin/nginx-cert/delete/`)
    if (res.data.success) {
      status.value = res.data.data
      ElMessage.success(res.data.message || '已删除')
    } else {
      ElMessage.error(res.data.error || '删除失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '删除失败')
  } finally {
    deleting.value = false
  }
}

const handleInstall = async () => {
  if (!status.value.pending) {
    ElMessage.warning('请先上传证书包')
    return
  }
  try {
    await ElMessageBox.confirm('确定用当前证书包更新 Nginx 证书？', '更新证书', {
      type: 'warning',
    })
  } catch {
    return
  }
  installing.value = true
  try {
    const res = await apiClient.post(`${apiUrl}admin/nginx-cert/install/`)
    if (res.data.success) {
      status.value = res.data.data
      ElMessage.success(res.data.message || '证书已更新')
    } else {
      ElMessage.error(res.data.error || '更新失败')
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '更新失败')
  } finally {
    installing.value = false
  }
}

onMounted(fetchStatus)
</script>

<template>
  <div class="cert-manage-container" v-loading="loading">
    <div class="page-header">
      <h1 class="page-title">证书更新</h1>
      <el-button plain @click="fetchStatus">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-card>
      <template #header>
        <span class="card-title">上传证书压缩包</span>
      </template>
      <div class="toolbar">
        <el-upload :show-file-list="false" accept=".zip,application/zip" :http-request="handleUpload">
          <el-button type="primary" plain :loading="uploading">
            <el-icon><Upload /></el-icon>
            上传 ZIP
          </el-button>
        </el-upload>
        <el-button type="primary" :loading="installing" :disabled="!status.pending" @click="handleInstall">
          更新
        </el-button>
        <el-button
          v-if="status.pending"
          type="danger"
          plain
          :loading="deleting"
          @click="handleDelete"
        >
          <el-icon><Delete /></el-icon>
          删除待安装压缩包
        </el-button>
      </div>

      <div class="status-block">
        <template v-if="status.pending">
          <p>待安装：{{ status.filename }}</p>
          <p>大小：{{ formatSize(status.size) }}</p>
          <p>上传时间：{{ status.uploaded_at }}</p>
        </template>
        <p v-else>当前没有待安装的证书压缩包</p>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.cert-manage-container {
  max-width: 900px;
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

.card-title {
  font-size: 18px;
  font-weight: bold;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar :deep(.el-button) {
  margin-left: 0;
}

.status-block p {
  margin: 0 0 6px;
  color: var(--el-text-color-primary);
}
</style>
