import { createRouter, createWebHistory } from 'vue-router'

const routes=[
  {
    path: '/',
    name: 'index',
    component: () => import('../pages/index.vue'),
    meta:{
      title: 'Index'
    }
  },

  {
    path: '/home',
    name: 'home',
    component: () => import('../pages/home.vue'),
    meta:{
      title: 'Home'
    }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
    if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})
export default router
