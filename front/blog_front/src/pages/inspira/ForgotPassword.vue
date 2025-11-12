<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { User, Notebook, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import FullScreenLoading from '../FullScreenLoading.vue'
import CaptchaDialog from '../../components/CaptchaDialog.vue'
const props = defineProps({
  visible: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close-dialog'])
const apiUrl = import.meta.env.VITE_API_URL
const active = ref(0)
const formRef = ref()
const protectQuestion = ref('') // 存储密保问题
const usernameInputRef = ref()
const answerInputRef = ref()
const passwordInputRef = ref()
const confirmInputRef = ref()
const isLoading = ref(false)
// 字段状态管理
const fieldStates = reactive({
  username: { validateState: '', validateMessage: '' },
  answer: { validateState: '', validateMessage: '' },
  password: { validateState: '', validateMessage: '' },
  confirm: { validateState: '', validateMessage: '' }
})

const form = reactive({
  username: '',
  answer: '',
  password: '',
  confirm: ''
})

// 验证码相关状态
const showCaptchaDialog = ref(false)
const captchaData = ref(null)
const captchaError = ref(false)

// 保留字黑名单（与登录注册保持一致）
const DB_KEYWORDS = [
  'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
  'USER', 'USERS', 'ORDER', 'GROUP', 'KEY', 'INDEX', 'TABLE', 'PASSWORD', 'ADMIN', 'ROOT'
]

/* 用户名验证规则 */
const validateUserName = (rule, value, callback) => {
  if (!value) return callback(new Error('请输入用户名'))
  if (!/^[A-Za-z0-9_\-\u4e00-\u9fa5]+$/.test(value)) {
    return callback(new Error('只允许字母、数字、下划线、连字符、中文'))
  }
  if (DB_KEYWORDS.includes(value.toUpperCase())) {
    return callback(new Error('不得使用该用户名，请更换'))
  }
  callback()
}

/* 密保答案验证规则 */
const validateAnswer = (_, value, callback) => {
  if (!value) return callback(new Error('请输入密保答案'))
  if (!/^[\u4e00-\u9fa5A-Za-z0-9]+$/.test(value)) {
    return callback(new Error('答案只能包含中文、英文和数字'))
  }
  callback()
}

/* 密码验证规则 */
const validatePass = (rule, value, callback) => {
  if (!value) return callback(new Error('请输入密码'))
  if (value.length < 8) return callback(new Error('密码至少 8 位'))
  if (!/[0-9]/.test(value)) return callback(new Error('需包含数字'))
  if (!/[A-Z]/.test(value)) return callback(new Error('需包含大写字母'))
  if (!/[a-z]/.test(value)) return callback(new Error('需包含小写字母'))
  callback()
}

/* 确认密码验证规则 */
const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUserName, trigger: ['blur', 'change'] }
  ],
  answer: [
    { required: true, message: '请输入密保答案', trigger: 'blur' },
    { validator: validateAnswer, trigger: ['blur', 'change'] }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { validator: validatePass, trigger: ['blur', 'change'] }
  ],
  confirm: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePass2, trigger: ['blur', 'change'] }
  ]
}

// 清除字段状态
const clearFieldState = (fieldName) => {
  fieldStates[fieldName].validateState = ''
  fieldStates[fieldName].validateMessage = ''
}

// 设置字段错误状态
const setFieldError = (fieldName, message) => {
  fieldStates[fieldName].validateState = 'error'
  fieldStates[fieldName].validateMessage = message
}

// 设置字段成功状态
const setFieldSuccess = (fieldName) => {
  fieldStates[fieldName].validateState = 'success'
  fieldStates[fieldName].validateMessage = ''
}

const pre = () => {
  if (active.value > 0) {
    active.value--;
  }
}

const next = async () => {
  // 防止重复提交
  if (isLoading.value) return
  
  if (active.value === 0) {
    // 验证用户名
    formRef.value.validateField('username', async (valid) => {
      if (!valid) return; // 验证失败，直接返回
      
      // 防止重复提交
      if (isLoading.value) return
      
      // 验证通过，发送请求
      try {
        setFieldSuccess('username')
        isLoading.value = true;
        const response = await axios.post(apiUrl + 'forgot/', {
          username: form.username
        });
        if (response.data.status === 'true') {
          // 用户存在，保存密保问题
          protectQuestion.value = response.data.protect
          active.value++;
        } else {
          // 显示服务端错误信息
          setFieldError('username', response.data.message || '用户不存在')
        }
      } catch (error) {
        // 网络或服务端错误
        const errorMessage = error.response?.data?.message || '用户名验证失败'
        setFieldError('username', errorMessage)
      } finally {
        isLoading.value = false;
      }
    })
  } else if (active.value === 1) {
    // 验证密保答案
    formRef.value.validateField('answer', async (valid) => {
      if (!valid) return; // 验证失败，直接返回
      
      // 防止重复提交
      if (isLoading.value) return
      
      // 验证通过，弹出验证码对话框
      setFieldSuccess('answer')
      showCaptchaDialog.value = true
    })
  } else if (active.value === 2) {
    // 验证新密码
    formRef.value.validateField(['password', 'confirm'], (valid) => {
      if (!valid) return; // 验证失败，直接返回
      // 验证通过
      setFieldSuccess('password')
      setFieldSuccess('confirm')
      // 完成所有步骤
      // 这里不需要发送请求，只是前端验证
    })
  }
}

