<script setup>
import Carousel from './element/Carousel.vue'
import logincard from './inspira/logincard.vue';
</script>
<template>
    <div id="out" class="w-screen h-screen">
        <div id="left">
            <Carousel />
        </div>

        <div id="right">
            <logincard />
        </div>
    </div>
</template>
<style scoped>
#out {
    /* background-color: rgba(255, 208, 132, 0.804); */
    display: flex;
    justify-content: flex-start;
    align-items: center;
    gap: 20px;
}

#left {
    margin: 40px;
    width: 800px;
    height: 500px;
}

#right {
    width: 500px;
    height: 500px;
}
</style>