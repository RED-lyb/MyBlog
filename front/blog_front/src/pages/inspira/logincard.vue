<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import FlipCard from './FlipCard.vue'
import { Lock, User, EditPen, Notebook } from '@element-plus/icons-vue'
const isFlipped = ref(false)// 控制翻转状态的响应式变量
const registerFormRef = ref()//注册表单引用
const router = useRouter()//创建路由实例

// 切换翻转状态的函数
const toggleFlip = () => {
    isFlipped.value = !isFlipped.value
}

const gohome = () => {
    router.push({ path: '/develop' })
}

const forgot = () => {
    router.push({ path: '/develop' })
}


const login = reactive({
    name: '',
    password: '',
})

const register = reactive({
    name: '',
    password: '',
    confirm: '',
    protect: '',
    answer: '',
    choice: []
})

// 添加密码验证规则
const validatePass = (rule, value, callback) => {
    if (value === '') {
        callback(new Error('请输入密码'))
    } else {
        if (register.confirm !== '' && registerFormRef.value) {
            registerFormRef.value.validateField('confirm')
        }
        callback()
    }
}

const validatePass2 = (rule, value, callback) => {
    if (value === '') {
        callback(new Error('请再次输入密码'))
    } else if (value !== register.password) {
        callback(new Error('两次输入密码不一致!'))
    } else {
        callback()
    }
}

// 定义注册表单的验证规则
const registerRules = {
    name: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 20, message: '用户名长度应在3-20个字符之间', trigger: 'blur' }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { validator: validatePass, trigger: 'blur' }
    ],
    confirm: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        { validator: validatePass2, trigger: 'blur' }
    ],
    protect: [
        { required: true, message: '请选择密保问题', trigger: 'change' }
    ],
    answer: [
        { required: true, message: '请输入密保答案', trigger: 'blur' }
    ],
    choice: [
        { type: 'array', required: true, message: '请阅读并接受博客协议', trigger: 'change' }
    ]
}

const onLogin = () => {
    console.log('login!', login.name, login.password)
}

