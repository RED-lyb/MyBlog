import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useStore = defineStore('allstores', () => {
  const num = ref(0)
  const doubleCount = computed(() => num.value * 2)
  function increment() {
    num.value++
  }

  return { num, doubleCount, increment }
})
