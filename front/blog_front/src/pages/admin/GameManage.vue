<template>
  <div class="game-manage-container">
    <div class="page-header">
      <h1 class="page-title">游戏管理</h1>
      <el-button type="primary" plain @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建游戏
      </el-button>
    </div>

    <div class="filter-bar">
      <div class="filter-right" v-if="selectedRows.length > 0">
        <el-button type="danger" plain @click="handleBatchDelete">
          <el-icon><Delete /></el-icon>
          删除
        </el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="gameList"
      stripe
      table-layout="auto"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" />
      <el-table-column prop="id" label="ID" width="72" align="center" />
      <el-table-column label="封面" width="88" align="center">
        <template #default="{ row }">
          <div class="thumb-cell">
            <img
              v-if="row.content"
              :src="thumbUrl(row.content)"
              alt=""
              class="thumb-img"
              @error="(e) => (e.target.style.visibility = 'hidden')"
            />
            <span v-else class="thumb-empty">无</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="140" show-overflow-tooltip />
      <el-table-column
        prop="introduction"
        label="卡片简介"
        min-width="160"
        show-overflow-tooltip
      />
      <el-table-column prop="detail" label="详情预览" min-width="200" show-overflow-tooltip />
      <el-table-column label="平台链接" width="120" align="center">
        <template #default="{ row }">
          <span class="link-brief">{{ platformBrief(row) }}</span>
        </template>
      </el-table-column>
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

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="150px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="formData.title" placeholder="游戏卡片标题（必填）" maxlength="255" show-word-limit />
        </el-form-item>

        <el-form-item label="封面图">
          <div class="cover-tools">
            <el-upload
              :show-file-list="false"
              accept="image/*"
              :http-request="handleCoverPick"
            >
              <el-button type="primary" plain>选择图片</el-button>
            </el-upload>
            <span v-if="pendingCoverFile" class="fname"
              >已选：{{ pendingCoverFile.name }}（点击确定后上传）</span
            >
            <span v-else-if="formData.content && !coverRemoved" class="fname">{{
              formData.content
            }}</span>
            <el-button
              v-if="pendingCoverFile || (formData.content && !coverRemoved)"
              link
              type="danger"
              @click="clearCover"
              >移除图片</el-button
            >
          </div>
          <div v-if="coverPreviewSrc" class="cover-preview">
            <img :src="coverPreviewSrc" alt="预览" />
          </div>
        </el-form-item>

        <el-form-item label="卡片简介" prop="introduction">
          <el-input
            v-model="formData.introduction"
            type="textarea"
            :rows="3"
            placeholder="游戏卡片简介（必填）"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>

        <el-form-item label="详情" prop="detail">
          <el-input
            v-model="formData.detail"
            type="textarea"
            :rows="8"
            placeholder="游戏详情描述（必填）"
          />
        </el-form-item>

        <el-form-item label="Web 端">
          <div class="asset-line">
            <el-upload
              :show-file-list="false"
              accept=".zip,application/zip"
              :http-request="handleWebZipPick"
            >
              <el-button type="primary" plain>选择zip压缩包</el-button>
            </el-upload>
            <span v-if="pendingWebZip" class="fname"
              >已选：{{ pendingWebZip.name }}</span
            >
            <span v-else-if="formData.web_entry" class="fname"
              >已部署：{{ formData.web_entry }}</span
            >
            <el-button
              v-if="formData.web_entry && !pendingWebZip"
              link
              type="danger"
              @click="clearDeployedWeb"
              >清除已部署 Web</el-button
            >
            <el-button v-if="pendingWebZip" link type="danger" @click="clearPendingWebZip"
              >取消压缩包选择</el-button
            >
          </div>
        </el-form-item>

        <el-form-item label="Windows 包">
          <div class="asset-line">
            <el-upload
              :show-file-list="false"
              :http-request="(o) => handlePlatformPick('windows', o)"
            >
              <el-button type="primary" plain>选择文件</el-button>
            </el-upload>
            <span v-if="pendingWindows" class="fname">{{ pendingWindows.name }}</span>
            <span v-else-if="formData.windows" class="fname">已部署：{{ formData.windows }}</span>
            <el-button
              v-if="pendingWindows || formData.windows"
              link
              type="danger"
              @click="clearPlatform('windows')"
              >移除</el-button
            >
          </div>
        </el-form-item>
        <el-form-item label="Linux 包">
          <div class="asset-line">
            <el-upload
              :show-file-list="false"
              :http-request="(o) => handlePlatformPick('linux', o)"
            >
              <el-button type="primary" plain>选择文件</el-button>
            </el-upload>
            <span v-if="pendingLinux" class="fname">{{ pendingLinux.name }}</span>
            <span v-else-if="formData.linux" class="fname">已部署：{{ formData.linux }}</span>
            <el-button
              v-if="pendingLinux || formData.linux"
              link
              type="danger"
              @click="clearPlatform('linux')"
              >移除</el-button
            >
          </div>
        </el-form-item>
        <el-form-item label="Android 包">
          <div class="asset-line">
            <el-upload
              :show-file-list="false"
              :http-request="(o) => handlePlatformPick('android', o)"
            >
              <el-button type="primary" plain>选择文件</el-button>
            </el-upload>
            <span v-if="pendingAndroid" class="fname">{{ pendingAndroid.name }}</span>
            <span v-else-if="formData.android" class="fname">已部署：{{ formData.android }}</span>
            <el-button
              v-if="pendingAndroid || formData.android"
              link
              type="danger"
              @click="clearPlatform('android')"
              >移除</el-button
            >
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" plain @click="handleSubmit" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL || ''

