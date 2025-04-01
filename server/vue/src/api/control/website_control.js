import request from '@/utils/request'

// 获取所有网站类型
export function getWebsiteType() {
  return request({
    url: '/website_control/type',
    method: 'get'
  })
}

// 添加网站类型
export function addWebsiteType(type_name) {
  return request({
    url: '/website_control/type/add',
    method: 'post',
    data: {
      type_name
    }
  })
}

// 删除网站类型
export function deleteWebsiteType(type_id) {
  return request({
    url: '/website_control/type/delete',
    method: 'post',
    data: {
      type_id
    }
  })
}

// 修改网站类型状态（启用/禁用）
export function updateWebsiteTypeStatus(type_id, status) {
  return request({
    url: '/website_control/type/updateStatus',
    method: 'post',
    data: {
      type_id,
      status
    }
  })
}

// 获取所有网站规则（按类型分组）
export function getWebsiteRule() {
  return request({
    url: '/website_control/listGrouped',
    method: 'get'
  })
}

// 添加网站访问规则
export function addWebsiteRule(data) {
  return request({
    url: '/website_control/add',
    method: 'post',
    data
  })
}

// 删除网站规则
export function deleteWebsiteRule(website_id) {
  return request({
    url: '/website_control/delete',
    method: 'post',
    data: {
      website_id
    }
  })
}

// 启用/禁用网站规则
export function updateWebsiteStatus(website_id, status) {
  return request({
    url: '/website_control/updateStatus',
    method: 'post',
    data: {
      website_id,
      status
    }
  })
}
