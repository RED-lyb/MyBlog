<script setup>
import bg from './pages/inspira/backgroud/bg.vue'
</script>
<template>
  <bg />
  <div class="relative z-index:10 bg-white/0">
  <router-view />
  </div>
</template>

<style scoped></style>
