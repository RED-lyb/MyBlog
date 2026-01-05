<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { marked } from 'marked'
import apiClient from '../lib/api.js'
import axios from 'axios'
// 导入代码高亮样式
import '@/assets/highlight.css'
// 按需导入highlight.js核心和语言包
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import java from 'highlight.js/lib/languages/java'
import xml from 'highlight.js/lib/languages/xml'
import css from 'highlight.js/lib/languages/css'
import typescript from 'highlight.js/lib/languages/typescript'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'
import sql from 'highlight.js/lib/languages/sql'
import php from 'highlight.js/lib/languages/php'

// 注册常用语言
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('java', java)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('css', css)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('php', php)

// 配置marked使用highlight.js进行代码高亮
marked.use({
  gfm: true,
  breaks: true,
  langPrefix: 'hljs language-',
  renderer: {
    code(token) {
      let codeStr = token.text || token.code || token.raw || ''
      const lang = token.lang || ''
      
      // 清理代码块标记
      codeStr = codeStr.replace(/^```+\s*/gm, '').replace(/\s*```+$/gm, '').trim()
      
      // 如果有语言标识且该语言已注册，使用highlight.js进行高亮
      if (lang && hljs.getLanguage(lang)) {
        try {
          const highlighted = hljs.highlight(codeStr, { language: lang })
          return `<pre class="hljs"><code class="language-${lang}">${highlighted.value}</code></pre>`
        } catch (err) {
          // 如果高亮失败，降级为转义代码
          const escaped = codeStr
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;')
          return `<pre class="hljs"><code class="language-${lang}">${escaped}</code></pre>`
        }
      }
      
      // 如果没有指定语言或语言未注册，直接转义代码
      const escaped = codeStr
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
      const langClass = lang ? `language-${lang}` : ''
      return `<pre class="hljs"><code class="${langClass}">${escaped}</code></pre>`
    }
  }
})

import { Star, ChatLineRound, View } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessage } from 'element-plus'
import CaptchaDialog from './CaptchaDialog.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { isAuthenticated, userId } = storeToRefs(authStore)
const article = ref(null)
const loading = ref(false)
const error = ref(null)
const isLiked = ref(false)

const emit = defineEmits(['author-loaded', 'comment-added'])

// 评论Drawer相关
const commentDrawerVisible = ref(false)
const commentContent = ref('')
const commentLoading = ref(false)
const captchaDialogVisible = ref(false)
const captchaData = ref(null)

// 跳转到作者主页
const goToAuthorHome = () => {
  if (article.value?.author_id) {
    router.push(`/user_home/${article.value.author_id}`)
  }
}

// 解析文章内容（支持Markdown和HTML）
const parsedContent = computed(() => {
  if (!article.value?.content) {
    return ''
  }
  
  try {
    // 使用marked解析Markdown
    const result = marked.parse(article.value.content)
    return typeof result === 'string' ? result : String(result || '')
  } catch (e) {
    console.error('Markdown解析错误:', e)
    return article.value.content
  }
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

// 获取用户头像
const fetchUserAvatar = async () => {
  if (!article.value?.author_id || !article.value?.author_avatar) {
    article.value.display_avatar = defaultAvatar
    article.value.avatar_loading = false
    return
  }
  
  article.value.avatar_loading = true
  const avatarFileName = `${article.value.author_id}${article.value.author_avatar}`
  
  try {
    const { data } = await axios.get(`${import.meta.env.VITE_API_URL}home/avatar/`, {
      params: {
        file_name: avatarFileName
      }
    })
    if (data?.success && data?.data?.avatar_url) {
      article.value.display_avatar = data.data.avatar_url
    } else {
      article.value.display_avatar = buildAvatarUrl(article.value.author_id, article.value.author_avatar)
    }
  } catch (error) {
    console.error('获取头像失败', error)
    article.value.display_avatar = buildAvatarUrl(article.value.author_id, article.value.author_avatar)
  } finally {
    article.value.avatar_loading = false
  }
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取文章详情
const fetchArticleDetail = async () => {
  const articleId = route.params.id
  if (!articleId) {
    error.value = '文章ID不存在'
    return
  }

  loading.value = true
  error.value = null
  
  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}article/${articleId}/`)
    if (response.data?.success) {
      article.value = response.data.data
      // 初始化头像相关属性
      article.value.display_avatar = defaultAvatar
      article.value.avatar_loading = true
      fetchUserAvatar()
      
      // 通知父组件作者ID已加载
      emit('author-loaded', article.value.author_id)
      
      // 如果用户已登录，检查喜欢状态
      if (isAuthenticated.value && userId.value) {
        try {
          const likeResponse = await apiClient.get(`${import.meta.env.VITE_API_URL}article/${articleId}/like/status/`)
          if (likeResponse.data?.success) {
            isLiked.value = likeResponse.data.data.is_liked
          }
        } catch (err) {
          console.error('获取喜欢状态失败:', err)
        }
      }
    } else {
      error.value = response.data?.error || '获取文章详情失败'
    }
  } catch (err) {
    error.value = err.message || '请求失败'
    console.error('获取文章详情错误:', err)
  } finally {
    loading.value = false
  }
}

// 处理喜欢点击事件
const handleLikeClick = async () => {
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}article/${route.params.id}/like/`)
    if (response.data?.success) {
      isLiked.value = response.data.data.is_liked
      // 更新文章的喜欢数量
      if (article.value) {
        article.value.love_count = response.data.data.is_liked 
          ? (article.value.love_count || 0) + 1 
          : Math.max((article.value.love_count || 0) - 1, 0)
      }
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data?.error || '操作失败')
    }
  } catch (err) {
    console.error('喜欢操作失败:', err)
    ElMessage.error(err.response?.data?.error || '操作失败')
  }
}

