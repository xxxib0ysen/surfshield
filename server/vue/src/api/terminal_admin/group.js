import request from '@/utils/request'

export const getGroupTree = () => request.get('/group/tree')
export const getGroupDetail = (id) => request.get(`/group/list/${id}`)
export const addGroup = (data) => request.post('/group/add', data)
export const updateGroup = (id, data) => request.put(`/group/edit/${id}`, data)
export const deleteGroup = (id) => request.delete(`/group/delete/${id}`)
export const getGroupUserTree = () => request.get('/group/user-tree')

// 邀请码
// 邀请码列表
export const getInviteList = () => request.get('/group/invite/list')
// 新增邀请码
export const addInvite = (data) => request.post('/group/invite/add', data)
// 编辑邀请码
export const updateInvite = (id, data) => request.put(`/group/invite/edit/${id}`, data)
// 删除邀请码
export const deleteInvite = (id) => request.delete(`/group/invite/delete/${id}`)