<script setup>
import { ref, computed, onMounted, watch, nextTick, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { useUserInfo } from '../lib/authState.js'
import apiClient from '../lib/api.js'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { UploadFilled, EditPen, Notebook, Lock } from '@element-plus/icons-vue'
import CaptchaDialog from './CaptchaDialog.vue'
import { showGuestDialog } from '../lib/guestDialog.js'
import FullScreenLoading from '../pages/FullScreenLoading.vue'

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
  userId,
  bgColor,
  bgPattern
} = storeToRefs(authStore)
const { fetchUserInfo } = useUserInfo()

// 编辑资料相关
const formData = ref({
  bg_color: '',
  bg_pattern: '',
  bio: ''
})
const saving = ref(false)
const showLoading = ref(false)

// 上传头像相关
const avatarDialogVisible = ref(false)
const avatarFileList = ref([])
const uploadingAvatar = ref(false)

// 重设密码相关
const passwordFormRef = ref(null)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const resettingPassword = ref(false)
const showPasswordCaptchaDialog = ref(false)
const passwordCaptchaError = ref(false)
const passwordCaptchaData = ref(null)

// 密码验证规则（与注册时一致）
const validatePass = (rule, value, callback) => {
  if (!value) return callback(new Error('请输入密码'))
  if (value.length < 8) return callback(new Error('密码至少 8 位'))
  if (!/[0-9]/.test(value)) return callback(new Error('需包含数字'))
  if (!/[A-Z]/.test(value)) return callback(new Error('需包含大写字母'))
  if (!/[a-z]/.test(value)) return callback(new Error('需包含小写字母'))
  callback()
}

const validatePass2 = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== passwordForm.value.new_password) {
    callback(new Error('两次输入密码不一致!'))
  } else {
    callback()
  }
}

const passwordRules = {
  old_password: [
    { required: true, message: '请输入旧密码', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { validator: validatePass, trigger: ['blur', 'change'] }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validatePass2, trigger: ['blur', 'change'] }
  ]
}

// 重设密保相关
const securityFormRef = ref(null)
const securityForm = ref({
  old_answer: '',
  new_protect: '',
  new_answer: ''
})
const resettingSecurity = ref(false)
const currentProtectQuestion = ref('') // 当前用户的密保问题
const showSecurityCaptchaDialog = ref(false)
const securityCaptchaError = ref(false)
const securityCaptchaData = ref(null)

// 防止重复权限检查的标志
const permissionChecked = ref(false)

// 密保问题列表（与注册面板一致）
const securityQuestions = ref([
  { value: '你的人生目标', label: '你的人生目标' },
  { value: '你最向往的地方', label: '你最向往的地方' },
  { value: '你最喜欢的食物', label: '你最喜欢的食物' },
  { value: '你最喜欢的老师', label: '你最喜欢的老师' },
  { value: '你童年最好的朋友', label: '你童年最好的朋友' }
])

// 自定义密保问题相关
const isAddingSecurityQuestion = ref(false)
const securityOptionName = ref('')
const securityOptionFormRef = ref(null)

// 密保答案验证规则
const validateAnswer = (_, value, callback) => {
  if (!value) return callback(new Error('请输入密保答案'))
  if (!/^[\u4e00-\u9fa5A-Za-z0-9]+$/.test(value)) {
    return callback(new Error('答案只能包含中文、英文和数字'))
  }
  callback()
}

// 密保问题验证规则
const validateQuestion = (_, value, callback) => {
  if (!value) return callback(new Error('请输入问题'))
  if (!/^[\u4e00-\u9fa5A-Za-z0-9]+$/.test(value)) {
    return callback(new Error('问题只能包含中文、英文和数字'))
  }
  callback()
}

const securityOptionRules = reactive({
  optionName: [
    { required: true, message: '请输入问题', trigger: 'blur' },
    { validator: validateQuestion, trigger: ['blur', 'change'] }
  ]
})

// 添加自定义密保问题
const onAddSecurityOption = () => {
  isAddingSecurityQuestion.value = true
}

