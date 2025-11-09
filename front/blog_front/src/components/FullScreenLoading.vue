<!-- FullScreenLoading.vue -->
<template>
  <!-- 仅当 visible 为 true 时渲染 -->
  <div
      class="fullscreen-loading-container"
      v-if="visible"
  >
    <!-- 半透明蒙版 -->
    <div class="loading-mask"></div>
    <!-- 加载图标（使用你提供的样式） -->
    <div class="loading-icon">
      <span class="dsi-loading dsi-loading-ring dsi-loading-xl"></span>
    </div>
  </div>
</template>

<script setup>

// 接收外部控制显示/隐藏的 props
const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
    required: true
  }
})
</script>

<style scoped>
/* 全屏容器：固定定位，覆盖整个视口 */
.fullscreen-loading-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  z-index: 9999; /* 层级最高，确保覆盖所有内容 */
  pointer-events: auto; /* 阻止蒙版下的元素被点击 */
}

/* 半透明蒙版：黑色半透，实现遮罩效果 */
.loading-mask {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5); /* 蒙版透明度可调整 */
}

/* 加载图标：居中显示 */
.loading-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%); /* 完美居中 */
}
.dsi-loading-xl {
  width: 60px;
  height: 60px;
  border-width: 1px;
}
</style>