<script setup>
import {ref, watch} from 'vue'
import { useDark } from '@vueuse/core'

// 直接使用全局配置的主题
const isDark = useDark()

// 设置主题变量，dark模式下为'd'，light模式下为'l'
const theme = ref(isDark.value ? 'd' : 'l')

// 监听主题变化，同步更新theme变量
watch(isDark, (newVal) => {
  theme.value = newVal ? 'd' : 'l'
})
</script>
<template>
    <el-carousel :interval=2000 height="500px" motion-blur style="width: 800px;border-radius: 20px; box-shadow: 0 0 18px rgba(0, 0, 0, 0.3);border: 1px solid var(--el-border-color-light);">
      <el-carousel-item v-for="item of 3" :key="item">
<img :src="`/images/login${item}_${theme}.jpg`" class= "pic" alt="网络不好，请重新加载">
      </el-carousel-item>
    </el-carousel>
</template>

<style scoped>
.pic{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.demonstration {
  color: var(--el-text-color-secondary);
}

.el-carousel__item h3 {
  color: #475669;
  opacity: 0.75;
  line-height: 200px;
  margin: 0;
  text-align: center;
}

.el-carousel__item:nth-child(2n) {
  background-color: #99a9bf;
}

.el-carousel__item:nth-child(2n + 1) {
  background-color: #d3dce6;
}
</style>
