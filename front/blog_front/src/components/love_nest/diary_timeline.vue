<script setup>
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { resolveStaticUrl } from '../../lib/loveNestApi.js'

const props = defineProps({
  diaries: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const scrollRef = ref(null)
const userPaused = ref(false)
let resumeTimer = null
let autoScrollRaf = null
let lastFrameTime = 0
let scrollDirection = 1
let scrollbarPointerActive = false
let resizeObserver = null

const SCROLLBAR_GUESS_PX = 16

const sortedDiaries = computed(() =>
  [...props.diaries].sort((a, b) => {
    const dateDiff = dayjs(a.diary_date).valueOf() - dayjs(b.diary_date).valueOf()
    return dateDiff !== 0 ? dateDiff : a.id - b.id
  })
)

const hasDiaries = computed(() => sortedDiaries.value.length > 0)

function formatDate(value) {
  if (!value) return ''
  return dayjs(value).format('YYYY.M.D')
}

function imageUrl(diary) {
  const url = diary.photo?.url || diary.image_url
  return resolveStaticUrl(url)
}

function scheduleResume(delay = 1000) {
  if (resumeTimer) {
    window.clearTimeout(resumeTimer)
  }
  resumeTimer = window.setTimeout(() => {
    userPaused.value = false
  }, delay)
}

function isHorizontalScrollbarInteraction(event, el) {
  if (el.scrollWidth <= el.clientWidth + 1) return false

  const rect = el.getBoundingClientRect()
  const localY = event.clientY - rect.top
  const localX = event.clientX - rect.left

  if (localX < 0 || localX > rect.width || localY < 0 || localY > rect.height) {
    return false
  }

  const nativeGutter = el.offsetHeight - el.clientHeight
  const gutter = nativeGutter > 0 ? nativeGutter : SCROLLBAR_GUESS_PX

  // 点击在滚动条区域（含 overlay 滚动条）
  if (event.clientY >= rect.bottom - gutter - 1) return true
  if (localY > el.clientHeight + 1) return true
  if (event.target === el && event.offsetY > el.clientHeight + 1) return true

  return false
}

function onScrollbarPointerDown(event) {
  const el = scrollRef.value
  if (!el || scrollbarPointerActive || !isHorizontalScrollbarInteraction(event, el)) return

  scrollbarPointerActive = true
  pauseForScrollbar()

  window.addEventListener('mouseup', onScrollbarPointerUp, { once: true })
}

function pauseForScrollbar() {
  userPaused.value = true
  if (resumeTimer) {
    window.clearTimeout(resumeTimer)
    resumeTimer = null
  }
}

function onScrollbarPointerUp() {
  scrollbarPointerActive = false
  scheduleResume(1000)
}

function stopAutoScroll() {
  if (autoScrollRaf) {
    cancelAnimationFrame(autoScrollRaf)
    autoScrollRaf = null
  }
}

function canAutoScroll() {
  const el = scrollRef.value
  if (!el) return false
  return el.scrollWidth > el.clientWidth + 4
}

function refreshAutoScrollState() {
  const el = scrollRef.value
  if (!el) return

  if (!canAutoScroll()) {
    stopAutoScroll()
    el.scrollLeft = 0
    scrollDirection = 1
    return
  }

  if (!autoScrollRaf) {
    startAutoScroll()
  }
}

function tickAutoScroll(now) {
  const el = scrollRef.value
  if (el && !userPaused.value && canAutoScroll()) {
    const delta = Math.min((now - lastFrameTime) / 1000, 0.05)
    const speed = 36
    el.scrollLeft += scrollDirection * speed * delta

    const maxScroll = el.scrollWidth - el.clientWidth
    if (el.scrollLeft >= maxScroll - 1) {
      scrollDirection = -1
    } else if (el.scrollLeft <= 1) {
      scrollDirection = 1
    }
  }
  lastFrameTime = now
  autoScrollRaf = requestAnimationFrame(tickAutoScroll)
}

function startAutoScroll() {
  stopAutoScroll()
  lastFrameTime = performance.now()
  autoScrollRaf = requestAnimationFrame(tickAutoScroll)
}

function bindUserInteraction() {
  unbindUserInteraction()
  document.addEventListener('mousedown', onScrollbarPointerDown, { capture: true })
}

function unbindUserInteraction() {
  document.removeEventListener('mousedown', onScrollbarPointerDown, { capture: true })
  window.removeEventListener('mouseup', onScrollbarPointerUp)
}

function disconnectResizeObserver() {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
}

watch(
  () => [props.loading, sortedDiaries.value.length],
  async ([loading, count]) => {
    disconnectResizeObserver()
    stopAutoScroll()

    if (!loading && count > 0) {
      await nextTick()
      bindUserInteraction()
      refreshAutoScrollState()

      const el = scrollRef.value
      if (el && typeof ResizeObserver !== 'undefined') {
        resizeObserver = new ResizeObserver(() => refreshAutoScrollState())
        resizeObserver.observe(el)
        const track = el.querySelector('.moment-track')
        if (track) resizeObserver.observe(track)
      }
    } else {
      unbindUserInteraction()
    }
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  stopAutoScroll()
  disconnectResizeObserver()
  if (resumeTimer) {
    window.clearTimeout(resumeTimer)
  }
  unbindUserInteraction()
})
</script>

<template>
  <section class="moment-rail">
    <header class="moment-rail__head">
      <h2>恋爱时光</h2>
      <span class="ln-meta">{{ diaries.length }} moments</span>
    </header>

    <div v-if="loading" class="moment-rail__loading">
      <el-skeleton :rows="4" animated />
    </div>

    <p v-else-if="!hasDiaries" class="ln-empty-hint">还没有记录</p>

    <div
      v-else
      ref="scrollRef"
      class="moment-rail__scroll"
    >
      <div
        class="moment-track"
        :style="{ '--node-count': sortedDiaries.length }"
      >
        <div class="moment-axis" aria-hidden="true" />

        <article
          v-for="(diary, index) in sortedDiaries"
          :key="diary.id"
          class="moment-node"
          :class="index % 2 === 0 ? 'is-top' : 'is-bottom'"
        >
          <div class="moment-node__dot" aria-hidden="true" />

          <time
            class="moment-node__date"
            :class="index % 2 === 0 ? 'moment-node__date--below' : 'moment-node__date--above'"
          >
            {{ formatDate(diary.diary_date) }}
          </time>

          <div class="moment-node__bundle">
            <div class="moment-node__photo-wrap">
              <img
                v-if="diary.photo?.url || diary.image_url"
                class="moment-node__photo"
                :src="imageUrl(diary)"
                :alt="diary.sentence"
                loading="lazy"
              />
              <div v-else class="moment-node__photo moment-node__photo--placeholder">
                <span>暂无配图</span>
              </div>
              <p class="moment-node__sentence">{{ diary.sentence }}</p>
            </div>

            <div class="moment-node__stem" aria-hidden="true" />
          </div>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.moment-rail {
  width: 100%;
  overflow: visible;
}

.moment-rail__head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto 24px;
  padding: 0 16px;
  box-sizing: border-box;
}

.moment-rail__head h2 {
  margin: 0;
  font-family: var(--ln-font-serif);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ln-ink);
}

