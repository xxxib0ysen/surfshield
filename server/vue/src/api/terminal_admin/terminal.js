import request from '@/utils/request'

// 获取终端列表
export function getTerminalList(params) {
  return request({
    url: '/terminal/list',
    method: 'get',
    params
  })
}

// 获取单个终端详情
export function getTerminalDetail(id) {
  return request({
    url: `/terminal/detail/${id}`,
    method: 'get'
  })
}

// 批量移动终端到分组
export function moveTerminalToGroup(data) {
  return request({
    url: '/terminal/move_group',
    method: 'post',
    data
  })
}

// 获取终端分组
export function getTerminalGroups() {
  return request({
    url: '/group/tree',
    method: 'get'
  })
}

// 获取自定义列
export function getTerminalColumns() {
  return request({
    url: '/terminal/columns',
    method: 'get'
  })
}