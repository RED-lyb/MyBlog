<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  milestones: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
})

const hasMilestones = computed(() => props.milestones.length > 0)

function formatDate(value) {
  if (!value) return ''
  return dayjs(value).format('M月D日')
}

function daysUntil(item) {
  if (!item?.milestone_date) return null
  const today = dayjs().startOf('day')
  let target = dayjs(item.milestone_date).startOf('day')
  if (item.is_yearly) {
    target = target.year(today.year())
    if (target.isBefore(today)) {
      target = target.add(1, 'year')
    }
  }
  return target.diff(today, 'day')
}

function countdownLabel(item) {
  const days = daysUntil(item)
  if (days === null) return ''
  if (days === 0) return '就是今天'
  if (item.is_yearly) return `还有 ${days} 天`
  return dayjs(item.milestone_date).isBefore(dayjs(), 'day') ? '已度过' : `还有 ${days} 天`
}
</script>

<template>
  <section class="milestone-cards ln-card">
    <header class="ln-section-head">
      <h2>纪念日</h2>
      <span class="ln-meta">{{ milestones.length }} dates</span>
    </header>

    <div v-if="loading" class="cards-loading">
      <el-skeleton :rows="3" animated />
    </div>

    <p v-else-if="!hasMilestones" class="ln-empty-hint">还没有纪念日</p>

    <div v-else class="cards-grid">
      <article
        v-for="item in milestones"
        :key="item.id"
        class="milestone-card"
      >
        <p class="milestone-countdown">{{ countdownLabel(item) }}</p>
        <h3 class="milestone-title">{{ item.title }}</h3>
        <p class="milestone-date">{{ formatDate(item.milestone_date) }}</p>
        <p v-if="item.description" class="milestone-desc">{{ item.description }}</p>
        <span v-if="item.is_yearly" class="milestone-badge">每年</span>
      </article>
    </div>
  </section>
</template>

<style scoped>
.milestone-cards {
  padding: 28px 24px 32px;
}

.cards-loading {
  padding: 8px 0;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.milestone-card {
  position: relative;
  padding: 20px 18px 22px;
  border: 2px solid var(--ln-ink);
  background: rgba(255, 252, 249, 0.88);
  box-shadow: 4px 4px 0 var(--ln-ink);
}

.milestone-countdown {
  margin: 0 0 10px;
  font-size: 0.72rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--ln-accent);
}

.milestone-title {
  margin: 0 0 6px;
  font-family: var(--ln-font-serif);
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--ln-ink);
}

.milestone-date {
  margin: 0 0 10px;
  font-size: 0.82rem;
  color: var(--ln-muted);
}

.milestone-desc {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.7;
  color: var(--ln-ink);
}

.milestone-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 2px 8px;
  border: 1px solid var(--ln-line);
  font-size: 0.68rem;
  letter-spacing: 0.1em;
  color: var(--ln-muted);
}
</style>
