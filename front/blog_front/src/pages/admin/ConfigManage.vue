<template>
  <div class="config-manage-container">
    <div class="page-header">
      <h1 class="page-title">全局配置</h1>
      <el-button type="primary" @click="handleSave" :loading="saving">
        <el-icon><Check /></el-icon>
        保存配置
      </el-button>
    </div>
    
    <el-card>
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
        label-position="left"
      >
        <el-form-item label="作者ID" prop="author_id">
          <el-input-number
            v-model="formData.author_id"
            :min="1"
            style="width: 100%"
          />
          <div class="form-tip">配置文件中作者的用户ID</div>
        </el-form-item>
        
        <el-form-item label="作者名称" prop="author">
          <el-input
            v-model="formData.author"
            placeholder="请输入作者名称"
            style="width: 100%"
          />
          <div class="form-tip">博客作者的名字</div>
        </el-form-item>
        
        <el-form-item label="博客名称" prop="blog_name">
          <el-input
            v-model="formData.blog_name"
            placeholder="请输入博客名称"
            style="width: 100%"
          />
          <div class="form-tip">博客的标题名称</div>
        </el-form-item>
        
        <el-form-item label="GitHub链接" prop="github_link">
          <el-input
            v-model="formData.github_link"
            placeholder="https://github.com/username"
            style="width: 100%"
          />
          <div class="form-tip">GitHub 个人主页链接</div>
        </el-form-item>
        
        <el-form-item label="Gitee链接" prop="gitee_link">
          <el-input
            v-model="formData.gitee_link"
            placeholder="https://gitee.com/username"
            style="width: 100%"
          />
          <div class="form-tip">Gitee 个人主页链接</div>
        </el-form-item>
        
        <el-form-item label="Bilibili链接" prop="bilibili_link">
          <el-input
            v-model="formData.bilibili_link"
            placeholder="https://space.bilibili.com/xxxxx"
            style="width: 100%"
          />
          <div class="form-tip">Bilibili 个人空间链接</div>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import apiClient from '../../lib/api.js'

const apiUrl = import.meta.env.VITE_API_URL

const saving = ref(false)
const formRef = ref(null)
const formData = ref({
  author_id: 1,
  author: '',
  blog_name: '',
  github_link: '',
  gitee_link: '',
  bilibili_link: ''
})

const formRules = {
  author_id: [
    { required: true, message: '请输入作者ID', trigger: 'blur' }
  ],
  author: [
    { required: true, message: '请输入作者名称', trigger: 'blur' }
  ],
  blog_name: [
    { required: true, message: '请输入博客名称', trigger: 'blur' }
  ]
}

const fetchConfig = async () => {
  try {
    const response = await apiClient.get(`${apiUrl}admin/config/`)
    
    if (response.data.success) {
      formData.value = {
        author_id: response.data.data.author_id || 1,
        author: response.data.data.author || '',
        blog_name: response.data.data.blog_name || '',
        github_link: response.data.data.github_link || '',
        gitee_link: response.data.data.gitee_link || '',
        bilibili_link: response.data.data.bilibili_link || ''
      }
    } else {
      ElMessage.error(response.data.error || '获取配置失败')
    }
  } catch (error) {
    console.error('获取配置错误:', error)
    ElMessage.error('获取配置失败')
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  try {
    const response = await apiClient.put(`${apiUrl}admin/config/update/`, formData.value)
    
    if (response.data.success) {
      ElMessage.success('配置保存成功，页面即将刷新')
      // 延迟一下再刷新，让用户看到成功消息
      setTimeout(() => {
        window.location.reload()
      }, 500)
    } else {
      ElMessage.error(response.data.error || '保存配置失败')
    }
  } catch (error) {
    console.error('保存配置错误:', error)
    ElMessage.error('保存配置失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  fetchConfig()
})
</script>

<style scoped>
.config-manage-container {
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0;
  color: var(--el-text-color-primary);
}

.form-tip {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-top: 4px;
}
</style>

