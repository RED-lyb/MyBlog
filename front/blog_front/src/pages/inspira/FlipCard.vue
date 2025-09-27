<script setup>
defineProps({
  flipped: {
    type: Boolean,
    default: false
  }
})
</script>

<template>
  <div class="flip-card" :class="{ 'is-flipped': flipped }">
    <div class="flip-card-inner">
      <div class="flip-card-front">
        <slot></slot>
      </div>
      <div class="flip-card-back">
        <slot name="back"></slot>
      </div>
    </div>
  </div>
</template>

<style scoped>
.flip-card {
  width: 100%;
  height: 100%;
  perspective: 1000px;
}

.flip-card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flip-card.is-flipped .flip-card-inner {
  transform: rotateY(180deg);
}

.flip-card-front,
.flip-card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
}



.flip-card-back {
  transform: rotateY(180deg);
}
</style>