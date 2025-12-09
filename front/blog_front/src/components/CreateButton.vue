<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleCreate = () => {
  router.push('/write')
}
</script>

<template>
  <div class="create-button-container">
    <button class="dsi-btn dsi-btn-outline dsi-btn-warning" @click="handleCreate">创作</button>
  </div>
</template>

<style scoped>
.create-button-container {
  display: flex;
  justify-content: center;
  align-items:end;
  padding: 20px;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 101; /* 确保高于页码组件的 z-index: 100 */
}

.create-btn {
  width: 100%;
}
</style>

