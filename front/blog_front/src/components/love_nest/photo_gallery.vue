<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import { resolveStaticUrl } from '../../lib/loveNestApi.js'

const props = defineProps({
  photos: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const PHOTO_GROUPS = [
  { key: 'person', label: '人物' },
  { key: 'scenery', label: '风景' },
  { key: 'food', label: '食物' },
]

const hoverRotateMap = new Map()

const hasPhotos = computed(() => props.photos.length > 0)

const photoGroups = computed(() =>
  PHOTO_GROUPS.map((group) => ({
    ...group,
    photos: props.photos.filter((photo) => photo.category === group.key),
  })).filter((group) => group.photos.length > 0)
)

const previewList = computed(() =>
  props.photos.map((photo) => resolveStaticUrl(photo.url))
)

const previewOpen = ref(false)

function photoUrl(photo) {
  return resolveStaticUrl(photo.url)
}

function previewIndex(photo) {
  return props.photos.findIndex((item) => item.id === photo.id)
}

function hoverRotate(photoId) {
  if (!hoverRotateMap.has(photoId)) {
    const sign = Math.random() > 0.5 ? 1 : -1
    const deg = sign * (2 + Math.random() * 5)
    hoverRotateMap.set(photoId, `${deg.toFixed(1)}deg`)
  }
  return hoverRotateMap.get(photoId)
}

function onPreviewShow() {
  previewOpen.value = true
  document.body.style.overflow = 'hidden'
}

function onPreviewClose() {
  previewOpen.value = false
  document.body.style.overflow = ''
}

onBeforeUnmount(() => {
  if (previewOpen.value) {
    document.body.style.overflow = ''
  }
})
</script>

<template>
  <section class="photo-gallery ln-card">
    <header class="ln-section-head">
      <h2>相册</h2>
      <span class="ln-meta">{{ photos.length }} photos</span>
    </header>

    <div v-if="loading" class="gallery-loading">
      <el-skeleton :rows="4" animated />
    </div>

    <el-empty
      v-else-if="!hasPhotos"
      description="还没有照片"
    />

    <div v-else class="gallery-sections">
      <section
        v-for="group in photoGroups"
        :key="group.key"
        class="gallery-section"
      >
        <header class="gallery-section__head">
          <h3 class="gallery-section__title">{{ group.label }}</h3>
          <span class="ln-meta">{{ group.photos.length }}</span>
        </header>

        <div class="gallery-grid">
          <article
            v-for="photo in group.photos"
            :key="photo.id"
            class="photo-item"
          >
            <div
              class="photo-thumb"
              :style="{ '--hover-rotate': hoverRotate(photo.id) }"
            >
              <el-image
                class="photo-image"
                :src="photoUrl(photo)"
                :preview-src-list="previewList"
                :initial-index="previewIndex(photo)"
                preview-teleported
                fit="cover"
                loading="lazy"
                :alt="photo.title || group.label"
                @show="onPreviewShow"
                @close="onPreviewClose"
              />
            </div>
            <div v-if="photo.title || photo.caption" class="photo-caption-block">
              <h4 v-if="photo.title" class="photo-title">{{ photo.title }}</h4>
              <p v-if="photo.caption" class="photo-caption">{{ photo.caption }}</p>
            </div>
          </article>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.photo-gallery {
  padding: 28px 24px 32px;
}

.gallery-loading {
  padding: 12px 0;
}

.gallery-sections {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.gallery-section__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--ln-line);
}

.gallery-section__title {
  margin: 0;
  font-family: var(--ln-font-serif);
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--ln-ink);
}

.gallery-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.photo-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.photo-thumb {
  overflow: visible;
}

.photo-image {
  width: 100%;
  aspect-ratio: 4 / 5;
  border: 1px solid var(--ln-line);
  cursor: zoom-in;
  display: block;
}

.photo-thumb :deep(.el-image__inner) {
  transition: transform 0.32s cubic-bezier(0.22, 1, 0.36, 1);
  transform-origin: center center;
}

.photo-thumb:hover :deep(.el-image__inner) {
  transform: scale(1.06) rotate(var(--hover-rotate, 3deg));
}

.photo-caption-block {
  padding: 0 2px;
}

.photo-title {
  margin: 0;
  font-family: var(--ln-font-serif);
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ln-ink);
}

.photo-caption {
  margin: 4px 0 0;
  font-size: 0.82rem;
  line-height: 1.55;
  color: var(--ln-muted);
}
</style>
