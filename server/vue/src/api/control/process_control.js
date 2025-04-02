import request from '@/utils/request'

// 添加单个进程
export function addSingleProcess(data) {
  return request({
    url: '/process/add_single',
    method: 'post',
    data: data
  })
}

// 批量添加进程
export function addBatchProcess(data) {
  return request({
    url: '/process/add_batch',
    method: 'post',
    data: data
  })
}

// 删除单个规则
export function deleteSingleProcess(data) {
  return request({
    url: '/process/delete_single',
    method: 'post',
    data: data
  })
}

// 批量删除规则
export function deleteBatchProcess(data) {
  return request({
    url: '/process/delete_batch',
    method: 'post',
    data: data
  })
}

// 启用/禁用规则
export function toggleProcessStatus(data) {
  return request({
    url: '/process/toggle',
    method: 'post',
    data: data
  })
}

// 获取进程规则列表
export function getProcessList() {
  return request({
    url: '/process/list',
    method: 'get'
  })
}