const submit = async () => {
  if (active.value !== 2) return
  
  // 防止重复提交
  if (isLoading.value) return

  // 先进行表单验证
  const valid = await new Promise((resolve) => {
    formRef.value.validate((isValid) => {
      resolve(isValid)
    })
  })
  
  if (!valid) return // 表单验证失败，直接返回
  
  // 再次检查，防止在验证过程中重复提交
  if (isLoading.value) return
  
  try {
    isLoading.value = true
    // 表单验证通过，发送请求
    const response = await axios.put(apiUrl + 'forgot/', {
      username: form.username,
      password: form.password
    })
    
    if (response.data.status === 'true') {
      ElMessage.success(response.data.message)
      // 重置表单
      formRef.value.resetFields()
      active.value = 0
      protectQuestion.value = ''
      emit('close-dialog')
    } else {
      // 显示服务端错误信息
      const errorMessage = response.data.message || '密码重置失败'
      // 可以根据需要设置特定字段的错误状态
      setFieldError('password', errorMessage)
      setFieldError('confirm', errorMessage)
    }
  } catch (error) {
    // 网络或服务端错误
    const errorMessage = error.response?.data?.message || '密码重置失败，请稍后重试'
    setFieldError('password', errorMessage)
    setFieldError('confirm', errorMessage)
  } finally {
    isLoading.value = false
  }
}

// 验证码验证成功后的密保答案验证
const handleAnswerWithCaptcha = async (captchaInfo) => {
  try {
    isLoading.value = true;
    const response = await axios.post(apiUrl + 'forgot/', {
      username: form.username,
      answer: form.answer,
      captcha_key: captchaInfo.captcha_key,
      captcha_value: captchaInfo.captcha_value
    });
    
    if (response.data.status === 'true') {
      // 密保验证成功
      active.value++;
    } else {
      // 显示服务端错误信息
      const errorMessage = response.data.message || '密保答案错误'
      
      // 如果是验证码错误，重新弹出验证码对话框，不设置字段错误
      if (errorMessage.includes('验证码')) {
        ElMessage.error(errorMessage)
        captchaError.value = true
        showCaptchaDialog.value = true
      } else if (errorMessage.includes('锁定')) {
        // 如果是锁定错误，显示错误信息但不设置字段错误
        ElMessage.error(errorMessage)
      } else {
        // 非验证码错误才设置字段错误
        setFieldError('answer', errorMessage)
      }
    }
  } catch (error) {
    // 网络或服务端错误
    const errorMessage = error.response?.data?.message || '密保答案验证失败'
    
    // 如果是验证码错误，重新弹出验证码对话框，不设置字段错误
    if (errorMessage.includes('验证码')) {
      ElMessage.error(errorMessage)
      captchaError.value = true
      showCaptchaDialog.value = true
    } else if (errorMessage.includes('锁定')) {
      // 如果是锁定错误，显示错误信息但不设置字段错误
      ElMessage.error(errorMessage)
    } else {
      // 非验证码错误才设置字段错误
      setFieldError('answer', errorMessage)
    }
  } finally {
    isLoading.value = false;
  }
}

// 验证码验证成功
const onCaptchaSuccess = (captchaInfo) => {
  captchaData.value = captchaInfo
  showCaptchaDialog.value = false
  captchaError.value = false
  handleAnswerWithCaptcha(captchaInfo)
}

// 验证码验证取消
const onCaptchaCancel = () => {
  showCaptchaDialog.value = false
  captchaError.value = false
}

// 键盘事件处理
const handleKeyPress = (event) => {
  if (event.key === 'Enter') {
    // 如果验证码弹窗打开，不处理回车事件
    if (showCaptchaDialog.value) {
      return
    }
    
    event.preventDefault()
    
    // 根据当前步骤触发对应的下一步函数
    if (active.value === 0) {
      // 第一步：验证用户名
      next()
    } else if (active.value === 1) {
      // 第二步：验证密保答案
      next()
    } else if (active.value === 2) {
      // 第三步：重置密码
      submit()
    }
  }
}

// 组件挂载时添加键盘事件监听
onMounted(() => {
  document.addEventListener('keydown', handleKeyPress)
  // 首次打开时聚焦到当前输入框
  focusCurrentInput()
})

// 组件卸载时移除键盘事件监听
onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyPress)
})

