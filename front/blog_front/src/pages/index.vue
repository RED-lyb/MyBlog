<script setup>
//导入必要组件
import {watch} from 'vue'
import { useDark, useToggle } from '@vueuse/core'//控制暗色模式

const isDark = useDark({//设置初始效果及控制准备
  selector: 'html',
  attribute: 'data-theme',//为daisyui设置全局主题属性
  valueDark: 'dark',
  valueLight: 'light',
  initialValue:'dark'
})
watch(isDark, (new_val) => {//监听是否处于暗色模式，为html的class属性更改主题样式
  const html_class=document.documentElement
  if(new_val){
    html_class.classList.remove('light')
    html_class.classList.add('dark')
  }else{
    html_class.classList.remove('dark')
    html_class.classList.add('light')
  }
}, { immediate: true })

const toggleDark=useToggle(isDark)

</script>
<template>
    
    我是首页
    <button @click="toggleDark()" class="dsi-btn dsi-btn-outline border border-1">切换主题</button>
    <button class="dsi-btn dsi-btn-outline dsi-btn-success">Success</button>
    <el-button @click="">I am ElButton</el-button>
</template>