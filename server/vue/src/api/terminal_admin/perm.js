import request from '@/utils/request'

// 获取全部权限列表
export function getAllPermissions() {
    return request.get('/permission/list')
}

// 获取按模块分组的权限列表
export function getGroupedPermissions() {
    return request.get('/permission/grouped')
}

// 获取指定角色绑定的权限 ID 列表
export function getPermissionsByRole(roleId) {
    return request.get(`/permission/role/${roleId}`)
}

// 保存角色权限绑定
export function bindPermissions(data) {
    return request.post('/permission/bind', data)
}