const staticRoot = computed(() => apiUrl.replace(/\/?$/, ''))

const loading = ref(false)
const gameList = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const selectedRows = ref([])

const allGamesCache = ref([])

const dialogVisible = ref(false)
const dialogTitle = ref('新建游戏')
const submitting = ref(false)
const formRef = ref(null)
const formData = ref({
  id: null,
  title: '',
  content: '',
  introduction: '',
  detail: '',
  web_entry: '',
  windows: '',
  linux: '',
  android: ''
})

/** 弹窗内新选文件，仅本地预览，确定时再上传 */
const pendingCoverFile = ref(null)
/** blob 预览地址，需在关闭/移除时 revoke */
const coverPreviewObjectUrl = ref('')
/** 编辑时用户主动移除封面（保存时需清空服务端文件与字段） */
const coverRemoved = ref(false)

const pendingWebZip = ref(null)
const webBundleRemoved = ref(false)
const pendingWindows = ref(null)
const pendingLinux = ref(null)
const pendingAndroid = ref(null)

const formRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  introduction: [{ required: true, message: '请输入卡片简介', trigger: 'blur' }],
  detail: [{ required: true, message: '请输入详情', trigger: 'blur' }]
}

const revokeCoverPreview = () => {
  if (coverPreviewObjectUrl.value) {
    URL.revokeObjectURL(coverPreviewObjectUrl.value)
    coverPreviewObjectUrl.value = ''
  }
}

const coverPreviewSrc = computed(() => {
  if (coverPreviewObjectUrl.value) return coverPreviewObjectUrl.value
  if (coverRemoved.value) return ''
  const f = (formData.value.content || '').trim()
  if (!f) return ''
  return `${staticRoot.value}/static/games/game_images/${encodeURIComponent(f)}`
})

const thumbUrl = (filename) => {
  const f = (filename || '').trim()
  if (!f) return ''
  return `${staticRoot.value}/static/games/game_images/${encodeURIComponent(f)}`
}

const platformBrief = (row) => {
  const parts = []
  if (row.has_web || row.web_entry) parts.push('Web')
  if (row.has_windows || row.windows) parts.push('Win')
  if (row.has_linux || row.linux) parts.push('Linux')
  if (row.has_android || row.android) parts.push('And')
  return parts.length ? parts.join(' / ') : '—'
}

const slicePage = () => {
  const start = (currentPage.value - 1) * pageSize.value
  gameList.value = allGamesCache.value.slice(start, start + pageSize.value)
  total.value = allGamesCache.value.length
}

const fetchGames = async () => {
  loading.value = true
  try {
    const response = await apiClient.get(`${apiUrl}games/admin/list/`)
    if (response.data.success) {
      allGamesCache.value = response.data.data.games || []
      slicePage()
    } else {
      ElMessage.error(response.data.error || '获取游戏列表失败')
    }
  } catch (e) {
    ElMessage.error('获取游戏列表失败')
  } finally {
    loading.value = false
  }
}

const handleSizeChange = () => {
  currentPage.value = 1
  slicePage()
}

const handlePageChange = () => {
  slicePage()
}

const handleSelectionChange = (rows) => {
  selectedRows.value = rows
}

const resetCoverDraft = () => {
  revokeCoverPreview()
  pendingCoverFile.value = null
  coverRemoved.value = false
  pendingWebZip.value = null
  webBundleRemoved.value = false
  pendingWindows.value = null
  pendingLinux.value = null
  pendingAndroid.value = null
}

