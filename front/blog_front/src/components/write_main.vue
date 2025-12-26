<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { marked } from 'marked'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/user_info.js'
import apiClient from '../lib/api.js'
import CaptchaDialog from '../components/CaptchaDialog.vue'
// 按需导入highlight.js核心和语言包（减小打包体积）
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import python from 'highlight.js/lib/languages/python'
import java from 'highlight.js/lib/languages/java'
import xml from 'highlight.js/lib/languages/xml' // HTML使用XML
import css from 'highlight.js/lib/languages/css'
import typescript from 'highlight.js/lib/languages/typescript'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'
import sql from 'highlight.js/lib/languages/sql'
import php from 'highlight.js/lib/languages/php'
// 导入自定义的代码高亮样式
import '@/assets/highlight.css'

const router = useRouter()
const authStore = useAuthStore()

// 注册常用语言
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('java', java)
hljs.registerLanguage('xml', xml) // HTML使用XML
hljs.registerLanguage('html', xml) // HTML作为XML的别名
hljs.registerLanguage('css', css)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('php', php)

// 标题和内容
const title = ref('')
const content = ref('')
const editorRef = ref(null)

// 配置marked@17.x使用highlight.js进行代码高亮
marked.use({
  gfm: true, // 支持GitHub风格的Markdown
  breaks: true, // 支持换行
  langPrefix: 'hljs language-', // 添加语言类前缀
  renderer: {
    code(token) {
      // marked@17.x 中，code 方法接收的是 token 对象
      // token 对象包含: { type: 'code', raw, code, lang, text }
      // 过滤掉代码块标记（```），只保留实际代码内容
      let codeStr = token.text || token.code || token.raw || ''
      const lang = token.lang || ''

      // 如果代码内容以 ``` 开头或结尾，说明 marked 解析有问题，需要清理
      // 这种情况通常发生在代码块未完整时
      codeStr = codeStr.replace(/^```+\s*/gm, '').replace(/\s*```+$/gm, '').trim()

      // 如果有语言标识且该语言已注册，使用highlight.js进行高亮
      if (lang && hljs.getLanguage(lang)) {
        try {
          // 执行高亮
          const highlighted = hljs.highlight(codeStr, { language: lang })

          // 返回带高亮的HTML结构（必须包含hljs类）
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

      // 如果没有指定语言或语言未注册，直接转义代码（不进行高亮）
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

// 解析Markdown和HTML
const parsedContent = computed(() => {
  if (!content.value) {
    return ''
  }

  try {
    const result = marked.parse(content.value)

    // 确保返回的是字符串
    if (typeof result === 'string') {
      return result
    } else {
      // 如果不是字符串，强制转换为字符串
      const stringResult = String(result || '')

      // 如果是 [object Object]，返回错误提示
      if (stringResult === '[object Object]') {
        return '<p style="color: red;">解析错误：返回了对象而非字符串</p>'
      }

      return stringResult
    }
  } catch (e) {
    return String(content.value || '')
  }
})

// 处理Tab键，在textarea中插入缩进
const handleTabKey = (e) => {
  if (e.key === 'Tab') {
    e.preventDefault()
    const textarea = e.target
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const value = textarea.value

    // 插入Tab字符（或2个空格）
    const tab = '  ' // 使用2个空格代替Tab
    const newValue = value.substring(0, start) + tab + value.substring(end)

    // 更新内容
    content.value = newValue

    // 恢复光标位置
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + tab.length
      textarea.focus()
    })
  }
}

onMounted(() => {
  if (editorRef.value) {
    editorRef.value.addEventListener('keydown', handleTabKey)
  }
})

onUnmounted(() => {
  if (editorRef.value) {
    editorRef.value.removeEventListener('keydown', handleTabKey)
  }
})

// 发布文章相关
const showCaptchaDialog = ref(false)
const captchaError = ref(false)
const publishing = ref(false)

// 验证文章内容
const validateArticle = () => {
  if (!title.value || !title.value.trim()) {
    ElMessage.error('请输入文章标题')
    return false
  }
  if (title.value.length > 500) {
    ElMessage.error('文章标题不能超过500个字符')
    return false
  }
  if (!content.value || !content.value.trim()) {
    ElMessage.error('请输入文章内容')
    return false
  }
  return true
}

// 处理发布按钮点击
const handlePublish = () => {
  if (!validateArticle()) {
    return
  }

  // 检查是否登录
  if (!authStore.isAuthenticated) {
    ElMessage.error('请先登录')
    router.push('/login')
    return
  }

  // 显示验证码对话框
  showCaptchaDialog.value = true
  captchaError.value = false
}

// 验证码验证成功
const onCaptchaSuccess = async (captchaData) => {
  publishing.value = true
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}article/create/`, {
      title: title.value.trim(),
      content: content.value,
      captcha_key: captchaData.captcha_key,
      captcha_value: captchaData.captcha_value
    })

    if (response.data?.success) {
      ElMessage.success('文章发布成功')
      // 跳转到文章详情页
      router.push(`/article/${response.data.data.article_id}`)
    } else {
      const errorMsg = response.data?.error || '发布失败'
      ElMessage.error(errorMsg)

      // 如果是验证码错误，重新显示验证码对话框
      if (errorMsg.includes('验证码') || errorMsg.includes('锁定')) {
        captchaError.value = true
        showCaptchaDialog.value = true
      }
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.message || '发布失败'
    ElMessage.error(errorMsg)

    // 如果是验证码错误或锁定，重新显示验证码对话框
    if (errorMsg.includes('验证码') || errorMsg.includes('锁定')) {
      captchaError.value = true
      showCaptchaDialog.value = true
    }
  } finally {
    publishing.value = false
  }
}

// 验证码取消
const onCaptchaCancel = () => {
  showCaptchaDialog.value = false
  captchaError.value = false
}
</script>

<template>
  <div class="write-container">
    <el-splitter class="splitter-wrapper">
      <el-splitter-panel size="50%" class="editor-panel">
        <div class="panel-content">
          <!-- 标题输入区域 -->
          <div class="title-section">
            <input v-model="title" type="text" placeholder="请输入文章标题..." class="title-input" />
          </div>

          <!-- 分割线 -->
          <el-divider class="section-divider" />

          <!-- 编辑器区域 -->
          <div class="editor-section">
            <textarea ref="editorRef" v-model="content" placeholder="请输入文章内容（支持Markdown和HTML）..." class="content-editor"
              @keydown="handleTabKey" />
          </div>
        </div>
      </el-splitter-panel>

      <el-splitter-panel class="preview-panel">
        <div class="panel-content">
          <!-- 标题预览区域 -->
          <div class="title-section">
            <h1 class="title-preview">{{ title || '请输入文章标题...' }}</h1>
          </div>

          <!-- 分割线 -->
          <el-divider class="section-divider" />

          <!-- 预览区域 -->
          <div class="preview-section">
            <div v-if="content" class="content-preview" v-html="parsedContent" />
            <div v-else class="content-placeholder">
              预览区域：输入内容后，这里将显示预览效果
            </div>
          </div>
        </div>
      </el-splitter-panel>
    </el-splitter>
    

  </div>
      <!-- 发布按钮 -->
      <div class="publish-button-container">
      <button class="dsi-btn dsi-btn-outline dsi-btn-warning" @click="handlePublish" :disabled="publishing">
        {{ publishing ? '发布中...' : '发布' }}
      </button>
    </div>
  <!-- 验证码对话框 -->
  <CaptchaDialog v-model="showCaptchaDialog" :has-error="captchaError" @success="onCaptchaSuccess"
    @cancel="onCaptchaCancel" />
</template>

<style scoped>
.write-container {
  width: 100%;
  height: max(500px, calc(100vh - 240px));
  border-radius: 8px;
  overflow: visible;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--el-border-color);
  display: flex;
  flex-direction: column;
}

.splitter-wrapper {
  flex: 1;
  border-radius: 8px;
  overflow: hidden;
}

.editor-panel,
.preview-panel {
  height: 100%;
  overflow: hidden;
}

.panel-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}

.title-section {
  flex-shrink: 0;
  padding-bottom: 10px;
}

.title-input {
  width: 100%;
  font-size: 24px;
  font-weight: bold;
  border: none;
  outline: none;
  background: transparent;
  color: var(--el-text-color-primary);
  padding: 8px 0;
}

.title-input::placeholder {
  color: var(--el-text-color-placeholder);
  font-weight: normal;
}

.title-preview {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  padding: 8px 0;
  color: var(--el-text-color-primary);
}

.title-preview:empty::before {
  content: '请输入文章标题...';
  color: var(--el-text-color-placeholder);
  font-weight: normal;
}

.section-divider {
  margin: 10px 0;
  flex-shrink: 0;
}

.editor-section,
.preview-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-editor {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  padding: 0;
  background: transparent;
  color: var(--el-text-color-primary);
  tab-size: 2;
}

.content-preview {
  width: 100%;
  height: 100%;
  overflow-y: auto;
  padding: 0;
  font-size: 14px;
  line-height: 1.8;
  color: var(--el-text-color-primary);
}

/* 标题样式 - 设置不同的字体大小 */
.content-preview :deep(h1) {
  font-size: 2em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.2;
}

.content-preview :deep(h2) {
  font-size: 1.5em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.3;
}

.content-preview :deep(h3) {
  font-size: 1.25em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.4;
}

.content-preview :deep(h4) {
  font-size: 1.1em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.4;
}

.content-preview :deep(h5) {
  font-size: 1em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.5;
}

.content-preview :deep(h6) {
  font-size: 0.9em !important;
  font-weight: bold !important;
  margin-top: 1em;
  margin-bottom: 0.5em;
  line-height: 1.5;
}

.content-preview :deep(p) {
  margin: 0.5em 0;
  display: block;
}

/* 列表样式 - 确保正常显示 */
.content-preview :deep(ul),
.content-preview :deep(ol) {
  margin: 0.5em 0 !important;
  padding-left: 2em !important;
  display: block !important;
}

.content-preview :deep(ul) {
  list-style-type: disc !important;
  /* 第一级：实心圆点 */
}

.content-preview :deep(ul ul) {
  list-style-type: circle !important;
  /* 第二级：空心圆点 */
}

.content-preview :deep(ul ul ul) {
  list-style-type: square !important;
  /* 第三级：方块 */
}

.content-preview :deep(ul ul ul ul) {
  list-style-type: disc !important;
  /* 第四级：回到实心圆点 */
}

.content-preview :deep(ol) {
  list-style-type: decimal !important;
  /* 有序列表：数字 */
}

.content-preview :deep(ol ol) {
  list-style-type: lower-alpha !important;
  /* 第二级：小写字母 */
}

.content-preview :deep(ol ol ol) {
  list-style-type: lower-roman !important;
  /* 第三级：小写罗马数字 */
}

.content-preview :deep(ol ol ol ol) {
  list-style-type: decimal !important;
  /* 第四级：回到数字 */
}

.content-preview :deep(li) {
  display: list-item !important;
  margin: 0.25em 0 !important;
}

.content-preview :deep(blockquote) {
  border-left: 4px solid var(--el-border-color);
  padding-left: 1em;
  margin: 0.5em 0;
  color: var(--el-text-color-secondary);
}

/* 行内代码样式 */
.content-preview :deep(code:not(pre code)) {
  background: var(--el-fill-color-light);
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

/* 代码块样式 - 确保highlight.js的样式生效 */
.content-preview :deep(pre) {
  /* 使用半透明背景，适配亮色和暗色主题 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 6px !important;
  margin-right: 5px;
  margin-left: 5px;
}

.content-preview :deep(pre code) {
  background: transparent !important;
  padding: 0 !important;
  line-height: 1.5 !important;
  color: var(--el-text-color-primary) !important;
}

.content-preview :deep(a) {
  color: var(--el-color-primary);
  text-decoration: none;
}

.content-preview :deep(a:hover) {
  text-decoration: underline;
}

.content-preview :deep(img) {
  max-width: 100%;
  height: auto;
}

.content-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--el-text-color-placeholder);
  font-size: 14px;
}

/* 组2: 拖拽器基础样式（双下划线 __dragger） */
:deep(.el-splitter-bar__dragger) {
  width: 4px !important;
  /* 拖拽区域稍微宽一点，方便操作 */
  background-color: transparent !important;
}


:deep(.el-splitter-bar__dragger-horizontal:hover:not(.is-disabled)::before),
:deep(.el-splitter-bar__dragger-horizontal:hover:not(.is-disabled)::after) {
  background-color: #EF5710 !important;
}

/* 拖动时的状态 - 使用正确的类名 el-splitter-bar__dragger-active */
:deep(.el-splitter-bar__dragger-active::before),
:deep(.el-splitter-bar__dragger-active::after),
:deep(.el-splitter-bar__dragger-horizontal.el-splitter-bar__dragger-active::before),
:deep(.el-splitter-bar__dragger-horizontal.el-splitter-bar__dragger-active::after) {
  background-color: #C8161D !important;
}

/* 组7: 容器圆角 */
:deep(.el-splitter) {
  border-radius: 8px;
}

:deep(.el-splitter__wrapper) {
  border-radius: 8px;
}

.publish-button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  padding-top: 19px;
  flex-shrink: 0;
}
</style>
