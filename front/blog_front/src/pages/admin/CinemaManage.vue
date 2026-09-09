<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import apiClient from '../../lib/api.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload, VideoPlay, VideoPause, Delete, Refresh, Check, Film } from '@element-plus/icons-vue'

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
const transcodeLoading = ref(false)
const transcodeStartedHere = ref(false)
const transcode = ref({
  status: 'idle',
  filename: null,
  percent: 0,
  error: '',
})
const mediaInfo = ref({
  duration_sec: 0,
  transcoded: false,
  width: 0,
  height: 0,
})
const mediaInfoLoading = ref(false)
const startSec = ref(0)
const startClock = ref('00:00:00')
const configLoading = ref(false)
const configSaving = ref(false)
const configForm = ref({
  app: {
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

const fetchAll = async (silent = false) => {
  if (fetchAll._inflight && silent) return
  fetchAll._inflight = true
  if (!silent) loading.value = true
  try {
    const [listRes, runtimeRes] = await Promise.all([
      apiClient.get(`${apiUrl}cinema/admin/list/`),
      apiClient.get(`${apiUrl}cinema/admin/runtime/`),
    ])
    if (listRes.data.success) {
      const data = listRes.data.data || {}
      cinemaList.value = data.cinema || []
      stream.value = data.stream || {}
      transcode.value = data.transcode || transcode.value
      if (!selectedCinema.value && cinemaList.value.length) {
        selectedCinema.value = cinemaList.value[0].filename
      }
    }
    if (runtimeRes.data.success) {
      runtime.value = runtimeRes.data.data || {}
      if (runtimeRes.data.data?.transcode) {
        transcode.value = runtimeRes.data.data.transcode
      }
    }
  } catch {
    if (!silent) ElMessage.error('加载影院数据失败')
  } finally {
    fetchAll._inflight = false
    if (!silent) loading.value = false
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
    await ElMessageBox.confirm(
      `确定删除「${row.filename}」？将同时删除原片和转码文件。`,
      '删除影片',
      { type: 'warning' }
    )
    const res = await apiClient.post(
      `${apiUrl}cinema/admin/${encodeURIComponent(row.filename)}/delete/`
    )
    if (res.data.success) {
      ElMessage.success('已删除')
      cinemaList.value = res.data.data?.cinema || []
      if (res.data.data?.transcode) {
        transcode.value = res.data.data.transcode
      }
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

const selectedRow = computed(
  () => cinemaList.value.find((item) => item.filename === selectedCinema.value) || null
)
const transcodeRunning = computed(() => transcode.value.status === 'running')
const durationSec = computed(() => Math.max(0, Math.floor(mediaInfo.value.duration_sec || 0)))
const maxStartSec = computed(() => Math.max(0, durationSec.value > 0 ? durationSec.value - 1 : 0))

const formatClock = (sec) => {
  const total = Math.max(0, Math.floor(Number(sec) || 0))
  const h = Math.floor(total / 3600)
  const m = Math.floor((total % 3600) / 60)
  const s = total % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
}

const parseClock = (text) => {
  const raw = String(text || '').trim()
  if (!raw) return 0
  if (raw.includes(':')) {
    const parts = raw.split(':').map((p) => Number(p))
    if (parts.some((n) => Number.isNaN(n))) return null
    if (parts.length === 3) return parts[0] * 3600 + parts[1] * 60 + parts[2]
    if (parts.length === 2) return parts[0] * 60 + parts[1]
    return null
  }
  const n = Number(raw)
  return Number.isNaN(n) ? null : n
}

const clampStart = (sec) => {
  const value = Math.floor(Number(sec) || 0)
  if (value < 0) return 0
  if (maxStartSec.value > 0 && value > maxStartSec.value) return maxStartSec.value
  return value
}

const applyStartSec = (sec) => {
  startSec.value = clampStart(sec)
  startClock.value = formatClock(startSec.value)
}

const onStartClockChange = () => {
  const parsed = parseClock(startClock.value)
  if (parsed === null) {
    startClock.value = formatClock(startSec.value)
    ElMessage.warning('时间格式为 hh:mm:ss')
    return
  }
  applyStartSec(parsed)
}

const fetchMediaInfo = async (filename) => {
  if (!filename) {
    mediaInfo.value = { duration_sec: 0, transcoded: false, width: 0, height: 0 }
    applyStartSec(0)
    return
  }
  mediaInfoLoading.value = true
  try {
    const res = await apiClient.get(
      `${apiUrl}cinema/admin/${encodeURIComponent(filename)}/info/`
    )
    if (res.data.success) {
      mediaInfo.value = res.data.data || mediaInfo.value
      applyStartSec(startSec.value)
    } else {
      ElMessage.error(res.data.error || '读取影片时长失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '读取影片时长失败')
  } finally {
    mediaInfoLoading.value = false
  }
}

const transcodeTag = (row) => {
  if (row.transcode_status === 'running') {
    return { type: 'warning', text: `转码中 ${row.transcode_percent || 0}%` }
  }
  if (row.transcoded) {
    return { type: 'success', text: '已转码' }
  }
  if (row.transcode_status === 'failed') {
    return { type: 'danger', text: '转码失败' }
  }
  return { type: 'info', text: '未转码' }
}

const startTranscode = async () => {
  if (!selectedCinema.value) {
    ElMessage.warning('请先选择要转码的影片')
    return
  }
  if (stream.value.running) {
    ElMessage.warning('请先停止推流再转码')
    return
  }
  if (transcodeRunning.value) {
    ElMessage.warning('已有转码任务进行中')
    return
  }
  if (selectedRow.value?.transcoded) {
    try {
      await ElMessageBox.confirm(
        '已有转码文件，确定重新转码？完成后仍是 1080p30，片头 10 秒黑屏。',
        '重新转码',
        { type: 'warning' }
      )
    } catch {
      return
    }
  }
  transcodeLoading.value = true
  try {
    const res = await apiClient.post(`${apiUrl}cinema/admin/transcode/start/`, {
      cinema_filename: selectedCinema.value,
    })
    if (res.data.success) {
      ElMessage.success(res.data.message || '已开始转码')
      transcodeStartedHere.value = true
      if (res.data.data?.cinema) {
        cinemaList.value = res.data.data.cinema
      }
      if (res.data.data?.transcode) {
        transcode.value = res.data.data.transcode
      }
      startPollingIfNeeded()
    } else {
      ElMessage.error(res.data.error || '转码启动失败')
    }
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '转码启动失败')
  } finally {
    transcodeLoading.value = false
  }
}

const startStream = async () => {
  if (!selectedCinema.value) {
    ElMessage.warning('请先选择要推流的影片')
    return
  }
  if (!selectedRow.value?.transcoded) {
    ElMessage.warning('该影片尚未转码，请先转码后再播放')
    return
  }
  if (transcodeRunning.value) {
    ElMessage.warning('正在转码，请等待完成后再播放')
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
      start_sec: startSec.value || 0,
    })
    if (res.data.success) {
      ElMessage.success(res.data.message || '放映已开始')
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

const startPollingIfNeeded = () => {
  stopPolling()
  if (stream.value.running || transcodeRunning.value) {
    pollTimer = setInterval(() => fetchAll(true), transcodeRunning.value ? 2000 : 5000)
  }
}

onMounted(async () => {
  await Promise.all([fetchAll(), fetchConfig()])
  startPollingIfNeeded()
})

onUnmounted(() => {
  stopPolling()
})

watch([() => stream.value.running, transcodeRunning], () => {
  startPollingIfNeeded()
})

watch(
  () => selectedCinema.value,
  (name) => {
    applyStartSec(0)
    fetchMediaInfo(name)
  }
)

watch(
  () => [transcode.value.status, transcode.value.filename, transcode.value.error],
  ([status]) => {
    if (!transcodeStartedHere.value) return
    if (status === 'done') {
      transcodeStartedHere.value = false
      ElMessage.success(`「${transcode.value.filename || '影片'}」转码完成`)
      if (transcode.value.filename === selectedCinema.value) {
        fetchMediaInfo(selectedCinema.value)
      }
    } else if (status === 'failed') {
      transcodeStartedHere.value = false
      ElMessage.error(transcode.value.error || '转码失败')
    }
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
              :label="`${item.title} (${item.size_mb}MB)${item.transcoded ? ' · 已转码' : ' · 未转码'}`"
              :value="item.filename"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button
            type="warning"
            plain
            :loading="transcodeLoading || transcodeRunning"
            :disabled="stream.running || !selectedCinema"
            @click="startTranscode"
          >
            <el-icon><Film /></el-icon>
            {{
              transcodeRunning && transcode.filename === selectedCinema
                ? `转码中 ${transcode.percent || 0}%`
                : '转码'
            }}
          </el-button>
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
        <el-form-item label="开播位置" class="start-form-item">
          <div class="start-picker" v-loading="mediaInfoLoading">
            <el-slider
              :model-value="startSec"
              :min="0"
              :max="maxStartSec || 0"
              :step="1"
              :disabled="!durationSec || stream.running"
              :format-tooltip="formatClock"
              @update:model-value="applyStartSec"
            />
            <el-input
              v-model="startClock"
              class="start-clock"
              placeholder="00:00:00"
              :disabled="!durationSec || stream.running"
              @change="onStartClockChange"
            />
            <span class="start-duration">
              {{ formatClock(startSec) }} / {{ formatClock(durationSec) }}
            </span>
          </div>
        </el-form-item>
      </el-form>
      <p v-if="stream.running" class="status-line">
        推流中 · 片源 {{ stream.cinema_filename }}
        <span v-if="stream.start_sec"> · 从 {{ formatClock(stream.start_sec) }} 起</span>
        · 路径 {{ stream.path_name || 'cinema' }}
      </p>
      <p v-else-if="transcodeRunning" class="status-line transcode-line">
        正在转码 {{ transcode.filename }} · {{ transcode.percent || 0 }}%
      </p>
      <p class="hint">
        推流只播放转码后的 1080p30 文件（片头 10 秒黑屏）。未转码无法开播。开播位置默认片头，可拖到任意时间续播。
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
      <el-table-column label="转码" width="130" align="center">
        <template #default="{ row }">
          <el-tag :type="transcodeTag(row).type" size="small">
            {{ transcodeTag(row).text }}
          </el-tag>
        </template>
      </el-table-column>
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
.stream-form {
  width: 100%;
}
.start-form-item {
  display: flex;
  width: 100%;
  flex-basis: 100%;
  margin-right: 0;
}
.start-form-item :deep(.el-form-item__content) {
  flex: 1;
  max-width: 720px;
}
.start-picker {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  min-height: 32px;
}
.start-picker .el-slider {
  flex: 1;
}
.start-clock {
  width: 110px;
  flex-shrink: 0;
}
.start-duration {
  flex-shrink: 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}
.status-line.transcode-line {
  color: var(--el-color-warning);
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
