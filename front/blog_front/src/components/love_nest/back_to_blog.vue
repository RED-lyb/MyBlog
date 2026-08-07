<script setup>
import { useRouter } from 'vue-router'
import { ArrowLeft } from '@element-plus/icons-vue'

const router = useRouter()

function goBack() {
  router.push('/home')
}
</script>

<template>
  <el-button
    class="back-btn"
    text
    :icon="ArrowLeft"
    @click="goBack"
  >
    返回博客
  </el-button>
</template>

<style scoped>
.back-btn {
  flex-shrink: 0;
  height: var(--ln-nav-height, 52px);
  padding: 0 16px;
  font-size: 0.82rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--ln-ink, #111) !important;
  background: rgba(255, 252, 249, 0.88) !important;
  border: 2px solid var(--ln-ink, #111) !important;
  border-radius: 0 !important;
  box-shadow: 4px 4px 0 var(--ln-ink, #111);
}
</style>
