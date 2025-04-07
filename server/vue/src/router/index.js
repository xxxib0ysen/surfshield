import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/layout/Layout.vue'
import Home from '@/views/Home.vue'
import WebsiteControl from '@/views/control/WebsiteControl.vue'
import ProcessControl from '@/views/control/ProcessControl.vue'
import Login from '@/views/Login.vue'
import Admin from '@/views/terminal_admin/Admin.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      component: Login
    },
    {
      path:'/',
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
          path: '/management/admin',
          name: Admin,
          component: Admin,
          meta: { requiresAuth: true }
        },
      ]
    },
    
  ]
})

router.beforeEach((to, from , next)=>{
  const token = localStorage.getItem('token')
  if(to.path==='/login') {
    if(token) {
      next('/home')
    } else {
      next()
    }
  } else if (to.meta.requiresAuth && !token) {
    next('login')
  } else {
    next()
  }
})
export default router
