import axios from 'axios'
import router from '@/router'
import { useUserStore } from '@/stores/useUserStore'

// 创建 axios 实例
const service = axios.create({
  baseURL: 'http://localhost:8000', 
  timeout: 5000
})

// 请求前加 token
service.interceptors.request.use((config) => {
  const store = useUserStore()
  if (store.token) {
    config.headers.Authorization = `Bearer ${store.token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截：处理 token 失效
service.interceptors.response.use(
  response => response,
  err => {
    if(err.response?.status === 401) {
      const store = useUserStore()
      store.logout()
      router.push('/login')
    }
    return Promise.reject(err)
  }
)
export default service
