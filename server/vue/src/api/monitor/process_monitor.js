import request from '@/utils/request'

export function getProcessList(terminalId) {
  return request({
    url: '/monitor/process_monitor',
    method: 'get',
    params: { terminal_id: terminalId }
  })
}
