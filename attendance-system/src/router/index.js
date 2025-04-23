// router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Login from '@/views/Login.vue'       // 使用别名路径
import StudentAttendance from '@/views/StudentAttendance.vue'
import SearchAttendance from '@/views/SearchAttendance.vue'
import AdminReport from '@/views/AdminReport.vue'
import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/login',
    component: Login,
    meta: { 
      guestOnly: true,
    }
  },
  // 新增主布局路由
  {
    path: '/',
    component: MainLayout, // 主布局容器
    meta: { requiresAuth: true },
    children: [ // 嵌套子路由
      {
        path: '/attendance',
        component: StudentAttendance,
        meta: { allowedRoles: ['student'] }
      },
      {
        path: '/search',
        component: SearchAttendance,
        meta: { allowedRoles: ['student'] }
      },
      {
        path: '/report',
        component: AdminReport,
        meta: { allowedRoles: ['admin'] }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from) => {
  console.log('-------------')
  const authStore = useAuthStore()
  // 重要！必须等待初始化完成
  await authStore.initialize()

   // 调试信息
   console.log('当前状态:', {
    isLoggedIn: authStore.isLoggedIn,
    role: authStore.user?.role,
    path: to.path
  })

  // 1. 已登录用户访问登录页
  if (to.path === '/login' && authStore.isLoggedIn) {
    return authStore.user?.role === 'admin' ? '/report' : '/attendance'
  }

  // 2. 认证检查
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return '/login'
  }

  // 3. 角色权限检查
  // if (to.meta.allowedRoles) {
  //   const hasRole = to.meta.allowedRoles.includes(authStore.user?.role)
  //   if (!hasRole) return authStore.isAdmin ? '/report' : '/attendance'
  // }

  // 4. 根路径重定向
  // if (to.path === '/') {
  //   return authStore.isLoggedIn ? 
  //     (authStore.isAdmin ? '/report' : '/attendance') : 
  //     '/login'
  // }

  return true
})
export default router
