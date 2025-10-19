<script setup>
import { ref, reactive } from 'vue'
import { User, Notebook } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const active = ref(0)
const formRef = ref()
const form = reactive({
  username: '',
  answer: '',
  captcha: ''
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

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { validator: validateUserName, trigger: ['blur', 'change'] }
  ],
  answer: [
    { required: true, message: '请输入密保答案', trigger: 'blur' },
    { validator: validateAnswer, trigger: ['blur', 'change'] }
  ],
  captcha: [
    { required: true, message: '请输入验证码', trigger: 'blur' }
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
      active.value++;
    } catch (error) {
      console.log('用户名验证失败')
    }
  } else if (active.value === 1) {
    // 验证密保答案
    try {
      await formRef.value.validateField('answer')
      active.value++;
    } catch (error) {
      console.log('密保答案验证失败')
    }
  } else if (active.value === 2) {
    // 验证验证码
    try {
      await formRef.value.validateField('captcha')
      // 完成所有步骤
      ElMessage.success('验证成功')
    } catch (error) {
      console.log('验证码验证失败')
    }
  }
}

const submit = () => {
  formRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success('表单验证通过')
      // 这里可以添加实际的提交逻辑
    } else {
      ElMessage.error('请检查表单内容')
    }
  })
}
</script>

<template>
  <el-container style="width: 100%">
    <el-header style="height: 100px;">
      <div style="height: 100%;" v-if="active === 0">
        <el-text class="mx-1" size="large">请输入用户名</el-text>
        <el-form 
          ref="formRef" 
          :model="form" 
          :rules="rules" 
          label-width="0px" 
          style="margin-top: 20px; padding: 0 20px;">
          <el-form-item prop="username">
            <el-input
              v-model="form.username" 
              :prefix-icon="User" 
              placeholder="请输入用户名" />
          </el-form-item>
        </el-form>
      </div>
      <div style="height: 100%;" v-if="active === 1">
        <el-text class="mx-1" size="large">请输入密保答案</el-text>
        <el-form 
          ref="formRef" 
          :model="form" 
          :rules="rules" 
          label-width="0px" 
          style="margin-top: 20px; padding: 0 20px;">
          <el-form-item prop="answer">
            <el-input 
              v-model="form.answer" 
              :prefix-icon="Notebook" 
              placeholder="请输入密保答案" />
          </el-form-item>
        </el-form>
      </div>
      <div style="height: 100%;" v-if="active === 2">
        <el-text class="mx-1" size="large">请完成验证码</el-text>
        <el-form 
          ref="formRef" 
          :model="form" 
          :rules="rules" 
          label-width="0px" 
          style="margin-top: 20px; padding: 0 20px;">
          <el-form-item prop="captcha">
            <el-input 
              v-model="form.captcha" 
              placeholder="请输入验证码" />
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
        <el-step title="第一步" />
        <el-step title="第二步" />
        <el-step title="第三步" />
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