const onConfirmSecurityOption = async () => {
  const valid = await securityOptionFormRef.value.validate().catch(() => false)
  if (!valid) return

  // 校验通过后写入列表并设置为选中
  securityQuestions.value.push({
    label: securityOptionName.value,
    value: securityOptionName.value
  })
  securityForm.value.new_protect = securityOptionName.value
  clearSecurityOption()
}

const clearSecurityOption = () => {
  securityOptionName.value = ''
  isAddingSecurityQuestion.value = false
}

// 获取目标用户信息
const fetchTargetUser = async (userId) => {
  if (!userId) {
    userError.value = '用户ID不存在'
    return
  }

  userLoading.value = true
  userError.value = null
  targetUser.value = null

  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/${userId}/`)
    if (response.data?.success) {
      targetUser.value = response.data.data.user
      loadProfile()
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

// 加载用户资料
const loadProfile = () => {
  if (targetUser.value) {
    formData.value = {
      bg_color: targetUser.value.bg_color || '',
      bg_pattern: targetUser.value.bg_pattern || '',
      bio: targetUser.value.bio || ''
    }
    // 加载密保问题
    currentProtectQuestion.value = targetUser.value.protect || ''
  } else if (isAuthenticated.value && user.value) {
    formData.value = {
      bg_color: bgColor.value || '',
      bg_pattern: bgPattern.value || '',
      bio: user.value.bio || ''
    }
    // 从用户信息中获取密保问题
    fetchCurrentUserProtect()
  }
}

// 获取当前用户的密保问题
const fetchCurrentUserProtect = async () => {
  try {
    const response = await apiClient.get(`${import.meta.env.VITE_API_URL}user/info/`)
    if (response.data?.success && response.data?.data?.user?.protect) {
      currentProtectQuestion.value = response.data.data.user.protect
    }
  } catch (error) {
    console.error('获取密保问题失败:', error)
  }
}

// 保存资料
const saveProfile = async () => {
  saving.value = true
  showLoading.value = true
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/profile/`, formData.value)
    if (response.data?.success) {
      ElMessage.success('资料保存成功，页面即将刷新')
      // 刷新用户信息
      await fetchUserInfo()
      if (targetUserId.value) {
        await fetchTargetUser(targetUserId.value)
      }
      // 延迟一下再刷新，让用户看到成功消息
      setTimeout(() => {
        window.location.reload()
      }, 500)
    } else {
      ElMessage.error(response.data?.error || '保存失败')
      showLoading.value = false
    }
  } catch (error) {
    console.error('保存资料失败:', error)
    ElMessage.error(error.response?.data?.error || '保存失败')
    showLoading.value = false
  } finally {
    saving.value = false
  }
}

