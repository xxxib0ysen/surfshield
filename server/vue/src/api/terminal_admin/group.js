import request from '@/utils/request'

export const getGroupTree = () => request.get('/group/tree')
export const getGroupDetail = (id) => request.get(`/group/list/${id}`)
export const addGroup = (data) => request.post('/group/add', data)
export const updateGroup = (id, data) => request.put(`/group/edit/${id}`, data)
export const deleteGroup = (id) => request.delete(`/group/delete/${id}`)
