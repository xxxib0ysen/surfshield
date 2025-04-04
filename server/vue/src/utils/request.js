import axios from 'axios'

// 创建 axios 实例
const service = axios.create({
  baseURL: 'http://localhost:8000', 
  timeout: 5000
})

service.interceptors.request.use((config)=>{
  const token = localStorage.getItem('token')
  if(token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default service
