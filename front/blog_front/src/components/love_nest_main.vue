<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import BlurReveal from '../pages/inspira/BlurReveal.vue'
import BackToBlog from './love_nest/back_to_blog.vue'
import CoupleBanner from './love_nest/couple_banner.vue'
import PhotoGallery from './love_nest/photo_gallery.vue'
import DiaryTimeline from './love_nest/diary_timeline.vue'
import MilestoneCards from './love_nest/milestone_cards.vue'
import ThemeNav from './love_nest/theme_nav.vue'
import {
  fetchLoveNestConfig,
  fetchLoveNestPhotos,
  fetchLoveNestDiaries,
  fetchLoveNestMilestones,
  checkLoveNestEditor,
} from '../lib/loveNestApi.js'

const activeTab = ref('home')
const config = ref({})
const photos = ref([])
const diaries = ref([])
const milestones = ref([])
const loadingConfig = ref(false)
const loadingPhotos = ref(false)
const loadingDiaries = ref(false)
const loadingMilestones = ref(false)
const canEdit = ref(false)

const tabOptions = [
  { label: '首页', value: 'home' },
  { label: '相册', value: 'album' },
  { label: '旅行', value: 'travel' },
  { label: '时光', value: 'diary' },
]

const pendingTabLabel = computed(() =>
  tabOptions.find((item) => item.value === activeTab.value && item.value === 'travel')?.label
)

const isDiaryTab = computed(() => activeTab.value === 'diary')

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
    const response = await fetchLoveNestPhotos({ page: 1, page_size: 100 })
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

async function loadEditorStatus() {
  try {
    const response = await checkLoveNestEditor()
    if (response.data.success) {
      canEdit.value = !!response.data.data?.can_edit
    }
  } catch (error) {
    canEdit.value = false
  }
}

watch(activeTab, (tab) => {
  if (tab === 'diary' && !diaries.value.length && !loadingDiaries.value) {
    loadDiaries()
  }
})

onMounted(async () => {
  await Promise.all([
    loadConfig(),
    loadPhotos(),
    loadMilestones(),
    loadEditorStatus(),
  ])
})
</script>

<template>
  <div class="love-nest-main" :class="{ 'love-nest-main--diary': isDiaryTab }">
    <header class="page-topbar">
      <BackToBlog />
      <div class="tab-nav-scroll">
        <nav class="tab-nav-shell">
          <ThemeNav v-model="activeTab" :options="tabOptions" />
        </nav>
      </div>
    </header>

    <div v-if="activeTab === 'home'" class="tab-panel">
      <BlurReveal :delay="0.08" :duration="0.68">
        <CoupleBanner :config="config" />
      </BlurReveal>

      <BlurReveal :delay="0.42" :duration="0.68">
        <MilestoneCards
          :milestones="milestones"
          :loading="loadingMilestones || loadingConfig"
        />
      </BlurReveal>

      <p v-if="canEdit" class="edit-hint">
        你拥有编辑权限，可在管理后台维护内容。
      </p>
    </div>

    <div v-else-if="activeTab === 'album'" class="tab-panel">
      <BlurReveal :delay="0.08" :duration="0.7">
        <PhotoGallery
          :photos="photos"
          :loading="loadingPhotos || loadingConfig"
        />
      </BlurReveal>
    </div>

    <div v-else-if="activeTab === 'diary'" class="tab-panel tab-panel--diary">
      <DiaryTimeline
        :diaries="diaries"
        :loading="loadingDiaries"
      />
    </div>

    <div v-else class="tab-panel">
      <BlurReveal :delay="0.08" :duration="0.7">
        <section class="notice ln-card">
          <header class="ln-section-head">
            <h2>{{ pendingTabLabel }}</h2>
          </header>
          <el-empty :description="`${pendingTabLabel}模块将在 Phase 3 开放`" />
        </section>
      </BlurReveal>
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

.love-nest-main--diary {
  width: 100%;
  max-width: none;
  padding-left: 0;
  padding-right: 0;
}

.love-nest-main--diary .page-topbar {
  width: min(1200px, calc(100% - 32px));
  margin-left: auto;
  margin-right: auto;
  padding-left: 16px;
  padding-right: 16px;
  box-sizing: border-box;
}

.page-topbar {
  display: flex;
  align-items: stretch;
  gap: 12px;
  margin-bottom: 24px;
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

.tab-panel--diary {
  width: 100vw;
  max-width: 100vw;
  margin-left: calc(50% - 50vw);
  gap: 0;
}

.notice {
  padding: 28px 24px 32px;
}

.edit-hint {
  margin: 0;
  text-align: center;
  font-size: 0.88rem;
  color: var(--ln-accent);
}

@media (max-width: 720px) {
  .love-nest-main {
    padding: 16px 12px 40px;
  }

  .page-topbar {
    gap: 10px;
  }
}
</style>
