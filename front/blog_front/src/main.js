import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { useDark } from '@vueuse/core'
import App from './App.vue'
import router from './router'
import '@/assets/main.css'
import './style.css'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import '@/assets/element-plus-override.css' // 在 Element Plus CSS 之后加载，确保覆盖生效
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import 'dayjs/locale/zh-cn' // 日期组件需要 dayjs 的中文语言包
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { useAuthStore } from './stores/user_info.js'
import { useConfigStore } from './stores/config.js'

const app = createApp(App)
const pinia = createPinia()
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus, {
  locale: zhCn,
})
app.use(pinia)
app.use(router)

useDark({
  selector: 'html',
  attribute: 'data-theme',
  valueDark: 'dark',
  valueLight: 'light',
  initialValue: 'dark',
})

app.mount('#app')

// 应用启动后只同步localStorage中的状态，不发起网络请求
// 让路由守卫和页面组件来处理用户信息的获取和token过期检查
const authStore = useAuthStore()
authStore.syncFromLocalStorage()

// 加载配置文件
const configStore = useConfigStore()
configStore.loadConfig()
