<script setup>
import Carousel from './element/Carousel.vue'
import logincard from './inspira/logincard.vue';
import Confetti from './inspira/Confetti.vue'//纸屑组件
import { ref } from 'vue'

const confettiRef = ref()                       // 2. 拿到组件实例

function onRegisterSuccess() {                  // 3. 注册成功回调
  confettiRef.value?.fire({
    particleCount: 800,
    startVelocity: 65,
    spread: 150,
    origin: { x: 0.5, y: 1 },   // 底部中心
    gravity: 1.2
  })
}
</script>
<template>
    <div id="out" class="w-screen h-screen">
        <div id="left">
            <Carousel />
        </div>

        <div id="right">
            <logincard @register-success="onRegisterSuccess" />
        </div>
    </div>
    <Confetti ref="confettiRef" manualstart class="w-screen h-screen pointer-events-none fixed inset-0 z-50" />
</template>
<style scoped>
#out {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    overflow-x: auto;
}

#left {
    flex: 1;
    margin-left: 50px;
    max-width: 800px;
    height: 500px;
}

#right {
    flex: 1;
    margin-right: 50px;
    max-width: 500px;
    min-width: 500px;
    height: 500px;
}
</style>