watch(dialogVisible, (open) => {
  if (!open) {
    resetCoverDraft()
  }
})

const handleCreate = () => {
  dialogTitle.value = '新建游戏'
  resetCoverDraft()
  formData.value = {
    id: null,
    title: '',
    content: '',
    introduction: '',
    detail: '',
    web_entry: '',
    windows: '',
    linux: '',
    android: ''
  }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑游戏'
  resetCoverDraft()
  formData.value = {
    id: row.id,
    title: row.title || '',
    content: row.content || '',
    introduction: row.introduction || '',
    detail: row.detail || '',
    web_entry: row.web_entry || '',
    windows: row.windows || '',
    linux: row.linux || '',
    android: row.android || ''
  }
  dialogVisible.value = true
}

const clearCover = () => {
  revokeCoverPreview()
  pendingCoverFile.value = null
  coverRemoved.value = true
  formData.value.content = ''
}

/** 仅本地选择文件，不请求服务器 */
const handleCoverPick = (options) => {
  try {
    revokeCoverPreview()
    pendingCoverFile.value = options.file
    coverRemoved.value = false
    coverPreviewObjectUrl.value = URL.createObjectURL(options.file)
    options.onSuccess()
  } catch (e) {
    options.onError(e)
  }
}

const clearPendingWebZip = () => {
  pendingWebZip.value = null
}

const clearDeployedWeb = () => {
  webBundleRemoved.value = true
  formData.value.web_entry = ''
  pendingWebZip.value = null
}

const handleWebZipPick = (options) => {
  try {
    pendingWebZip.value = options.file
    webBundleRemoved.value = false
    options.onSuccess()
  } catch (e) {
    options.onError(e)
  }
}

const handlePlatformPick = (plat, options) => {
  try {
    if (plat === 'windows') pendingWindows.value = options.file
    if (plat === 'linux') pendingLinux.value = options.file
    if (plat === 'android') pendingAndroid.value = options.file
    options.onSuccess()
  } catch (e) {
    options.onError(e)
  }
}

const clearPlatform = (plat) => {
  if (plat === 'windows') {
    pendingWindows.value = null
    formData.value.windows = ''
  }
  if (plat === 'linux') {
    pendingLinux.value = null
    formData.value.linux = ''
  }
  if (plat === 'android') {
    pendingAndroid.value = null
    formData.value.android = ''
  }
}

const uploadWebZip = (gameId) => {
  const fd = new FormData()
  fd.append('file', pendingWebZip.value)
  return apiClient.post(`${apiUrl}games/admin/${gameId}/upload-web-zip/`, fd)
}

const uploadPlatform = (gameId, platform, file) => {
  const fd = new FormData()
  fd.append('platform', platform)
  fd.append('file', file)
  return apiClient.post(`${apiUrl}games/admin/${gameId}/upload-platform/`, fd)
}

const postGameCover = (gameId, file) => {
  const fd = new FormData()
  fd.append('file', file)
  return apiClient.post(`${apiUrl}games/admin/${gameId}/upload-image/`, fd)
}

const runAssetUploads = async (gameId) => {
  if (pendingWebZip.value) {
    const r = await uploadWebZip(gameId)
    if (!r.data.success) {
      ElMessage.error(r.data?.error || 'Web 资源部署失败')
      throw new Error('web zip')
    }
    if (r.data.data?.web_entry) {
      formData.value.web_entry = r.data.data.web_entry
    }
  }
  if (pendingWindows.value) {
    const r = await uploadPlatform(gameId, 'windows', pendingWindows.value)
    if (!r.data.success) {
      ElMessage.error(r.data?.error || 'Windows 包上传失败')
      throw new Error('win')
    }
    if (r.data.data?.windows) formData.value.windows = r.data.data.windows
  }
  if (pendingLinux.value) {
    const r = await uploadPlatform(gameId, 'linux', pendingLinux.value)
    if (!r.data.success) {
      ElMessage.error(r.data?.error || 'Linux 包上传失败')
      throw new Error('linux')
    }
    if (r.data.data?.linux) formData.value.linux = r.data.data.linux
  }
  if (pendingAndroid.value) {
    const r = await uploadPlatform(gameId, 'android', pendingAndroid.value)
    if (!r.data.success) {
      ElMessage.error(r.data?.error || 'Android 包上传失败')
      throw new Error('android')
    }
    if (r.data.data?.android) formData.value.android = r.data.data.android
  }
}