// 焦点管理
const focusCurrentInput = async () => {
  await nextTick()
  
  setTimeout(() => {
    if (active.value === 0 && usernameInputRef.value) {
      usernameInputRef.value.focus()
    } else if (active.value === 1 && answerInputRef.value) {
      answerInputRef.value.focus()
    } else if (active.value === 2 && passwordInputRef.value) {
      passwordInputRef.value.focus()
    }
  }, 150) // 使用150ms延迟确保DOM完全渲染
}

// 监听步骤变化，自动聚焦到对应输入框
watch(active, () => {
  focusCurrentInput()
})

// 监听弹窗显示状态，当弹窗显示时聚焦
watch(() => props.visible, (newValue) => {
  if (newValue) {
    focusCurrentInput()
  }
})
</script>

<template>
  <FullScreenLoading :visible="isLoading" />
  <el-container style="width: 100%">
    <el-header style="height: 130px;">
      <div style="height: 100%;" v-if="active === 0">
        <el-text class="mx-1" size="large">请输入用户名</el-text>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="0px"
          style="margin-top: 50px; padding: 0 20px;">
          <el-form-item prop="username" :class="[`is-${fieldStates.username.validateState}`]">
            <el-input ref="usernameInputRef" v-model="form.username" :prefix-icon="User" placeholder="请输入用户名"
              @input="clearFieldState('username')" />
            <div v-if="fieldStates.username.validateMessage" class="el-form-item__error">
              {{ fieldStates.username.validateMessage }}
            </div>
          </el-form-item>
        </el-form>
      </div>

      <div style="height: 100%;" v-else-if="active === 1">
        <el-text class="mx-1" size="large">密保问题：{{ protectQuestion }}</el-text>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="0px"
          style="margin-top: 50px; padding: 0 20px;">
          <el-form-item prop="answer" :class="[`is-${fieldStates.answer.validateState}`]">
            <el-input ref="answerInputRef" v-model="form.answer" :prefix-icon="Notebook" placeholder="请输入密保答案"
              @input="clearFieldState('answer')" />
            <div v-if="fieldStates.answer.validateMessage" class="el-form-item__error">
              {{ fieldStates.answer.validateMessage }}
            </div>
          </el-form-item>
        </el-form>
      </div>

      <div style="height: 100%;" v-else-if="active === 2">
        <el-text class="mx-1" size="large">请设置新密码</el-text>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="0px"
          style="margin-top: 20px; padding: 0 20px;">
          <el-form-item prop="password" :class="[`is-${fieldStates.password.validateState}`]">
            <el-input ref="passwordInputRef" v-model="form.password" type="password" show-password :prefix-icon="Lock" placeholder="请输入新密码"
              @input="clearFieldState('password')" />
            <div v-if="fieldStates.password.validateMessage" class="el-form-item__error">
              {{ fieldStates.password.validateMessage }}
            </div>
          </el-form-item>

          <el-form-item prop="confirm" :class="[`is-${fieldStates.confirm.validateState}`]">
            <el-input ref="confirmInputRef" v-model="form.confirm" type="password" show-password :prefix-icon="Lock" placeholder="请再次输入新密码"
              @input="clearFieldState('confirm')" />
            <div v-if="fieldStates.confirm.validateMessage" class="el-form-item__error">
              {{ fieldStates.confirm.validateMessage }}
            </div>
          </el-form-item>
        </el-form>
      </div>
    </el-header>

    <el-main class="button-container">
      <el-button @click="pre" :disabled="active === 0">上一步</el-button>
      <el-button @click="next" v-if="active < 2">下一步</el-button>
      <el-button @click="submit" v-else>提交</el-button>
    </el-main>

    <el-footer>
      <el-steps style="width: 100%" :active="active" finish-status="success" align-center>
        <el-step title="验证用户" />
        <el-step title="验证密保" />
        <el-step title="重置密码" />
      </el-steps>
    </el-footer>
    
    <!-- 验证码弹窗 -->
    <CaptchaDialog 
      v-model="showCaptchaDialog"
      :has-error="captchaError"
      @success="onCaptchaSuccess"
      @cancel="onCaptchaCancel"
    />
  </el-container>
</template>

<style scoped>
.button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}

/* 校验通过样式 */
.el-form-item.is-success :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #13CE66 inset;
}

/* 校验失败样式 */
.el-form-item.is-error :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px var(--el-color-danger) inset;
}

/* 成功状态图标颜色 */
.el-form-item.is-success :deep(.el-input__icon) {
  color: #13CE66 !important;
}

/* 失败状态图标颜色 */
.el-form-item.is-error :deep(.el-input__icon) {
  color: var(--el-color-danger) !important;
}

.el-form-item__error {
  color: var(--el-color-danger);
  font-size: 12px;
  line-height: 1.5;
  padding-top: 2px;
  text-align: left;
}
</style>