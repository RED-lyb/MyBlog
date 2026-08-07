<script setup>
import { computed } from 'vue'
import { resolveStaticUrl } from '../../lib/loveNestApi.js'

const props = defineProps({
  config: {
    type: Object,
    default: () => ({}),
  },
})

const members = computed(() => props.config?.members || [])
const daysTogether = computed(() => props.config?.days_together)
const slogan = computed(() => props.config?.slogan || '记录一起走过的日子')
const hasStartDate = computed(() => daysTogether.value !== null && daysTogether.value !== undefined)

function avatarSrc(member) {
  if (member?.avatar_url) {
    return resolveStaticUrl(member.avatar_url)
  }
  return ''
}
</script>

<template>
  <section class="couple-banner ln-card">
    <div class="banner-grid">
      <div class="banner-main">
        <p class="eyebrow">Love Nest</p>
        <h1 class="title ln-serif">爱情小窝</h1>
        <div class="ln-divider banner-divider" />
        <p class="slogan">{{ slogan }}</p>

        <div class="stat-block">
          <template v-if="hasStartDate">
            <div class="ln-stat-value">{{ daysTogether }}</div>
            <div class="ln-stat-label">DAYS TOGETHER</div>
          </template>
          <p v-else class="stat-placeholder">尚未设置在一起的日子</p>
        </div>
      </div>

      <aside v-if="members.length" class="members-panel">
        <p class="members-label">成员</p>
        <div
          v-for="member in members"
          :key="member.id"
          class="member-row"
        >
          <el-avatar :size="52" :src="avatarSrc(member)">
            {{ (member.username || '?').slice(0, 1) }}
          </el-avatar>
          <div class="member-info">
            <span class="member-name">{{ member.username }}</span>
          </div>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.couple-banner {
  padding: 36px 32px;
}

.banner-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 32px;
  align-items: start;
}

.eyebrow {
  margin: 0 0 8px;
  font-size: 0.72rem;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--ln-muted);
}

.title {
  margin: 0;
  font-size: clamp(2rem, 5vw, 2.75rem);
  font-weight: 600;
  letter-spacing: 0.08em;
  color: var(--ln-ink);
}

.banner-divider {
  margin: 18px 0;
}

.slogan {
  margin: 0;
  max-width: 28em;
  font-size: 1rem;
  line-height: 1.75;
  color: var(--ln-muted);
}

.stat-block {
  margin-top: 28px;
  padding-top: 20px;
  border-top: 1px solid var(--ln-line);
}

.stat-placeholder {
  margin: 0;
  font-size: 0.9rem;
  color: var(--ln-muted);
}

.members-panel {
  min-width: 160px;
  padding: 20px;
  border: 1px solid var(--ln-line);
  background: rgba(255, 252, 249, 0.6);
}

.members-label {
  margin: 0 0 16px;
  font-size: 0.72rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: var(--ln-muted);
}

.member-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.member-row + .member-row {
  margin-top: 14px;
}

.member-name {
  font-size: 0.95rem;
  font-weight: 500;
  color: var(--ln-ink);
}

@media (max-width: 720px) {
  .couple-banner {
    padding: 28px 20px;
  }

  .banner-grid {
    grid-template-columns: 1fr;
  }

  .members-panel {
    min-width: 0;
  }
}
</style>
