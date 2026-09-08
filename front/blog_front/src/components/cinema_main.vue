<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessage } from 'element-plus'
import { FullScreen, VideoPlay } from '@element-plus/icons-vue'
import FullScreenLoading from '../pages/FullScreenLoading.vue'
import { fetchCinemaList, fetchCinemaStreamStatus } from '../lib/cinemaApi.js'
import { startCinemaStreamPoll, stopCinemaStreamPoll } from '../lib/cinemaStreamPoll.js'
import { resolveViewerIdentity } from '../lib/cinemaViewerIdentity.js'
import { showCinemaLoginDialog } from '../lib/guestDialog.js'
import { CinemaViewer } from '../lib/cinemaViewer.js'

const authStore = useAuthStore()
const router = useRouter()
const { username } = storeToRefs(authStore)

const loading = ref(true)
const playerPhase = ref('idle')
const playerError = ref('')
const needUserGesture = ref(false)
const gestureLoading = ref(false)
const hasStream = ref(false)

const streamConfig = ref({
  running: false,
  cinema_filename: null,
  playback: null,
  started_at: null,
  prelude_seconds: 10,
})

const videoRef = ref(null)
const playerShellRef = ref(null)
const viewerIdentity = ref({ displayName: '' })
const isMobileLayout = ref(false)
const isMobileFsLandscape = ref(false)

const MOBILE_MEDIA = '(max-width: 768px)'
const STATUS_POLL_MS = 5000

let statusPollInFlight = false
let preludeTimer = null
let connectGeneration = 0
const preludeClock = ref(Date.now())
const preludeEndsAtClient = ref(0)

const syncMobileLayout = () => {
  isMobileLayout.value = window.matchMedia(MOBILE_MEDIA).matches
}

const onFullscreenChange = () => {
  const el = playerShellRef.value
  const active = !!el && document.fullscreenElement === el
  isMobileFsLandscape.value = active && isMobileLayout.value
  if (!active) {
    try {
      screen.orientation?.unlock?.()
    } catch {
      // ignore
    }
  }
}

const viewer = new CinemaViewer({
  onStreamStart: () => {
    hasStream.value = true
    startPreludeTicker()
    if (playerPhase.value !== 'error') {
      playerPhase.value = 'watching'
    }
  },
  onStreamStop: () => {
    hasStream.value = false
    if (playerPhase.value !== 'error') {
      playerPhase.value = 'idle'
    }
  },
  onAutoplayFailed: () => {
    needUserGesture.value = true
  },
  onNeedUnmute: () => {
    if (playerPhase.value === 'watching' || playerPhase.value === 'connecting') {
      needUserGesture.value = true
    }
  },
  onAutoplayRecovered: () => {
    needUserGesture.value = false
    gestureLoading.value = false
  },
  onError: (err) => {
    const msg = String(err || '')
    if (msg.includes('retrying')) return
    playerError.value = playerPhase.value === 'connecting'
      ? (msg || '连接放映流失败')
      : '播放连接中断'
    playerPhase.value = 'error'
    hasStream.value = false
  },
})

const displayTitle = computed(() => {
  const name = streamConfig.value.cinema_filename
  if (name) return String(name).replace(/\.mp4$/i, '')
  return '同频影院'
})

const viewerLabel = computed(() => viewerIdentity.value.displayName || username.value || '')

const isLoggedIn = computed(() => !!resolveViewerIdentity(authStore))

const showNoStreamHint = computed(() => {
  return !streamConfig.value.running && playerPhase.value !== 'error'
})

const applyStreamPayload = (stream) => {
  const preludeSeconds = Number(stream?.prelude_seconds)
  streamConfig.value = {
    running: !!stream?.running,
    cinema_filename: stream?.cinema_filename || null,
    playback: stream?.playback || null,
    started_at: stream?.started_at || null,
    prelude_seconds: Number.isFinite(preludeSeconds) ? preludeSeconds : 10,
  }

  const cap = streamConfig.value.prelude_seconds
  const nowClient = Date.now()
  preludeClock.value = nowClient

  const endsAt = Number(stream?.prelude_ends_at_ms)
  const serverNow = Number(stream?.server_now_ms)
  if (streamConfig.value.running && cap > 0 && Number.isFinite(endsAt) && endsAt > 0) {
    const base = Number.isFinite(serverNow) ? serverNow : nowClient
    preludeEndsAtClient.value = nowClient + (endsAt - base)
  } else {
    preludeEndsAtClient.value = 0
  }

  if (streamConfig.value.running) {
    startPreludeTicker()
  } else {
    stopPreludeTicker()
  }
}

