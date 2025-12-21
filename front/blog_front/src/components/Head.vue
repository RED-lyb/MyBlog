<script setup>
import { onBeforeMount, ref, watch, computed,onMounted, onBeforeUnmount } from 'vue'
import axios from 'axios'
import theme from './theme.vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { useRouter, useRoute } from 'vue-router'
import Logout from './Logout.vue'

const router = useRouter()
const route = useRoute()

// 根据当前路由设置激活的菜单项
const activeIndex = computed(() => {
  const path = route.path
  // 使用startsWith匹配二级URL，保持active状态
  if (path === '/home' || path.startsWith('/home/')) return '1'
  if (path === '/network_disk' || path.startsWith('/network_disk/')) return '2'
  if (path === '/tools' || path.startsWith('/tools/')) return '3'
  if (path === '/games' || path.startsWith('/games/')) return '4'
  if (path === '/feedback' || path.startsWith('/feedback/')) return '5'
  if (path === '/history' || path.startsWith('/history/')) return '6'
  if (path === '/user_home/1') return '7' // 关于作者页面
  // 匹配 /user_home 或 /user_home/:userId
  if (path.startsWith('/user_home')) return '9-home'
  return '1'
})

// 添加遮罩状态
const showMask = ref(false)

// 滚动监听
const handleScroll = () => {
  showMask.value = window.scrollY > 10
}

const handleSelect = (key, keyPath) => {
  console.log(key, keyPath)
  // 退出登录菜单项不触发路由跳转（由 Logout 组件内部处理）
  if (key === '9-logout') {
    return
  }

  // 个人主页跳转，需要带上 userId
  if (key === '9-home') {
    if (userId.value) {
      const targetPath = `/user_home/${userId.value}`
      if (route.path !== targetPath) {
        router.push(targetPath)
      }
    } else {
      // 如果没有 userId，跳转到不带参数的路由
      if (route.path !== '/user_home') {
        router.push('/user_home')
      }
    }
    return
  }

  // 根据菜单项索引跳转到对应路由
  const routeMap = {
    '0': '/', // Logo点击回到首页
    '1': '/home', // 博客主页
    '2': '/network_disk', // 流动网盘
    '3': '/tools', // 实用工具
    '4': '/games', // 趣味游戏
    '5': '/feedback', // 意见反馈
    '6': '/history', // 更新历史
    '7': '/user_home/1', // 关于作者（跳转到用户ID为1的主页）
  }

  const targetPath = routeMap[key]
  if (targetPath && route.path !== targetPath) {
    router.push(targetPath)
  }
}

const authStore = useAuthStore()
const {
  userId,
  avatar,
  isAuthenticated
} = storeToRefs(authStore)

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}

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
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll)
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
  <el-affix>
    <div class="header-mask" :class="{ 'mask-active': showMask }">
    <el-menu :default-active="activeIndex" class="el-menu-demo" mode="horizontal" :ellipsis="false" :router="false"
      @select="handleSelect" text-color="#EF5710" active-text-color="#C8161D">
      <el-menu-item index="0" style="padding-left: 10px;padding-right: 20px">
        <img style="width: 50px;" src="/icon.png" alt="L-BLOG" />
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
      <el-sub-menu index="9" class="avatar-sub-menu" popper-class="avatar-submenu"
        :popper-style="{ marginLeft: '-10px' }" style="padding-right: 10px;">
        <template #title>
          <div class="avatar-trigger" style="margin-right: 20px;padding-right: 0px;">
            <el-skeleton :loading="avatarLoading" animated
              style="display: flex;align-items: center;justify-content: center;width: 35px;height: 35px;">
              <template #template>
                <el-skeleton-item variant="circle" style="width: 35px;height: 35px;" />
              </template>
              <template #default>
                <el-avatar :size="35" :src="user_avatar" />
              </template>
            </el-skeleton>
          </div>
        </template>
        <template v-if="isAuthenticated">
          <el-menu-item index="9-home" class="avatar-menu-item" :route="userId ? `/user_home/${userId}` : '/user_home'">
            个人主页
          </el-menu-item>
          <el-menu-item index="9-logout" class="avatar-menu-item">
            <Logout />
          </el-menu-item>
        </template>
        <template v-else>
          <el-menu-item index="9-login" class="avatar-menu-item" @click="goToLogin">
            去登录
          </el-menu-item>
        </template>
      </el-sub-menu>
    </el-menu>
  </div>
  </el-affix>
</template>
<style scoped>
/* 添加遮罩层 */
.header-mask {
  width: 100%;
  background: transparent;
  transition: background 0.3s ease;
}

.mask-active {
  background: var(--el-bg-color); /* 使用Element Plus主题色 */
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.el-menu--horizontal>.el-menu-item:nth-child(1) {
  margin-right: auto;
}

.el-menu {
  background-color: transparent !important;
}

.el-menu-item {
  background-color: transparent !important;
  font-size: 17px;
}

.avatar-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 35px;
  height: 35px;
  cursor: pointer;
  margin-right: 8px;
}

/* 隐藏头像子菜单的箭头图标 - 使用多种选择器确保生效 */
:deep(.avatar-sub-menu .el-sub-menu__icon-arrow),
:deep(.avatar-sub-menu .el-icon),
:deep(.avatar-sub-menu i.el-sub-menu__icon-arrow) {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  opacity: 0 !important;
  visibility: hidden !important;
}

/* 调整头像子菜单的标题区域，移除箭头占用的空间 */
:deep(.avatar-sub-menu .el-sub-menu__title) {
  padding-right: 0 !important;
}

.avatar-menu-item {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 确保子菜单项激活状态正确显示 */
:deep(.el-menu--horizontal .el-sub-menu .el-menu-item.is-active) {
  color: #C8161D !important;
  border-bottom-color: #C8161D !important;
}
</style>

<style>
/* 全局样式作为备选方案，确保箭头被隐藏 */
.el-menu--horizontal .avatar-sub-menu .el-sub-menu__icon-arrow,
.el-menu--horizontal .avatar-sub-menu .el-icon.el-sub-menu__icon-arrow {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  opacity: 0 !important;
  visibility: hidden !important;
}

.el-menu--horizontal .avatar-sub-menu .el-sub-menu__title {
  padding-right: 0 !important;
}
</style>