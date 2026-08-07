<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { fetchLoveNestDecorPhotos, resolveStaticUrl } from '../../lib/loveNestApi.js'

const MAX_FLOATERS = 8
const EASING_POOL = [
  'ease-in-out',
  'ease-out',
  'linear',
  'cubic-bezier(0.45, 0.05, 0.55, 0.95)',
  'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
]

const sceneRef = ref(null)
const sceneSize = ref({ width: 0, height: 0 })
const activeItems = ref([])
const assetPool = ref([])
const timers = new Set()

function randomBetween(min, max) {
  return min + Math.random() * (max - min)
}

function pickEasing() {
  return EASING_POOL[Math.floor(Math.random() * EASING_POOL.length)]
}

function buildAssetPool(photos) {
  return photos.map((item) => {
    const url = item.url || ''
    const base = {
      src: resolveStaticUrl(url),
    }

    if (item.category === 'person') {
      return {
        ...base,
        kind: 'person',
        minSize: 64,
        maxSize: 96,
      }
    }

    if (item.category === 'food') {
      return {
        ...base,
        kind: 'food',
        minSize: 72,
        maxSize: 108,
      }
    }

    return {
      ...base,
      kind: 'scenery',
      minSize: 84,
      maxSize: 124,
    }
  })
}

function updateSceneSize() {
  sceneSize.value = {
    width: window.innerWidth,
    height: window.innerHeight,
  }
}

function bindSceneObserver() {
  updateSceneSize()
  window.addEventListener('resize', updateSceneSize)
}

async function loadAssetPool() {
  try {
    const response = await fetchLoveNestDecorPhotos()
    if (response.data.success) {
      assetPool.value = buildAssetPool(response.data.data?.photos || [])
    }
  } catch (error) {
    assetPool.value = []
  }
}

function pickAsset() {
  const pool = assetPool.value
  if (!pool.length) {
    return null
  }
  return pool[Math.floor(Math.random() * pool.length)]
}

function randomPoint(size) {
  const { width, height } = sceneSize.value
  const maxLeft = Math.max(width - size, 0)
  const maxTop = Math.max(height - size, 0)
  const peripheryBias = Math.random() < 0.72

  if (!peripheryBias) {
    const marginX = width * 0.22
    const marginY = height * 0.22
    return {
      left: randomBetween(marginX, Math.max(marginX, maxLeft - marginX)),
      top: randomBetween(marginY, Math.max(marginY, maxTop - marginY)),
    }
  }

  const zone = Math.floor(Math.random() * 4)
  const bandX = width * 0.3
  const bandY = height * 0.3

  if (zone === 0) {
    return { left: randomBetween(0, maxLeft), top: randomBetween(0, Math.min(bandY, maxTop)) }
  }
  if (zone === 1) {
    return {
      left: randomBetween(0, maxLeft),
      top: randomBetween(Math.max(0, maxTop - bandY), maxTop),
    }
  }
  if (zone === 2) {
    return { left: randomBetween(0, Math.min(bandX, maxLeft)), top: randomBetween(0, maxTop) }
  }
  return {
    left: randomBetween(Math.max(0, maxLeft - bandX), maxLeft),
    top: randomBetween(0, maxTop),
  }
}

function createFloater() {
  const asset = pickAsset()
  if (!asset || sceneSize.value.width <= 0 || sceneSize.value.height <= 0) {
    return null
  }

  const lifeMs = randomBetween(7000, 22000)
  const speedFactor = randomBetween(0.75, 1.45)
  const size = randomBetween(asset.minSize, asset.maxSize)
  const point = randomPoint(size)

  return {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
    src: asset.src,
    kind: asset.kind,
    left: point.left,
    top: point.top,
    size,
    rotate: randomBetween(-18, 18),
    driftX: randomBetween(-100, 100) * speedFactor,
    driftY: randomBetween(-72, 88) * speedFactor,
    lifeMs,
    easing: pickEasing(),
  }
}

function trackTimeout(fn, delay) {
  const timer = window.setTimeout(() => {
    timers.delete(timer)
    fn()
  }, delay)
  timers.add(timer)
  return timer
}

function removeFloater(id) {
  activeItems.value = activeItems.value.filter((item) => item.id !== id)
}

function spawnFloater() {
  if (activeItems.value.length >= MAX_FLOATERS || !assetPool.value.length) {
    return
  }

  const floater = createFloater()
  if (floater) {
    activeItems.value.push(floater)
  }
}

function handleFloaterEnd(id) {
  removeFloater(id)
  spawnFloater()
}

function startFloaters() {
  for (let i = 0; i < MAX_FLOATERS; i += 1) {
    trackTimeout(() => spawnFloater(), i * randomBetween(300, 1100))
  }
}

onMounted(async () => {
  await loadAssetPool()
  bindSceneObserver()
  startFloaters()
})

onBeforeUnmount(() => {
  timers.forEach((timer) => window.clearTimeout(timer))
  timers.clear()
  window.removeEventListener('resize', updateSceneSize)
})
</script>

<template>
  <div ref="sceneRef" class="doodle-scene" aria-hidden="true">
    <div class="doodle-bg">
      <img
        class="doodle-bg-photo"
        src="/love_nest/background.jpg"
        alt=""
      />
    </div>
    <img
      v-for="item in activeItems"
      :key="item.id"
      :src="item.src"
      alt=""
      class="floater"
      :class="`floater--${item.kind}`"
      :style="{
        left: `${item.left}px`,
        top: `${item.top}px`,
        width: `${item.size}px`,
        '--drift-x': `${item.driftX}px`,
        '--drift-y': `${item.driftY}px`,
        '--rotate': `${item.rotate}deg`,
        '--life-ms': `${item.lifeMs}ms`,
        'animation-timing-function': item.easing,
      }"
      @animationend="handleFloaterEnd(item.id)"
    />
  </div>
</template>

<style scoped>
.doodle-scene {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.doodle-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.doodle-bg-photo {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  opacity: 0.12;
  filter: blur(2px) saturate(1.05);
}

.floater {
  position: absolute;
  pointer-events: none;
  user-select: none;
  opacity: 0;
  animation: floater-life var(--life-ms) forwards;
  will-change: transform, opacity;
}

.floater--scenery,
.floater--food {
  object-fit: cover;
  height: auto;
  aspect-ratio: 1;
  border: 3px solid #fff;
  border-radius: 4px;
  box-shadow: 0 10px 28px rgba(45, 42, 38, 0.14);
}

.floater--person {
  object-fit: cover;
  aspect-ratio: 1;
  height: auto;
  border: 3px solid #fff;
  border-radius: 50%;
  box-shadow: 0 10px 24px rgba(45, 42, 38, 0.12);
}

@keyframes floater-life {
  0% {
    transform: translate3d(0, 0, 0) rotate(var(--rotate));
    opacity: 0;
  }

  14% {
    opacity: 1;
  }

  66% {
    opacity: 1;
  }

  100% {
    transform: translate3d(var(--drift-x), var(--drift-y), 0) rotate(calc(var(--rotate) + 5deg));
    opacity: 0;
  }
}

@media (max-width: 640px) {
  .floater--scenery,
  .floater--food,
  .floater--person {
    max-width: 96px;
  }
}
</style>
