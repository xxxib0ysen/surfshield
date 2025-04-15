import request from '@/utils/request'

export function getProcessList(terminalId) {
  return request({
    url: '/monitor/process_monitor',
    method: 'get',
    params: { terminal_id: terminalId }
  })
}

export const postKillProcess = (data) => {
    return request.post('/client/kill_process', data)
}