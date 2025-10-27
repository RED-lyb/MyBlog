<script setup>
import { ref, onMounted } from 'vue'
import { useStore } from '../stores/counter.js'
import apiClient from '../lib/api.js'

const stores = useStore()
const data = ref("")
const status = ref("")
const userInfo = ref(null)
const isAuthenticated = ref(false)
const loading = ref(true)

const fetchHomeData = async () => {
    try {
        loading.value = true
        const response = await apiClient.get(`${import.meta.env.VITE_API_URL}home/`)
        
        data.value = response.data
        status.value = response.status
        
        // 处理用户信息
        if (response.data.success && response.data.data) {
            isAuthenticated.value = response.data.data.is_authenticated
            userInfo.value = response.data.data.user
        }
    } catch (error) {
        console.error('获取首页数据失败:', error)
        data.value = error.response?.data || error.message
        status.value = error.response?.status || 'error'
    } finally {
        loading.value = false
    }
}

const logout = async () => {
    try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
            await apiClient.post(`${import.meta.env.VITE_API_URL}auth/logout/`, {
                refresh_token: refreshToken
            })
        }
    } catch (error) {
        console.error('退出登录失败:', error)
    } finally {
        // 清除本地存储的token
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_info')
        
        // 重新加载页面或跳转到登录页
        window.location.href = '/login'
    }
}

// 页面挂载时获取数据
onMounted(() => {
    fetchHomeData()
})
</script>

<template>
    <div>
        <h1>目前正处于测试部署状态，还未正式部署相关内容</h1>
        
        <div v-if="loading">
            <p>加载中...</p>
        </div>
        
        <div v-else>
            <div v-if="isAuthenticated && userInfo">
                <h2>欢迎回来，{{ userInfo.username }}！</h2>
                <p>用户ID: {{ userInfo.id }}</p>
                <p>注册时间: {{ userInfo.registered_time }}</p>
                <p>密保问题: {{ userInfo.protect }}</p>
                <button @click="logout" style="margin-top: 10px; padding: 8px 16px; background-color: #f56c6c; color: white; border: none; border-radius: 4px; cursor: pointer;">
                    退出登录
                </button>
            </div>
            
            <div v-else>
                <h2>访客模式</h2>
                <p>{{ data?.data?.guest_message || '您当前以访客身份访问，请登录以获得完整功能' }}</p>
            </div>
            
            <hr>
            <h3>调试信息：</h3>
            <p>测试后端返回的信息：data:{{ data }}, status:{{ status }}</p>
        </div>
    </div>
</template>