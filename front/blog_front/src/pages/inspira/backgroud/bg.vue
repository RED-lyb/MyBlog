<script setup lang="ts">
import {computed} from "vue";
import { useColorMode } from "@vueuse/core";
import Sparkles from "./Sparkles.vue";
const colorMode = useColorMode();
const particlesColor = computed(() => (colorMode.value === "dark" ? "#FFFFFF" : "#00EAFF"));
const bgcolor=computed(()=>(colorMode.value==="dark"?"dark:bg-black":"dark:bg-white"));
</script>
<template>
  <div :class="bgcolor"
    class="fixed inset-0 h-full w-full overflow-hidden rounded-md z-index:-10"
  >
      <Sparkles
        background="transparent"
        :min-size="0.8"
        :max-size="3"
        :speed="1"
        :particle-density="120"
        class="size-full"
        :particle-color="particlesColor"
      />
    </div>
</template>


<style scoped>
</style>