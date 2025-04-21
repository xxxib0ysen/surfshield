import request from '@/utils/request' 

// 获取管理员列表
export function getAdminList(params) {
  return request({
    url: '/admin/list',
    method: 'get',
    params
  })
}

// 获取所有管理员名称
export function getAdminNameList() {
  return request({
    url: '/admin/list-name',
    method: 'get'
  })
}


// 新增管理员
export function addAdmin(data) {
  return request({
    url: '/admin/add',
    method: 'post',
    data
  })
}

// 编辑管理员
export function updateAdmin(id, data) {
  return request({
    url: `/admin/update/${id}`,
    method: 'put',
    data
  })
}

// 修改管理员启用状态
export function updateStatus(id, status) {
  return request({
    url: `/admin/status/${id}`,
    method: 'put',
    data: { status }
  })
}

// 重置管理员密码
export function resetPassword(id) {
  return request({
    url: `/admin/reset_password/${id}`,
    method: 'put'
  })
}

// 删除管理员
export function deleteAdmin(id) {
  return request({
    url: `/admin/delete/${id}`,
    method: 'delete'
  })
}

// 修改密码
export function changePassword(data) {
  return request({
    url: '/admin/change_password',
    method: 'put',
    data
  })
}
