<template>
  <div class="flex justify-center">
    <div
      v-for="(letter, index) in letters"
      :key="letter"
    >
      <Motion
        as="h1"
        :initial="pullupVariant.initial"
        :animate="pullupVariant.animate"
        :transition="{
          delay: index * (props.delay ? props.delay : 0.05),
        }"
        :class="
          cn(
            'font-display text-center text-lg tracking-[-0.02em] md:leading-[5rem]',
            font_class,
          )
        "
        style="line-height: 2.5"
      >
        <span v-if="letter === ' '">&nbsp;</span>
        <span v-else>{{ letter }}</span>
      </Motion>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Motion } from "motion-v";
import { cn } from "@/lib/utils";
import {computed} from 'vue';
import { useColorMode } from "@vueuse/core";
const colorMode = useColorMode();
interface LetterPullupProps {
  words: string;
  delay?: number;
}
const font_class=computed(()=>(colorMode.value=="dark"? "text-white" : "text-black"))
const props = defineProps<LetterPullupProps>();

const letters = props.words.split("");

const pullupVariant = {
  initial: { y: 30, opacity: 0 },
  animate: {
    y: 0,
    opacity: 1,
  },
};
</script>