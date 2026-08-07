<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import bg from './pages/inspira/backgroud/bg.vue'

const route = useRoute()
const hideGlobalBg = computed(() => !!route.meta.hideGlobalBg)
</script>
<template>
  <bg v-if="!hideGlobalBg" />
  <div class="relative z-[10] bg-white/0 h-full w-full size-full">
    <router-view />
  </div>
</template>

<style scoped>
</style>
