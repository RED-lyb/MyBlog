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
    <span @click.stop="logout" class="logout-text">
        退出登录
    </span>
</template>

<style scoped>
.logout-text {
    cursor: pointer;
    user-select: none;
}
.logout-text:hover {
    color: #C8161D;
}
</style>


