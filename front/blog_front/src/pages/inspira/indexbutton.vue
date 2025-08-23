<script lang="ts" setup>
import GradientButton from './GradientButton.vue'
import { computed } from "vue";
import { useColorMode } from "@vueuse/core";
const colorMode = useColorMode();
const isDark = computed(() => colorMode.value == "dark");
const bgColor = computed(() => (isDark.value ? "#000" : "#fff"));
const emit = defineEmits(['click']);
</script>
<template>
  <div class="z-10 flex h-20 w-full flex-col items-center justify-center font-bold">
    <GradientButton :bgColor="bgColor" @click="emit('click')" style="cursor: pointer;">GO</GradientButton>
  </div>
</template>