// 修改注册提交函数
const onRegister = () => {
    if (!registerFormRef.value) return
    registerFormRef.value.validate((valid) => {
        if (valid) {
            console.log('register!', register.name, register.password, register.confirm, register.protect, register.answer, register.choice)
        } else {
            console.log('注册表单验证失败!')
            return false
        }
    }).catch(error => {
        console.error('表单验证出错:', error)
    })
}
</script>
<template>
    <div class="flex items-center justify-center" style="height: 100%;">
        <FlipCard :flipped="isFlipped">

            <template #default>
                <el-card style="max-width: 100%;border-radius: 20px; height: 100%;" class="login-el-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon :size="50">
                                <Edit />
                            </el-icon>
                            <span class="title-text">登 录</span>
                            <button class="dsi-btn dsi-btn-soft dsi-btn-info choice-btn"
                                @click="toggleFlip">切换注册</button>
                        </div>
                    </template>

                    <div class="card-body">
                        <el-form :model="login" label-width="auto" label-position="top"
                            style="max-width: 300px ;width: 300px;">
                            <el-form-item label="用户名">
                                <el-input v-model="login.name" :prefix-icon="User" />
                            </el-form-item>
                            <el-form-item label="密码">
                                <el-input v-model="login.password" type="password" show-password :prefix-icon="Lock" />
                            </el-form-item>
                        </el-form>
                    </div>
                    <template #footer>
                        <div class="footer-container">
                            <button class="dsi-btn dsi-btn-outline dsi-btn-success sub-btn" @click="onLogin">登
                                录</button>
                            <a @click="forgot" class="dsi-link dsi-link-info" style="margin: 5px;">忘记密码</a>
                        </div>
                    </template>

                </el-card>
            </template>
            <template #back>
                <el-card style="max-width: 100%;border-radius: 20px; height: 100%;" class="register-el-card">
                    <template #header>
                        <div class="card-header">
                            <el-icon :size="50">
                                <Edit />
                            </el-icon>
                            <span class="title-text">注 册</span>
                            <button class="dsi-btn dsi-btn-soft dsi-btn-info choice-btn"
                                @click="toggleFlip">切换登录</button>
                        </div>
                    </template>
                    <div class="card-body">

                        <el-form ref="registerFormRef" :model="register" :rules="registerRules" label-width="auto"
                            label-position="left" status-icon hide-required-asterisk
                            style="max-width: 300px;width: 300px;">
                            <el-form-item label="用户昵称" prop="name">
                                <el-input v-model="register.name" :prefix-icon="User" />
                            </el-form-item>
                            <el-form-item label="登录密码" prop="password">
                                <el-input v-model="register.password" type="password" show-password
                                    :prefix-icon="Lock" />
                            </el-form-item>
                            <el-form-item label="确认密码" prop="confirm">
                                <el-input v-model="register.confirm" type="password" show-password
                                    :prefix-icon="Lock" />
                            </el-form-item>
                            <el-form-item label="密保问题" prop="protect">
                                <el-icon :size="14"
                                    style="position: absolute;left: 11px;top: 50%;transform: translateY(-50%);z-index: 10;color: #9A9DA3;">
                                    <EditPen />
                                </el-icon>
                                <el-select v-model="register.protect" placeholder="选择你的密保问题">
                                    <template #prefix>
                                        <span style="display:inline-block;width:15px;"></span>
                                    </template>
                                    <el-option label="你父亲的名字" value="你父亲的名字" />
                                    <el-option label="你母亲的名字" value="你母亲的名字" />
                                    <el-option label="你配偶的名字" value="你配偶的名字" />
                                </el-select>
                            </el-form-item>
                            <el-form-item label="密保答案" prop="answer">
                                <el-input v-model="register.answer" :prefix-icon="Notebook" />
                            </el-form-item>
                            <el-form-item prop="choice">
                                <el-checkbox-group v-model="register.choice"
                                    style="display:flex; justify-content:center; width:100%;">
                                    <el-checkbox value="choice" text-color="#ff0000">
                                        <!-- 默认插槽里可以放任意 HTML -->
                                        <span class="checkbox-text">阅读并接受</span>
                                        <a href="#" class="dsi-link-info" @click.stop>《博客协议》</a>
                                    </el-checkbox>
                                </el-checkbox-group>

                                <template #error="{ error }">
                                    <div class="el-form-item__error">{{ error }}</div>
                                </template>
                            </el-form-item>
                        </el-form>

                    </div>
                    <template #footer>
                        <div class="footer-container">
                            <button class="dsi-btn dsi-btn-outline dsi-btn-success sub-btn" @click="onRegister">注
                                册</button>
                        </div>
                    </template>
                </el-card>
            </template>
        </FlipCard>
    </div>
</template>
<style scoped>
.card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

}

.footer-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 100%;
}

.title-text {
    font-size: 40px;
    font-weight: bolder;
    margin-left: 12%;
}

.sub-btn {
    width: 40%;
    height: 50px;
    font-size: 19px;
}

.login-el-card {
    display: grid;
    grid-template-rows: 20% 55% 25%;
    /* header, body, footer 的高度比例 */
    height: 500px;
    /* 需要设置总高度 */
}

.register-el-card {
    display: grid;
    grid-template-rows: 20% 65% 15%;
    /* header, body, footer 的高度比例 */
    height: 500px;
    /* 需要设置总高度 */
}

.card-header {
    grid-row: 1;
}

.card-body {
    grid-row: 2;
    display: flex;
    justify-content: center;
}

.footer-container {
    grid-row: 3;
}

.el-form-item__error {
    text-align: center;
    width: 100%;
}
/* 选中 */
.el-checkbox.is-checked .checkbox-text { color: #13CE66; }

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #13ce66;
  border-color: #13ce66;
}

.el-form-item.is-error .checkbox-text,
.el-form-item.is-error .checkbox-text a {
  color: var(--el-color-danger) !important;
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
.el-form-item.is-success .el-icon { color: #13CE66 !important; }
.el-form-item.is-error  .el-icon { color: var(--el-color-danger) !important; }
.el-form-item.is-success :deep(.el-select__caret) {
  color: #13CE66 !important;
}

/* 校验失败：下拉箭头变红 */
.el-form-item.is-error :deep(.el-select__caret) {
  color: var(--el-color-danger) !important;
}
</style>