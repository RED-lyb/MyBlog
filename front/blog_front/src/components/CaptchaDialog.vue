<template>
  <el-dialog
    v-model="visible"
    title="验证码验证"
    width="400px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
    center
    @keydown.enter.prevent.stop
  >
    <div class="captcha-dialog-content">
      <div class="captcha-form">
        <el-form :model="form" label-width="80px">
          <el-form-item label="验证码" required>
            <div class="captcha-input-group">
              <el-input
                ref="captchaInputRef"
                v-model="form.captcha_value"
                placeholder="请输入验证码"
                maxlength="4"
                clearable
                @keyup.enter="handleSubmit"
                @input="inputError = false"
                :class="['captcha-input', { 'error-input': inputError }]"
              />
              <div class="captcha-image-container">
                <img 
                  v-if="captchaImage" 
                  :src="captchaImage" 
                  :alt="'验证码'"
                  @click="refreshCaptcha"
                  class="captcha-image"
                  title="点击刷新验证码"
                />
                <div v-else class="captcha-loading">
                  <el-icon class="is-loading"><Loading /></el-icon>
                </div>
              </div>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleCancel" :disabled="loading">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">
          验证
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import axios from 'axios'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  hasError: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success', 'cancel'])

const apiUrl = import.meta.env.VITE_API_URL
const visible = ref(props.modelValue)
const loading = ref(false)
const captchaImage = ref('')
const captchaKey = ref('')
const inputError = ref(false)
const captchaInputRef = ref()

const form = reactive({
  captcha_value: ''
})

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  visible.value = newValue
  if (newValue) {
    // 弹窗打开时获取验证码
    getCaptcha()
    // 清空表单
    form.captcha_value = ''
    inputError.value = false
    // 自动聚焦到输入框
    nextTick(() => {
      setTimeout(() => {
        if (captchaInputRef.value) {
          captchaInputRef.value.focus()
        }
      }, 150) // 使用150ms延迟确保弹窗完全显示
    })
  }
})

// 监听错误状态
watch(() => props.hasError, (newError) => {
  if (newError && visible.value) {
    inputError.value = true
  }
})

// 监听visible变化
watch(visible, (newValue) => {
  emit('update:modelValue', newValue)
})

// 获取验证码
const getCaptcha = async () => {
  try {
    const response = await axios.get(`${apiUrl}captcha/`)
    
    if (response.data.success) {
      captchaKey.value = response.data.captcha_key
      captchaImage.value = response.data.captcha_image
    } else {
      ElMessage.error(response.data.error || '获取验证码失败')
    }
  } catch (error) {
    console.error('获取验证码失败:', error)
    ElMessage.error('获取验证码失败，请稍后重试')
  }
}

// 刷新验证码
const refreshCaptcha = () => {
  getCaptcha()
  form.captcha_value = ''
  inputError.value = false
}

// 验证验证码（只做基本验证，不调用后端API）
const verifyCaptcha = async () => {
  if (!form.captcha_value) {
    ElMessage.error('请输入验证码')
    inputError.value = true
    return false
  }

  if (!captchaKey.value) {
    ElMessage.error('验证码已过期，请刷新')
    inputError.value = true
    return false
  }

  // 基本验证通过，清除错误状态
  inputError.value = false
  return true
}

// 提交验证
const handleSubmit = async (event) => {
  // 阻止默认行为和事件传播
  if (event) {
    event.preventDefault()
    event.stopPropagation()
  }
  
  // 防止重复提交
  if (loading.value) return
  
  loading.value = true
  try {
    const isValid = await verifyCaptcha()
    if (isValid) {
      // 基本验证通过，返回验证码信息让后端验证
      emit('success', {
        captcha_key: captchaKey.value,
        captcha_value: form.captcha_value
      })
      visible.value = false
    }
    // 如果基本验证失败，不刷新验证码，让用户重新输入
  } finally {
    loading.value = false
  }
}

// 取消验证
const handleCancel = () => {
  visible.value = false
  emit('cancel')
}

// 键盘事件处理 - 只在弹窗打开时处理回车键
const handleKeyPress = (event) => {
  if (event.key === 'Enter' && visible.value) {
    // 检查是否在输入框内，如果是则不处理（让输入框的@keyup.enter处理）
    if (event.target.tagName === 'INPUT' && event.target.closest('.captcha-input-group')) {
      return
    }
    
    event.preventDefault()
    event.stopPropagation()
    event.stopImmediatePropagation()
    handleSubmit(event)
  }
}

// 组件挂载时添加键盘事件监听
onMounted(() => {
  document.addEventListener('keydown', handleKeyPress, true) // 使用捕获阶段
})

// 组件卸载时移除键盘事件监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress, true)
})
</script>
<style scoped>
   .captcha-input-group {
     display: flex;
     gap: 10px;
     align-items: center;        /* 垂直居中对齐 */
     flex-wrap: nowrap;         /* 防止换行 */
   }
   .captcha-image-container {
     width: 120px;
     height: 40px;
     min-width: 120px;          /* 最小宽度 */
     flex-shrink: 0;            /* 防止被压缩 */
     /* ... 其他样式 */
   }
   .captcha-input {
     flex: 1;                   /* 占据剩余空间 */
     min-width: 0;              /* 允许收缩 */
   }
   .captcha-dialog-content {
     padding: 20px 0;
     min-width: 350px;          /* 确保有足够空间 */
   }
</style>