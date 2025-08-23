import { createRouter, createWebHistory } from 'vue-router'

const routes=[
  {
    path: '/',
    name: 'index',
    component: () => import('../pages/index.vue'),//全部异步加载，可以加快首屏加载速度
    meta:{
      title: '首页|L-BLOG'
    }
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../pages/develop.vue'),//全部异步加载，可以加快首屏加载速度
    meta:{
      title: '登录|L-BLOG'
    }
  },
  {
    path: '/home',
    name: 'home',
    component: () => import('../pages/home.vue'),
    meta:{
      title: '主页|L-BLOG'
    }
  }
]
//创建路由器实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
    if (to.meta.title) {
    document.title = to.meta.title//如果要跳转的页面有meta:{title:'标题'}，那就把页面的title设置为该标题
  }
  next()
})
export default router
