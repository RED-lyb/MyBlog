<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import FlipCard from './FlipCard.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Lock, User, EditPen, Notebook } from '@element-plus/icons-vue'
const isFlipped = ref(false)// 控制翻转状态的响应式变量
const registerFormRef = ref()//注册表单引用
const router = useRouter()//创建路由实例
const isAdding = ref(false)
const optionName = ref('')
const optionFormRef = ref()
const emit = defineEmits(['register-success'])   // 1. 声明事件
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
const questions = ref([
    {
        value: '你父亲的名字',
        label: '你父亲的名字',
    },
    {
        value: '你母亲的名字',
        label: '你母亲的名字',
    },
    {
        value: '你对象的名字',
        label: '你对象的名字',
    },
])
const onAddOption = () => {
    isAdding.value = true
}

const onConfirm = async () => {
    const valid = await optionFormRef.value.validate().catch(() => false)
    if (!valid) return

    // 校验通过后写入列表
    questions.value.push({
        label: optionName.value,
        value: optionName.value
    })
    clear()
}

const clear = () => {
    optionName.value = ''
    isAdding.value = false
}

const register_success = () => {
    ElMessage({
        message: '恭喜你，注册成功，可以登录啦！',
        type: 'success',
    })
    emit('register-success')   // 2. 抛出事件
    registerFormRef.value?.resetFields()
    toggleFlip()
}
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



const agreement_show = () => {
    console.log('用户协议')
    ElMessageBox.confirm(
        `1.这是一个开源博客系统，仅供用户交流学习<br/>
    2.请勿以任何形式对本站进行网络攻击，如影响本站正常使用，本站有权采取相应措施<br/>
    3.请勿在本站发布任何违法违规内容，如有发现，本站有权删除违规内容并封禁用户账号<br/>
    4.本站不对用户发布的内容承担任何责任，用户需对其发布的内容负责<br/>
    5.本站尊重并保护用户隐私，除用户名外，其余任何注册信息都将加密存储<br/>
    6.未经用户同意，不会向第三方披露用户信息<br/>
    7.本站可能会不定期更新本协议`,
        '用户协议',
        {
            showCancelButton: false,
            dangerouslyUseHTMLString: true,
            confirmButtonText: '我已阅读完毕',
            type: 'info',
            center: true,
        }
    )
}

// 保留字黑名单（MySQL/Oracle 常见，可按需再扩）
const DB_KEYWORDS = [
    'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'TRUNCATE',
    'USER', 'USERS', 'ORDER', 'GROUP', 'KEY', 'INDEX', 'TABLE', 'PASSWORD', 'ADMIN', 'ROOT'
]
/* 白名单 + 黑名单 校验 */
const validateUserName = (rule, value, callback) => {
    if (!value) return callback(new Error('请输入用户名'))
    // 2. 白名单字符：中英数字下划线连字符
    if (!/^[A-Za-z0-9_\-\u4e00-\u9fa5]+$/.test(value)) {
        return callback(new Error('只允许字母、数字、下划线、连字符、中文'))
    }
    // 4. 保留字大小写不敏感匹配
    if (DB_KEYWORDS.includes(value.toUpperCase())) {
        return callback(new Error('不得使用该用户名，请更换'))
    }
    callback()
}

// 添加密码验证规则
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
    } else if (value !== register.password) {
        callback(new Error('两次输入密码不一致!'))
    } else {
        callback()
    }
}

/* --------- 密保答案：仅中英数，禁止任何符号 --------- */
const validateAnswer = (_, value, callback) => {
    if (!value) return callback(new Error('请输入密保答案'))
    // 纯中文 + 英文 + 数字，无符号
    if (!/^[\u4e00-\u9fa5A-Za-z0-9]+$/.test(value)) {
        return callback(new Error('答案只能包含中文、英文和数字'))
    }
    callback()
}

const optionRules = reactive({
    optionName: [
        { required: true, message: '请输入自定义问题', trigger: 'blur' },
        { validator: validateAnswer, trigger: ['blur', 'change'] }   // 直接复用
    ]
})

// 定义注册表单的验证规则
const registerRules = {
    name: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { validator: validateUserName, trigger: ['blur', 'change'] }
    ],
    password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { validator: validatePass, trigger: ['blur', 'change'] }
    ],
    confirm: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        { validator: validatePass2, trigger: 'blur' }
    ],
    protect: [
        { required: true, message: '请选择密保问题', trigger: 'change' }
    ],
    answer: [
        { required: true, message: '请输入密保答案', trigger: 'blur' },
        { validator: validateAnswer, trigger: ['blur', 'change'] }
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
            register_success()
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
                            <el-form-item label="用户名称" prop="name">
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
                                    <el-option v-for="item in questions" :key="item.value" :label="item.label"
                                        :value="item.value" />
                                    <template #footer>
                                        <el-button v-if="!isAdding" text bg size="small" @click="onAddOption">
                                            输入自定义问题
                                        </el-button>
                                        <template v-else>
                                            <el-form :model="{ optionName }" :rules="optionRules" ref="optionFormRef"
                                                style="width: 100%;">
                                                <el-form-item prop="optionName" class="compact-error">
                                                    <el-input v-model="optionName" class="option-input"
                                                        placeholder="请输入自定义问题" size="small" />
                                                </el-form-item>
                                            </el-form>
                                            <el-button type="primary" size="small" @click="onConfirm">
                                                确认
                                            </el-button>
                                            <el-button size="small" @click="clear">取消</el-button>
                                        </template>
                                    </template>
                                </el-select>
                            </el-form-item>
                            <el-form-item label="密保答案" prop="answer">
                                <el-input v-model="register.answer" :prefix-icon="Notebook" />
                            </el-form-item>
                            <el-form-item prop="choice">
                                <el-checkbox-group v-model="register.choice"
                                    style="display:flex; justify-content:center; width:100%;">
                                    <el-checkbox value="choice">
                                        <span class="checkbox-text">阅读并接受</span>
                                        <a href="javascript:void(0)" class="dsi-link-info"
                                            @click.stop="agreement_show">《博客协议》</a>
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

.option-input {
    width: 100%;
    margin-bottom: 8px;
}

/* 选中 */
.el-checkbox.is-checked .checkbox-text {
    color: #13CE66;
}

:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
    background-color: #13ce66;
    border-color: #13ce66;
}

.el-form-item.is-error .checkbox-text {
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
.option-input{
    margin-bottom: 0px;
}
</style>