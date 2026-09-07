<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import apiClient from '../../lib/api.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, VideoPlay, VideoPause, Delete, Refresh, Check } from '@element-plus/icons-vue'

const apiUrl = import.meta.env.VITE_API_URL || ''

const loading = ref(false)
const cinemaList = ref([])
const stream = ref({ running: false, cinema_filename: null, playback: null })
const runtime = ref({
  mediamtx_binary_exists: false,
  mediamtx_running: false,
  playback: null,
})

const selectedCinema = ref('')
const uploading = ref(false)
const streamLoading = ref(false)
const configLoading = ref(false)
const configSaving = ref(false)
const configForm = ref({
  app: {
    prelude_seconds: 10,
    ffmpeg_bin: 'ffmpeg',
    file: 'back/config/config_back.json',
  },
  server: {
    log_level: 'info',
    rtsp_address: '127.0.0.1:8554',
    api_address: '127.0.0.1:9997',
    webrtc_address: '127.0.0.1:8889',
    webrtc_additional_hosts: '',
    file: 'back/cinema/mediamtx/cinema.yml',
  },
})

const applyConfig = (data) => {
  if (!data) return
  configForm.value = {
    app: {
      prelude_seconds: data.app?.prelude_seconds ?? 10,
      ffmpeg_bin: data.app?.ffmpeg_bin || 'ffmpeg',
      file: data.app?.file || 'back/config/config_back.json',
    },
    server: {
      log_level: data.server?.log_level || 'info',
      rtsp_address: data.server?.rtsp_address || '127.0.0.1:8554',
      api_address: data.server?.api_address || '127.0.0.1:9997',
      webrtc_address: data.server?.webrtc_address || '127.0.0.1:8889',
      webrtc_additional_hosts: (data.server?.webrtc_additional_hosts || []).join(', '),
      file: data.server?.file || 'back/cinema/mediamtx/cinema.yml',
    },
  }
}

const fetchConfig = async () => {
  configLoading.value = true
  try {
    const res = await apiClient.get(`${apiUrl}cinema/admin/config/`)
    if (res.data.success) {
      applyConfig(res.data.data)
    } else {
      ElMessage.error(res.data.error || '读取影院配置失败')
    }
  } catch {
    ElMessage.error('读取影院配置失败')
  } finally {
    configLoading.value = false
  }
}

