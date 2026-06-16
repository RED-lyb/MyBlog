<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessage } from 'element-plus'
import { FullScreen, VideoPlay } from '@element-plus/icons-vue'
import FullScreenLoading from '../pages/FullScreenLoading.vue'
import { fetchCinemaList } from '../lib/cinemaApi.js'
import { resolveLoggedInViewerIdentity } from '../lib/cinemaGuestId.js'
import { CinemaRtcViewer, fetchCinemaToken } from '../lib/cinemaRtcViewer.js'

const authStore = useAuthStore()
const { username } = storeToRefs(authStore)

const loading = ref(true)
const joining = ref(false)
/** idle | joining | in_room | watching | error */
const rtcPhase = ref('idle')
const rtcError = ref('')
const needUserGesture = ref(false)
const hasRemoteStream = ref(false)

const rtcConfig = ref({
  app_id: '',
  room_id: '',
  publisher_user_id: '',
  cinema_filename: null,
})

const playerShellRef = ref(null)
const playerDomRef = ref(null)
const viewerIdentity = ref({ rtcUserId: '', displayName: '' })
const isMobileLayout = ref(false)
const isMobileFsLandscape = ref(false)

const MOBILE_MEDIA = '(max-width: 768px)'

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

const viewer = new CinemaRtcViewer({
  onRoomJoined: () => {
    if (rtcPhase.value !== 'error') {
      rtcPhase.value = 'in_room'
    }
  },
  onPublisherStream: () => {
    hasRemoteStream.value = true
    rtcPhase.value = 'watching'
  },
  onPublisherUnpublish: () => {
    hasRemoteStream.value = false
    if (rtcPhase.value !== 'error') {
      rtcPhase.value = 'in_room'
    }
  },
  onPublisherLeave: () => {
    hasRemoteStream.value = false
    if (rtcPhase.value !== 'error') {
      rtcPhase.value = 'in_room'
    }
  },
  onAutoplayFailed: () => {
    needUserGesture.value = true
  },
  onAutoplayRecovered: () => {
    needUserGesture.value = false
  },
  onDuplicateLogin: () => {
    rtcError.value = '账号在其他页面重复进房，已断开'
    rtcPhase.value = 'error'
    leaveRtc()
  },
  onError: () => {
    // RTC 错误由 overlay 提示，避免在控制台输出敏感信息
  },
})

let joinGeneration = 0

const displayTitle = computed(() => {
  const name = rtcConfig.value.cinema_filename
  if (name) return String(name).replace(/\.mp4$/i, '')
  return '同频影院'
})

const viewerLabel = computed(() => viewerIdentity.value.displayName || username.value || '')

const showNoStreamHint = computed(() => {
  return rtcPhase.value === 'in_room' && !hasRemoteStream.value
})

const loadRtcConfig = async () => {
  const { response } = await fetchCinemaList()
  if (!response.data?.success) {
    throw new Error(response.data?.error || '获取影院配置失败')
  }
  const stream = response.data.data?.stream || {}
  rtcConfig.value = {
    app_id: stream.app_id || '',
    room_id: stream.room_id || '',
    publisher_user_id: stream.user_id || '',
    cinema_filename: stream.cinema_filename || null,
  }
}

const waitPlayerDom = async () => {
  for (let i = 0; i < 20; i += 1) {
    await nextTick()
    if (playerDomRef.value) return true
    await new Promise((r) => setTimeout(r, 50))
  }
  return !!playerDomRef.value
}

const leaveRtc = async () => {
  joinGeneration += 1
  joining.value = false
  needUserGesture.value = false
  hasRemoteStream.value = false
  await viewer.leave()
  if (rtcPhase.value !== 'error') {
    rtcPhase.value = 'idle'
  }
}

const joinRtc = async () => {
  const gen = ++joinGeneration
  const cfg = rtcConfig.value
  if (!cfg.app_id || !cfg.room_id || !cfg.publisher_user_id) {
    rtcError.value = '放映厅未就绪，请稍后再试'
    rtcPhase.value = 'error'
    return
  }

  const loggedIn = resolveLoggedInViewerIdentity(authStore)
  if (!loggedIn?.rtcUserId) {
    rtcError.value = '请先登录后再观看'
    rtcPhase.value = 'error'
    return
  }

  const domReady = await waitPlayerDom()
  if (!domReady) {
    rtcError.value = '播放器未就绪'
    rtcPhase.value = 'error'
    return
  }

  joining.value = true
  rtcError.value = ''
  rtcPhase.value = 'joining'
  hasRemoteStream.value = false
  viewerIdentity.value = loggedIn

  try {
    const tokenResult = await fetchCinemaToken(cfg.room_id, loggedIn.rtcUserId)
    if (gen !== joinGeneration) return

    await viewer.join({
      appId: cfg.app_id,
      roomId: cfg.room_id,
      userId: tokenResult.user_id,
      token: tokenResult.token,
      publisherUserId: cfg.publisher_user_id,
      renderDom: playerDomRef.value,
    })
    if (gen !== joinGeneration) return
  } catch (e) {
    rtcError.value = e.message || '连接放映厅失败'
    rtcPhase.value = 'error'
    await viewer.leave()
    ElMessage.error(rtcError.value)
  } finally {
    if (gen === joinGeneration) {
      joining.value = false
    }
  }
}

const handleUserPlay = async () => {
  await viewer.playFailedUsers()
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
          // iOS 等可能不支持，由 CSS 旋转兜底
        }
      }
    } else {
      await document.exitFullscreen()
    }
  } catch {
    ElMessage.warning('全屏不可用')
  }
}

const handlePageHide = () => {
  viewer.leave()
}