const preludeRemainSec = computed(() => {
  if (!streamConfig.value.running || !preludeEndsAtClient.value) return 0
  const cap = streamConfig.value.prelude_seconds || 0
  if (cap <= 0) return 0
  const remain = Math.ceil((preludeEndsAtClient.value - preludeClock.value) / 1000)
  if (!Number.isFinite(remain)) return 0
  return Math.min(cap, Math.max(0, remain))
})

const inPrelude = computed(() => preludeRemainSec.value > 0)

const waitVideoEl = async () => {
  for (let i = 0; i < 20; i += 1) {
    await nextTick()
    if (videoRef.value) return true
    await new Promise((r) => setTimeout(r, 50))
  }
  return !!videoRef.value
}

const stopPlayer = async () => {
  connectGeneration += 1
  needUserGesture.value = false
  hasStream.value = false
  await viewer.stop()
  if (playerPhase.value !== 'error') {
    playerPhase.value = 'idle'
  }
}

const startPlayer = async () => {
  const gen = ++connectGeneration
  const cfg = streamConfig.value

  const loggedIn = resolveViewerIdentity(authStore)
  if (!loggedIn) {
    playerError.value = '请先登录后再观看'
    playerPhase.value = 'error'
    return
  }
  viewerIdentity.value = loggedIn

  if (!cfg.running || !cfg.playback) {
    await stopPlayer()
    return
  }

  const domReady = await waitVideoEl()
  if (!domReady) {
    playerError.value = '播放器未就绪'
    playerPhase.value = 'error'
    return
  }

  playerError.value = ''
  playerPhase.value = 'connecting'
  needUserGesture.value = false
  hasStream.value = false

  const preludeSec = cfg.prelude_seconds || 10
  const connectTimeoutMs = (preludeSec + 30) * 1000

  try {
    const ok = await viewer.play({
      videoEl: videoRef.value,
      playback: cfg.playback,
      connectTimeoutMs,
    })
    if (gen !== connectGeneration) return
    if (!ok) {
      playerError.value = '连接放映流失败'
      playerPhase.value = 'error'
      await viewer.stop()
      return
    }
    hasStream.value = true
    if (playerPhase.value !== 'error') {
      playerPhase.value = 'watching'
    }
  } catch (e) {
    if (gen !== connectGeneration) return
    playerError.value = e.message || '连接放映厅失败'
    playerPhase.value = 'error'
    await viewer.stop()
    ElMessage.error(playerError.value)
  }
}

const shouldStartPlayer = () => {
  if (playerPhase.value === 'connecting') return false
  if (playerPhase.value === 'error') return false
  if (hasStream.value && playerPhase.value === 'watching') return false
  return !hasStream.value || playerPhase.value === 'idle'
}

const refreshStreamStatus = async () => {
  if (statusPollInFlight) return
  statusPollInFlight = true
  try {
    const { response } = await fetchCinemaStreamStatus()
    if (!response.data?.success) {
      throw new Error(response.data?.error || '获取放映状态失败')
    }
    const stream = response.data.data || {}
    const wasRunning = streamConfig.value.running
    applyStreamPayload(stream)

    if (!isLoggedIn.value) {
      await stopPlayer()
      if (stream.running) {
        playerError.value = '请先登录后再观看'
        playerPhase.value = 'error'
      } else if (playerPhase.value === 'error') {
        playerError.value = '请先登录后再观看'
      }
      return
    }

    if (stream.running) {
      if (!wasRunning || shouldStartPlayer()) {
        await startPlayer()
      }
    } else {
      await stopPlayer()
    }
  } finally {
    statusPollInFlight = false
  }
}

const loadInitialConfig = async () => {
  const { response } = await fetchCinemaList()
  if (!response.data?.success) {
    throw new Error(response.data?.error || '获取影院配置失败')
  }
  const data = response.data.data || {}
  applyStreamPayload(data.stream || {})
  if (data.stream?.running && isLoggedIn.value) {
    await startPlayer()
  } else if (!isLoggedIn.value && data.stream?.running) {
    playerError.value = '请先登录后再观看'
    playerPhase.value = 'error'
  }
}

const pollStreamStatus = () => refreshStreamStatus()

