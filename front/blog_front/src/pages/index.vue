<script setup>
//导入必要组件
import theme from './theme.vue';
import BlurReveal from './inspira/BlurReveal.vue';
import indexbutton from './inspira/indexbutton.vue';
import LetterPullup from './inspira/LetterPullup.vue';
import { ref, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router'
const showComponents = ref({
  first: false,
  second: false,
  third: false,
  fourth: false
})
// 创建一个延迟函数
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));
onMounted(async () => {
  // 按顺序显示组件
  await delay(2000);

  showComponents.value.first = true;
  await delay(2500); // 等待第一个动画完成
  
  showComponents.value.second = true;
  await delay(2500); // 等待第二个动画完成
  
  showComponents.value.third = true;
  await delay(2500); // 等待第三个动画完成
  
  showComponents.value.fourth = true;
})
const router=useRouter()
const go = () => {
  router.push({ path: '/login' })
}
const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
        go()
    }
}
onMounted(() => {
    document.addEventListener('keydown', handleKeyPress)
})

// 组件卸载时移除键盘事件监听
onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyPress)
})
</script>
<template>

  <BlurReveal :delay="0.3" :duration="0.75">
    <div  style="display: flex; justify-content: center; padding-top:3.125rem;">
      <theme size="6.25" />
    </div>
    <h3 class="text-pretty text-xl tracking-tighter xl:text-4xl/none sm:text-3xl"
      style="text-align: center;padding-top: 0.625rem;">
      <span>切换</span><el-icon>
        <ArrowUpBold style="position: relative; bottom: 0.0625rem;" />
      </el-icon><span>主题</span>
    </h3>
    <h1 class="text-3xl font-bold tracking-tighter xl:text-6xl/none sm:text-5xl"
      style="text-align: center;font-size: 6.25rem; padding: 2.5rem; letter-spacing:0.4375rem">欢迎来到我的博客</h1>
    <h3 class="text-pretty text-xl tracking-tighter xl:text-4xl/none sm:text-3xl" style="text-align: center;">
      <span>点击按钮</span><el-icon>
        <ArrowDownBold style="position: relative; top: 0.75rem;" />
      </el-icon><span>进入博客</span>
    </h3>
    <indexbutton @click="go()" style="padding-top: 0.625rem;padding-bottom: 0.3125rem;" />
  </BlurReveal>
<LetterPullup v-if="showComponents.first"
    words="该网站是由李远博编写的技术网站，会不定期分享个人的计算机学习经验，也欢迎各路大神发布知识与补充，大家一起交流学习"
    :delay="0.04"
  />
  <LetterPullup v-if="showComponents.second"
    words="也欢迎大家在该网站分享个人的日常生活，希望大家可以多多发一些开心快乐的日常，营造美好的交流氛围，保持心情的愉悦"
    :delay="0.04"
  />
    <LetterPullup v-if="showComponents.third"
    words="如果对该网站有任何建议，或是发现了BUG，也可以在该网站准备发布的建议版块和BUG版块留言，我看到了会尽量添加和解决的"
    :delay="0.04"
  />
    <LetterPullup v-if="showComponents.fourth"
    words="最后希望大家可以经常光顾该网站，我会持续向网站增加一些实用的小工具小组件，以便在生活中帮助到大家，希望大家天天开心！"
    :delay="0.04"
  />
</template>
<style scoped>
</style>
