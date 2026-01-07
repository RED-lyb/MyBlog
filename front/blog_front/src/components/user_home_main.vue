<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import apiClient from '../lib/api.js'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import RadiantText from '../pages/inspira/RadiantText.vue'

const route = useRoute()
const router = useRouter()
const targetUserId = ref(null)
const loading = ref(false)
const error = ref(null)

// 用户信息
const targetUser = ref(null)
const userLoading = ref(false)
const userError = ref(null)

// 列表数据
const followingList = ref([])
const followersList = ref([])
const likedArticlesList = ref([])
const articlesList = ref([])

// 当前显示的类型
const currentType = computed(() => {
  const path = route.path
  if (path.includes('/following')) return 'following'
  if (path.includes('/followers')) return 'followers'
  if (path.includes('/liked-articles')) return 'liked-articles'
  if (path.includes('/articles')) return 'articles'
  return 'home'
})

// 默认头像
const defaultAvatar = '/default_head.png'

// 构建头像URL
const buildAvatarUrl = (userId, avatar) => {
  if (!userId || !avatar) return defaultAvatar
  const baseUrl = import.meta.env?.VITE_API_FILE_URL || import.meta.env?.VITE_API_URL || ''
  const avatarFileName = `${userId}${avatar}`
  if (!baseUrl) return `/api/static/user_heads/${avatarFileName}`
  const normalizedBase = baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`
  return `${normalizedBase}static/user_heads/${avatarFileName}`
}

// 获取用户头像URL
const getUserAvatarUrl = async (userId, avatar) => {
  if (!userId || !avatar) return defaultAvatar

  const avatarFileName = `${userId}${avatar}`

  try {
    const { data } = await axios.get(`${import.meta.env.VITE_API_URL}home/avatar/`, {
      params: {
        file_name: avatarFileName
      }
    })
    if (data?.success && data?.data?.avatar_url) {
      return data.data.avatar_url
    } else {
      return buildAvatarUrl(userId, avatar)
    }
  } catch (error) {
    console.error('获取头像失败', error)
    return buildAvatarUrl(userId, avatar)
  }
}

// 获取关注列表
const fetchFollowingList = async () => {
  if (!targetUserId.value) return

  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${targetUserId.value}/following/`)
    if (response.data?.success) {
      followingList.value = response.data.data.following_list || []
      // 加载头像
      for (const user of followingList.value) {
        if (user.avatar) {
          user.avatarUrl = await getUserAvatarUrl(user.id, user.avatar)
        } else {
          user.avatarUrl = defaultAvatar
        }
      }
    } else {
      error.value = response.data?.error || '获取关注列表失败'
    }
  } catch (err) {
    console.error('获取关注列表错误:', err)
    error.value = err.response?.data?.error || '获取关注列表失败'
  } finally {
    loading.value = false
  }
}

// 获取粉丝列表
const fetchFollowersList = async () => {
  if (!targetUserId.value) return

  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${targetUserId.value}/followers/`)
    if (response.data?.success) {
      followersList.value = response.data.data.followers_list || []
      // 加载头像
      for (const user of followersList.value) {
        if (user.avatar) {
          user.avatarUrl = await getUserAvatarUrl(user.id, user.avatar)
        } else {
          user.avatarUrl = defaultAvatar
        }
      }
    } else {
      error.value = response.data?.error || '获取粉丝列表失败'
    }
  } catch (err) {
    console.error('获取粉丝列表错误:', err)
    error.value = err.response?.data?.error || '获取粉丝列表失败'
  } finally {
    loading.value = false
  }
}

// 获取喜欢的文章列表
const fetchLikedArticlesList = async () => {
  if (!targetUserId.value) return

  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${targetUserId.value}/liked-articles/`)
    if (response.data?.success) {
      likedArticlesList.value = response.data.data.articles_list || []
    } else {
      error.value = response.data?.error || '获取喜欢的文章列表失败'
    }
  } catch (err) {
    console.error('获取喜欢的文章列表错误:', err)
    error.value = err.response?.data?.error || '获取喜欢的文章列表失败'
  } finally {
    loading.value = false
  }
}

// 获取发布的文章列表
const fetchArticlesList = async () => {
  if (!targetUserId.value) return

  loading.value = true
  error.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${targetUserId.value}/articles/`)
    if (response.data?.success) {
      articlesList.value = response.data.data.articles_list || []
    } else {
      error.value = response.data?.error || '获取文章列表失败'
    }
  } catch (err) {
    console.error('获取文章列表错误:', err)
    error.value = err.response?.data?.error || '获取文章列表失败'
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 跳转到用户主页
const goToUserHome = (userId) => {
  router.push(`/user_home/${userId}`)
}

// 跳转到文章详情
const goToArticle = (articleId) => {
  router.push(`/article/${articleId}`)
}

// 获取用户信息
const fetchUserInfo = async () => {
  if (!targetUserId.value) return

  userLoading.value = true
  userError.value = null
  targetUser.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${targetUserId.value}/`)
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

// 加载数据
const loadData = () => {
  if (!targetUserId.value) return

  switch (currentType.value) {
    case 'home':
      fetchUserInfo()
      break
    case 'following':
      fetchFollowingList()
      break
    case 'followers':
      fetchFollowersList()
      break
    case 'liked-articles':
      fetchLikedArticlesList()
      break
    case 'articles':
      fetchArticlesList()
      break
  }
}

