<script setup>
import { onMounted, ref, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import UserInfoSidebar from '../components/UserInfoSidebar.vue'
import apiClient from '../lib/api.js'

const route = useRoute()
const router = useRouter()
const targetUserId = ref(null)
const targetUser = ref(null)
const userLoading = ref(false)
const userError = ref(null)

const authStore = useAuthStore()
const {
  user,
  isAuthenticated,
  tokenExpired,
  userId
} = storeToRefs(authStore)
const { loading, fetchUserInfo } = useUserInfo()
const isLoading = ref(true)
const layoutReady = ref(false)
const showPageLoading = computed(() => loading.value || isLoading.value || !layoutReady.value)

// 判断当前页面类型
const currentPageType = computed(() => {
  const path = route.path
  if (path.includes('/edit')) return 'edit'
  if (path.includes('/following')) return 'following'
  if (path.includes('/followers')) return 'followers'
  if (path.includes('/liked-articles')) return 'liked-articles'
  if (path.includes('/articles')) return 'articles'
  return 'home'
})

// 面包屑导航
const breadcrumbs = computed(() => {
  const crumbs = []
  if (targetUserId.value) {
    crumbs.push({
      name: '个人主页',
      path: `/user_home/${targetUserId.value}`,
      isLast: currentPageType.value === 'home'
    })
    
    if (currentPageType.value === 'edit') {
      crumbs.push({
        name: '编辑资料',
        path: `/user_home/${targetUserId.value}/edit`,
        isLast: true
      })
    } else if (currentPageType.value === 'following') {
      crumbs.push({
        name: '关注列表',
        path: `/user_home/${targetUserId.value}/following`,
        isLast: true
      })
    } else if (currentPageType.value === 'followers') {
      crumbs.push({
        name: '粉丝列表',
        path: `/user_home/${targetUserId.value}/followers`,
        isLast: true
      })
    } else if (currentPageType.value === 'liked-articles') {
      crumbs.push({
        name: '喜欢的文章',
        path: `/user_home/${targetUserId.value}/liked-articles`,
        isLast: true
      })
    } else if (currentPageType.value === 'articles') {
      crumbs.push({
        name: '发布的文章',
        path: `/user_home/${targetUserId.value}/articles`,
        isLast: true
      })
    }
  }
  return crumbs
})

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}

