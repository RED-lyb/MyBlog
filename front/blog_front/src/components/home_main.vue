<script setup>
import page_number from "./page_number.vue"
</script>
<template>
<div class="page-number-container">
  <page_number />
</div>
</template>
<style scoped>
.page-number-container {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 60px;
  display: flex;
  justify-content: center;
  align-items: flex-end;
  margin-right: 0px;
  margin-bottom: 0px;
}
</style>