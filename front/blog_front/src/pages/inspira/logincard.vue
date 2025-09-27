<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FlipCard from './FlipCard.vue'

const isFlipped = ref(false)// 控制翻转状态的响应式变量
const router = useRouter()//创建路由实例
// 切换翻转状态的函数
const toggleFlip = () => {
    isFlipped.value = !isFlipped.value
}

const gohome = () => {
  router.push({ path: '/develop' })
}

const register = () => {
  router.push({ path: '/develop' })
}

const forgot = () => {
  router.push({ path: '/develop' })
}
</script>
<template>
    <div class="flex items-center justify-center" style="height: 100%;">
        <FlipCard :flipped="isFlipped">
            <template #default>
                <el-card style="max-width: 100%;border-radius: 20px; height: 100%;">
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
                    <p v-for="o in 4" :key="o" class="text item">{{ 'List item ' + o }}</p>
                    </div>
                    <template #footer>
                        <div class="footer-container">
                            <button class="dsi-btn dsi-btn-outline dsi-btn-success sub-btn" @click="gohome()">登 录</button>
                            <a @click="forgot()" class="dsi-link dsi-link-info" style="margin: 5px;">忘记密码</a>
                        </div>
                    </template>
                </el-card>
            </template>
            <template #back>
                <el-card style="max-width: 100%;border-radius: 20px; height: 100%;">
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
                    <p v-for="o in 4" :key="o" class="text item">{{ 'List item ' + o }}</p>
                    </div>
                    <template #footer>
                        <div class="footer-container">
                            <button class="dsi-btn dsi-btn-outline dsi-btn-success sub-btn shadow" @click="register()">注 册</button>
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
    margin-left: 10%;
}

.sub-btn {
    width: 40%;
    height: 50px;
    font-size: 19px;
}
.el-card {
  display: grid;
  grid-template-rows: 20% 55% 25%; /* header, body, footer 的高度比例 */
  height: 500px; /* 需要设置总高度 */
}

.card-header {
  grid-row: 1;
}

.card-body {
  grid-row: 2;
}

.footer-container {
  grid-row: 3;
}
</style>