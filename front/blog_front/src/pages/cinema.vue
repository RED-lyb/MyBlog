<script setup>
import { onMounted, ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useUserInfo } from '../lib/authState.js'
import { useAuthStore } from '../stores/user_info.js'
import { showCinemaLoginDialog } from '../lib/guestDialog.js'
import FullScreenLoading from './FullScreenLoading.vue'
import Head from '../components/Head.vue'
import Footer from '../components/Footer.vue'
import Cinema_main from '../components/cinema_main.vue'

const authStore = useAuthStore()
const router = useRouter()
const { tokenExpired, isAuthenticated } = storeToRefs(authStore)
const { loading, fetchUserInfo } = useUserInfo()
const isLoading = ref(true)
const layoutReady = ref(false)
const showPageContent = ref(false)
const showPageLoading = computed(() => loading.value || isLoading.value || !layoutReady.value)

const markLayoutReady = async () => {
  if (layoutReady.value) return
  await nextTick()
  layoutReady.value = true
}

const promptLogin = async () => {
  await markLayoutReady()
  await nextTick()
  showCinemaLoginDialog(router, '/home')
}

onMounted(async () => {
  authStore.syncFromLocalStorage()

  if (tokenExpired.value) {
    isLoading.value = false
    await promptLogin()
    return
  }

  const accessToken = localStorage.getItem('access_token')

  if (!accessToken) {
    isLoading.value = false
    await promptLogin()
    return
  }

  try {
    await fetchUserInfo()
  } catch (error) {
    if (error.message !== 'TOKEN_EXPIRED') {
      // 其它错误由调用方处理
    }
  } finally {
    isLoading.value = false
    if (!isAuthenticated.value || tokenExpired.value) {
      await promptLogin()
    } else {
      await markLayoutReady()
      showPageContent.value = true
    }
  }
})
</script>

<template>
  <FullScreenLoading :visible="showPageLoading" />
  <div v-if="showPageLoading"></div>
  <div v-else-if="showPageContent">
    <div class="common-layout">
      <el-container>
        <el-header style="padding: 0">
          <Head />
        </el-header>
        <el-container>
          <el-main class="cinema-main">
            <Cinema_main />
          </el-main>
        </el-container>
        <el-footer style="padding: 0">
          <Footer />
        </el-footer>
      </el-container>
    </div>
  </div>
</template>

<style scoped>
.cinema-main {
  width: 100%;
  flex: 1;
  background-color: #00000000;
  min-height: max(570px, calc(100vh - 165px));
  padding: 20px;
  border: 1px solid var(--el-border-color-light);
  margin-top: 10px;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0, 0, 0, 0.1);
  box-sizing: border-box;
}
</style>
