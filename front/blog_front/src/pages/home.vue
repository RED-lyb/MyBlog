<script setup>
import { onMounted, ref, nextTick, provide } from 'vue'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import Home_main from '../components/home_main.vue'
import CreateButton from '../components/CreateButton.vue'

// 搜索筛选参数
const searchFilters = ref({
  author_id: '',
  author_name: '',
  title: '',
  start_date: '',
  end_date: ''
})

// 排序参数
const sortOptions = ref({
  sort_by: 'published_at',
  sort_order: 'desc'
})

// 提供给子组件使用
provide('searchFilters', searchFilters)
provide('sortOptions', sortOptions)

const authStore = useAuthStore()
const {
  user,
  isAuthenticated,
  tokenExpired,
  username,
  userId,
  registeredTime,
  avatar,
  bgColor,
  bgPattern
} = storeToRefs(authStore)
const { fetchUserInfo } = useUserInfo()
const router = useRouter()
const route = useRoute()
const guest_info_show = () => {
  ElMessageBox.confirm(
    `您当前正在以游客身份访问，仅可进行博客文档内容阅读，<br/>
        无个人主页，无法撰写与上传内容，无法与其他用户进行互动，
        如需获得完整体验，请进行登录<br/>`,
    '游客须知',
    {
      dangerouslyUseHTMLString: true,
      cancelButtonText: '继续访问',
      confirmButtonText: '去登录',
      type: 'info',
      center: true,
    }
  )
    .then(() => {
      router.push({ path: '/login' })
    })
    .catch(() => {
    })
}
// 页面挂载时刷新用户信息（确保数据最新）
// 注意：应用启动时已自动获取，这里作为刷新机制
onMounted(async () => {
  authStore.syncFromLocalStorage()

  if (tokenExpired.value) {
    // token已过期，等待路由守卫处理
    return
  }

  const accessToken = localStorage.getItem('access_token')

  if (!accessToken) {
    // 游客模式：没有 token
    // 只有从登录页的游客登录进入时才显示弹窗
    const shouldShowDialog = sessionStorage.getItem('show_guest_dialog') === 'true'
    if (!isAuthenticated.value && shouldShowDialog) {
      // 清除标记，确保只弹出一次
      sessionStorage.removeItem('show_guest_dialog')
      await nextTick()
      guest_info_show()
    }
    return
  }

  try {
    await fetchUserInfo()
  } catch (error) {
    // 如果是token过期错误，不显示错误消息，让路由守卫处理
    if (error.message !== 'TOKEN_EXPIRED') {
      // 其他错误可以在这里处理
    }
  } finally {
    // 只有在不是过期状态且未认证时，且从登录页的游客登录进入时才显示游客提示
    const shouldShowDialog = sessionStorage.getItem('show_guest_dialog') === 'true'
    if (!isAuthenticated.value && !tokenExpired.value && shouldShowDialog) {
      // 清除标记，确保只弹出一次
      sessionStorage.removeItem('show_guest_dialog')
      await nextTick()
      guest_info_show()
    }
  }
})

// 重置筛选条件
const resetFilters = () => {
  searchFilters.value = {
    author_id: '',
    author_name: '',
    title: '',
    start_date: '',
    end_date: ''
  }
  sortOptions.value = {
    sort_by: 'published_at',
    sort_order: 'desc'
  }
}
</script>

<template>
  <div class="common-layout">
      <el-container>
        <el-header style="padding: 0">
          <Head />
        </el-header>
        <el-container>
          <el-aside class="search-aside">
            <div class="search-filter-container">
              <div class="filter-title">
                <span>搜索筛选</span>
                <el-icon><Search /></el-icon>
              </div>
              
              <!-- 用户ID -->
              <div class="filter-item">
                <label>用户ID</label>
                <el-input
                  v-model="searchFilters.author_id"
                  placeholder="精确匹配"
                  clearable
                  size="small"
                />
              </div>
              
              <!-- 用户名 -->
              <div class="filter-item">
                <label>用户名</label>
                <el-input
                  v-model="searchFilters.author_name"
                  placeholder="模糊匹配"
                  clearable
                  size="small"
                />
              </div>
              
              <!-- 文章名 -->
              <div class="filter-item">
                <label>文章名</label>
                <el-input
                  v-model="searchFilters.title"
                  placeholder="模糊匹配"
                  clearable
                  size="small"
                />
              </div>
              
              <!-- 发布时间区间 -->
              <div class="filter-item">
                <label>发布时间</label>
                <el-date-picker
                  v-model="searchFilters.start_date"
                  type="date"
                  placeholder="开始日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  size="small"
                  style="width: 100%; margin-bottom: 8px;"
                />
                <el-date-picker
                  v-model="searchFilters.end_date"
                  type="date"
                  placeholder="结束日期"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                  size="small"
                  style="width: 100%;"
                />
              </div>
              
              <!-- 排序方式 -->
              <div class="filter-item">
                <label>排序方式</label>
                <el-select
                  v-model="sortOptions.sort_by"
                  size="small"
                  style="width: 100%; margin-bottom: 8px;"
                >
                  <el-option label="发布时间" value="published_at" />
                  <el-option label="阅读数" value="view_count" />
                  <el-option label="喜欢数" value="love_count" />
                  <el-option label="评论数" value="comment_count" />
                </el-select>
                <el-select
                  v-model="sortOptions.sort_order"
                  size="small"
                  style="width: 100%;"
                >
                  <el-option label="降序" value="desc" />
                  <el-option label="升序" value="asc" />
                </el-select>
              </div>
              
              <!-- 重置按钮 -->
              <div class="filter-actions">
                <el-button
                  type="default"
                  size="small"
                  plain
                  @click="resetFilters"
                  style="width: 100%;"
                >
                  重置筛选
                </el-button>
              </div>
            </div>
          </el-aside>
          <el-main>
            <Home_main />
          </el-main>
          <el-aside>
            <CreateButton />
          </el-aside>
        </el-container>
        <el-footer >
          <Footer />
        </el-footer>
      </el-container>
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
  padding: 20px 20px 20px 20px;
  border: 1px solid var(--el-border-color-light);
  margin-top: 10px;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
}


.search-filter-container {
  padding: 20px;
}

.filter-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 20px 0;
  color: var(--el-text-color-primary);
  border-bottom: 2px solid var(--el-border-color-light);
  padding-bottom: 10px;
}

.filter-item {
  margin-bottom: 16px;
}

.filter-item label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: var(--el-text-color-regular);
  font-weight: 500;
}

.filter-actions {
  margin-top: 20px;
}
</style>