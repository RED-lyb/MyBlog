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
import c from 'highlight.js/lib/languages/c'
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
hljs.registerLanguage('c++', c)
hljs.registerLanguage('c', c)

// 标题和内容
const title = ref('')
const content = ref('')
const editorRef = ref(null)

// 富文本编辑器工具栏状态
const showHeadingDropdown = ref(false)
const showCodeLangDropdown = ref(false)
const showColorPicker = ref(false)
const selectedColor = ref('#000000')

// 插入文本到编辑器（支持撤销）
const insertText = (beforeText, afterText = '', cursorPosition = 'end') => {
  const textarea = editorRef.value
  if (!textarea) return

  // 聚焦到编辑器
  textarea.focus()

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const text = textarea.value
  const selectedText = text.substring(start, end)

  // 使用 execCommand 插入文本，这样浏览器会自动记录撤销历史
  const newText = beforeText + selectedText + afterText

  // 先删除选中的文本
  if (start !== end) {
    textarea.setSelectionRange(start, end)
    document.execCommand('delete')
  }

  // 插入新文本
  document.execCommand('insertText', false, newText)

  // 更新 content.value
  content.value = textarea.value

  // 设置光标位置
  nextTick(() => {
    if (cursorPosition === 'middle') {
      // 光标放在中间（开始标签和结束标签之间）
      const newCursorPos = start + beforeText.length + selectedText.length
      textarea.setSelectionRange(newCursorPos, newCursorPos)
    } else {
      // 光标放在末尾
      const newCursorPos = start + beforeText.length + selectedText.length + afterText.length
      textarea.setSelectionRange(newCursorPos, newCursorPos)
    }
    textarea.focus()
  })
}

// 加粗
const handleBold = () => {
  insertText('**', '**')
}

// 斜体
const handleItalic = () => {
  insertText('*', '*')
}

// 下划线（Markdown不支持原生下划线，使用HTML）
const handleUnderline = () => {
  insertText('<u>', '</u>')
}

// 标题
const handleHeading = (level) => {
  const prefix = '#'.repeat(level) + ' '
  insertText(prefix, '')
}

// 有序列表
const handleOrderedList = () => {
  insertText('1. ', '')
}

// 无序列表
const handleUnorderedList = () => {
  insertText('- ', '')
}

// 代码块
const handleCodeBlock = (lang) => {
  insertText(`\`\`\`${lang}\n`, '\n\`\`\`', 'middle')
}

// 颜色（使用HTML span标签）
const handleColor = () => {
  const color = selectedColor.value
  insertText(`<span style="color: ${color}">`, '</span>', 'middle')
  // 关闭颜色选择器弹窗
  showColorPicker.value = false
}

// 标题选项
const headingOptions = [
  { label: '标题 1 (H1)', value: 'h1' },
  { label: '标题 2 (H2)', value: 'h2' },
  { label: '标题 3 (H3)', value: 'h3' },
  { label: '标题 4 (H4)', value: 'h4' },
  { label: '标题 5 (H5)', value: 'h5' },
  { label: '标题 6 (H6)', value: 'h6' }
]

