<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessage } from 'element-plus'
import { FullScreen, VideoPlay } from '@element-plus/icons-vue'
import FullScreenLoading from '../pages/FullScreenLoading.vue'
import { fetchCinemaList } from '../lib/cinemaApi.js'
import {
  readCachedGuestIdentity,
  cacheGuestIdentity,
  resolveLoggedInViewerIdentity,
  displayNameFromRtcUserId,
} from '../lib/cinemaGuestId.js'
import { CinemaRtcViewer, fetchCinemaToken } from '../lib/cinemaRtcViewer.js'

const authStore = useAuthStore()
const { username, isAuthenticated } = storeToRefs(authStore)

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

const viewer = new CinemaRtcViewer({
  onRoomJoined: () => {
    if (rtcPhase.value !== 'error') {
      rtcPhase.value = 'in_room'
    }
  },
  onPublisherStream: () => {
    hasRemoteStream.value = true
    rtcPhase.value = 'watching'
    logCinema('收到推流端发布流')
  },
  onPublisherUnpublish: () => {
    hasRemoteStream.value = false
    if (rtcPhase.value !== 'error') {
      rtcPhase.value = 'in_room'
    }
    logCinema('推流端停止发布')
  },
  onPublisherLeave: () => {
    hasRemoteStream.value = false
    if (rtcPhase.value !== 'error') {
      rtcPhase.value = 'in_room'
    }
    logCinema('推流端离开房间')
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
  onError: (e) => {
    console.error('[cinema] RTC error', e)
  },
})

let joinGeneration = 0

const displayTitle = computed(() => {
  const name = rtcConfig.value.cinema_filename
  if (name) return String(name).replace(/\.mp4$/i, '')
  return '同频影院'
})

const viewerLabel = computed(() => viewerIdentity.value.displayName)

const showNoStreamHint = computed(() => {
  return rtcPhase.value === 'in_room' && !hasRemoteStream.value
})

const logCinema = (...args) => {
  console.log('[cinema]', ...args)
}

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
  logCinema('config', rtcConfig.value)
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
    rtcError.value = 'RTC 未配置（app_id / room_id / 推流端 user_id）'
    rtcPhase.value = 'error'
    return
  }

  const domReady = await waitPlayerDom()
  if (!domReady) {
    rtcError.value = '播放器容器未就绪'
    rtcPhase.value = 'error'
    return
  }

  joining.value = true
  rtcError.value = ''
  rtcPhase.value = 'joining'
  hasRemoteStream.value = false

  try {
    let requestUserId = viewerIdentity.value.rtcUserId || null
    if (isAuthenticated.value) {
      const loggedIn = resolveLoggedInViewerIdentity(authStore)
      if (loggedIn) {
        requestUserId = loggedIn.rtcUserId
      }
    } else if (!requestUserId) {
      const cached = readCachedGuestIdentity()
      requestUserId = cached?.rtcUserId || null
    }

    logCinema('进房', { room: cfg.room_id, viewer: requestUserId || '(新游客)', publisher: cfg.publisher_user_id })
    const tokenResult = await fetchCinemaToken(cfg.room_id, requestUserId)
    if (gen !== joinGeneration) return

    const rtcUserId = tokenResult.user_id
    viewerIdentity.value = {
      rtcUserId,
      displayName: tokenResult.display_name || displayNameFromRtcUserId(rtcUserId),
    }
    if (!isAuthenticated.value) {
      cacheGuestIdentity(viewerIdentity.value)
    }

    await viewer.join({
      appId: cfg.app_id,
      roomId: cfg.room_id,
      userId: rtcUserId,
      token: tokenResult.token,
      publisherUserId: cfg.publisher_user_id,
      renderDom: playerDomRef.value,
    })
    if (gen !== joinGeneration) return
  } catch (e) {
    console.error(e)
    rtcError.value = e.message || '进房失败'
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
    } else {
      await document.exitFullscreen()
    }
  } catch {
    ElMessage.warning('全屏不可用')
  }
}

onMounted(async () => {
  loading.value = true
  authStore.syncFromLocalStorage()
  if (isAuthenticated.value) {
    const loggedIn = resolveLoggedInViewerIdentity(authStore)
    if (loggedIn) {
      viewerIdentity.value = loggedIn
    }
  } else {
    const cached = readCachedGuestIdentity()
    if (cached) {
      viewerIdentity.value = cached
    }
  }
  try {
    await loadRtcConfig()
    await joinRtc()
  } catch (e) {
    rtcError.value = e.message || '初始化失败'
    rtcPhase.value = 'error'
    logCinema('init error', e)
  } finally {
    loading.value = false
  }
})

onUnmounted(async () => {
  await leaveRtc()
})
</script>

<template>
  <div class="cinema-theater">
    <FullScreenLoading :visible="loading || joining" />

    <header class="theater-header">
      <div class="header-left">
        <h1 class="title">{{ displayTitle }}</h1>
        <p class="meta">
          <span v-if="isAuthenticated">用户：{{ username || viewerLabel }}</span>
          <span v-else>观众：{{ viewerLabel }}</span>
        </p>
      </div>
      <div class="header-actions">
        <el-tag v-if="hasRemoteStream" type="danger" effect="dark" class="live-tag">LIVE</el-tag>
        <el-button :icon="FullScreen" circle title="全屏" @click="toggleFullscreen" />
      </div>
    </header>

    <div class="player-stage">
      <div ref="playerShellRef" class="player-shell">
        <div ref="playerDomRef" class="rtc-player" />

        <div v-if="showNoStreamHint" class="overlay-mask overlay-waiting">
          <p class="overlay-title">当前暂无放映</p>
          <p class="overlay-desc">等待放映开始</p>
          <el-button link type="primary" @click="joinRtc">重新连接</el-button>
        </div>

        <div v-if="rtcPhase === 'joining'" class="overlay-mask overlay-waiting">
          <p class="overlay-title">正在加入放映厅</p>
        </div>

        <div v-if="needUserGesture" class="overlay-mask">
          <el-button type="primary" size="large" :icon="VideoPlay" @click="handleUserPlay">
            点击播放
          </el-button>
          <p>浏览器需要一次点击才能播放声音</p>
        </div>

        <div v-if="rtcPhase === 'error'" class="overlay-mask">
          <p>{{ rtcError }}</p>
          <el-button type="primary" @click="joinRtc">重新连接</el-button>
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
  gap: 8px;
}

.theater-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-shrink: 0;
  width: 100%;
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

/* 100% 宽度 + 16:9，高度设上限，避免带鱼屏过高 */
.player-stage {
  width: 100%;
  display: flex;
  justify-content: center;
}

.player-shell {
  position: relative;
  width: min(100%, calc(min(80vh, 1080px) * 16 / 9));
  max-width: 1920px;
  aspect-ratio: 16 / 9;
  max-height: min(80vh, 1080px);
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.player-shell:fullscreen {
  width: 100vw;
  height: 100vh;
  max-width: none;
  max-height: none;
  aspect-ratio: auto;
  border-radius: 0;
}

.player-shell:fullscreen .rtc-player {
  width: 100%;
  height: 100%;
}

.rtc-player {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.rtc-player :deep(video) {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain;
}

.overlay-mask {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 24px;
  text-align: center;
  background: rgba(0, 0, 0, 0.55);
  color: #fff;
}

.overlay-waiting {
  background: rgba(0, 0, 0, 0.72);
}

.overlay-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.overlay-desc {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.85);
}

</style>
