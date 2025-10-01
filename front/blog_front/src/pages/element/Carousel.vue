<template>
    <el-carousel :interval=2000 height="500px" motion-blur style="width: 800px;border-radius: 20px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);">
      <el-carousel-item v-for="item of 3" :key="item">
<img :src="`/public/images/login${item}.jpg`" class= "pic" alt="网络不好，请重新加载">
      </el-carousel-item>
    </el-carousel>
</template>

<style scoped>
.pic{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}
.demonstration {
  color: var(--el-text-color-secondary);
}

.el-carousel__item h3 {
  color: #475669;
  opacity: 0.75;
  line-height: 200px;
  margin: 0;
  text-align: center;
}

.el-carousel__item:nth-child(2n) {
  background-color: #99a9bf;
}

.el-carousel__item:nth-child(2n + 1) {
  background-color: #d3dce6;
}
</style>
