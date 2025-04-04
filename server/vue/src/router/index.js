import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/layout/Layout.vue'
import Home from '@/views/Home.vue'
import WebsiteControl from '@/views/control/WebsiteControl.vue'
import ProcessControl from '@/views/control/ProcessControl.vue'
import Login from '@/views/Login.vue'

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
          component: Home
        },
        {
          path: '/policy/website',
          name: WebsiteControl,
          component: WebsiteControl
        },
        {
          path: '/policy/process',
          name: ProcessControl,
          component: ProcessControl
        },
      ]
    },
    
  ]
})

export default router
