import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/components/layout/Layout.vue'
import Home from '@/views/Home.vue'
import WebsiteControl from '@/views/control/WebsiteControl.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path:'/',
      redirect: '/home',
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
      ]
    },
    
  ]
})

export default router
