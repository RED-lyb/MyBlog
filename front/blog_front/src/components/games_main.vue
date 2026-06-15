<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import FullScreenLoading from '../pages/FullScreenLoading.vue'
import apiClient from '../lib/api.js'
import { ElMessage } from 'element-plus'

const apiUrl = import.meta.env.VITE_API_URL || ''

const router = useRouter()

const loading = ref(true)
const games = ref([])
const imgFailed = reactive({})
const detailOpen = ref(false)
const selected = ref(null)

const staticRoot = computed(() => apiUrl.replace(/\/?$/, ''))

const coverSrc = (filename) => {
  const f = (filename || '').trim()
  if (!f) return ''
  return `${staticRoot.value}/static/games/game_images/${encodeURIComponent(f)}`
}

const onImgErr = (id) => {
  imgFailed[id] = true
}

const showPlaceholder = (game) => {
  if (!game.content || !String(game.content).trim()) return true
  return !!imgFailed[game.id]
}

const openDetail = (game) => {
  selected.value = game
  detailOpen.value = true
}

const hasPlatformLinks = computed(() => {
  const g = selected.value
  if (!g) return false
  return !!(g.has_web || g.has_windows || g.has_linux || g.has_android)
})

const downloadUrl = (gameId, platform) => `${apiUrl}games/download/${gameId}/${platform}/`

const goWebPlay = (game) => {
  if (!game.has_web) return
  router.push({ name: 'game_play', params: { gameId: String(game.id) } })
}

const fetchGames = async () => {
  loading.value = true
  try {
    const response = await apiClient.get(`${apiUrl}games/list/`)
    if (response.data.success) {
      games.value = response.data.data.games || []
    } else {
      ElMessage.error(response.data.error || '获取游戏列表失败')
      games.value = []
    }
  } catch (e) {
    ElMessage.error('获取游戏列表失败')
    games.value = []
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchGames()
})
</script>

<template>
  <div class="games-page-inner">
    <div class="content-header">
      <h1>趣味游戏</h1>
    </div>

    <FullScreenLoading :visible="loading" />

    <div v-if="!loading && games.length === 0" class="empty-hint">
      暂无游戏，敬请期待
    </div>

    <div v-else-if="!loading" class="games-grid">
      <el-card
        v-for="game in games"
        :key="game.id"
        class="game-card"
        shadow="never"
        @click="openDetail(game)"
      >
        <template #header>
          <div class="card-head">
            <span class="head-title">{{ game.title }}</span>
          </div>
        </template>

        <div class="body-image">
          <img
            v-if="!showPlaceholder(game)"
            :src="coverSrc(game.content)"
            :alt="game.title"
            @error="onImgErr(game.id)"
          />
          <div v-else class="image-placeholder" aria-hidden="true">
            <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
              <g fill="currentColor">
                <path
                  d="M224 56v32l-48 16l-16 40l-23.35 9.34l-39-39a8 8 0 0 0-11.32 0L32 168.69V56a8 8 0 0 1 8-8h176a8 8 0 0 1 8 8"
                  opacity=".2"
                ></path>
                <path
                  d="M216 40H40a16 16 0 0 0-16 16v144a16 16 0 0 0 16 16h64a8 8 0 0 0 7.59-5.47l14.83-44.48L163 151.43a8.07 8.07 0 0 0 4.46-4.46l14.62-36.55l44.48-14.83A8 8 0 0 0 232 88V56a16 16 0 0 0-16-16M112.41 157.47L98.23 200H40v-28l52-52l30.42 30.42l-5.42 2.15a8 8 0 0 0-4.59 4.9M216 82.23l-42.53 14.18a8 8 0 0 0-4.9 4.62l-14.72 36.82l-15.27 6.15l-35.27-35.27a16 16 0 0 0-22.62 0L40 149.37V56h176Zm12.68 33a8 8 0 0 0-7.21-1.1l-23.8 7.94a8 8 0 0 0-4.9 4.61l-14.31 35.77l-35.77 14.31a8 8 0 0 0-4.61 4.9l-7.94 23.8a8 8 0 0 0 7.59 10.54H216a16 16 0 0 0 16-16v-78.27a8 8 0 0 0-3.32-6.49ZM216 200h-67.17l3.25-9.75l35.51-14.2a8.07 8.07 0 0 0 4.46-4.46l14.2-35.51l9.75-3.25Z"
                ></path>
              </g>
            </svg>
          </div>
        </div>

        <template #footer>
          <div class="card-foot">
            {{ game.introduction }}
          </div>
        </template>
      </el-card>
    </div>

    <el-dialog
      v-model="detailOpen"
      :title="selected?.title || '详情'"
      width="560px"
      class="game-detail-dialog"
      @closed="selected = null"
    >
      <div v-if="selected" class="detail-wrap">
        <p class="detail-text">{{ selected.detail }}</p>
        <div v-if="hasPlatformLinks" class="platform-block">
          <div class="plat-title">游玩方式</div>
          <div class="plat-links">
            <a
              v-if="selected.has_web"
              href="#"
              class="plat-link"
              @click.prevent.stop="goWebPlay(selected)"
              >Web游玩</a
            >
            <a
              v-if="selected.has_windows"
              :href="downloadUrl(selected.id, 'windows')"
              class="plat-link"
              download
              @click.stop
              >Windows 下载</a
            >
            <a
              v-if="selected.has_linux"
              :href="downloadUrl(selected.id, 'linux')"
              class="plat-link"
              download
              @click.stop
              >Linux 下载</a
            >
            <a
              v-if="selected.has_android"
              :href="downloadUrl(selected.id, 'android')"
              class="plat-link"
              download
              @click.stop
              >Android 下载</a
            >
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.content-header {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.empty-hint {
  text-align: center;
  padding: 48px 16px;
  color: var(--el-text-color-secondary);
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  align-items: stretch;
}

@media (max-width: 1200px) {
  .games-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .games-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .games-grid {
    grid-template-columns: 1fr;
  }
}

.game-card {
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: rgba(245, 245, 245, 0.1);
  cursor: pointer;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}

.game-card:hover {
  transform: scale(1.02);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.card-head {
  min-height: 24px;
}

.head-title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  overflow: hidden;
}

.body-image {
  aspect-ratio: 16 / 10;
  border-radius: 6px;
  overflow: hidden;
  background: var(--el-fill-color-lighter);
  display: flex;
  align-items: center;
  justify-content: center;
}

.body-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
}

.image-placeholder svg {
  width: 40%;
  max-width: 120px;
  height: auto;
  opacity: 0.85;
}

.card-foot {
  font-size: 13px;
  color: var(--el-text-color-regular);
  line-height: 1.45;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
  min-height: 1.9em;
}

.detail-wrap {
  max-height: 60vh;
  overflow-y: auto;
}

.detail-text {
  margin: 0 0 16px;
  white-space: pre-wrap;
  line-height: 1.65;
  color: var(--el-text-color-primary);
}

.platform-block {
  padding-top: 8px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.plat-title {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  margin-bottom: 10px;
}

.plat-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 16px;
}

.plat-link {
  color: var(--el-color-primary);
  text-decoration: none;
  font-size: 14px;
}

.plat-link:hover {
  text-decoration: underline;
}

:deep(.el-card__header) {
  padding: 12px 14px;
}

:deep(.el-card__body) {
  padding: 12px 14px;
  flex: 1;
}

:deep(.el-card__footer) {
  padding: 10px 14px 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
