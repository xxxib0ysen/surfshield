import request from '@/utils/request'

// 查询终端列表
export function getTerminalList(params) {
    return request.get('/terminal/list', { params })
}

// 获取终端详情
export function getTerminalDetail(terminalId) {
    return request.get(`/terminal/detail/${terminalId}`)
}

// 获取自定义列字段
export function getTerminalColumns() {
    return request.get('/terminal/columns')
}

// 批量移动终端到分组
export function moveTerminalToGroup(data) {
    return request.post('/terminal/move_group', data)
}

// 获取终端状态统计
export function getTerminalStatusCount() {
    return request.get('/terminal/status-count')
  }
  
  // 获取操作系统分布
  export function getTerminalOSDistribution() {
    return request.get('/terminal/os-distribution')
  }