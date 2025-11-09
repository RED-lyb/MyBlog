<script setup>
import apiClient from '../lib/api.js'
import { useAuthStore } from '../stores/user_info.js'
import { useRouter } from 'vue-router'
const router = useRouter()
const logout = async () => {
    try {
        await apiClient.post(`${import.meta.env.VITE_API_URL}auth/logout/`, {}, { withCredentials: true })
    } catch (_) {
    } finally {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
        const authStore = useAuthStore()
        authStore.resetLoginState()
        router.push('/login')
    }
}
</script>

<template>
    <button @click="logout" style="margin-top: 10px; padding: 8px 16px; background-color: #f56c6c; color: white; border: none; border-radius: 4px; cursor: pointer;">
        退出登录
    </button>
    
</template>


