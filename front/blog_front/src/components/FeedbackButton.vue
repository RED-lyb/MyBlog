<script setup>
import { ref, inject } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '../stores/user_info.js'
import { storeToRefs } from 'pinia'
import apiClient from '../lib/api.js'

const authStore = useAuthStore()
const { isAuthenticated, userId } = storeToRefs(authStore)
const apiUrl = import.meta.env.VITE_API_URL

// 注入父组件的刷新函数（如果存在）
const refreshFeedbackList = inject('refreshFeedbackList', null)

const dialogVisible = ref(false)
const submitting = ref(false)
const formData = ref({
  issue_type: '',
  description: ''
})

const formRules = {
  issue_type: [
    { required: true, message: '请选择问题类型', trigger: 'change' }
  ],
  description: [
    { required: true, message: '请输入问题描述', trigger: 'blur' }
  ]
}

const handleClick = () => {
  if (!isAuthenticated.value) {
    ElMessage.warning('请先登录')
    return
  }
  dialogVisible.value = true
  // 重置表单
  formData.value = {
    issue_type: '',
    description: ''
  }
}

const handleSubmit = async () => {
  if (!formData.value.issue_type || !formData.value.description.trim()) {
    ElMessage.warning('请填写完整信息')
    return
  }

  submitting.value = true
  try {
    const response = await apiClient.post(
      `${apiUrl}feedback/create/`,
      {
        issue_type: formData.value.issue_type,
        description: formData.value.description
      }
    )
    
    if (response.data.success) {
      ElMessage.success('反馈提交成功，感谢您的反馈！')
      dialogVisible.value = false
      formData.value = {
        issue_type: '',
        description: ''
      }
      // 如果父组件提供了刷新函数，调用它
      if (refreshFeedbackList) {
        refreshFeedbackList()
      }
    } else {
      ElMessage.error(response.data.error || '提交失败')
    }
  } catch (error) {
    console.error('提交反馈错误:', error)
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="feedback-button-container">
    <button class="dsi-btn dsi-btn-outline dsi-btn-warning" @click="handleClick">反馈</button>
    
    <!-- 反馈对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="意见反馈"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="问题类型" prop="issue_type">
          <el-select
            v-model="formData.issue_type"
            placeholder="请选择问题类型"
            style="width: 100%"
          >
            <el-option label="使用错误" value="使用错误" />
            <el-option label="功能建议" value="功能建议" />
          </el-select>
        </el-form-item>
        <el-form-item label="问题描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="8"
            placeholder="请详细描述您遇到的问题或建议"
            maxlength="1000"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button plain @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" plain @click="handleSubmit" :loading="submitting">
          提交
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.feedback-button-container {
  display: flex;
  justify-content: center;
  align-items: end;
  padding: 20px;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 101;
}
</style>

