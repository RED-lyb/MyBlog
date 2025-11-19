<script setup>
import { onBeforeMount, ref, watch } from 'vue'
import axios from 'axios'
import theme from '../pages/theme.vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'

const activeIndex = ref('1')
const handleSelect = (key, keyPath) => {
  console.log(key, keyPath)
}

const authStore = useAuthStore()
const {
  userId,
  avatar
} = storeToRefs(authStore)

const defaultAvatar = '/default_head.png'
const user_avatar = ref(defaultAvatar)
const avatarLoading = ref(true)

const buildAvatarUrl = (fileName) => {
  const baseUrl = import.meta.env?.VITE_API_FILE_URL || import.meta.env?.VITE_API_URL || ''
  if (!baseUrl) return `/api/static/user_heads/${fileName}`
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`
  return `${normalizedBase}static/user_heads/${fileName}`
}

const fetchUserAvatar = async () => {
  if (!userId.value || !avatar.value) {
    user_avatar.value = defaultAvatar
    avatarLoading.value = false
    return
  }
  avatarLoading.value = true
  const avatarFileName = `${userId.value}${avatar.value}`
  try {
    const { data } = await axios.get(`${import.meta.env.VITE_API_URL}home/avatar/`, {
      params: {
        file_name: avatarFileName
      }
    })
    if (data?.success && data?.data?.avatar_url) {
      user_avatar.value = data.data.avatar_url
    } else {
      user_avatar.value = buildAvatarUrl(avatarFileName)
    }
  } catch (error) {
    console.error('获取头像失败', error)
    user_avatar.value = buildAvatarUrl(avatarFileName)
  } finally {
    avatarLoading.value = false
  }
}

onBeforeMount(() => {
  fetchUserAvatar()
})

watch(
  [userId, avatar],
  ([nextId, nextAvatar], [prevId, prevAvatar]) => {
    if (nextId === prevId && nextAvatar === prevAvatar) return
    if (nextId && nextAvatar) {
      fetchUserAvatar()
    } else {
      user_avatar.value = defaultAvatar
    }
  }
)
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
    <el-menu-item index="6">更新历史</el-menu-item>
    <el-menu-item index="7">关于作者</el-menu-item>
    <el-menu-item index="8" style="padding-left: 0px;padding-right: 0px;margin-left: 10px;margin-right: 10px">
      <theme size="2.5" />
    </el-menu-item>
    <el-menu-item index="9" style="padding-left: 0px;padding-right: 0px;margin-left: 10px;margin-right: 20px">
      <el-skeleton
        :loading="avatarLoading"
        animated
        style="display: flex;align-items: center;justify-content: center;width: 35px;height: 35px;"
      >
        <template #template>
          <el-skeleton-item variant="circle" style="width: 35px;height: 35px;" />
        </template>
        <template #default>
          <el-avatar :size="35" :src="user_avatar" />
        </template>
      </el-skeleton>
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