<script setup>
//导入必要组件
import {ref,watch} from 'vue'
import { useDark, useToggle } from '@vueuse/core'//控制暗色模式
const isDark = useDark({//设置初始效果及控制准备
  selector: 'html',
  attribute: 'data-theme',//为daisyui设置全局主题属性
  valueDark: 'dark',
  valueLight: 'light',
  initialValue:'dark'
})
const theme_type=ref(isDark.value)
const toggle_theme=useToggle(isDark)

const toggleTheme = () => {// 点击切换主题状态
  theme_type.value = !theme_type.value
}
watch(theme_type, (new_val) => {//监听主题状态，为html的class属性更改主题样式，以确保daisyui和element两者元素都能实现同步
  const html_class=document.documentElement
  toggle_theme()
  if(new_val){
    html_class.classList.remove('light')
    html_class.classList.add('dark')
  }else{
    html_class.classList.remove('dark')
    html_class.classList.add('light')
  }
})
const size_val=defineProps({'size':{default: '50'}})
const size=ref('width:'+size_val.size+'px;height:'+size_val.size+'px;')

</script>
<template>
    <div class="theme-switch" @click="toggleTheme" :style="size">
    <!-- 太阳图标（亮色模式） -->
    <transition name="theme">
      <svg 
        v-if="!theme_type" 
        class="icon" 
        xmlns="http://www.w3.org/2000/svg" 
        viewBox="0 0 24 24"
        fill="black"
      >
        <path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" />
      </svg>
    </transition>

    <!-- 月亮图标（暗色模式） -->
    <transition name="theme">
      <svg
        v-if="theme_type" 
        class="icon" 
        xmlns="http://www.w3.org/2000/svg" 
        viewBox="0 0 24 24"
        fill="white"
      >
        <path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" />
      </svg>
    </transition>
  </div>
</template>
<style scoped>
/* 容器：设置固定大小，作为图标的定位基准 */
.theme-switch {
  position: relative;
  cursor: pointer; /* 显示点击指针 */
}

/* 图标样式：重叠在容器中心 */
.icon {
  position: absolute; /* 绝对定位实现重叠 */
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}

/* 动画定义：旋转+透明度渐变 */
/* 进入动画：顺时针旋转 + 中途缩小 */
.theme-enter-from {
  opacity: 0;
  transform: rotate(180deg) scale(0.7);
}
.theme-enter-active {
  transition: all 0.5s ease;
  /* 动画过程中会自动从初始状态过渡到结束状态，中间会经过缩放0.5的状态 */
}
.theme-enter-to {
  opacity: 1;
  transform: rotate(360deg) scale(1);
}

/* 离开动画：逆时针旋转 + 中途缩小 */
.theme-leave-from {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}
.theme-leave-active {
  transition: all 0.5s ease;
}
.theme-leave-to {
  opacity: 0;
  transform: rotate(-180deg) scale(0.7);
}

/* 防止离开动画不显示的问题（让离开的元素保留在DOM中直到动画结束） */
.theme-leave-active {
  position: absolute;
}
</style>