// 处理评论点击事件
const handleCommentClick = () => {
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  
  commentContent.value = ''
  commentDrawerVisible.value = true
}

// 提交评论
const handleCommentSubmit = () => {
  if (!commentContent.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  
  if (commentContent.value.length > 200) {
    ElMessage.warning('评论内容不能超过200字')
    return
  }
  
  // 打开验证码对话框
  captchaDialogVisible.value = true
}

// 验证码验证成功回调
const handleCaptchaSuccess = async (captchaInfo) => {
  captchaData.value = captchaInfo
  captchaDialogVisible.value = false
  
  commentLoading.value = true
  try {
    const response = await apiClient.post(
      `${import.meta.env.VITE_API_URL}article/${route.params.id}/comments/create/`,
      {
        content: commentContent.value,
        captcha_key: captchaInfo.captcha_key,
        captcha_value: captchaInfo.captcha_value
      }
    )
    
    if (response.data?.success) {
      ElMessage.success('评论发布成功')
      commentContent.value = ''
      commentDrawerVisible.value = false
      // 更新文章的评论数
      if (article.value) {
        article.value.comment_count = (article.value.comment_count || 0) + 1
      }
      // 通知父组件刷新评论列表
      emit('comment-added')
    } else {
      ElMessage.error(response.data?.error || '发布评论失败')
    }
  } catch (err) {
    console.error('发布评论失败:', err)
    ElMessage.error(err.response?.data?.error || '发布评论失败')
  } finally {
    commentLoading.value = false
  }
}

// 验证码取消回调
const handleCaptchaCancel = () => {
  captchaDialogVisible.value = false
}

// 处理Drawer关闭
const handleDrawerClose = (done) => {
  commentContent.value = ''
  done()
}

// 监听路由参数变化
watch(() => route.params.id, () => {
  fetchArticleDetail()
})

// 组件挂载时获取文章详情
onMounted(() => {
  fetchArticleDetail()
})
</script>

<template>
  <div class="article-main-container">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">错误: {{ error }}</div>
    <div v-else-if="article" class="article-detail">
      <!-- 文章标题 -->
      <h1 class="article-title">{{ article.title }}</h1>
      
      <!-- 作者信息 -->
      <div class="article-author">
        <div class="author-avatar-wrapper" @click="goToAuthorHome" :title="`查看 ${article.author_name} 的主页`">
          <el-skeleton :loading="article.avatar_loading" animated
            style="display: flex;align-items: center;justify-content: center;width: 40px;height: 40px;">
            <template #template>
              <el-skeleton-item variant="circle" style="width: 40px;height: 40px;" />
            </template>
            <template #default>
              <el-avatar :size="40" :src="article.display_avatar || defaultAvatar" />
            </template>
          </el-skeleton>
        </div>
        <div class="author-info">
          <span class="author-name" @click="goToAuthorHome" :title="`查看 ${article.author_name} 的主页`">{{ article.author_name }}</span>
          <span class="publish-time">发布时间：{{ formatDate(article.published_at) }}</span>
        </div>
      </div>
      
      <!-- 文章内容 -->
      <div class="article-content" v-html="parsedContent"></div>

      
      <!-- 文章统计信息 -->
      <div class="article-stats">
        <span class="stat-item">
          <el-icon><View /></el-icon>
          阅读 {{ article.view_count || 0 }}
        </span>
        <span 
          class="stat-item clickable" 
          :class="{ 'liked': isLiked }"
          @click="handleLikeClick"
          :title="isLiked ? '取消喜欢' : '喜欢'"
        >
          <el-icon :class="{ 'filled-star': isLiked }"><Star /></el-icon>
          喜欢 {{ article.love_count || 0 }}
        </span>
        <span 
          class="stat-item clickable" 
          @click="handleCommentClick"
          title="评论"
        >
          <el-icon><ChatLineRound /></el-icon>
          评论 {{ article.comment_count || 0 }}
        </span>
      </div>
      
    </div>
    
    <!-- 评论Drawer -->
    <el-drawer
      v-model="commentDrawerVisible"
      title="发表评论"
      direction="btt"
      size="300px"
      :close-on-click-modal="true"
      :show-close="true"
      :before-close="handleDrawerClose"
    >
      <div class="comment-drawer-content">
        <el-input
          v-model="commentContent"
          type="textarea"
          :rows="6"
          placeholder="请输入评论内容（最多200字）"
          maxlength="200"
          show-word-limit
        />
        <div class="comment-actions">
          <el-button plain @click="commentDrawerVisible = false">取消</el-button>
          <el-button type="primary" plain @click="handleCommentSubmit" :loading="commentLoading">
            发布
          </el-button>
        </div>
      </div>
    </el-drawer>
    
    <!-- 验证码对话框 -->
    <CaptchaDialog
      v-model="captchaDialogVisible"
      @success="handleCaptchaSuccess"
      @cancel="handleCaptchaCancel"
    />
  </div>
</template>

<style scoped>
.article-main-container {
  width: 100%;
  height: 100%;
  padding: 20px;
  overflow-y: auto;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
}

.error {
  color: #f56c6c;
}

.article-detail {
  max-width: 1200px;
  margin: 0 auto;
}

.article-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 20px;
  line-height: 1.4;
}

