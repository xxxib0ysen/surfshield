import request from '@/utils/request'

// 获取系统操作日志
export function getOperationLogList(params) {
  return request({
    url: '/log/operation/list',
    method: 'get',
    params
  })
}

// 获取模块
export const getModuleList = () => {
  return request({
    url: '/log/operation/module',
    method: 'get'
  })
}
