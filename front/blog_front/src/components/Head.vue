<script lang="ts" setup>
import {onBeforeMount, ref} from 'vue'
import theme from '../pages/theme.vue';
import { useAuthStore } from '../stores/user_info';
const activeIndex = ref('1')
const handleSelect = (key: string, keyPath: string[]) => {
  console.log(key, keyPath)
}
const authState = useAuthStore()
const user_avatar = ref('/default_head.png')//用户默认头像
const onBeforeMount=()=>{
  if(authState.user==null){
    const user_avatar="/default_head.png"
  }
  else{
    const user_avatar="/default_head.png"
  }
}
if (authState.user){

}
</script>

<template>
  <el-menu
      :default-active="activeIndex"
      class="el-menu-demo"
      mode="horizontal"
      :ellipsis="false"
      @select="handleSelect"
      text-color="#EF5710"
      active-text-color="	#C8161D"
  >
    <el-menu-item index="0" style="padding-left: 10px;padding-right: 20px">
      <img style="width: 50px;"
          src="/icon.png"
          alt="L-BLOG"
      />
      <h1 style="font-size: 20px;font-weight: bolder">L-BLOG</h1>
    </el-menu-item>
    <el-menu-item index="1">博客主页</el-menu-item>
    <el-menu-item index="2">流动网盘</el-menu-item>
    <el-menu-item index="3">实用工具</el-menu-item>
    <el-menu-item index="4">趣味游戏</el-menu-item>
    <el-menu-item index="5">意见反馈</el-menu-item>
    <el-menu-item index="6">关于作者</el-menu-item>
    <el-menu-item index="7" style="padding-left: 0px;padding-right: 0px;margin-left: 10px;margin-right: 10px">
      <theme size="2.5" />
    </el-menu-item>
    <el-menu-item index="8" style="padding-left: 0px;padding-right: 0px;margin-left: 10px;margin-right: 20px">
      <el-avatar :size="35" :src="user_avatar" />
    </el-menu-item>
  </el-menu>

</template>
<style scoped>
.el-menu--horizontal > .el-menu-item:nth-child(1) {
  margin-right: auto;
}
.el-menu {
  background-color: transparent !important;
}

.el-menu-item{
  background-color: transparent !important;
  font-size: 17px;
}
</style>