.moment-rail__loading {
  width: min(1200px, calc(100% - 32px));
  margin: 0 auto;
  padding: 12px 16px;
  box-sizing: border-box;
}

.moment-rail__scroll {
  width: 100%;
  overflow-x: auto;
  overflow-y: visible;
  padding: 100px 0;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
  scrollbar-gutter: stable;
}

.moment-track {
  position: relative;
  display: flex;
  align-items: stretch;
  width: max-content;
  min-width: calc(var(--node-count, 1) * 184px + 96px);
  min-height: 450px;
  padding: 0 48px;
  overflow: visible;
}

.moment-axis {
  position: absolute;
  left: 0;
  right: 0;
  top: 50%;
  height: 3px;
  background: var(--ln-ink);
  transform: translateY(-50%);
  box-shadow: 2px 2px 0 var(--ln-shadow);
  pointer-events: none;
}

/* 右侧黑线延伸，长度与左侧 padding 一致 */
.moment-axis::after {
  content: '';
  position: absolute;
  top: 0;
  left: 100%;
  width: 48px;
  height: 100%;
  background: var(--ln-ink);
  box-shadow: 2px 2px 0 var(--ln-shadow);
}

.moment-node {
  position: relative;
  flex: 0 0 184px;
  overflow: visible;
}

.moment-node__dot {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 14px;
  height: 14px;
  margin-left: -7px;
  margin-top: -7px;
  border: 3px solid var(--ln-ink);
  border-radius: 50%;
  background: var(--ln-paper);
  box-shadow: 2px 2px 0 var(--ln-shadow);
  z-index: 2;
}

.moment-node__bundle {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  overflow: visible;
}

.moment-node.is-top .moment-node__bundle {
  bottom: calc(50% + 7px);
}

.moment-node.is-bottom .moment-node__bundle {
  top: calc(50% + 7px);
}

.moment-node__date {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.82rem;
  letter-spacing: 0.06em;
  color: var(--ln-muted);
  white-space: nowrap;
  z-index: 1;
}

.moment-node__date--below {
  top: calc(50% + 14px);
}

.moment-node__date--above {
  bottom: calc(50% + 14px);
}

.moment-node__stem {
  width: 2px;
  height: 28px;
  background: var(--ln-ink);
  box-shadow: 1px 0 0 var(--ln-shadow);
  flex-shrink: 0;
}

.moment-node.is-top .moment-node__stem {
  order: 2;
}

.moment-node.is-bottom .moment-node__stem {
  order: 1;
}

.moment-node.is-top .moment-node__photo-wrap {
  order: 1;
}

.moment-node.is-bottom .moment-node__photo-wrap {
  order: 2;
}
.moment-node__photo-wrap {
  position: relative;
  width: 136px;
  overflow: visible;
}

.moment-node__photo {
  display: block;
  width: 136px;
  height: 136px;
  object-fit: cover;
  border: 3px solid var(--ln-ink);
  box-shadow: 4px 4px 0 var(--ln-shadow);
  background: var(--ln-paper);
  transition: transform 0.28s ease, box-shadow 0.28s ease;
}

.moment-node__photo--placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
  color: var(--ln-muted);
}

.moment-node__photo-wrap:hover .moment-node__photo {
  transform: scale(1.06);
  box-shadow: 6px 6px 0 var(--ln-shadow);
}

.moment-node__sentence {
  position: absolute;
  left: 50%;
  width: min(220px, 70vw);
  margin: 0;
  padding: 10px 12px;
  font-size: 0.9rem;
  line-height: 1.5;
  color: var(--ln-ink);
  background: var(--ln-paper);
  border: 2px solid var(--ln-ink);
  box-shadow: 3px 3px 0 var(--ln-shadow);
  opacity: 0;
  transform: translate(-50%, 8px);
  transition: opacity 0.24s ease, transform 0.24s ease;
  pointer-events: none;
  z-index: 5;
}

.moment-node.is-top .moment-node__sentence {
  bottom: calc(100% + 10px);
}

.moment-node.is-bottom .moment-node__sentence {
  top: calc(100% + 10px);
  transform: translate(-50%, -8px);
}

.moment-node__photo-wrap:hover .moment-node__sentence {
  opacity: 1;
  transform: translate(-50%, 0);
}
</style>