// 监听路由变化
watch(() => route.params.userId, (newUserId) => {
  if (newUserId) {
    targetUserId.value = parseInt(newUserId)
    loadData()
  }
}, { immediate: true })

watch(() => currentType.value, () => {
  loadData()
})

onMounted(() => {
  if (route.params.userId) {
    targetUserId.value = parseInt(route.params.userId)
    loadData()
  }
})
</script>

<template>
  <div class="user-home-main">
    <!-- 主页内容 -->
    <div v-if="currentType === 'home'">
      <div v-if="userLoading" class="loading">加载中...</div>
      <div v-else-if="userError" class="error">{{ userError }}</div>
      <div v-else class="welcome-message">

        <div class="user-introduction">
          <RadiantText
            class="inline-flex items-center justify-center px-4 py-1 transition ease-out hover:text-neutral-600 hover:duration-300 hover:dark:text-neutral-400"
            :duration="5">
            <span class="text-3xl font-bold">个人介绍</span>
          </RadiantText>
          <p v-if="targetUser?.bio">{{ targetUser.bio }}</p>
          <p v-else class="empty-introduction">该用户还没有个人介绍</p>
        </div>
      </div>
    </div>

    <!-- 关注列表 -->
    <div v-else-if="currentType === 'following'" class="list-content">
      <h2 class="list-title">关注列表</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="followingList.length === 0" class="empty">暂无关注</div>
      <div v-else class="user-list">
        <div v-for="user in followingList" :key="user.id" class="user-item" @click="goToUserHome(user.id)">
          <img :src="user.avatarUrl" :alt="user.username" class="user-avatar" />
          <div class="user-info">
            <div class="user-name">{{ user.username }}</div>
            <div class="user-stats">
              <span>关注 {{ user.follow_count || 0 }}</span>
              <span>粉丝 {{ user.follower_count || 0 }}</span>
              <span>文章 {{ user.article_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 粉丝列表 -->
    <div v-else-if="currentType === 'followers'" class="list-content">
      <h2 class="list-title">粉丝列表</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="followersList.length === 0" class="empty">暂无粉丝</div>
      <div v-else class="user-list">
        <div v-for="user in followersList" :key="user.id" class="user-item" @click="goToUserHome(user.id)">
          <img :src="user.avatarUrl" :alt="user.username" class="user-avatar" />
          <div class="user-info">
            <div class="user-name">{{ user.username }}</div>
            <div class="user-stats">
              <span>关注 {{ user.follow_count || 0 }}</span>
              <span>粉丝 {{ user.follower_count || 0 }}</span>
              <span>文章 {{ user.article_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 喜欢的文章列表 -->
    <div v-else-if="currentType === 'liked-articles'" class="list-content">
      <h2 class="list-title">喜欢的文章</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="likedArticlesList.length === 0" class="empty">暂无喜欢的文章</div>
      <div v-else class="article-list">
        <div v-for="article in likedArticlesList" :key="article.id" class="article-item"
          @click="goToArticle(article.id)">
          <h3 class="article-title">{{ article.title }}</h3>
          <p class="article-content">{{ article.content }}</p>
          <div class="article-meta">
            <span>作者：{{ article.author_name }}</span>
            <span>浏览：{{ article.view_count }}</span>
            <span>喜欢：{{ article.love_count }}</span>
            <span>评论：{{ article.comment_count }}</span>
            <span>发布时间：{{ formatDate(article.published_at) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 发布的文章列表 -->
    <div v-else-if="currentType === 'articles'" class="list-content">
      <h2 class="list-title">发布的文章</h2>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="articlesList.length === 0" class="empty">暂无发布的文章</div>
      <div v-else class="article-list">
        <div v-for="article in articlesList" :key="article.id" class="article-item" @click="goToArticle(article.id)">
          <h3 class="article-title">{{ article.title }}</h3>
          <p class="article-content">{{ article.content }}</p>
          <div class="article-meta">
            <span>浏览：{{ article.view_count }}</span>
            <span>喜欢：{{ article.love_count }}</span>
            <span>评论：{{ article.comment_count }}</span>
            <span>发布时间：{{ formatDate(article.published_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.user-home-main {
  padding: 20px;
}



.welcome-message h2 {
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
}

.welcome-message p {
  color: var(--el-text-color-regular);
}

.user-introduction {
  padding: 20px;
  background-color: var(--el-bg-color-page);
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
  text-align: left;
}

.intro-title {
  display: block;
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 20px;
  text-align: center;
}

@media (max-width: 768px) {
  .intro-title {
    font-size: 28px;
  }
}

.empty-introduction {
  color: var(--el-text-color-secondary);
  font-style: italic;
}

.list-content {
  min-height: 400px;
}

.list-title {
  margin-bottom: 20px;
  color: var(--el-text-color-primary);
  font-size: 24px;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 40px;
  color: var(--el-text-color-regular);
}

.error {
  color: #f56c6c;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.user-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.user-item:hover {
  background-color: var(--el-fill-color-light);
  border-color: var(--el-color-primary);
}

.user-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 15px;
  border: 2px solid var(--el-border-color-light);
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
  color: var(--el-text-color-primary);
}

.user-stats {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.article-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.article-item {
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.article-item:hover {
  background-color: var(--el-fill-color-light);
  border-color: var(--el-color-primary);
}

.article-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
  color: var(--el-text-color-primary);
}

.article-content {
  color: var(--el-text-color-regular);
  margin-bottom: 15px;
  line-height: 1.6;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.article-meta {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: var(--el-text-color-secondary);
}
</style>
