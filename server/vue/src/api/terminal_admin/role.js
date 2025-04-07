import request from '@/utils/request'

// 获取角色分页列表
export function getRoleList(page = 1, size = 6) {
  return request.get('/role/list', {
    params: { page, size }
  })
}

// 所有角色
export function getAllRoles() {
    return request.get('/role/all')
  }
  
// 新增角色
export function addRole(data) {
  return request.post('/role/add', data)
}

// 编辑角色
export function updateRole(data) {
  return request.post('/role/update', data)
}

// 启用/禁用
export function updateRoleStatus(data) {
  return request.post('/role/status', data)
}

// 删除角色
export function deleteRole(data) {
  return request.post('/role/delete', data)
}
