import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/useUserStore'
import { ElMessage } from 'element-plus'
import Layout from '@/components/layout/Layout.vue'
import Home from '@/views/Home.vue'
import WebsiteControl from '@/views/control/WebsiteControl.vue'
import ProcessControl from '@/views/control/ProcessControl.vue'
import Login from '@/views/Login.vue'
import Admin from '@/views/terminal_admin/Admin.vue'
import Role from '@/views/terminal_admin/Role.vue'
import Group from '@/views/terminal_admin/Group.vue'
import Terminal from '@/views/terminal_admin/Terminal.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      component: Login
    },
    {
      path: '/',
      redirect: '/login',
      component: Layout,
      children: [
        {
          path: '/home',
          name: 'Home',
          component: Home,
          meta: { requiresAuth: true }
        },
        {
          path: '/policy/website',
          name: WebsiteControl,
          component: WebsiteControl,
          meta: { requiresAuth: true }
        },
        {
          path: '/policy/process',
          name: ProcessControl,
          component: ProcessControl,
          meta: { requiresAuth: true }
        },
        {
          path: '/management/terminal',
          name: Terminal,
          component: Terminal,
          meta: {
            requiresAuth: true,
          }
        },
        {
          path: '/management/terminal/detail/:id',
          name: 'TerminalDetail',
          component: () => import('@/views/terminal_admin/TerminalDetail.vue'),
          meta: { requiresAuth: true, title: '终端详情' }
        },
        {
          path: '/management/admin',
          name: Admin,
          component: Admin,
          meta: {
            requiresAuth: true,
            perm: 'admin:list'
          }
        },
        {
          path: '/management/role',
          name: Role,
          component: Role,
          meta: {
            requiresAuth: true,
            perm: 'role:list'
          }
        },
        {
          path: '/management/group',
          name: Group,
          component: Group,
          meta: {
            requiresAuth: true,
          }
        },
        {
          path: '/change-password',
          name: 'ChangePassword',
          component: () => import('@/views/ChangePassword.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/monitor/process_monitor',
          name: 'ProcessMonitor',
          component: () => import('@/views/monitor/ProcessMonitor.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/monitor/behavior',
          name: 'Behavior',
          component: () => import('@/views/monitor/Behavior.vue'),
          meta: { requiresAuth: true }
        },
        {
          path: '/log/behavior',
          name: 'BehaviorLog',
          component: () => import('@/views/log/Log.vue'),
        },
        {
          path: '/log/operation',
          name: 'operation',
          component: () => import('@/views/log/OperationLog.vue'),
        },
        {
          path: '/403',
          component: () => import('@/views/403.vue'),
          meta: { title: '无权限' }
        },

      ]
    },


  ]
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  userStore.init() 
  const token = userStore.userInfo?.token
  const userPerms = userStore.userInfo?.permissions || []

  // 登录页逻辑
  if (to.path === '/login') {
    if (token) {
      next('/home')
    } else {
      next()
    }
    return
  }

  // 未登录，跳转到登录页
  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  // 页面权限拦截
  const requiredPerm = to.meta.perm
  if (requiredPerm && !userPerms.includes(requiredPerm)) {
    ElMessage.warning('您暂无访问权限，请联系管理员授权')
    return next('/403')
  }

  next()
})
export default router
