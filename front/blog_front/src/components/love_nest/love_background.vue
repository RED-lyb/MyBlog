<script setup>
import SeasonsFalling from 'vue-seasons-falling'
import DoodleScene from './doodle_scene.vue'

const sakuraConfig = {
  amount: 72,
  size: 5,
  speed: 0.85,
  color: '#ddb8c0',
  opacity: 0.38,
}
</script>

<template>
  <div class="love-bg-root">
    <div class="love-bg-layer love-bg-base" />
    <div class="love-bg-layer love-bg-overlay" />
    <div class="love-bg-layer love-bg-grain" aria-hidden="true" />
    <DoodleScene class="love-bg-layer" />
    <SeasonsFalling
      class="love-bg-sakura"
      season="spring"
      theme="light"
      full-screen
      :amount="sakuraConfig.amount"
      :size="sakuraConfig.size"
      :speed="sakuraConfig.speed"
      :wind="0.2"
      :swing="1.2"
      :color="sakuraConfig.color"
      :opacity="sakuraConfig.opacity"
      :mouse-interaction="true"
      :resize="true"
    />
  </div>
</template>

<style scoped>
.love-bg-root {
  position: fixed;
  inset: 0;
  z-index: 0;
  overflow: hidden;
  pointer-events: none;
}

.love-bg-layer {
  position: absolute;
  inset: 0;
}

.love-bg-base,
.love-bg-overlay {
  background: var(--ln-bg-layer-base, var(--ln-bg));
}

.love-bg-overlay {
  background: var(--ln-bg-layer-overlay, transparent);
}

.love-bg-grain {
  opacity: var(--ln-bg-grain-opacity, 0.35);
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.5'/%3E%3C/svg%3E");
  background-size: 180px 180px;
}

.love-bg-sakura {
  position: absolute;
  inset: 0;
  z-index: 1;
}
</style>
