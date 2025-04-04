import request from '@/utils/request'

export function login(username, password) {
  const formData = new URLSearchParams()
  formData.append('username', username)
  formData.append('password', password)

  return request({
    url: '/login',
    method: 'post',
    data: formData
  })
}

// 获取当前登录用户信息
export function getCurrentUser() {
    return request({
      url: '/user/me',
      method: 'get'
    })
  }