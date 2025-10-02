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