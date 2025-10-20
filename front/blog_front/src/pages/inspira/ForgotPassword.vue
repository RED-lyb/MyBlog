<script setup>
import { ref, reactive } from 'vue'
import { User, Notebook, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const apiUrl = import.meta.env.VITE_API_URL
const active = ref(0)
const formRef = ref()
const protectQuestion = ref('') // 存储密保问题

const form = reactive({
  username: '',
  answer: '',
  password: '',
  confirm: ''
})

// 保留字黑名单（与logincard.vue中一致）
const DB_KEYWORDS = [
  'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
  'USER', 'USERS', 'ORDER', 'GROUP', 'KEY', 'INDEX', 'TABLE', 'PASSWORD', 'ADMIN', 'ROOT'
]

/* 白名单 + 黑名单 校验 */
const validateUserName = (rule, value, callback) => {
  if (!value) return callback(new Error('请输入用户名'))
  // 白名单字符：中英数字下划线连字符
  if (!/^[A-Za-z0-9_\-\u4e00-\u9fa5]+$/.test(value)) {
    return callback(new Error('只允许字母、数字、下划线、连字符、中文'))
  }
  // 保留字大小写不敏感匹配
  if (DB_KEYWORDS.includes(value.toUpperCase())) {
    return callback(new Error('不得使用该用户名，请更换'))
  }
  callback()
}

/* 密保答案：仅中英数，禁止任何符号 */
const validateAnswer = (_, value, callback) => {
  if (!value) return callback(new Error('请输入密保答案'))
  // 纯中文 + 英文 + 数字，无符号
  if (!/^[\u4e00-\u9fa5A-Za-z0-9]+$/.test(value)) {
    return callback(new Error('答案只能包含中文、英文和数字'))
  }
  callback()
}

// 添加密码验证规则（从logincard.vue复制）
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

const pre = () => {
  if (active.value > 0) {
    active.value--;
  }
}

const next = async () => {
  if (active.value === 0) {
    // 验证用户名
    try {
      await formRef.value.validateField('username')
      const response = await axios.post(apiUrl + 'forgot/', {
        username: form.username
      })
      
      if (response.data.status === 'true') {
        // 用户存在，保存密保问题
        protectQuestion.value = response.data.protect
        active.value++;
      } else {
        ElMessage.error(response.data.message || '用户不存在')
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '用户名验证失败')
    }
  } else if (active.value === 1) {
    // 验证密保答案
    try {
      await formRef.value.validateField('answer')
      const response = await axios.post(apiUrl + 'forgot/', {
        username: form.username,
        answer: form.answer
      })
      
      if (response.data.status === 'true') {
        // 密保验证成功
        active.value++;
      } else {
        ElMessage.error(response.data.message || '密保答案错误')
      }
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '密保答案验证失败')
    }
  } else if (active.value === 2) {
    // 验证新密码
    try {
      await formRef.value.validateField('password')
      await formRef.value.validateField('confirm')
      // 完成所有步骤
      ElMessage.success('验证成功')
    } catch (error) {
      console.log('密码验证失败')
      ElMessage.error('密码验证失败')
    }
  }
}

const submit = async () => {
  if (active.value !== 2) return
  
  try {
    await formRef.value.validate()
    // 发送重置密码请求
    const response = await axios.put(apiUrl + 'forgot/', {
      username: form.username,
      password: form.password
    })
    
    ElMessage.success('密码重置成功')
    // 重置表单并返回第一步
    formRef.value.resetFields()
    active.value = 0
    protectQuestion.value = ''
    
    // 可以在这里添加跳转到登录页的逻辑
    // emit('password-reset-success')
  } catch (error) {
    ElMessage.error(error.response?.data?.message || '密码重置失败，请稍后重试')
  }
}
</script>

<template>
  <el-container style="width: 100%">
    <el-header style="height: 130px;">
      <div style="height: 100%;" v-if="active === 0">
        <el-text class="mx-1" size="large">请输入用户名</el-text>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="0px"
          style="margin-top: 50px; padding: 0 20px;">
          <el-form-item prop="username">
            <el-input v-model="form.username" :prefix-icon="User" placeholder="请输入用户名" />
          </el-form-item>
        </el-form>
      </div>
      <div style="height: 100%;" v-else-if="active === 1">
        <el-text class="mx-1" size="large">密保问题：{{ protectQuestion }}</el-text>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="0px"
          style="margin-top: 30px; padding: 0 20px;">
          <el-form-item prop="answer">
            <el-input v-model="form.answer" :prefix-icon="Notebook" placeholder="请输入密保答案" />
          </el-form-item>
        </el-form>
      </div>
      <div style="height: 100%;" v-else-if="active === 2">
        <el-text class="mx-1" size="large">请设置新密码</el-text>
        <el-form ref="formRef" :model="form" :rules="rules" label-width="0px"
          style="margin-top: 20px; padding: 0 20px;">
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" show-password :prefix-icon="Lock" placeholder="请输入新密码" />
          </el-form-item>
          <el-form-item prop="confirm">
            <el-input v-model="form.confirm" type="password" show-password :prefix-icon="Lock" placeholder="请再次输入新密码" />
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
  </el-container>
</template>

<style scoped>
.button-container {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
}
</style>
