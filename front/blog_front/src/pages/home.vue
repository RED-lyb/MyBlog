<script setup>
import { onMounted } from 'vue'
import Logout from '../components/Logout.vue'
import { useAuthState, useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'
const authState = useAuthState()
const { loading, fetchUserInfo } = useUserInfo()
const router=useRouter()
const guest_info_show = () => {
    ElMessageBox.confirm(
        `您当前正在以游客身份访问，仅可进行博客文档内容阅读，<br/>
        无个人主页，无法撰写与上传内容，无法与其他用户进行互动，
        如需获得完整体验，请进行登录<br/>`,
        '游客须知',
        {
            dangerouslyUseHTMLString: true,
            cancelButtonText: '继续访问',
            confirmButtonText: '去登录',
            type: 'info',
            center: true,
        }
    )
        .then(() => {
            router.push({ path: '/login' })
        })
        .catch(() => {
        })
}
// 页面挂载时刷新用户信息（确保数据最新）
// 注意：应用启动时已自动获取，这里作为刷新机制
onMounted(async () => {
    const authStore = useAuthStore()
    
    // 如果已经标记为过期，不要再次调用fetchUserInfo，避免清空用户信息
    if (authStore.tokenExpired) {
        // token已过期，等待路由守卫处理
    } else {
        try {
            await fetchUserInfo()
        } catch (error) {
            // 如果是token过期错误，不显示错误消息，让路由守卫处理
            if (error.message !== 'TOKEN_EXPIRED') {
                // 其他错误可以在这里处理
            }
        }
    }
    
    // 只有在不是过期状态且未认证时才显示游客提示
    // 如果是过期状态，路由守卫会处理
    if (!authState.isAuthenticated && !authStore.tokenExpired) {
        guest_info_show()
    }
})
</script>

<template>
    <div>
        <h1>目前正处于测试部署状态，还未正式部署相关内容</h1>

        <div v-if="loading">
            <p>加载中...</p>
        </div>

        <div v-else>
            <div v-if="authState.isAuthenticated && authState.user">
                <h2>欢迎回来，{{ authState.user.username }}！</h2>
                <p>用户ID: {{ authState.user.id }}</p>
                <p>注册时间: {{ authState.user.registered_time }}</p>
                <p>密保问题: {{ authState.user.protect }}</p>
                <Logout />
            </div>

            <div v-else>
                <h2>访客模式</h2>
                <p>您当前以访客身份访问，请登录以获得完整功能</p>
            </div>

        </div>
    </div>
</template>