// 代码语言选项
const codeLangOptions = [
  { label: 'C', value: 'c' },
  { label: 'C++', value: 'c++' },
  { label: 'Java', value: 'java' },
  { label: 'Python', value: 'python' },
  { label: 'HTML', value: 'html' },
  { label: 'CSS', value: 'css' },
  { label: 'JavaScript', value: 'javascript' },
  { label: 'TypeScript', value: 'typescript' },
  { label: 'JSON', value: 'json' },
  { label: 'Bash', value: 'bash' },
  { label: 'SQL', value: 'sql' },
  { label: 'PHP', value: 'php' }

]

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

      // 生成唯一的代码块ID
      const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

      // 如果有语言标识且该语言已注册，使用highlight.js进行高亮
      if (lang && hljs.getLanguage(lang)) {
        try {
          // 执行高亮
          const highlighted = hljs.highlight(codeStr, { language: lang })

          // 返回带头部和高亮的HTML结构
          return `
<div class="code-block-wrapper" data-code-id="${codeBlockId}">
  <div class="code-block-header">
    <span class="code-block-lang">${lang}</span>
    <button class="code-block-copy-btn" onclick="copyCodeBlock('${codeBlockId}')" title="复制代码">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
    </button>
  </div>
  <pre class="hljs"><code class="language-${lang}" data-code-content="${encodeURIComponent(codeStr)}">${highlighted.value}</code></pre>
</div>`
        } catch (err) {
          // 如果高亮失败，降级为转义代码
          const escaped = codeStr
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;')
          return `
<div class="code-block-wrapper" data-code-id="${codeBlockId}">
  <div class="code-block-header">
    <span class="code-block-lang">${lang}</span>
    <button class="code-block-copy-btn" onclick="copyCodeBlock('${codeBlockId}')" title="复制代码">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
    </button>
  </div>
  <pre class="hljs"><code class="language-${lang}" data-code-content="${encodeURIComponent(codeStr)}">${escaped}</code></pre>
</div>`
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
      const langDisplay = lang || 'code'
      return `
<div class="code-block-wrapper" data-code-id="${codeBlockId}">
  <div class="code-block-header">
    <span class="code-block-lang">${langDisplay}</span>
    <button class="code-block-copy-btn" onclick="copyCodeBlock('${codeBlockId}')" title="复制代码">
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
      </svg>
    </button>
  </div>
  <pre class="hljs"><code class="${langClass}" data-code-content="${encodeURIComponent(codeStr)}">${escaped}</code></pre>
</div>`
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

    // 插入Tab字符
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

// 复制代码块函数（挂载到window对象）
onMounted(() => {
  // 注册全局复制函数
  window.copyCodeBlock = (codeBlockId) => {
    const codeBlock = document.querySelector(`[data-code-id="${codeBlockId}"]`)
    if (!codeBlock) return

    const codeElement = codeBlock.querySelector('code[data-code-content]')
    if (!codeElement) return

    const codeContent = decodeURIComponent(codeElement.getAttribute('data-code-content'))

    navigator.clipboard.writeText(codeContent).then(() => {
      ElMessage.success('代码已复制到剪贴板')
    }).catch(() => {
      ElMessage.error('复制失败')
    })
  }
})

onUnmounted(() => {
  // 清理全局函数
  if (window.copyCodeBlock) {
    delete window.copyCodeBlock
  }
})

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
    <div class="write-container-header">
      <!-- 工具栏 -->
      <div class="toolbar">

        <!-- 标题下拉菜单 -->
        <el-dropdown trigger="click" @visible-change="(visible) => showHeadingDropdown = visible">
          <button class="toolbar-btn" title="标准字号">
            <el-icon>
              <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 24 24">
                <path fill="currentColor" d="M5.554 22H3.4L11 3h2l7.6 19h-2.154l-2.4-6H7.954zm3.2-8h6.492L12 5.885z">
                </path>
              </svg>
            </el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="option in headingOptions" :key="option.value"
                @click="handleHeading(parseInt(option.value.replace('h', '')))">
                {{ option.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 分隔线 -->
        <div class="toolbar-divider">|</div>

        <!-- 加粗按钮 -->
        <button class="toolbar-btn" title="加粗" @click="handleBold">
          <el-icon>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round" style="width: 18px; height: 18px;">
              <path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"></path>
              <path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"></path>
            </svg>
          </el-icon>
        </button>

        <!-- 分隔线 -->
        <div class="toolbar-divider">|</div>

        <!-- 斜体按钮 -->
        <button class="toolbar-btn" title="斜体" @click="handleItalic">
          <el-icon>
            <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 24 24">
              <g fill="none">
                <path
                  d="M24 0v24H0V0zM12.593 23.258l-.011.002l-.071.035l-.02.004l-.014-.004l-.071-.035q-.016-.005-.024.005l-.004.01l-.017.428l.005.02l.01.013l.104.074l.015.004l.012-.004l.104-.074l.012-.016l.004-.017l-.017-.427q-.004-.016-.017-.018m.265-.113l-.013.002l-.185.093l-.01.01l-.003.011l.018.43l.005.012l.008.007l.201.093q.019.005.029-.008l.004-.014l-.034-.614q-.005-.019-.02-.022m-.715.002a.02.02 0 0 0-.027.006l-.006.014l-.034.614q.001.018.017.024l.015-.002l.201-.093l.01-.008l.004-.011l.017-.43l-.003-.012l-.01-.01z">
                </path>
                <path fill="currentColor"
                  d="M9 4a1 1 0 0 1 1-1h6a1 1 0 1 1 0 2h-2.117l-1.75 14H14a1 1 0 1 1 0 2H8a1 1 0 1 1 0-2h2.117l1.75-14H10a1 1 0 0 1-1-1">
                </path>
              </g>
            </svg>
          </el-icon>
        </button>

        <!-- 分隔线 -->
        <div class="toolbar-divider">|</div>

        <!-- 下划线按钮 -->
        <button class="toolbar-btn" title="下划线" @click="handleUnderline">
          <el-icon>
            <svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 2048 2048">
              <path fill="currentColor"
                d="M1011 1792q-161 0-274-46t-184-133t-105-209t-33-275V128h192v988q0 109 21 201t71 159t131 106t201 38q115 0 193-36t127-101t69-154t21-195V128h192v975q0 158-34 285t-109 217t-193 138t-286 49m-627 128h1280v128H384z">
              </path>
            </svg>
          </el-icon>
        </button>

        <!-- 分隔线 -->
        <div class="toolbar-divider">|</div>



        <!-- 有序列表按钮 -->
        <button class="toolbar-btn" title="有序列表" @click="handleOrderedList">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 16 16">
              <path fill="currentColor"
                d="M3.684 1.01c.193.045.33.21.33.402v3.294a.42.42 0 0 1-.428.412a.42.42 0 0 1-.428-.412V2.58a3 3 0 0 1-.664.435a.436.436 0 0 1-.574-.184a.405.405 0 0 1 .192-.552c.353-.17.629-.432.82-.661a3 3 0 0 0 .27-.388a.44.44 0 0 1 .482-.22m-1.53 6.046a.4.4 0 0 1 0-.582l.002-.001V6.47l.004-.002l.008-.008a1 1 0 0 1 .103-.084a2.2 2.2 0 0 1 1.313-.435h.007c.32.004.668.084.947.283c.295.21.485.536.485.951c0 .452-.207.767-.488.992c-.214.173-.49.303-.714.409q-.054.024-.103.049c-.267.128-.468.24-.61.39a.8.8 0 0 0-.147.22h1.635a.42.42 0 0 1 .427.411a.42.42 0 0 1-.428.412H2.457a.42.42 0 0 1-.428-.412c0-.51.17-.893.446-1.184c.259-.275.592-.445.86-.574q.065-.03.124-.06c.231-.11.4-.19.529-.293c.12-.097.18-.193.18-.36c0-.148-.057-.23-.14-.289a.8.8 0 0 0-.448-.122a1.32 1.32 0 0 0-.818.289l-.005.005a.44.44 0 0 1-.602-.003m.94 5.885a.42.42 0 0 1 .427-.412c.294 0 .456-.08.537-.15a.3.3 0 0 0 .11-.246c-.006-.16-.158-.427-.647-.427c-.352 0-.535.084-.618.137a.4.4 0 0 0-.076.062l-.003.004l.01-.018v.001l-.002.002l-.002.004l-.003.006l-.005.008l.002-.003a.436.436 0 0 1-.563.165a.405.405 0 0 1-.191-.552v-.002l.002-.003l.003-.006l.008-.013a.7.7 0 0 1 .087-.12c.058-.067.142-.146.259-.22c.238-.153.59-.276 1.092-.276c.88 0 1.477.556 1.502 1.22c.012.303-.1.606-.339.84c.238.232.351.535.34.838c-.026.664-.622 1.22-1.503 1.22c-.502 0-.854-.122-1.092-.275a1.2 1.2 0 0 1-.326-.308l-.02-.033l-.008-.013l-.003-.005l-.001-.003v-.001l-.001-.001a.405.405 0 0 1 .19-.553a.436.436 0 0 1 .564.165l.003.004c.01.01.033.035.076.063c.083.053.266.137.618.137c.489 0 .641-.268.648-.428a.3.3 0 0 0-.11-.245c-.082-.072-.244-.151-.538-.151a.42.42 0 0 1-.427-.412M7.5 3a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1zm0 4a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1zm0 4a.5.5 0 0 0 0 1h6a.5.5 0 0 0 0-1z">
              </path>
            </svg></el-icon>
        </button>

        <!-- 分隔线 -->
        <div class="toolbar-divider">|</div>

        <!-- 无序列表按钮 -->
        <button class="toolbar-btn" title="无序列表" @click="handleUnorderedList">
          <el-icon><svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 24 24">
              <path fill="currentColor"
                d="M9 19h12v-2H9zm0-6h12v-2H9zm0-8v2h12V5zm-4-.5a1.5 1.5 0 1 0 .001 3.001A1.5 1.5 0 0 0 5 4.5m0 6a1.5 1.5 0 1 0 .001 3.001A1.5 1.5 0 0 0 5 10.5m0 6a1.5 1.5 0 1 0 .001 3.001A1.5 1.5 0 0 0 5 16.5">
              </path>
            </svg></el-icon>
        </button>

        <!-- 分隔线 -->
        <div class="toolbar-divider">|</div>

        <!-- 代码语言下拉菜单 -->
        <el-dropdown trigger="click" @visible-change="(visible) => showCodeLangDropdown = visible">
          <button class="toolbar-btn" title="代码">
            <el-icon><svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 256 256">
                <path fill="currentColor"
                  d="M69.12 94.15L28.5 128l40.62 33.85a8 8 0 1 1-10.24 12.29l-48-40a8 8 0 0 1 0-12.29l48-40a8 8 0 0 1 10.24 12.3m176 27.7l-48-40a8 8 0 1 0-10.24 12.3L227.5 128l-40.62 33.85a8 8 0 1 0 10.24 12.29l48-40a8 8 0 0 0 0-12.29m-82.39-89.37a8 8 0 0 0-10.25 4.79l-64 176a8 8 0 0 0 4.79 10.26A8.1 8.1 0 0 0 96 224a8 8 0 0 0 7.52-5.27l64-176a8 8 0 0 0-4.79-10.25">
                </path>
              </svg></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="option in codeLangOptions" :key="option.value"
                @click="handleCodeBlock(option.value)">
                {{ option.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <!-- 分隔线 -->
        <div class="toolbar-divider">|</div>

        <!-- 颜色选择器 -->
        <el-popover v-model:visible="showColorPicker" trigger="click" placement="bottom" :width="350">
          <template #reference>
            <button class="toolbar-btn" title="颜色">
              <el-icon><svg xmlns="http://www.w3.org/2000/svg" width="256" height="256" viewBox="0 0 16 16">
                  <path fill="currentColor"
                    d="M13.432 2.569c.18.18.324.394.42.63h.002c.098.236.147.489.147.744a1.98 1.98 0 0 1-.573 1.456l-.7.7l.25.26a1.137 1.137 0 0 1 0 1.6l-.583.583a1.137 1.137 0 0 1-1.6 0l-.255-.255l-.002-.002l-4.935 4.935a.5.5 0 0 1-.354.146h-.532l-1.286.552a1.025 1.025 0 0 1-1.35-1.348l.553-1.287v-.532a.5.5 0 0 1 .146-.353l4.935-4.945l-.254-.254a1.136 1.136 0 0 1 0-1.6l.59-.585a1.14 1.14 0 0 1 1.234-.245q.207.087.367.245l.256.254l.7-.7a1.95 1.95 0 0 1 1.375-.57a1.98 1.98 0 0 1 1.449.57M8.424 6.164l-4.785 4.788v.428a.5.5 0 0 1-.04.2l-.6 1.38l1.415-.557a.5.5 0 0 1 .2-.04h.428L9.83 7.574zm4.299-1.48a.9.9 0 0 0 .205-.307l-.001.002a1 1 0 0 0 .07-.362a1 1 0 0 0-.276-.741a.95.95 0 0 0-.667-.276a1 1 0 0 0-.731.277l-1.057 1.058a.5.5 0 0 1-.707 0l-.61-.608a.14.14 0 0 0-.046-.03a.1.1 0 0 0-.054-.01a.1.1 0 0 0-.054.01a.14.14 0 0 0-.046.03l-.583.583a.13.13 0 0 0-.04.095a.13.13 0 0 0 .04.095l3.333 3.332a.13.13 0 0 0 .096.04a.13.13 0 0 0 .095-.04l.583-.583a.13.13 0 0 0 .04-.096a.13.13 0 0 0-.04-.095l-.608-.61a.5.5 0 0 1 0-.707z">
                  </path>
                </svg></el-icon>
            </button>
          </template>
          <div style="padding: 10px;">
            <el-color-picker-panel v-model="selectedColor" show-alpha />
            <div style="margin-top: 10px; text-align: center;">
              <button class="dsi-btn dsi-btn-outline dsi-btn-warning" @click="handleColor" style="width: 100%;">
                应用颜色
              </button>
            </div>
          </div>
        </el-popover>
      </div>
    </div>


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

.write-container-header {
  height: 50px;
  background-color: rgba(170, 170, 170, 0.2);
  border-radius: 8px;
  display: flex;
  align-items: center;
  padding: 0 15px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 100%;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 32px;
  height: 32px;
  border: none;
  background-color: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: var(--el-text-color-primary);
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.toolbar-btn:active {
  background-color: rgba(0, 0, 0, 0.1);
}

.toolbar-btn .el-icon {
  font-size: 18px;
}

.toolbar-btn .dropdown-arrow {
  font-size: 12px;
  margin-left: -4px;
}

.toolbar-divider {
  width: 1px;
  height: 24px;
  margin-right: 5px;
  margin-left: 4px;
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
.content-preview :deep(.code-block-wrapper) {
  margin: 1em 0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.content-preview :deep(.code-block-header) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 16px;
  background: rgba(200, 200, 200, 0.2);
  border-bottom: 1px solid var(--el-border-color-light);
}

.content-preview :deep(.code-block-lang) {
  font-size: 12px;
  font-weight: 500;
  color: var(--el-text-color-secondary);
  text-transform: uppercase;
}

.content-preview :deep(.code-block-copy-btn) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  border-radius: 4px;
  cursor: pointer;
  color: var(--el-text-color-secondary);
  transition: all 0.2s;
}

.content-preview :deep(.code-block-copy-btn:hover) {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.content-preview :deep(.code-block-copy-btn:active) {
  background: var(--el-color-primary-light-7);
}

.content-preview :deep(pre) {
  /* 使用半透明背景，适配亮色和暗色主题 */
  background: rgba(245, 245, 245, 0.2);
  border-radius: 0 0 8px 8px !important;
  margin: 0 !important;
  padding: 16px !important;
  overflow-x: auto !important;
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