// 恢复默认样式
const resetStyle = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要恢复默认样式吗？这将清空背景颜色和点缀颜色。',
      '确认恢复默认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    saving.value = true
    showLoading.value = true
    
    try {
      const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/profile/`, {
        bg_color: '',
        bg_pattern: '',
        bio: formData.value.bio // 保留个人介绍不变
      })
      
      if (response.data?.success) {
        ElMessage.success('样式已恢复默认，页面即将刷新')
        // 更新本地表单数据
        formData.value.bg_color = ''
        formData.value.bg_pattern = ''
        // 刷新用户信息
        await fetchUserInfo()
        if (targetUserId.value) {
          await fetchTargetUser(targetUserId.value)
        }
        // 延迟一下再刷新，让用户看到成功消息
        setTimeout(() => {
          window.location.reload()
        }, 500)
      } else {
        ElMessage.error(response.data?.error || '恢复失败')
        showLoading.value = false
      }
    } catch (error) {
      console.error('恢复默认样式失败:', error)
      ElMessage.error(error.response?.data?.error || '恢复失败')
      showLoading.value = false
    } finally {
      saving.value = false
    }
  } catch {
    // 用户取消操作
  }
}

// 打开头像上传弹窗
const openAvatarDialog = () => {
  avatarDialogVisible.value = true
  avatarFileList.value = []
}

// 上传头像
const handleAvatarUpload = async () => {
  if (avatarFileList.value.length === 0) {
    ElMessage.warning('请选择要上传的头像')
    return
  }

  uploadingAvatar.value = true
  try {
    const formData = new FormData()
    formData.append('file', avatarFileList.value[0].raw)
    
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/avatar/upload/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    if (response.data?.success) {
      ElMessage.success('头像上传成功，页面即将刷新')
      avatarDialogVisible.value = false
      avatarFileList.value = []
      // 延迟一下再刷新，让用户看到成功消息
      setTimeout(() => {
        window.location.reload()
      }, 500)
    } else {
      ElMessage.error(response.data?.error || '上传失败')
    }
  } catch (error) {
    console.error('上传头像失败:', error)
    ElMessage.error(error.response?.data?.error || '上传失败')
  } finally {
    uploadingAvatar.value = false
  }
}

// 重设密码 - 打开验证码弹窗
const handleResetPassword = async () => {
  if (!passwordFormRef.value) return
  
  try {
    const valid = await passwordFormRef.value.validate()
    if (!valid) return
  } catch {
    return
  }

  // 直接打开验证码弹窗
  passwordCaptchaError.value = false
  showPasswordCaptchaDialog.value = true
}

// 验证码验证成功后的密码重置
const handleResetPasswordWithCaptcha = async (captchaInfo) => {
  resettingPassword.value = true
  showLoading.value = true
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/password/reset/`, {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
      captcha_key: captchaInfo.captcha_key,
      captcha_value: captchaInfo.captcha_value
    })
    
    if (response.data?.success) {
      ElMessage.success('密码修改成功，页面即将刷新')
      // 延迟一下再刷新，让用户看到成功消息
      setTimeout(() => {
        window.location.reload()
      }, 500)
    } else {
      ElMessage.error(response.data?.error || '修改失败')
      showLoading.value = false
      // 如果是验证码错误，重新弹出验证码对话框
      if (response.data?.error && response.data.error.includes('验证码')) {
        passwordCaptchaError.value = true
        showPasswordCaptchaDialog.value = true
      }
      // 处理字段错误
      if (response.data?.field_errors && passwordFormRef.value) {
        nextTick(() => {
          Object.keys(response.data.field_errors).forEach(field => {
            const fieldInstance = passwordFormRef.value.fields?.find(f => f.prop === field)
            if (fieldInstance) {
              fieldInstance.validateState = 'error'
              fieldInstance.validateMessage = response.data.field_errors[field]
            }
          })
        })
      }
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    let errorMessage = '修改失败'
    showLoading.value = false
    
    if (error.response) {
      if (error.response.status === 404) {
        errorMessage = 'API接口不存在，请检查后端路由配置'
      } else if (error.response.data?.error) {
        errorMessage = error.response.data.error
        // 如果是验证码错误，重新弹出验证码对话框
        if (error.response.data.error.includes('验证码')) {
          passwordCaptchaError.value = true
          showPasswordCaptchaDialog.value = true
        }
        // 处理字段错误
        if (error.response.data?.field_errors && passwordFormRef.value) {
          nextTick(() => {
            Object.keys(error.response.data.field_errors).forEach(field => {
              const fieldInstance = passwordFormRef.value.fields?.find(f => f.prop === field)
              if (fieldInstance) {
                fieldInstance.validateState = 'error'
                fieldInstance.validateMessage = error.response.data.field_errors[field]
              }
            })
          })
        }
      } else if (error.response.status === 400) {
        errorMessage = '请求参数错误'
      } else if (error.response.status === 401) {
        errorMessage = '请先登录'
      } else if (error.response.status >= 500) {
        errorMessage = '服务器错误，请稍后重试'
      }
    } else if (error.request) {
      errorMessage = '网络错误，请检查网络连接'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    resettingPassword.value = false
  }
}

// 密码验证码成功
const onPasswordCaptchaSuccess = (captchaInfo) => {
  passwordCaptchaData.value = captchaInfo
  showPasswordCaptchaDialog.value = false
  passwordCaptchaError.value = false
  handleResetPasswordWithCaptcha(captchaInfo)
}

