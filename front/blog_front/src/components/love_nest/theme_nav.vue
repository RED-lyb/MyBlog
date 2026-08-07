<script setup>
defineProps({
  modelValue: {
    type: String,
    required: true,
  },
  options: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits(['update:modelValue'])

function selectTab(value) {
  emit('update:modelValue', value)
}
</script>

<template>
  <nav class="ln-nav">
    <button
      v-for="item in options"
      :key="item.value"
      type="button"
      class="ln-nav__item"
      :class="{ 'is-active': modelValue === item.value }"
      @click="selectTab(item.value)"
    >
      <span class="ln-nav__text">{{ item.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.ln-nav {
  display: flex;
  width: 100%;
  min-width: 420px;
  min-height: var(--ln-nav-height, 52px);
  border: none;
  background: transparent;
}

.ln-nav__item {
  flex: 1 0 25%;
  min-width: 96px;
  min-height: var(--ln-nav-height, 52px);
  padding: 0 12px;
  border: none;
  border-right: 2px solid var(--ln-ink);
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ln-ink);
  transition: background 0.18s ease, color 0.18s ease;
}

.ln-nav__item:last-child {
  border-right: none;
}

.ln-nav__text {
  position: relative;
  z-index: 1;
  display: block;
  white-space: nowrap;
}

.ln-nav__item:not(.is-active):hover {
  background: color-mix(in srgb, var(--ln-ink) 5%, var(--ln-paper, #fffcf9));
}

.ln-nav__item.is-active {
  color: var(--ln-paper, #fffcf9);
  background: var(--ln-ink);
}

@media (max-width: 640px) {
  .ln-nav {
    min-width: 380px;
  }

  .ln-nav__item {
    min-width: 88px;
    font-size: 0.72rem;
    padding: 0 8px;
  }
}
</style>
