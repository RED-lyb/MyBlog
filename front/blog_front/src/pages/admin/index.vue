<template>
  <div class="admin-layout">
    <!-- 左侧导航栏 -->
    <aside class="admin-sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <h2 v-if="!sidebarCollapsed" class="sidebar-title">{{ config?.blog_name || 'L-BLOG' }} 管理后台</h2>
        <el-button 
          :icon="sidebarCollapsed ? Expand : Fold" 
          circle 
          size="small"
          @click="toggleSidebar"
          class="toggle-btn"
        />
      </div>
      
      <nav class="sidebar-nav">
        <router-link
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ 'active': $route.path.startsWith(item.path) }"
        >
          <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
          <span v-if="!sidebarCollapsed" class="nav-text">{{ item.label }}</span>
        </router-link>
      </nav>
      
      <div class="sidebar-footer">
        <el-button 
          type="info" 
          plain 
          size="small" 
          @click="toggleTheme"
          style="width: 100%; margin-bottom: 12px"
        >
          <div class="theme-icon-wrapper">
            <transition name="theme">
              <svg 
                v-if="!theme_type" 
                class="theme-icon" 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M5.64,17l-.71.71a1,1,0,0,0,0,1.41,1,1,0,0,0,1.41,0l.71-.71A1,1,0,0,0,5.64,17ZM5,12a1,1,0,0,0-1-1H3a1,1,0,0,0,0,2H4A1,1,0,0,0,5,12Zm7-7a1,1,0,0,0,1-1V3a1,1,0,0,0-2,0V4A1,1,0,0,0,12,5ZM5.64,7.05a1,1,0,0,0,.7.29,1,1,0,0,0,.71-.29,1,1,0,0,0,0-1.41l-.71-.71A1,1,0,0,0,4.93,6.34Zm12,.29a1,1,0,0,0,.7-.29l.71-.71a1,1,0,1,0-1.41-1.41L17,5.64a1,1,0,0,0,0,1.41A1,1,0,0,0,17.66,7.34ZM21,11H20a1,1,0,0,0,0,2h1a1,1,0,0,0,0-2Zm-9,8a1,1,0,0,0-1,1v1a1,1,0,0,0,2,0V20A1,1,0,0,0,12,19ZM18.36,17A1,1,0,0,0,17,18.36l.71.71a1,1,0,0,0,1.41,0,1,1,0,0,0,0-1.41ZM12,6.5A5.5,5.5,0,1,0,17.5,12,5.51,5.51,0,0,0,12,6.5Zm0,9A3.5,3.5,0,1,1,15.5,12,3.5,3.5,0,0,1,12,15.5Z" />
              </svg>
            </transition>
            <transition name="theme">
              <svg
                v-if="theme_type" 
                class="theme-icon" 
                xmlns="http://www.w3.org/2000/svg" 
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M21.64,13a1,1,0,0,0-1.05-.14,8.05,8.05,0,0,1-3.37.73A8.15,8.15,0,0,1,9.08,5.49a8.59,8.59,0,0,1,.25-2A1,1,0,0,0,8,2.36,10.14,10.14,0,1,0,22,14.05,1,1,0,0,0,21.64,13Zm-9.5,6.69A8.14,8.14,0,0,1,7.08,5.22v.27A10.15,10.15,0,0,0,17.22,15.63a9.79,9.79,0,0,0,2.1-.22A8.11,8.11,0,0,1,12.14,19.73Z" />
              </svg>
            </transition>
          </div>
          <span v-if="!sidebarCollapsed" style="margin-left: 8px">切换主题</span>
        </el-button>
        <br/>
        <el-button 
          type="success" 
          plain 
          size="small" 
          @click="router.push('/home')"
          style="width: 100%; margin-bottom: 12px"
        >
          <el-icon><HomeFilled /></el-icon>
          <span v-if="!sidebarCollapsed" style="margin-left: 8px">进入博客</span>
        </el-button>
        <br/>
        <el-button 
          type="danger" 
          plain 
          size="small" 
          @click="handleLogout"
          style="width: 100%"
        >
          <el-icon><SwitchButton /></el-icon>
          <span v-if="!sidebarCollapsed" style="margin-left: 8px">退出登录</span>
        </el-button>
      </div>
    </aside>
    
    <!-- 右侧内容区 -->
    <main class="admin-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/user_info.js'
