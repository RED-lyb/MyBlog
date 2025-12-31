<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '../stores/user_info.js'
import { useUserInfo } from '../lib/authState.js'
import apiClient from '../lib/api.js'
import { ElMessage, ElMessageBox, ElDialog } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'

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
  bg_pattern: ''
})
const saving = ref(false)

// 上传头像相关
const avatarDialogVisible = ref(false)
const avatarFileList = ref([])
const uploadingAvatar = ref(false)

// 重设密码相关
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const resettingPassword = ref(false)

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
      bg_pattern: targetUser.value.bg_pattern || ''
    }
  } else if (isAuthenticated.value && user.value) {
    formData.value = {
      bg_color: bgColor.value || '',
      bg_pattern: bgPattern.value || ''
    }
  }
}

// 保存资料
const saveProfile = async () => {
  saving.value = true
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/profile/`, formData.value)
    if (response.data?.success) {
      ElMessage.success('资料保存成功')
      // 刷新用户信息
      await fetchUserInfo()
      if (targetUserId.value) {
        await fetchTargetUser(targetUserId.value)
      }
    } else {
      ElMessage.error(response.data?.error || '保存失败')
    }
  } catch (error) {
    console.error('保存资料失败:', error)
    ElMessage.error(error.response?.data?.error || '保存失败')
  } finally {
    saving.value = false
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

// 重设密码
const handleResetPassword = async () => {
  if (!passwordForm.value.old_password || !passwordForm.value.new_password || !passwordForm.value.confirm_password) {
    ElMessage.warning('请填写所有密码字段')
    return
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  try {
    await ElMessageBox.confirm('确定要修改密码吗？', '确认修改', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  resettingPassword.value = true
  try {
    const response = await apiClient.post(`${import.meta.env.VITE_API_URL}user/password/reset/`, {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password
    })
    
    if (response.data?.success) {
      ElMessage.success('密码修改成功')
      passwordForm.value = {
        old_password: '',
        new_password: '',
        confirm_password: ''
      }
    } else {
      ElMessage.error(response.data?.error || '修改失败')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    ElMessage.error(error.response?.data?.error || '修改失败')
  } finally {
    resettingPassword.value = false
  }
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

onMounted(async () => {
  if (route.params.userId) {
    targetUserId.value = parseInt(route.params.userId)
    await fetchTargetUser(targetUserId.value)
  } else if (isAuthenticated.value && userId.value) {
    targetUserId.value = userId.value
    loadProfile()
  }
})
</script>

<template>
  <div class="edit-profile-container">
    <div v-if="userLoading" class="user-loading">加载中...</div>
    <div v-else-if="userError" class="user-error">{{ userError }}</div>
    <div v-else class="edit-profile-content">
      <h2 class="section-title">编辑资料</h2>
      
      <!-- 上传头像 -->
      <div class="form-section">
        <div class="section-header">
          <h3 class="form-section-title">头像设置</h3>
          <el-button type="primary" @click="openAvatarDialog">上传头像</el-button>
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
            <el-button @click="avatarDialogVisible = false">取消</el-button>
            <el-button 
              type="primary" 
              :loading="uploadingAvatar"
              @click="handleAvatarUpload"
            >
              上传
            </el-button>
          </span>
        </template>
      </el-dialog>

      <!-- 样式设置 -->
      <div class="form-section">
        <div class="section-header">
          <h3 class="form-section-title">样式设置</h3>
          <el-button 
            type="primary" 
            :loading="saving"
            @click="saveProfile"
          >
            保存资料
          </el-button>
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
          <h3 class="form-section-title">重设密码</h3>
          <el-button 
            type="warning" 
            :loading="resettingPassword"
            @click="handleResetPassword"
          >
            修改密码
          </el-button>
        </div>
        <el-form :model="passwordForm" label-width="120px">
          <el-form-item label="旧密码">
            <el-input 
              v-model="passwordForm.old_password" 
              type="password"
              show-password
              placeholder="请输入旧密码"
            />
          </el-form-item>
          <el-form-item label="新密码">
            <el-input 
              v-model="passwordForm.new_password" 
              type="password"
              show-password
              placeholder="请输入新密码"
            />
          </el-form-item>
          <el-form-item label="确认密码">
            <el-input 
              v-model="passwordForm.confirm_password" 
              type="password"
              show-password
              placeholder="请再次输入新密码"
            />
          </el-form-item>
        </el-form>
      </div>
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid var(--el-border-color-light);
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
</style>

