<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import BlurReveal from '../pages/inspira/BlurReveal.vue'
import BackToBlog from './love_nest/back_to_blog.vue'
import CoupleBanner from './love_nest/couple_banner.vue'
import PhotoGallery from './love_nest/photo_gallery.vue'
import DiaryTimeline from './love_nest/diary_timeline.vue'
import MilestoneCards from './love_nest/milestone_cards.vue'
import TravelMap from './love_nest/travel_map.vue'
import ThemeNav from './love_nest/theme_nav.vue'
import {
  fetchLoveNestConfig,
  fetchLoveNestPhotos,
  fetchLoveNestDiaries,
  fetchLoveNestMilestones,
  fetchLoveNestTravel,
} from '../lib/loveNestApi.js'

const activeTab = ref('home')
const config = ref({})
const photos = ref([])
const diaries = ref([])
const milestones = ref([])
const travelData = ref({ cities: [], province_stats: {} })
const loadingConfig = ref(false)
const loadingPhotos = ref(false)
const loadingDiaries = ref(false)
const loadingMilestones = ref(false)
const loadingTravel = ref(false)

const tabOptions = [
  { label: '首页', value: 'home' },
  { label: '相册', value: 'album' },
  { label: '旅行', value: 'travel' },
  { label: '时光', value: 'diary' },
]

const isFullBleedTab = computed(() => activeTab.value === 'diary' || activeTab.value === 'travel')
const isTravelTab = computed(() => activeTab.value === 'travel')

async function loadConfig() {
  loadingConfig.value = true
  try {
    const response = await fetchLoveNestConfig()
    if (response.data.success) {
      config.value = response.data.data || {}
    }
  } catch (error) {
    ElMessage.error('加载配置失败')
  } finally {
    loadingConfig.value = false
  }
}

async function loadPhotos() {
  loadingPhotos.value = true
  try {
    const response = await fetchLoveNestPhotos({ page: 1, page_size: 200 })
    if (response.data.success) {
      photos.value = response.data.data?.photos || []
    }
  } catch (error) {
    ElMessage.error('加载相册失败')
  } finally {
    loadingPhotos.value = false
  }
}

async function loadDiaries() {
  loadingDiaries.value = true
  try {
    const response = await fetchLoveNestDiaries({ page: 1, page_size: 50 })
    if (response.data.success) {
      diaries.value = response.data.data?.diaries || []
    }
  } catch (error) {
    ElMessage.error('加载时光记录失败')
  } finally {
    loadingDiaries.value = false
  }
}

async function loadMilestones() {
  loadingMilestones.value = true
  try {
    const response = await fetchLoveNestMilestones()
    if (response.data.success) {
      milestones.value = response.data.data?.milestones || []
    }
  } catch (error) {
    ElMessage.error('加载纪念日失败')
  } finally {
    loadingMilestones.value = false
  }
}

async function loadTravel() {
  loadingTravel.value = true
  try {
    const response = await fetchLoveNestTravel()
    if (response.data.success) {
      travelData.value = response.data.data || { cities: [], province_stats: {} }
    }
  } catch (error) {
    ElMessage.error('加载旅行数据失败')
  } finally {
    loadingTravel.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'diary' && !diaries.value.length && !loadingDiaries.value) {
    loadDiaries()
  }
  if (tab === 'travel' && !travelData.value.cities?.length && !loadingTravel.value) {
    loadTravel()
  }
})

onMounted(async () => {
  await Promise.all([
    loadConfig(),
    loadPhotos(),
    loadMilestones(),
  ])
})
</script>

<template>
  <div
    class="love-nest-main"
    :class="{
      'love-nest-main--fullbleed': isFullBleedTab,
      'love-nest-main--travel': isTravelTab,
    }"
  >
    <header class="page-topbar">
      <BackToBlog />
      <div class="tab-nav-scroll">
        <nav class="tab-nav-shell">
          <ThemeNav v-model="activeTab" :options="tabOptions" />
        </nav>
      </div>
    </header>

    <div v-if="activeTab === 'home'" class="tab-panel">
      <BlurReveal class="home-sections" :delay="0.38" :duration="0.68">
        <CoupleBanner :config="config" />
        <MilestoneCards
          :milestones="milestones"
          :loading="loadingMilestones || loadingConfig"
        />
      </BlurReveal>
    </div>

    <div v-else-if="activeTab === 'album'" class="tab-panel">
      <BlurReveal :delay="0.08" :duration="0.7">
        <PhotoGallery
          :photos="photos"
          :loading="loadingPhotos || loadingConfig"
        />
      </BlurReveal>
    </div>

    <div v-else-if="activeTab === 'travel'" class="tab-panel tab-panel--fullbleed tab-panel--travel">
      <TravelMap
        :cities="travelData.cities || []"
        :province-stats="travelData.province_stats || {}"
        :loading="loadingTravel"
      />
    </div>

    <div v-else-if="activeTab === 'diary'" class="tab-panel tab-panel--fullbleed">
      <DiaryTimeline
        :diaries="diaries"
        :loading="loadingDiaries"
      />
    </div>
  </div>
</template>

<style scoped>
.love-nest-main {
  position: relative;
  z-index: 10;
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
  padding: 22px 16px 48px;
  box-sizing: border-box;
}

.love-nest-main--travel {
  height: 100vh;
  max-height: 100vh;
  min-height: 0;
  display: flex;
  flex-direction: column;
  padding-bottom: 0;
  overflow: visible;
  box-sizing: border-box;
  background: transparent;
  pointer-events: none;
}

.love-nest-main--travel .page-topbar {
  position: relative;
  z-index: 50;
  pointer-events: auto;
}

.page-topbar {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin-bottom: 24px;
  flex-shrink: 0;
}

.tab-nav-scroll {
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

.tab-nav-shell {
  min-width: 100%;
}

.tab-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.home-sections {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.tab-panel--fullbleed {
  width: 100vw;
  max-width: 100vw;
  margin-left: calc(50% - 50vw);
  gap: 0;
}

.tab-panel--travel {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  pointer-events: none;
}

@media (max-width: 720px) {
  .love-nest-main {
    padding: 16px 12px 40px;
  }

  .love-nest-main--travel {
    padding-bottom: 0;
  }

  .page-topbar {
    gap: 10px;
  }
}
</style>
