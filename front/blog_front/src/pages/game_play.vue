<script setup>
/**
 * Web 游玩：拉到游戏入口后直接整页跳转至静态 HTML，不占博客布局、不用 iframe。
 */
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FullScreenLoading from './FullScreenLoading.vue'
import apiClient from '../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL || ''
const route = useRoute()
const router = useRouter()

const showLoading = ref(true)
const err = ref('')

const buildGameAbsoluteUrl = (g) => {
  const root = apiUrl.replace(/\/?$/, '')
  const parts = String(g.web_entry).split('/').filter(Boolean)
  const pathSeg = parts.map((p) => encodeURIComponent(p)).join('/')
  return `${root}/static/games/game_files/${g.id}/web/${pathSeg}`
}

onMounted(async () => {
  document.title = '加载游戏…|L-BLOG'
  const id = route.params.gameId
  try {
    const res = await apiClient.get(`${apiUrl}games/public/${id}/`)
    if (!res.data.success) {
      err.value = res.data.error || '加载失败'
      showLoading.value = false
      return
    }
    const g = res.data.data
    if (!g?.web_entry?.trim()) {
      err.value = '该游戏未部署 Web 版资源'
      showLoading.value = false
      return
    }
    window.location.replace(buildGameAbsoluteUrl(g))
  } catch {
    err.value = '加载失败'
    showLoading.value = false
  }
})

const backToGames = () => {
  router.push({ name: 'games' })
}
</script>

<template>
  <FullScreenLoading :visible="showLoading && !err" />
  <div v-if="err" class="game-play-fallback">
    <p class="game-play-fallback__msg">{{ err }}</p>
    <button type="button" class="game-play-fallback__btn" @click="backToGames">
      返回游戏列表
    </button>
  </div>
</template>

<style scoped>
.game-play-fallback {
  min-height: 100vh;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1.5rem;
  box-sizing: border-box;
  font-family: system-ui, sans-serif;
  background: #0f1419;
  color: #e6edf3;
}

.game-play-fallback__msg {
  margin: 0;
  font-size: 1rem;
  text-align: center;
}

.game-play-fallback__btn {
  cursor: pointer;
  padding: 0.55rem 1.1rem;
  border-radius: 8px;
  border: 1px solid rgba(230, 237, 243, 0.35);
  background: transparent;
  color: #e6edf3;
  font-size: 0.95rem;
}

.game-play-fallback__btn:hover {
  background: rgba(230, 237, 243, 0.08);
}
</style>
