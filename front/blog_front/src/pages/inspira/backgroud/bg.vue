<script setup lang="ts">
import {computed} from "vue";
import { useColorMode } from "@vueuse/core";
import Sparkles from "./Sparkles.vue";
import { useConfigStore } from "../../../stores/config.js";
import { useAuthStore } from "../../../stores/user_info.js";
import { storeToRefs } from "pinia";

const colorMode = useColorMode();
const configStore = useConfigStore();
const authStore = useAuthStore();
const { bgColor: userBgColor, bgPattern: userParticlesColor } = storeToRefs(authStore);

// 优先使用用户数据库中的颜色，如果为空则使用配置文件的值，最后使用默认值
// 用户数据不区分亮色和暗色主题
const particlesColor = computed(() => {
  // 优先使用用户数据库中的点缀颜色
  if (userParticlesColor.value && userParticlesColor.value.trim() !== '') {
    return userParticlesColor.value;
  }
  
  // 其次使用配置文件中的颜色（根据当前主题模式）
  const mode = colorMode.value === "dark" ? "dark" : "light";
  const configColor = configStore.config[mode]?.particlesColor;
  if (configColor) {
    return configColor;
  }
  
  // 最后使用默认值
  return mode === "dark" ? "#FFFFFF" : "#00EAFF";
});

const bgcolor = computed(() => {
  // 优先使用用户数据库中的背景颜色
  if (userBgColor.value && userBgColor.value.trim() !== '') {
    return userBgColor.value;
  }
  
  // 其次使用配置文件中的颜色（根据当前主题模式）
  const mode = colorMode.value === "dark" ? "dark" : "light";
  const configBg = configStore.config[mode]?.bgcolor;
  if (configBg) {
    return configBg;
  }
  
  // 最后使用默认值
  return mode === "dark" ? "#000000" : "#FFFFFF";
});
</script>
<template>
  <div :style="{ backgroundColor: bgcolor }"
    class="fixed inset-0 h-full w-full overflow-hidden z-[0]"
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