import { useConfigStore } from '../../stores/config.js'
import { storeToRefs } from 'pinia'
import { ElMessageBox } from 'element-plus'
import { useDark, useToggle } from '@vueuse/core'
import { 
  DataAnalysis, 
  Document, 
  User, 
  Folder, 
  Setting,
  Fold,
  Expand,
  SwitchButton,
  HomeFilled,
  Clock,
  ChatDotRound
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const configStore = useConfigStore()
const { config } = storeToRefs(configStore)

onMounted(() => {
  configStore.loadConfig()
})

const sidebarCollapsed = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// 主题切换逻辑
const isDark = useDark({
  selector: 'html',
  attribute: 'data-theme',
  valueDark: 'dark',
  valueLight: 'light',
  initialValue: 'dark'
})
const theme_type = ref(isDark.value)
const toggle_theme = useToggle(isDark)

const toggleTheme = () => {
  theme_type.value = !theme_type.value
}

watch(theme_type, (new_val) => {
  const html_class = document.documentElement
  toggle_theme()
  if (new_val) {
    html_class.classList.remove('light')
    html_class.classList.add('dark')
  } else {
    html_class.classList.remove('dark')
    html_class.classList.add('light')
  }
})

const menuItems = computed(() => [
  {
    path: '/admin/dashboard',
    label: '统计面板',
    icon: DataAnalysis
  },
  {
    path: '/admin/articles',
    label: '文章管理',
    icon: Document
  },
  {
    path: '/admin/users',
    label: '用户管理',
    icon: User
  },
  {
    path: '/admin/network-disk',
    label: '网盘管理',
    icon: Folder
  },
  {
    path: '/admin/history',
    label: '更新管理',
    icon: Clock
  },
  {
    path: '/admin/feedback',
    label: '反馈管理',
    icon: ChatDotRound
  },
  {
    path: '/admin/config',
    label: '全局配置',
    icon: Setting
  }
])

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '确认退出', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    authStore.resetLoginState()
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
    router.push('/login')
  }).catch(() => {})
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.admin-sidebar {
  width: 250px;
  background-color: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
}

.admin-sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--el-border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-title {
  margin: 0;
  font-size: 18px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.toggle-btn {
  min-width: auto;
  padding: 8px;
}

.sidebar-nav {
  flex: 1;
  padding: 20px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px 20px;
  color: var(--el-text-color-regular);
  text-decoration: none;
  transition: all 0.3s;
  gap: 12px;
}

.admin-sidebar:not(.collapsed) .nav-item {
  justify-content: flex-start;
}

.nav-item:hover {
  background-color: var(--el-fill-color-light);
  color: var(--el-color-primary);
}

.nav-item.active {
  background-color: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
  border-right: 3px solid var(--el-color-primary);
}

.nav-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.nav-text {
  white-space: nowrap;
}

.admin-sidebar.collapsed .nav-text {
  display: none;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid var(--el-border-color);
}

.admin-main {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.theme-icon-wrapper {
  position: relative;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-icon {
  position: absolute;
  width: 16px;
  height: 16px;
}

/* 主题切换动画 */
.theme-enter-from {
  opacity: 0;
  transform: rotate(180deg) scale(0.7);
}
.theme-enter-active {
  transition: all 0.5s ease;
}
.theme-enter-to {
  opacity: 1;
  transform: rotate(360deg) scale(1);
}

.theme-leave-from {
  opacity: 1;
  transform: rotate(0deg) scale(1);
}
.theme-leave-active {
  transition: all 0.5s ease;
  position: absolute;
}
.theme-leave-to {
  opacity: 0;
  transform: rotate(-180deg) scale(0.7);
}
</style>

