<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import apiClient from '../../lib/api.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, VideoPlay, VideoPause, Delete, Refresh } from '@element-plus/icons-vue'

const apiUrl = import.meta.env.VITE_API_URL || ''

const loading = ref(false)
const cinemaList = ref([])
const stream = ref({ running: false, room_id: '', user_id: '', cinema_filename: null })
const runtime = ref({ rtccli_exists: false, token_endpoint: '' })

const selectedCinema = ref('')
const roomId = ref('cinema_room')
const userId = ref('cinema_publisher')
const uploading = ref(false)
const streamLoading = ref(false)

const fetchAll = async () => {
  loading.value = true
  try {
    const [listRes, runtimeRes] = await Promise.all([
      apiClient.get(`${apiUrl}cinema/admin/list/`),
      apiClient.get(`${apiUrl}cinema/admin/runtime/`)
    ])
    if (listRes.data.success) {
      const data = listRes.data.data || {}
      cinemaList.value = data.cinema || []
      stream.value = data.stream || {}
      if (!selectedCinema.value && cinemaList.value.length) {
        selectedCinema.value = cinemaList.value[0].filename
      }
      if (stream.value.room_id) roomId.value = stream.value.room_id
      if (stream.value.user_id) userId.value = stream.value.user_id
    }
    if (runtimeRes.data.success) {
      runtime.value = runtimeRes.data.data || {}
    }
  } catch (e) {
    ElMessage.error('加载影院数据失败')
  } finally {
    loading.value = false
  }
}

const handleUpload = async ({ file }) => {
  uploading.value = true
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await apiClient.post(`${apiUrl}cinema/admin/upload/`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    if (res.data.success) {
      ElMessage.success('上传成功')
      cinemaList.value = res.data.data?.cinema || []
      if (!selectedCinema.value && cinemaList.value.length) {
        selectedCinema.value = cinemaList.value[0].filename
      }
    } else {
      ElMessage.error(res.data.error || '上传失败')
    }
  } catch (e) {
    ElMessage.error('上传失败')
  } finally {
    uploading.value = false
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(`确定删除「${row.filename}」？`, '删除影片', { type: 'warning' })
    const res = await apiClient.post(
      `${apiUrl}cinema/admin/${encodeURIComponent(row.filename)}/delete/`
    )
    if (res.data.success) {
      ElMessage.success('已删除')
      cinemaList.value = res.data.data?.cinema || []
      if (selectedCinema.value === row.filename) {
        selectedCinema.value = cinemaList.value[0]?.filename || ''
      }
    } else {
      ElMessage.error(res.data.error || '删除失败')
    }
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const startStream = async () => {
  if (!selectedCinema.value) {
    ElMessage.warning('请先选择要推流的影片')
    return
  }
  if (!runtime.value.rtccli_exists) {
    ElMessage.error('未部署 rtccli，请在 back/cinema/rtc_build 编译或运行 deploy_rtc_runtime.sh')
    return
  }
  streamLoading.value = true
  try {
    const res = await apiClient.post(`${apiUrl}cinema/admin/stream/start/`, {
      cinema_filename: selectedCinema.value,
      room_id: roomId.value,
      user_id: userId.value
    })
    if (res.data.success) {
      ElMessage.success('推流已启动')
      await fetchAll()
    } else {
      ElMessage.error(res.data.error || '启动失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '启动推流失败')
  } finally {
    streamLoading.value = false
  }
}

const stopStream = async () => {
  streamLoading.value = true
  try {
    const res = await apiClient.post(`${apiUrl}cinema/admin/stream/stop/`)
    if (res.data.success) {
      ElMessage.success('推流已停止')
      await fetchAll()
    } else {
      ElMessage.error(res.data.error || '停止失败')
    }
  } catch (e) {
    ElMessage.error('停止推流失败')
  } finally {
    streamLoading.value = false
  }
}

let pollTimer = null

const stopPolling = () => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

const startPollingIfStreaming = () => {
  stopPolling()
  if (stream.value.running) {
    pollTimer = setInterval(fetchAll, 5000)
  }
}

onMounted(async () => {
  await fetchAll()
  startPollingIfStreaming()
})

onUnmounted(() => {
  stopPolling()
})

watch(
  () => stream.value.running,
  () => {
    startPollingIfStreaming()
  }
)
</script>

<template>
  <div class="cinema-manage">
    <div class="page-header">
      <h1 class="page-title">同频影院</h1>
      <el-button plain @click="fetchAll">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-alert
      v-if="!runtime.rtccli_exists"
      type="warning"
      :closable="false"
      show-icon
      title="RTC 推流程序未就绪"
      class="mb-16"
    >
      <template #default>
        请在服务器执行：
        <code>back/cinema/scripts/deploy_rtc_runtime.sh</code>
        或在 <code>back/cinema/rtc_build</code> 下执行
        <code>cmake -Bbuild -S. &amp;&amp; cmake --build build</code>（产物输出到 <code>rtc_runtime/</code>）。
      </template>
    </el-alert>

    <el-card shadow="never" class="mb-16">
      <template #header>推流控制</template>
      <el-form label-width="100px" inline class="stream-form">
        <el-form-item label="选择影片">
          <el-select v-model="selectedCinema" placeholder="选择 MP4" style="min-width: 220px">
            <el-option
              v-for="item in cinemaList"
              :key="item.filename"
              :label="`${item.title} (${item.size_mb}MB)`"
              :value="item.filename"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="房间号">
          <el-input v-model="roomId" maxlength="128" style="width: 160px" />
        </el-form-item>
        <el-form-item label="推流用户">
          <el-input v-model="userId" maxlength="128" style="width: 160px" />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="streamLoading"
            :disabled="stream.running"
            @click="startStream"
          >
            <el-icon><VideoPlay /></el-icon>
            启动推流
          </el-button>
          <el-button
            type="danger"
            plain
            :loading="streamLoading"
            :disabled="!stream.running"
            @click="stopStream"
          >
            <el-icon><VideoPause /></el-icon>
            停止推流
          </el-button>
        </el-form-item>
      </el-form>
      <p v-if="stream.running" class="status-line">
        推流中 · 片源 {{ stream.cinema_filename }} · 房间 {{ stream.room_id }}
      </p>
    </el-card>

    <div class="toolbar mb-16">
      <el-upload :show-file-list="false" accept=".mp4,video/mp4" :http-request="handleUpload">
        <el-button type="primary" plain :loading="uploading">
          <el-icon><Upload /></el-icon>
          上传MP4视频
        </el-button>
      </el-upload>
    </div>

    <el-table v-loading="loading" :data="cinemaList" stripe>
      <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column prop="size_mb" label="大小(MB)" width="100" align="center" />
      <el-table-column prop="modified_at" label="修改时间" width="180" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag v-if="stream.running && stream.cinema_filename === row.filename" type="danger">
            推流中
          </el-tag>
          <span v-else>—</span>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-button link type="danger" @click="handleDelete(row)">
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.cinema-manage {
  padding: 0 4px;
}
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}
.page-title {
  margin: 0;
  font-size: 24px;
}
.mb-16 {
  margin-bottom: 16px;
}
.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
}
.hint {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
.status-line {
  margin: 12px 0 0;
  font-size: 14px;
  color: var(--el-color-success);
}
code {
  font-size: 12px;
  word-break: break-all;
}
</style>
