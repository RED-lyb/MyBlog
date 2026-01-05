<template>
  <div class="config-manage-container">
    <div class="page-header">
      <h1 class="page-title">全局配置</h1>
      <el-button type="primary" plain @click="handleSave" :loading="saving">
        <el-icon><Check /></el-icon>
        保存配置
      </el-button>
    </div>
    
    <el-card>
      <template #header>
        <span style="font-size: 18px; font-weight: bold">前端配置</span>
      </template>
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

        <!-- 主题颜色配置 -->
        <el-divider content-position="left" style="margin-top: 20px">主题颜色配置</el-divider>
        
        <!-- 浅色主题 -->
        <el-form-item label="浅色主题">
          <div style="display: flex; flex-direction: column; gap: 16px; width: 100%">
            <div>
              <span>点缀颜色</span>
              &nbsp;
              <el-color-picker
                v-model="formData.light.particlesColor"
                color-format="hex"
                size="small"
              />
              <div class="form-tip">浅色主题下的粒子点缀默认颜色：#00EAFF</div>
            </div>
            <div>
              <span>背景颜色</span>
              &nbsp;
              <el-color-picker
                v-model="formData.light.bgcolor"
                color-format="hex"
                size="small"
              />
              <div class="form-tip">浅色主题下的背景颜色默认颜色：#FFFFFF</div>
            </div>
          </div>
        </el-form-item>

        <!-- 深色主题 -->
        <el-form-item label="深色主题">
          <div style="display: flex; flex-direction: column; gap: 16px; width: 100%">
            <div>
              <span>点缀颜色</span>
              &nbsp;
              <el-color-picker
                v-model="formData.dark.particlesColor"
                color-format="hex"
                size="small"
              />
              <div class="form-tip">深色主题下的粒子点缀默认颜色：#FFFFFF</div>
            </div>
            <div>
              <span>背景颜色</span>
              &nbsp;
              <el-color-picker
                v-model="formData.dark.bgcolor"
                color-format="hex"
                size="small"
              />
              <div class="form-tip">深色主题下的背景颜色默认颜色：#000000</div>
            </div>
          </div>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 后端配置 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <span style="font-size: 18px; font-weight: bold">后端配置（修改后将会重启服务器，谨慎修改）</span>
      </template>
      
      <el-form
        ref="backFormRef"
        :model="backFormData"
        label-width="150px"
        label-position="left"
      >
        <!-- 网盘配置 -->
        <el-divider content-position="left">网盘配置</el-divider>
        <el-form-item label="清理天数">
          <el-input-number
            v-model="backFormData.network_disk.cleanup_days"
            :min="1"
            :max="365"
            style="width: 100%"
          />
          <div class="form-tip">删除多少天前修改的文件（默认7天）</div>
        </el-form-item>

        <!-- 验证码配置 -->
        <el-divider content-position="left">验证码配置</el-divider>
        <el-form-item label="验证码长度">
          <el-input-number
            v-model="backFormData.captcha.length"
            :min="4"
            :max="8"
            style="width: 100%"
          />
          <div class="form-tip">验证码字符数量（默认4）</div>
        </el-form-item>
        <el-form-item label="有效期（分钟）">
          <el-input-number
            v-model="backFormData.captcha.timeout"
            :min="1"
            :max="60"
            style="width: 100%"
          />
          <div class="form-tip">验证码有效期（默认5分钟）</div>
        </el-form-item>
        <el-form-item label="图片宽度">
          <el-input-number
            v-model="backFormData.captcha.image_size[0]"
            :min="80"
            :max="300"
            style="width: 100%"
          />
          <div class="form-tip">验证码图片宽度（默认120px）</div>
        </el-form-item>
        <el-form-item label="图片高度">
          <el-input-number
            v-model="backFormData.captcha.image_size[1]"
            :min="30"
            :max="100"
            style="width: 100%"
          />
          <div class="form-tip">验证码图片高度（默认40px）</div>
        </el-form-item>
        <el-form-item label="字体大小">
          <el-input-number
            v-model="backFormData.captcha.font_size"
            :min="12"
            :max="40"
            style="width: 100%"
          />
          <div class="form-tip">验证码字体大小（默认20）</div>
        </el-form-item>
        <el-form-item label="前景颜色">
          <el-color-picker
            v-model="backFormData.captcha.foreground_color"
            color-format="hex"
            size="small"
          />
          &nbsp;
          <div class="form-tip">验证码文字颜色默认颜色：#001100</div>
        </el-form-item>
        <el-form-item label="背景颜色">
          <el-color-picker
            v-model="backFormData.captcha.background_color"
            color-format="hex"
            size="small"
          />
          &nbsp;
          <div class="form-tip">验证码背景颜色默认颜色：#ffffff</div>
        </el-form-item>
        <!-- JWT Token配置 -->
        <el-divider content-position="left">Token时间配置</el-divider>
        <el-form-item label="Access Token过期时间（分钟）">
          <el-input-number
            v-model="backFormData.jwt.access_token_expire_minutes"
            :min="1"
            :max="1440"
            style="width: 100%"
          />
          <div class="form-tip">Access Token过期时间（默认60分钟）</div>
        </el-form-item>
        <el-form-item label="Refresh Token过期时间（天）">
          <el-input-number
            v-model="backFormData.jwt.refresh_token_expire_days"
            :min="1"
            :max="365"
            style="width: 100%"
          />
          <div class="form-tip">Refresh Token过期时间（默认30天）</div>
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
const backFormRef = ref(null)
const formData = ref({
  author_id: 1,
  author: '',
  blog_name: '',
  github_link: '',
  gitee_link: '',
  bilibili_link: '',
  light: {
    particlesColor: '#00EAFF',
    bgcolor: '#FFFFFF'
  },
  dark: {
    particlesColor: '#FFFFFF',
    bgcolor: '#000000'
  }
})