const handleUserPlay = async () => {
  if (gestureLoading.value) return
  gestureLoading.value = true
  const ok = await viewer.playWithUserGesture()
  if (ok) {
    needUserGesture.value = false
    ElMessage.success('声音已开启')
  } else {
    gestureLoading.value = false
    ElMessage.warning('开启声音失败，请重试')
  }
}

const goToLogin = () => {
  showCinemaLoginDialog(router, '/home')
}

const retryConnect = async () => {
  playerPhase.value = 'idle'
  playerError.value = ''
  try {
    await refreshStreamStatus()
  } catch (e) {
    playerError.value = e.message || '重新连接失败'
    playerPhase.value = 'error'
  }
}

const toggleFullscreen = async () => {
  const el = playerShellRef.value
  if (!el) return
  try {
    if (!document.fullscreenElement) {
      await el.requestFullscreen()
      if (isMobileLayout.value) {
        try {
          await screen.orientation?.lock?.('landscape-primary')
        } catch {
          // iOS 等可能不支持
        }
      }
    } else {
      await document.exitFullscreen()
    }
  } catch {
    ElMessage.warning('全屏不可用')
  }
}

const stopPreludeTicker = () => {
  if (preludeTimer) {
    clearInterval(preludeTimer)
    preludeTimer = null
  }
}

const startPreludeTicker = () => {
  stopPreludeTicker()
  preludeClock.value = Date.now()
  if (streamConfig.value.running && preludeEndsAtClient.value) {
    preludeTimer = setInterval(() => {
      preludeClock.value = Date.now()
    }, 200)
  }
}

const startStatusPolling = () => {
  startCinemaStreamPoll(pollStreamStatus, STATUS_POLL_MS)
}

const stopStatusPolling = () => {
  stopCinemaStreamPoll()
}

const handlePageHide = () => {
  viewer.stop()
}

onMounted(async () => {
  loading.value = true
  authStore.syncFromLocalStorage()
  syncMobileLayout()
  window.addEventListener('resize', syncMobileLayout)
  document.addEventListener('fullscreenchange', onFullscreenChange)
  window.addEventListener('pagehide', handlePageHide)
  try {
    await loadInitialConfig()
  } catch (e) {
    playerError.value = e.message || '初始化失败'
    playerPhase.value = 'error'
  } finally {
    loading.value = false
    startStatusPolling()
  }
})

onUnmounted(async () => {
  stopStatusPolling()
  stopPreludeTicker()
  window.removeEventListener('resize', syncMobileLayout)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  window.removeEventListener('pagehide', handlePageHide)
  await stopPlayer()
})
</script>

<template>
  <div class="cinema-theater">
    <FullScreenLoading :visible="loading" />

    <header class="theater-header">
      <div class="header-left">
        <h1 class="title">{{ displayTitle }}</h1>
        <p class="meta">
          <span>用户：{{ viewerLabel }}</span>
        </p>
      </div>
      <div class="header-actions">
        <el-tag v-if="streamConfig.running" type="danger" effect="dark" class="live-tag">LIVE</el-tag>
        <el-button :icon="FullScreen" circle title="全屏" @click="toggleFullscreen" />
      </div>
    </header>

    <div class="player-stage">
      <div
        ref="playerShellRef"
        class="player-shell"
        :class="{ 'mobile-fs-landscape': isMobileFsLandscape }"
      >
        <video
          ref="videoRef"
          class="cinema-video"
          playsinline
          autoplay
          preload="auto"
          disablepictureinpicture
          disableremoteplayback
        />

        <div v-if="showNoStreamHint" class="overlay-mask overlay-waiting">
          <p class="overlay-title">当前暂无放映</p>
          <p class="overlay-desc">等待放映开始</p>
          <el-button link type="primary" @click="retryConnect">刷新状态</el-button>
        </div>

        <div
          v-if="playerPhase === 'connecting' && !hasStream && !inPrelude"
          class="overlay-mask overlay-waiting"
        >
          <p class="overlay-title">正在连接放映流</p>
        </div>

        <div v-if="streamConfig.running && inPrelude" class="overlay-mask overlay-prelude">
          <p class="overlay-title">放映即将开始</p>
          <p class="overlay-desc">{{ preludeRemainSec }} 秒后开始正片</p>
          <p v-if="playerPhase === 'connecting'" class="overlay-desc">正在连接放映通道…</p>
        </div>

        <div v-if="needUserGesture && hasStream" class="overlay-mask overlay-sound">
          <el-button
            type="primary"
            size="large"
            :icon="VideoPlay"
            :loading="gestureLoading"
            @click="handleUserPlay"
          >
            开启声音
          </el-button>
          <p class="overlay-desc">画面已开始播放，点击开启声音</p>
        </div>

        <div v-if="playerPhase === 'error'" class="overlay-mask">
          <p class="overlay-title">{{ playerError }}</p>
          <el-button v-if="!isLoggedIn" type="primary" @click="goToLogin">去登录</el-button>
          <el-button v-else type="primary" @click="retryConnect">重新连接</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cinema-theater {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
  height: 100%;
  min-height: 0;
  gap: 8px;
  box-sizing: border-box;
}