onMounted(async () => {
  loading.value = true
  authStore.syncFromLocalStorage()
  syncMobileLayout()
  window.addEventListener('resize', syncMobileLayout)
  document.addEventListener('fullscreenchange', onFullscreenChange)
  window.addEventListener('pagehide', handlePageHide)
  try {
    await loadRtcConfig()
    await joinRtc()
  } catch (e) {
    rtcError.value = e.message || '初始化失败'
    rtcPhase.value = 'error'
  } finally {
    loading.value = false
  }
})

onUnmounted(async () => {
  window.removeEventListener('resize', syncMobileLayout)
  document.removeEventListener('fullscreenchange', onFullscreenChange)
  window.removeEventListener('pagehide', handlePageHide)
  await leaveRtc()
})
</script>

<template>
  <div class="cinema-theater">
    <FullScreenLoading :visible="loading || joining" />

    <div class="cinema-layout">
      <div class="theater-side theater-side--left">
        <h1 class="title">{{ displayTitle }}</h1>
        <p class="meta">
          <span>用户：{{ viewerLabel }}</span>
        </p>
      </div>

      <div
        ref="playerShellRef"
        class="player-shell"
        :class="{ 'mobile-fs-landscape': isMobileFsLandscape }"
      >
        <div ref="playerDomRef" class="rtc-player" />

        <div v-if="showNoStreamHint" class="overlay-mask overlay-waiting">
          <p class="overlay-title">当前暂无放映</p>
          <p class="overlay-desc">等待放映开始</p>
          <el-button link type="primary" @click="joinRtc">重新连接</el-button>
        </div>

        <div v-else-if="rtcPhase === 'joining'" class="overlay-mask overlay-waiting">
          <p class="overlay-title">正在加入放映厅</p>
        </div>

        <div v-else-if="needUserGesture" class="overlay-mask">
          <el-button type="primary" size="large" :icon="VideoPlay" @click="handleUserPlay">
            点击播放
          </el-button>
          <p class="overlay-desc">浏览器需要一次点击才能播放声音</p>
        </div>

        <div v-else-if="rtcPhase === 'error'" class="overlay-mask">
          <p class="overlay-title">{{ rtcError }}</p>
          <el-button type="primary" @click="joinRtc">重新连接</el-button>
        </div>
      </div>

      <div class="theater-side theater-side--right">
        <el-tag v-if="hasRemoteStream" type="danger" effect="dark" class="live-tag">LIVE</el-tag>
        <el-button :icon="FullScreen" circle title="全屏" @click="toggleFullscreen" />
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
  box-sizing: border-box;
  overflow-x: auto;
  overflow-y: hidden;
  -webkit-overflow-scrolling: touch;
}

.cinema-layout {
  display: grid;
  flex: 1;
  min-height: 0;
  min-width: min-content;
  height: 100%;
  width: 100%;
  box-sizing: border-box;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: start;
  align-content: center;
  column-gap: clamp(10px, 1.5vw, 16px);
}

.theater-side--left {
  grid-column: 1;
  justify-self: start;
  align-self: start;
  min-width: 0;
  text-align: left;
}

.theater-side--right {
  grid-column: 3;
  justify-self: end;
  align-self: start;
  flex-shrink: 0;
  display: flex;
  flex-direction: row;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 8px;
}

.player-shell {
  grid-column: 2;
  justify-self: center;
  align-self: start;
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  container-type: size;
  isolation: isolate;
  width: 100%;
  max-width: 1920px;
  aspect-ratio: 16 / 9;
  min-height: 180px;
}

.title {
  margin: 0;
  font-size: clamp(1rem, 2.2vw, 1.35rem);
  font-weight: 700;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--el-text-color-primary);
}

.meta {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.3;
  color: var(--el-text-color-secondary);
}

.live-tag {
  font-weight: 600;
}

.player-shell:fullscreen {
  width: 100vw;
  height: 100vh;
  max-width: none;
  max-height: none;
  aspect-ratio: auto;
  border-radius: 0;
}

/* 手机竖屏全屏：旋转 90° 横屏铺满，避免上下大黑边 */
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

.player-shell.mobile-fs-landscape:fullscreen .rtc-player,
.player-shell.mobile-fs-landscape:-webkit-full-screen .rtc-player {
  width: 100%;
  height: 100%;
}

.rtc-player {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  z-index: 1;
}

.rtc-player :deep(video) {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain;
}

.overlay-mask {
  position: absolute;
  inset: 0;
  z-index: 5;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px;
  text-align: center;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
  pointer-events: auto;
}

@media (min-width: 769px) {
  .cinema-layout {
    container-type: size;
  }

  .theater-side--left {
    max-width: min(36cqw, 380px);
  }

  .player-shell {
    width: min(calc(100cqh * 16 / 9), 100%, 1920px);
    max-width: 100%;
    max-height: 100cqh;
  }

  .title {
    font-size: clamp(14px, 1.8vw, 20px);
  }

  .meta {
    font-size: clamp(11px, 1.2vw, 13px);
  }

  /* 间距保持紧凑；字号随播放器容器放大（cqmin 相对 player-shell） */
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
  .cinema-theater {
    overflow: visible;
  }

  .cinema-layout {
    display: flex;
    flex-wrap: wrap;
    align-items: flex-start;
    height: auto;
    column-gap: 8px;
    row-gap: 8px;
  }

  .theater-side--left {
    flex: 1 1 auto;
    min-width: 0;
    order: 1;
  }

  .theater-side--right {
    flex: 0 0 auto;
    order: 2;
  }

  .player-shell {
    flex: 1 1 100%;
    order: 3;
    width: 100%;
    max-width: 100%;
    max-height: none;
  }

  .title {
    font-size: 1rem;
    white-space: normal;
  }

  .meta {
    font-size: 11px;
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