const saveConfig = async () => {
  configSaving.value = true
  try {
    const res = await apiClient.put(`${apiUrl}cinema/admin/config/`, {
      app: {
        prelude_seconds: configForm.value.app.prelude_seconds,
        ffmpeg_bin: configForm.value.app.ffmpeg_bin,
      },
      server: {
        log_level: configForm.value.server.log_level,
        rtsp_address: configForm.value.server.rtsp_address,
        api_address: configForm.value.server.api_address,
        webrtc_address: configForm.value.server.webrtc_address,
        webrtc_additional_hosts: configForm.value.server.webrtc_additional_hosts,
      },
    })
    if (res.data.success) {
      applyConfig(res.data.data)
      ElMessage.success(res.data.message || '配置已保存')
    } else {
      ElMessage.error(res.data.error || '保存失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '保存配置失败')
  } finally {
    configSaving.value = false
  }
}

const fetchAll = async () => {
  loading.value = true
  try {
    const [listRes, runtimeRes] = await Promise.all([
      apiClient.get(`${apiUrl}cinema/admin/list/`),
      apiClient.get(`${apiUrl}cinema/admin/runtime/`),
    ])
    if (listRes.data.success) {
      const data = listRes.data.data || {}
      cinemaList.value = data.cinema || []
      stream.value = data.stream || {}
      if (!selectedCinema.value && cinemaList.value.length) {
        selectedCinema.value = cinemaList.value[0].filename
      }
    }
    if (runtimeRes.data.success) {
      runtime.value = runtimeRes.data.data || {}
    }
  } catch {
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
      headers: { 'Content-Type': 'multipart/form-data' },
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
  } catch {
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
  if (!runtime.value.mediamtx_binary_exists) {
    ElMessage.error('未部署 mediamtx，请运行 back/cinema/scripts/deploy_mediamtx.sh')
    return
  }
  streamLoading.value = true
  try {
    const res = await apiClient.post(`${apiUrl}cinema/admin/stream/start/`, {
      cinema_filename: selectedCinema.value,
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
  } catch {
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
  await Promise.all([fetchAll(), fetchConfig()])
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
      <el-button plain @click="() => Promise.all([fetchAll(), fetchConfig()])">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-alert
      v-if="!runtime.mediamtx_binary_exists"
      type="warning"
      :closable="false"
      show-icon
      title="MediaMTX 未就绪"
      class="mb-16"
    >
      <template #default>
        请在服务器执行：
        <code>back/cinema/scripts/deploy_mediamtx.sh</code>
        （需 Go 1.26+，产物输出到 <code>mediamtx_runtime/</code>）。
      </template>
    </el-alert>

    <el-alert
      v-else-if="!runtime.mediamtx_running && !stream.running"
      type="info"
      :closable="false"
      show-icon
      title="MediaMTX 未运行"
      class="mb-16"
    >
      <template #default>
        启动推流时会自动拉起 MediaMTX；也可手动运行
        <code>mediamtx_runtime/mediamtx mediamtx/cinema.yml</code>。
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
        推流中 · 片源 {{ stream.cinema_filename }} · 路径 {{ stream.path_name || 'cinema' }}
      </p>
      <p v-if="runtime.playback?.play_url" class="hint">
        播放地址：{{ runtime.playback.play_url }}
      </p>
    </el-card>

    <el-card v-loading="configLoading" shadow="never" class="mb-16">
      <template #header>
        <div class="card-header">
          <span>影院配置</span>
          <el-button type="primary" :loading="configSaving" @click="saveConfig">
            <el-icon><Check /></el-icon>
            保存配置
          </el-button>
        </div>
      </template>

      <el-form label-width="140px" class="config-form">
        <el-divider content-position="left">
          {{ configForm.app.file }}
        </el-divider>
        <el-form-item label="开播黑场秒数">
          <el-input-number
            v-model="configForm.app.prelude_seconds"
            :min="0"
            :max="120"
            :step="1"
          />
          <div class="form-tip">每次开播前插入的黑场时长，下次启动推流生效</div>
        </el-form-item>
        <el-form-item label="ffmpeg 路径">
          <el-input v-model="configForm.app.ffmpeg_bin" placeholder="ffmpeg" />
          <div class="form-tip">服务器上的 ffmpeg 可执行文件，一般填 ffmpeg</div>
        </el-form-item>

        <el-divider content-position="left">
          {{ configForm.server.file }}
        </el-divider>
        <el-form-item label="RTSP 监听">
          <el-input v-model="configForm.server.rtsp_address" placeholder="127.0.0.1:8554" />
          <div class="form-tip">本机 ffmpeg 推流入口，同机部署保持 127.0.0.1:8554</div>
        </el-form-item>
        <el-form-item label="控制 API">
          <el-input v-model="configForm.server.api_address" placeholder="127.0.0.1:9997" />
          <div class="form-tip">Django 检测流是否在线，同机部署保持 127.0.0.1:9997</div>
        </el-form-item>
        <el-form-item label="WebRTC 信令">
          <el-input v-model="configForm.server.webrtc_address" placeholder="127.0.0.1:8889" />
          <div class="form-tip">WHEP 信令由博客代理到这里，同机部署保持 127.0.0.1:8889</div>
        </el-form-item>
        <el-form-item label="日志级别">
          <el-select v-model="configForm.server.log_level" style="width: 160px">
            <el-option label="error" value="error" />
            <el-option label="warn" value="warn" />
            <el-option label="info" value="info" />
            <el-option label="debug" value="debug" />
          </el-select>
        </el-form-item>
        <el-form-item label="公网 ICE 地址">
          <el-input
            v-model="configForm.server.webrtc_additional_hosts"
            placeholder="ip地址，多个用逗号分隔"
          />
          <div class="form-tip">外网观看时填写服务器的公网 IP 需开放 8189 端口</div>
        </el-form-item>
      </el-form>
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
  margin: 8px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  word-break: break-all;
}
.status-line {
  margin: 12px 0 0;
  font-size: 14px;
  color: var(--el-color-success);
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.config-form {
  max-width: 720px;
}
.form-tip {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.4;
  color: var(--el-text-color-secondary);
}
code {
  font-size: 12px;
  word-break: break-all;
}
</style>