const payloadFromForm = (contentOverride) => {
  const c =
    contentOverride !== undefined
      ? contentOverride === null || contentOverride === ''
        ? null
        : String(contentOverride).trim() || null
      : (formData.value.content || '').trim() || null
  let webEntryVal = (formData.value.web_entry || '').trim() || null
  if (webBundleRemoved.value) {
    webEntryVal = null
  }
  return {
    title: formData.value.title.trim(),
    content: c,
    introduction: formData.value.introduction.trim(),
    detail: formData.value.detail.trim(),
    web_entry: webEntryVal,
    windows: (formData.value.windows || '').trim() || null,
    linux: (formData.value.linux || '').trim() || null,
    android: (formData.value.android || '').trim() || null
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    if (formData.value.id) {
      let contentForDb = (formData.value.content || '').trim()
      if (coverRemoved.value) {
        contentForDb = ''
      } else if (pendingCoverFile.value) {
        const up = await postGameCover(formData.value.id, pendingCoverFile.value)
        if (!up.data.success || !up.data.data?.filename) {
          ElMessage.error(up.data?.error || '封面上传失败')
          return
        }
        contentForDb = up.data.data.filename
      }
      const body = payloadFromForm(contentForDb)
      const response = await apiClient.put(
        `${apiUrl}games/admin/${formData.value.id}/update/`,
        body
      )
      if (!response.data.success) {
        ElMessage.error(response.data.error || '更新失败')
        return
      }
      try {
        await runAssetUploads(formData.value.id)
      } catch {
        ElMessage.warning('基本信息已保存，但部分资源包上传失败，可重新编辑后上传')
      }
      ElMessage.success('游戏已更新')
      dialogVisible.value = false
      allGamesCache.value = []
      await fetchGames()
    } else {
      const response = await apiClient.post(`${apiUrl}games/admin/create/`, payloadFromForm(null))
      if (!response.data.success) {
        ElMessage.error(response.data.error || '创建失败')
        return
      }
      const newId = response.data.data?.id
      if (pendingCoverFile.value && newId) {
        const up = await postGameCover(newId, pendingCoverFile.value)
        if (!up.data.success) {
          ElMessage.warning(
            `游戏记录已创建，但封面上传失败：${up.data?.error || '未知错误'}`
          )
        }
      }
      if (newId) {
        try {
          await runAssetUploads(newId)
        } catch {
          ElMessage.warning('游戏已创建，但部分资源包上传失败，请编辑后重试')
        }
      }
      ElMessage.success('游戏已创建')
      dialogVisible.value = false
      allGamesCache.value = []
      await fetchGames()
    }
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    submitting.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除游戏「${row.title}」吗？`, '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(async () => {
      try {
        const response = await apiClient.delete(`${apiUrl}games/admin/${row.id}/delete/`)
        if (response.data.success) {
          ElMessage.success('删除成功')
          allGamesCache.value = []
          await fetchGames()
        } else {
          ElMessage.error(response.data.error || '删除失败')
        }
      } catch (e) {
        ElMessage.error('删除失败')
      }
    })
    .catch(() => {})
}

const handleBatchDelete = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning('请选择要删除的游戏')
    return
  }
  ElMessageBox.confirm(
    `确定删除选中的 ${selectedRows.value.length} 个游戏吗？`,
    '确认批量删除',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(async () => {
      let ok = 0
      let fail = 0
      for (const g of selectedRows.value) {
        try {
          const response = await apiClient.delete(`${apiUrl}games/admin/${g.id}/delete/`)
          if (response.data.success) ok++
          else fail++
        } catch {
          fail++
        }
      }
      selectedRows.value = []
      allGamesCache.value = []
      await fetchGames()
      if (fail === 0) ElMessage.success(`已删除 ${ok} 条`)
      else ElMessage.warning(`成功 ${ok} 条，失败 ${fail} 条`)
    })
    .catch(() => {})
}

onMounted(() => {
  fetchGames()
})
</script>

<style scoped>
.game-manage-container {
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
  justify-content: flex-end;
  align-items: center;
  min-height: 32px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.cover-tools {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.fname {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  word-break: break-all;
}

.cover-preview {
  margin-top: 10px;
  max-width: 280px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
}

.cover-preview img {
  width: 100%;
  display: block;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 8px;
  line-height: 1.4;
}

.thumb-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 48px;
}

.thumb-img {
  width: 72px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid var(--el-border-color-lighter);
}

.thumb-empty {
  font-size: 12px;
  color: var(--el-text-color-placeholder);
}

.link-brief {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.asset-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.asset-label {
  flex-shrink: 0;
}
</style>
