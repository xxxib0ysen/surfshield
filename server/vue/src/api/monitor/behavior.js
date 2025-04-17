import request from '@/utils/request'

export const getWebBehavior = (username) => {
  return request.get('/behavior/web', { params: { username } })
}

export const getSearchBehavior = (username) => {
  return request.get('/behavior/search', { params: { username } })
}


export const getTerminalUserList = () => {
  return request.get('/behavior/userlist')
}
