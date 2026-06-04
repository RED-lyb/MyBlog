<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import FullScreenLoading from '../pages/FullScreenLoading.vue'
import apiClient from '../lib/api.js'
import { ElMessage } from 'element-plus'

const apiUrl = import.meta.env.VITE_API_URL || ''

const loading = ref(true)
const cinemaList = ref([])
const stream = ref({
  running: false,
  room_id: '',
  user_id: '',
  cinema_filename: null,
  app_id: '',
  started_at: null
})

let pollTimer = null

const staticRoot = computed(() => apiUrl.replace(/\/?$/, ''))

const videoSrc = (item) => {
  const f = (item.filename || '').trim()
  if (!f) return ''
  return `${staticRoot.value}/static/cinema/${encodeURIComponent(f)}`
}

const fetchCinemaList = async () => {
  loading.value = true
  try {
    const response = await apiClient.get(`${apiUrl}cinema/list/`)
    if (response.data.success) {
      const data = response.data.data || {}
      cinemaList.value = data.cinema || []
      stream.value = data.stream || stream.value
    } else {
      ElMessage.error(response.data.error || '获取片库失败')
      cinemaList.value = []
    }
  } catch (e) {
    console.error(e)
    ElMessage.error('获取片库失败')
    cinemaList.value = []
  } finally {
    loading.value = false
  }
}

const refreshStreamOnly = async () => {
  try {
    const response = await apiClient.get(`${apiUrl}cinema/stream/status/`)
    if (response.data.success) {
      stream.value = { ...stream.value, ...response.data.data }
    }
  } catch (e) {
    console.error(e)
  }
}

onMounted(() => {
  fetchCinemaList()
  pollTimer = setInterval(refreshStreamOnly, 8000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <div class="cinema-page-inner">
    <div class="content-header">
      <h1>同频影院</h1>
      <p class="subtitle">通过火山 RTC 同步观影；管理员在后台选择影片并启动推流后，可使用相同房间号加入观看。</p>
    </div>

    <el-alert
      v-if="stream.running"
      type="success"
      :closable="false"
      show-icon
      class="stream-alert"
      title="正在放映"
    >
      <template #default>
        <div class="stream-meta">
          <span>房间：<strong>{{ stream.room_id }}</strong></span>
          <span>推流端：<strong>{{ stream.user_id }}</strong></span>
          <span v-if="stream.cinema_filename">片源：<strong>{{ stream.cinema_filename }}</strong></span>
          <span v-if="stream.app_id">App ID：<code>{{ stream.app_id }}</code></span>
        </div>
      </template>
    </el-alert>
    <el-alert
      v-else
      type="info"
      :closable="false"
      show-icon
      class="stream-alert"
      title="当前暂无推流"
      description="请管理员在「管理后台 → 同频影院」上传 H.264 MP4 并启动推流。"
    />

    <FullScreenLoading :visible="loading" />

    <div v-if="!loading && cinemaList.length === 0" class="empty-hint">
      暂无影片，请管理员上传 MP4 至影院片库
    </div>

    <div v-else-if="!loading" class="cinema-grid">
      <el-card
        v-for="item in cinemaList"
        :key="item.filename"
        class="cinema-card"
        shadow="never"
        :class="{ 'is-live': stream.running && stream.cinema_filename === item.filename }"
      >
        <template #header>
          <div class="card-head">
            <span class="head-title">{{ item.title }}</span>
            <el-tag
              v-if="stream.running && stream.cinema_filename === item.filename"
              type="danger"
              size="small"
            >
              LIVE
            </el-tag>
          </div>
        </template>
        <div class="card-body">
          <div class="video-thumb">
            <video
              v-if="item.filename"
              :src="videoSrc(item)"
              preload="metadata"
              muted
              playsinline
            />
          </div>
          <p class="intro">{{ item.filename }} · {{ item.size_mb }} MB</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.content-header {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 12px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--el-border-color-light);
}
.subtitle {
  font-size: 14px;
  font-weight: normal;
  color: var(--el-text-color-secondary);
  margin: 0 0 8px;
}
.stream-alert {
  margin-bottom: 20px;
}
.stream-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 14px;
}
.empty-hint {
  text-align: center;
  color: var(--el-text-color-secondary);
  padding: 48px 0;
}
.cinema-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.cinema-card.is-live {
  border-color: var(--el-color-danger);
}
.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.head-title {
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.video-thumb {
  aspect-ratio: 16 / 9;
  background: #000;
  border-radius: 4px;
  overflow: hidden;
}
.video-thumb video {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.intro {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--el-text-color-secondary);
}
</style>