// 获取目标用户信息
const fetchTargetUser = async (userId) => {
  if (!userId || userId === null || userId === undefined || isNaN(userId)) {
    userError.value = '用户ID不存在'
    userLoading.value = false
    return
  }

  userLoading.value = true
  userError.value = null
  targetUser.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${userId}/`)
    if (response.data?.success) {
      targetUser.value = response.data.data.user
    } else {
      userError.value = response.data?.error || '获取用户信息失败'
    }
  } catch (err) {
    if (err.response?.status === 404) {
      userError.value = '用户不存在'
    } else {
      userError.value = err.message || '请求失败'
    }
    console.error('获取用户信息错误:', err)
  } finally {
    userLoading.value = false
  }
}


// 导航到路径
const navigateToPath = (path) => {
  router.push(path)
}

// 监听路由参数变化
watch(() => route.params.userId, async (newUserId) => {
  if (newUserId) {
    targetUserId.value = parseInt(newUserId)
    await fetchTargetUser(targetUserId.value)
  } else {
    targetUser.value = null
    userError.value = null
  }
}, { immediate: true })

// 监听路由变化，更新面包屑
watch(() => route.path, () => {
  // 路由变化时可能需要重新加载数据
})

// 页面挂载时刷新用户信息
onMounted(async () => {
  authStore.syncFromLocalStorage()

  // 从路由参数获取目标用户ID
  if (route.params.userId) {
    targetUserId.value = parseInt(route.params.userId)
    await fetchTargetUser(targetUserId.value)
  }

  if (tokenExpired.value) {
    isLoading.value = false
    await markLayoutReady()
    return
  }

  const accessToken = localStorage.getItem('access_token')

  if (!accessToken) {
    isLoading.value = false
    await markLayoutReady()
    return
  }

  try {
    await fetchUserInfo()
  } catch (error) {
    if (error.message !== 'TOKEN_EXPIRED') {
      // 其他错误可以在这里处理
    }
  } finally {
    isLoading.value = false
    await markLayoutReady()
  }
})
</script>

<template>
  <FullScreenLoading :visible="showPageLoading" />
  <div v-if="showPageLoading">
  </div>
  <div v-else>
    <div class="common-layout">
      <el-container>
        <el-header style="padding: 0">
          <Head />
        </el-header>
        <el-container>
          <el-aside class="user-aside">
            <UserInfoSidebar 
              :user-id="targetUserId || userId"
              :username="targetUser?.username || user?.username"
            />
          </el-aside>
          <el-main>
            <!-- 面包屑导航 -->
            <div class="breadcrumb-container">
              <div class="dsi-breadcrumbs text-sm items-center gap-2">
                <ul>
                  <li v-for="(crumb, index) in breadcrumbs" :key="crumb.path">
                    <a 
                      v-if="!crumb.isLast"
                      @click.prevent="navigateToPath(crumb.path)"
                    >
                      <!-- 个人主页使用房子图标 -->
                      <svg
                        v-if="crumb.name === '个人主页'"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        class="h-4 w-4">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
                        />
                      </svg>
                      <!-- 其他使用右箭头图标 -->
                      <svg
                        v-else
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        class="h-4 w-4">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                      {{ crumb.name }}
                    </a>
                    
                    <span v-else class="inline-flex items-center gap-2">
                      <!-- 编辑资料使用编辑图标 -->
                      <svg
                        v-if="crumb.name === '编辑资料'"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        class="h-4 w-4">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                        />
                      </svg>
                      <!-- 统计列表使用列表图标 -->
                      <svg
                        v-else-if="crumb.name.includes('关注') || crumb.name.includes('粉丝') || crumb.name.includes('喜欢') || crumb.name.includes('文章')"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        class="h-4 w-4">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M4 6h16M4 10h16M4 14h16M4 18h16"
                        />
                      </svg>
                      <!-- 默认使用文档图标 -->
                      <svg
                        v-else
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                        class="h-4 w-4">
                        <path
                          stroke-linecap="round"
                          stroke-linejoin="round"
                          stroke-width="2"
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      {{ crumb.name }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>
            <!-- 子路由内容 -->
            <router-view />
          </el-main>
        </el-container>
        <el-footer style="padding: 0">
          <Footer />
        </el-footer>
      </el-container>
    </div>
  </div>
</template>

<style scoped>
.el-aside {
  background-color: #00000000;
  width: 230px;
  position: sticky;
  top: 60px;
  align-self: flex-start;
  height: calc(100vh - 165px);
}

.el-main {
  background-color: #00000000;
  min-height: max(570px, calc(100vh - 165px));
  padding: 0px 20px 20px 20px;
  border: 1px solid var(--el-border-color-light);
  margin-top: 10px;
  margin-right: 100px;
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
}

.user-aside {
  padding: 0;
}

.breadcrumb-container {
  margin: 10px;
  display: flex;
  align-items: center;
}

.user-loading,
.user-error {
  text-align: center;
  padding: 40px;
}

.user-error {
  color: #f56c6c;
}

.user-info {
  padding: 20px;
}

.user-info h2 {
  margin-bottom: 15px;
}

.user-info p {
  margin: 10px 0;
}

.edit-profile-container {
  padding: 20px;
}

.section-title {
  font-size: 24px;
  margin-bottom: 30px;
  color: var(--el-text-color-primary);
}

.form-section {
  margin-bottom: 40px;
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.form-section-title {
  font-size: 18px;
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
  border-bottom: 2px solid var(--el-border-color-light);
  padding-bottom: 10px;
}

.user-home-content {
  padding: 20px;
}
</style>
