/**
 * 管理员子路由配置
 */
const adminRoutes = [
  {
    path: '',
    redirect: '/admin/dashboard'
  },
  {
    path: 'dashboard',
    name: 'admin_dashboard',
    component: () => import('../pages/admin/Dashboard.vue'),
    meta: {
      title: '统计面板|L-BLOG管理后台'
    }
  },
  {
    path: 'articles',
    name: 'admin_articles',
    component: () => import('../pages/admin/ArticleManage.vue'),
    meta: {
      title: '文章管理|L-BLOG管理后台'
    }
  },
  {
    path: 'users',
    name: 'admin_users',
    component: () => import('../pages/admin/UserManage.vue'),
    meta: {
      title: '用户管理|L-BLOG管理后台'
    }
  },
  {
    path: 'network-disk',
    name: 'admin_network_disk',
    component: () => import('../pages/admin/NetworkDiskManage.vue'),
    meta: {
      title: '网盘管理|L-BLOG管理后台'
    }
  },
  {
    path: 'config',
    name: 'admin_config',
    component: () => import('../pages/admin/ConfigManage.vue'),
    meta: {
      title: '全局配置|L-BLOG管理后台'
    }
  }
]

export default adminRoutes