.article-author {
  display: flex;
  align-items: center;
  gap: 15px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--el-border-color);
}


.author-avatar-wrapper {
  cursor: pointer;
}

.author-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.author-name {
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
}
.author-name:hover{
  text-decoration: underline;
}

.publish-time {
  font-size: 14px;
  color: #999;
}

.article-stats {
  display: flex;
  gap: 20px;
  padding: 20px 0 20px 0;

  border-bottom: 1px solid var(--el-border-color);
  border-top: 1px solid var(--el-border-color);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #858585;
}

.stat-item.clickable {
  cursor: pointer;
  transition: color 0.3s;
}

.stat-item.clickable:hover {
  color: var(--el-color-primary);
}

.stat-item.clickable:hover .el-icon {
  color: var(--el-color-primary);
}

.stat-item.clickable:hover .el-icon.filled-star {
  fill: var(--el-color-primary);
}

.stat-item.liked {
  color: var(--el-color-warning);
}

.stat-item.liked .el-icon {
  color: var(--el-color-warning);
}

.stat-item.liked .el-icon.filled-star {
  fill: var(--el-color-warning);
}

.comment-drawer-content {
  padding: 0;
}

.comment-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.article-content {
  line-height: 1.8;
  word-wrap: break-word;
  margin-bottom: 20px;
  margin-top: 20px;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

/* 标题样式 */
.article-content :deep(h1) {
  font-size: 2em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.2;
}

.article-content :deep(h2) {
  font-size: 1.5em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.3;
}

.article-content :deep(h3) {
  font-size: 1.25em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.4;
}

.article-content :deep(h4) {
  font-size: 1.1em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.4;
}

.article-content :deep(h5) {
  font-size: 1em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.5;
}

.article-content :deep(h6) {
  font-size: 0.9em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.5;
}

.article-content :deep(p) {
  margin: 0.5em 0;
  display: block;
}

/* 列表样式 */
.article-content :deep(ul),
.article-content :deep(ol) {
  margin: 0.5em 0 !important;
  padding-left: 2em !important;
  display: block !important;
}

.article-content :deep(ul) {
  list-style-type: disc !important;
}

.article-content :deep(ul ul) {
  list-style-type: circle !important;
}

.article-content :deep(ul ul ul) {
  list-style-type: square !important;
}

.article-content :deep(ul ul ul ul) {
  list-style-type: disc !important;
}

.article-content :deep(ol) {
  list-style-type: decimal !important;
}

.article-content :deep(ol ol) {
  list-style-type: lower-alpha !important;
}

.article-content :deep(ol ol ol) {
  list-style-type: lower-roman !important;
}

.article-content :deep(ol ol ol ol) {
  list-style-type: decimal !important;
}

.article-content :deep(li) {
  display: list-item !important;
  margin: 0.25em 0 !important;
}

.article-content :deep(blockquote) {
  border-left: 4px solid var(--el-border-color);
  padding-left: 1em;
  margin: 0.5em 0;
  color: var(--el-text-color-secondary);
}

/* 行内代码样式 */
.article-content :deep(code:not(pre code)) {
  background: var(--el-fill-color-light);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

/* 代码块样式 */
.article-content :deep(pre) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px !important;
  margin: 1em 0 !important;
  padding: 16px !important;
  overflow-x: auto !important;
}

.article-content :deep(pre code) {
  background: transparent !important;
  padding: 0 !important;
  line-height: 1.5 !important;
  color: var(--el-text-color-primary) !important;
}

.article-content :deep(a) {
  color: var(--el-color-primary);
  text-decoration: none;
}

.article-content :deep(a:hover) {
  text-decoration: underline;
}

.article-content :deep(img) {
  max-width: 100%;
  height: auto;
}
:deep(.el-drawer__body){
  padding-top: 0 !important;
}
</style>

