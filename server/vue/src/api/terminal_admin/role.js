import request from '@/utils/request'


// 所有角色
export function getAllRoles() {
    return request.get('/role/list')
}

// 获取单个角色详情
export function getRoleDetail(role_id) {
    return request.get('/role/detail', {
        params: { role_id }
    })
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