.theater-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-shrink: 0;
  width: 100%;
  min-width: 0;
  min-height: 0;
}

.header-left {
  min-width: 0;
  flex: 1;
}

.title {
  margin: 0;
  font-size: clamp(1.1rem, 2.5vw, 1.5rem);
  font-weight: 700;
  line-height: 1.15;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta {
  margin: 2px 0 0;
  font-size: 12px;
  line-height: 1.2;
  color: var(--el-text-color-secondary);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.live-tag {
  font-weight: 600;
}

.player-stage {
  width: 100%;
  max-width: 100%;
  flex: 1;
  min-height: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
}

.player-shell {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  container-type: size;
}

.player-shell:fullscreen {
  width: 100vw;
  height: 100vh;
  max-width: none;
  max-height: none;
  aspect-ratio: auto;
  border-radius: 0;
}

.player-shell.mobile-fs-landscape:fullscreen,
.player-shell.mobile-fs-landscape:-webkit-full-screen {
  width: 100vh !important;
  height: 100vw !important;
  max-width: none !important;
  max-height: none !important;
  aspect-ratio: auto;
  border-radius: 0;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(90deg);
  transform-origin: center center;
}

.player-shell.mobile-fs-landscape:fullscreen .cinema-video,
.player-shell.mobile-fs-landscape:-webkit-full-screen .cinema-video {
  width: 100%;
  height: 100%;
}

.cinema-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
  pointer-events: none;
}

.cinema-video::-webkit-media-controls {
  display: none !important;
}

.overlay-mask {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px;
  text-align: center;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
}

@media (min-width: 769px) {
  .player-stage {
    container-type: size;
  }

  .player-shell {
    width: min(100cqw, calc(100cqh * 16 / 9), 1920px);
    height: min(100cqh, calc(100cqw * 9 / 16), 1080px);
    aspect-ratio: 16 / 9;
  }

  .overlay-mask {
    gap: clamp(2px, 0.6cqmin, 4px);
    padding: clamp(3px, 1.2cqmin, 8px);
    font-size: clamp(14px, 2cqmin, 18px);
  }

  .overlay-title {
    font-size: clamp(15px, 2.4cqmin, 22px);
  }

  .overlay-desc {
    font-size: clamp(13px, 1.8cqmin, 16px);
  }

  .overlay-mask :deep(.el-button--large) {
    --el-button-size: clamp(36px, 6cqmin, 44px);
    padding: clamp(8px, 1.2cqmin, 12px) clamp(12px, 2.2cqmin, 20px);
    font-size: clamp(13px, 1.9cqmin, 16px);
  }

  .overlay-mask :deep(.el-button .el-icon) {
    font-size: clamp(14px, 2.2cqmin, 18px);
  }

  .overlay-mask :deep(.el-button.is-link),
  .overlay-mask :deep(.el-button--primary:not(.el-button--large)) {
    font-size: clamp(13px, 1.8cqmin, 16px);
  }
}

.overlay-waiting {
  background: rgba(0, 0, 0, 0.72);
}

.overlay-sound {
  background: rgba(0, 0, 0, 0.35);
  pointer-events: auto;
}

.overlay-prelude {
  background: rgba(0, 0, 0, 0.82);
  pointer-events: none;
}

.overlay-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.35;
}

.overlay-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.35;
  color: rgba(255, 255, 255, 0.85);
}

@media (max-width: 768px) {
  .theater-header {
    gap: 8px;
  }

  .title {
    font-size: 1rem;
  }

  .meta {
    font-size: 11px;
  }

  .player-shell {
    width: 100%;
    max-width: 100%;
    aspect-ratio: 16 / 9;
    max-height: none;
  }

  .overlay-title {
    font-size: 15px;
  }

  .overlay-desc {
    font-size: 13px;
  }

  .overlay-mask {
    gap: 4px;
    padding: 8px;
  }
}
</style>