// 密码验证码取消
const onPasswordCaptchaCancel = () => {
  showPasswordCaptchaDialog.value = false
  passwordCaptchaError.value = false
}

// 重设密保 - 打开验证码弹窗
const handleResetSecurityQuestion = async () => {
  if (!securityForm.value.old_answer || !securityForm.value.new_protect || !securityForm.value.new_answer) {
    ElMessage.warning('请填写所有字段')
    return
  }
  
  // 验证新密保问题格式（允许自定义问题）
  if (!/^[\u4e00-\u9fa5A-Za-z0-9]+$/.test(securityForm.value.new_protect)) {
    ElMessage.error('密保问题只能包含中文、英文和数字')
    return
  }
  
  // 验证新密保答案格式
  if (!/^[\u4e00-\u9fa5A-Za-z0-9]+$/.test(securityForm.value.new_answer)) {
    ElMessage.error('新密保答案只能包含中文、英文和数字')
    return
  }
  
  // 直接打开验证码弹窗
  securityCaptchaError.value = false
  showSecurityCaptchaDialog.value = true
}

// 验证码验证成功后的密保重置
const handleResetSecurityQuestionWithCaptcha = async (captchaInfo) => {
  resettingSecurity.value = true
  showLoading.value = true
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/security-question/reset/`, {
      old_answer: securityForm.value.old_answer,
      new_protect: securityForm.value.new_protect,
      new_answer: securityForm.value.new_answer,
      captcha_key: captchaInfo.captcha_key,
      captcha_value: captchaInfo.captcha_value
    })
    
    if (response.data?.success) {
      ElMessage.success('密保修改成功，页面即将刷新')
      // 延迟一下再刷新，让用户看到成功消息
      setTimeout(() => {
        window.location.reload()
      }, 500)
    } else {
      ElMessage.error(response.data?.error || '修改失败')
      showLoading.value = false
      // 如果是验证码错误，重新弹出验证码对话框
      if (response.data?.error && response.data.error.includes('验证码')) {
        securityCaptchaError.value = true
        showSecurityCaptchaDialog.value = true
      }
      if (response.data?.field_errors) {
        nextTick(() => {
          Object.keys(response.data.field_errors).forEach(field => {
            const fieldInstance = securityFormRef.value?.fields?.find(f => f.prop === field)
            if (fieldInstance) {
              fieldInstance.validateState = 'error'
              fieldInstance.validateMessage = response.data.field_errors[field]
            }
          })
        })
      }
    }
  } catch (error) {
    console.error('修改密保失败:', error)
    let errorMessage = '修改失败'
    showLoading.value = false
    
    if (error.response) {
      if (error.response.status === 404) {
        errorMessage = 'API接口不存在，请检查后端路由配置'
      } else if (error.response.data?.error) {
        errorMessage = error.response.data.error
        // 如果是验证码错误，重新弹出验证码对话框
        if (error.response.data.error.includes('验证码')) {
          securityCaptchaError.value = true
          showSecurityCaptchaDialog.value = true
        }
      } else if (error.response.status === 400) {
        errorMessage = '请求参数错误'
      } else if (error.response.status === 401) {
        errorMessage = '请先登录'
      } else if (error.response.status === 403) {
        errorMessage = '权限不足'
      } else if (error.response.status >= 500) {
        errorMessage = '服务器错误，请稍后重试'
      }
      
      if (error.response.data?.field_errors) {
        nextTick(() => {
          Object.keys(error.response.data.field_errors).forEach(field => {
            const fieldInstance = securityFormRef.value?.fields?.find(f => f.prop === field)
            if (fieldInstance) {
              fieldInstance.validateState = 'error'
              fieldInstance.validateMessage = error.response.data.field_errors[field]
            }
          })
        })
      }
    } else if (error.request) {
      errorMessage = '网络错误，请检查网络连接'
    }
    
    ElMessage.error(errorMessage)
  } finally {
    resettingSecurity.value = false
  }
}

// 密保验证码成功
const onSecurityCaptchaSuccess = (captchaInfo) => {
  securityCaptchaData.value = captchaInfo
  showSecurityCaptchaDialog.value = false
  securityCaptchaError.value = false
  handleResetSecurityQuestionWithCaptcha(captchaInfo)
}

// 密保验证码取消
const onSecurityCaptchaCancel = () => {
  showSecurityCaptchaDialog.value = false
  securityCaptchaError.value = false
}

// 监听路由参数变化（只处理数据加载，不进行权限检查，避免重复）
watch(() => route.params.userId, async (newUserId) => {
  if (newUserId) {
    const routeUserId = parseInt(newUserId)
    targetUserId.value = routeUserId
    await fetchTargetUser(targetUserId.value)
  } else {
    targetUser.value = null
    userError.value = null
  }
  
  // 触发浏览器重新计算页面高度
  triggerResize()
}, { immediate: false }) // 改为 false，避免与 onMounted 重复

// 监听路由路径变化（只触发 resize，不进行权限检查）
watch(() => route.path, async (newPath) => {
  if (newPath.includes('/edit')) {
    // 触发浏览器重新计算页面高度
    triggerResize()
  }
})

// 触发浏览器重新计算页面高度（修复滚动条问题）
const triggerResize = () => {
  nextTick(() => {
    // 触发窗口resize事件，让浏览器重新计算页面高度
    window.dispatchEvent(new Event('resize'))
    // 也可以直接设置body的overflow样式
    document.body.style.overflow = 'auto'
  })
}

onMounted(async () => {
  // 防止重复权限检查
  if (permissionChecked.value) {
    return
  }
  permissionChecked.value = true
  
  // 权限检查：编辑页面只能访问自己的（只在这里检查一次，避免重复）
  const routeUserId = route.params.userId ? parseInt(route.params.userId) : null
  
  // 检查是否为游客
  if (!isAuthenticated.value) {
    // 游客不能访问任何用户的编辑页面（只显示弹窗，不显示错误消息）
    showGuestDialog(router, '/home')
    return
  }
  
  // 检查登录用户是否尝试访问其他用户的编辑页面（只跳转，不显示错误消息，避免重复）
  if (routeUserId && routeUserId !== userId.value) {
    router.push(`/user_home/${userId.value}`)
    return
  }
  
  // 正常访问自己的编辑页面
  if (routeUserId) {
    targetUserId.value = routeUserId
    await fetchTargetUser(targetUserId.value)
  } else if (isAuthenticated.value && userId.value) {
    targetUserId.value = userId.value
    loadProfile()
    // 如果loadProfile中没有获取到密保问题，单独获取
    if (!currentProtectQuestion.value) {
      await fetchCurrentUserProtect()
    }
  }
  
  // 触发浏览器重新计算页面高度
  triggerResize()
})
</script>

<template>
  <FullScreenLoading :visible="showLoading" />
  <div class="edit-profile-container">
    <div v-if="userLoading" class="user-loading">加载中...</div>
    <div v-else-if="userError" class="user-error">{{ userError }}</div>
    <div v-else class="edit-profile-content">
      
      <!-- 上传头像 -->
      <div class="form-section">
        <div class="section-header">
          <h3 class="form-section-title">头像设置</h3>
          <el-button type="primary" plain @click="openAvatarDialog">上传头像</el-button>
        </div>
        <div class="el-upload__tip">
          支持 jpg、jpeg、png、gif、bmp、webp 格式，文件大小不超过5MB
        </div>
      </div>

      <!-- 头像上传弹窗 -->
      <el-dialog
        v-model="avatarDialogVisible"
        title="上传头像"
        width="500px"
      >
        <el-upload
          v-model:file-list="avatarFileList"
          :auto-upload="false"
          :limit="1"
          accept="image/*"
          :on-exceed="() => ElMessage.warning('只能上传一个头像')"
          drag
        >
          <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
          <div class="el-upload__text">
            将头像拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              支持 jpg、jpeg、png、gif、bmp、webp 格式，文件大小不超过5MB
            </div>
          </template>
        </el-upload>
        <template #footer>
          <span class="dialog-footer">
            <el-button plain @click="avatarDialogVisible = false">取消</el-button>
            <el-button 
              type="primary" 
              plain
              :loading="uploadingAvatar"
              @click="handleAvatarUpload"
            >
              上传
            </el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 个人介绍 -->
      <div class="form-section">
        <div class="section-header">
          <h3 class="form-section-title">个人介绍</h3>
          <el-button 
            type="primary" 
            plain
            :loading="saving"
            @click="saveProfile"
          >
            保存介绍
          </el-button>
        </div>
        <el-form :model="formData" label-width="120px">
          <el-form-item label="个人介绍">
            <el-input
              v-model="formData.bio"
              type="textarea"
              :rows="6"
              placeholder="请输入个人介绍"
              maxlength="1000"
              show-word-limit
            />
            <div class="form-tip">个人介绍将显示在个人主页</div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 样式设置 -->
      <div class="form-section">
        <div class="section-header">
          <h3 class="form-section-title">样式设置</h3>
          <div class="section-actions">
            <el-button 
              type="default" 
              plain
              :loading="saving"
              @click="resetStyle"
            >
              恢复默认
            </el-button>
            <el-button 
              type="primary" 
              plain
              :loading="saving"
              @click="saveProfile"
            >
              保存样式
            </el-button>
          </div>
        </div>
        <el-form :model="formData" label-width="120px">
          <el-form-item label="背景颜色">
            <el-color-picker
              v-model="formData.bg_color"
              color-format="hex"
              size="small"
            />
            <div class="form-tip">个人中心背景颜色</div>
          </el-form-item>
          <el-form-item label="点缀颜色">
            <el-color-picker
              v-model="formData.bg_pattern"
              color-format="hex"
              size="small"
            />
            <div class="form-tip">背景粒子点缀颜色</div>
          </el-form-item>
        </el-form>
      </div>

      <!-- 重设密码 -->
      <div class="form-section">
        <div class="section-header">
          <h3 class="form-section-title">修改密码</h3>
          <el-button 
            type="primary" 
            plain
            :loading="resettingPassword"
            @click="handleResetPassword"
          >
            修改密码
          </el-button>
        </div>
        <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="120px" hide-required-asterisk status-icon>
          <el-form-item label="旧密码" prop="old_password">
            <el-input 
              v-model="passwordForm.old_password" 
              type="password"
              show-password
              placeholder="请输入旧密码"
              :prefix-icon="Lock"
            />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input 
              v-model="passwordForm.new_password" 
              type="password"
              show-password
              placeholder="请输入新密码"
              :prefix-icon="Lock"
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm_password">
            <el-input 
              v-model="passwordForm.confirm_password" 
              type="password"
              show-password
              placeholder="请再次输入新密码"
              :prefix-icon="Lock"
            />
          </el-form-item>
        </el-form>
      </div>

      <!-- 重设密保 -->
      <div class="form-section">
        <div class="section-header">
          <h3 class="form-section-title">修改密保</h3>
          <el-button 
            type="primary" 
            plain
            :loading="resettingSecurity"
            @click="handleResetSecurityQuestion"
          >
            修改密保
          </el-button>
        </div>
        <el-form :model="securityForm" label-width="120px" hide-required-asterisk>
          <el-form-item label="原密保问题">
            <el-input 
              :value="currentProtectQuestion" 
              disabled
              placeholder="当前密保问题"
            />
          </el-form-item>
          <el-form-item label="原密保答案">
            <el-input 
              v-model="securityForm.old_answer" 
              placeholder="请输入原密保答案"
              :prefix-icon="Notebook"
            />
          </el-form-item>
          <el-form-item label="新密保问题">
            <el-icon :size="14"
              style="position: absolute;left: 11px;top: 50%;transform: translateY(-50%);z-index: 10;color: #9A9DA3;">
              <EditPen />
            </el-icon>
            <el-select v-model="securityForm.new_protect" placeholder="密保问题只能自己知道答案" style="width: 100%">
              <template #prefix>
                <span style="display:inline-block;width:15px;"></span>
              </template>
              <el-option
                v-for="item in securityQuestions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
              <template #footer>
                <el-button v-if="!isAddingSecurityQuestion" text bg size="small" plain @click="onAddSecurityOption">
                  输入自定义问题
                </el-button>
                <template v-else>
                  <el-form :model="{ optionName: securityOptionName }" :rules="securityOptionRules" ref="securityOptionFormRef"
                    style="width: 100%;">
                    <el-form-item prop="optionName" class="compact-error">
                      <el-input v-model="securityOptionName" class="option-input"
                        placeholder="请输入自定义问题" size="small" />
                    </el-form-item>
                  </el-form>
                  <el-button type="primary" size="small" plain @click="onConfirmSecurityOption">
                    确认
                  </el-button>
                  <el-button size="small" plain @click="clearSecurityOption">取消</el-button>
                </template>
              </template>
            </el-select>
          </el-form-item>
          <el-form-item label="新密保答案">
            <el-input 
              v-model="securityForm.new_answer" 
              placeholder="请输入新密保答案"
              :prefix-icon="Notebook"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 密码验证码弹窗 -->
      <CaptchaDialog 
        v-model="showPasswordCaptchaDialog"
        :has-error="passwordCaptchaError"
        @success="onPasswordCaptchaSuccess"
        @cancel="onPasswordCaptchaCancel"
      />
      
      <!-- 密保验证码弹窗 -->
      <CaptchaDialog 
        v-model="showSecurityCaptchaDialog"
        :has-error="securityCaptchaError"
        @success="onSecurityCaptchaSuccess"
        @cancel="onSecurityCaptchaCancel"
      />
    </div>
  </div>
</template>

<style scoped>
.edit-profile-container {
  padding: 20px;
}

.user-loading,
.user-error {
  text-align: center;
  padding: 40px;
}

.user-error {
  color: #f56c6c;
}


.form-section {
  margin-bottom: 40px;
  padding: 20px;
  background-color: rgba(245, 245, 245, 0.1);;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-light);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--el-border-color-light);
}

.section-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.form-section-title {
  font-size: 18px;
  margin: 0;
  color: var(--el-text-color-primary);
}

.el-upload__tip {
  margin-top: 10px;
  color: var(--el-text-color-regular);
  font-size: 12px;
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}

/* 校验通过：边框变 #13CE66 */
.el-form-item.is-success :deep(.el-input__wrapper),
.el-form-item.is-success :deep(.el-select__wrapper) {
  box-shadow: 0 0 0 1px #13CE66 inset;
}

/* 校验失败：保持官方红色 */
.el-form-item.is-error :deep(.el-input__wrapper),
.el-form-item.is-error :deep(.el-select__wrapper) {
  box-shadow: 0 0 0 1px var(--el-color-danger) inset;
}

/* 成功 */
.el-form-item.is-success :deep(.el-input__icon),
.el-form-item.is-success :deep(.el-select__caret) {
  color: #13CE66 !important;
}

/* 失败 */
.el-form-item.is-error :deep(.el-input__icon),
.el-form-item.is-error :deep(.el-select__caret) {
  color: var(--el-color-danger) !important;
}

/* 密保答案/用户名等带图标的输入框，图标颜色也跟着变绿 */
.el-form-item.is-success :deep(.el-input__icon) {
  color: #13CE66;
}

.el-form-item.is-success .el-icon {
  color: #13CE66 !important;
}

.el-form-item.is-error .el-icon {
  color: var(--el-color-danger) !important;
}

.el-form-item.is-success :deep(.el-select__caret) {
  color: #13CE66 !important;
}

/* 校验失败：下拉箭头变红 */
.el-form-item.is-error :deep(.el-select__caret) {
  color: var(--el-color-danger) !important;
}

.compact-error .el-form-item__error {
  line-height: 1;
}

.option-input {
  margin-bottom: 0px;
  width: 100%;
}
</style>