const backFormData = ref({
  network_disk: {
    cleanup_days: 7
  },
  captcha: {
    challenge_funct: 'captcha.helpers.random_char_challenge',
    length: 4,
    timeout: 5,
    image_size: [120, 40],
    font_size: 20,
    background_color: '#ffffff',
    foreground_color: '#001100',
    noise_functions: ['captcha.helpers.noise_arcs', 'captcha.helpers.noise_dots']
  },
  jwt: {
    access_token_expire_minutes: 60,
    refresh_token_expire_days: 30
  }
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
      const data = response.data.data
      
      // 前端配置
      formData.value = {
        author_id: data.author_id || 1,
        author: data.author || '',
        blog_name: data.blog_name || '',
        github_link: data.github_link || '',
        gitee_link: data.gitee_link || '',
        bilibili_link: data.bilibili_link || '',
        light: {
          particlesColor: data.light?.particlesColor || '#00EAFF',
          bgcolor: data.light?.bgcolor || '#FFFFFF'
        },
        dark: {
          particlesColor: data.dark?.particlesColor || '#FFFFFF',
          bgcolor: data.dark?.bgcolor || '#000000'
        }
      }
      
      // 后端配置
      if (data.network_disk) {
        backFormData.value.network_disk = {
          cleanup_days: data.network_disk.cleanup_days || 7
        }
      }
      
      if (data.captcha) {
        backFormData.value.captcha = {
          challenge_funct: data.captcha.challenge_funct || 'captcha.helpers.random_char_challenge',
          length: data.captcha.length || 4,
          timeout: data.captcha.timeout || 5,
          image_size: data.captcha.image_size || [120, 40],
          font_size: data.captcha.font_size || 20,
          background_color: data.captcha.background_color || '#ffffff',
          foreground_color: data.captcha.foreground_color || '#001100',
          noise_functions: data.captcha.noise_functions || ['captcha.helpers.noise_arcs', 'captcha.helpers.noise_dots']
        }
      }
      
      if (data.jwt) {
        backFormData.value.jwt = {
          access_token_expire_minutes: data.jwt.access_token_expire_minutes || 60,
          refresh_token_expire_days: data.jwt.refresh_token_expire_days || 30
        }
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
    // 合并前端和后端配置
    const allConfig = {
      author_id: formData.value.author_id,
      author: formData.value.author,
      blog_name: formData.value.blog_name,
      github_link: formData.value.github_link,
      gitee_link: formData.value.gitee_link,
      bilibili_link: formData.value.bilibili_link,
      light: formData.value.light,
      dark: formData.value.dark,
      network_disk: backFormData.value.network_disk,
      captcha: backFormData.value.captcha,
      jwt: backFormData.value.jwt
    }
    
    const response = await apiClient.put(`${apiUrl}admin/config/update/`, allConfig)
    
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
::v-deep(.el-divider__text){
  background-color: var(--el-bg-color-overlay) !important;
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

