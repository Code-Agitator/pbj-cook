import { normalizeApiBase } from '../utils/app'

const DEFAULT_BASE = import.meta.env.VITE_API_BASE ?? ''
let unauthorizedRedirected = false

function errorFrom(value, fallback) {
  if (value instanceof Error) return value
  return new Error(value?.errMsg || value?.message || fallback)
}

function redirectAfterUnauthorized(options = {}) {
  clearSession()
  if (options.redirectOnUnauthorized === false || unauthorizedRedirected) return

  unauthorizedRedirected = true
  uni.reLaunch({ url: '/pages/login/index' })
}

export const apiBase = () => normalizeApiBase(uni.getStorageSync('dacook_api_base')) || DEFAULT_BASE
export const token = () => uni.getStorageSync('dacook_token') || ''
export const currentUser = () => uni.getStorageSync('dacook_user') || null
export const assetUrl = (path) => path ? `${apiBase()}${path.startsWith('/') ? '' : '/uploads/'}${path}` : ''

export function setApiBase(value) {
  const normalized = normalizeApiBase(value)
  if (!normalized) return false

  try {
    uni.setStorageSync('dacook_api_base', normalized)
    return true
  } catch {
    return false
  }
}

export function setSession(data) {
  uni.setStorageSync('dacook_token', data.token)
  uni.setStorageSync('dacook_user', data.user)
  unauthorizedRedirected = false
}

export function clearSession() {
  uni.removeStorageSync('dacook_token')
  uni.removeStorageSync('dacook_user')
}

export function request(path, options = {}) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${apiBase()}${path}`,
      method: options.method || 'GET',
      data: options.data,
      header: {
        'content-type': 'application/json',
        ...(token() ? { Authorization: `Bearer ${token()}` } : {}),
        ...(options.header || {})
      },
      success(res) {
        try {
          if (res.statusCode >= 200 && res.statusCode < 300) return resolve(res.data)
          if (res.statusCode === 401) redirectAfterUnauthorized(options)
          const error = new Error(res.data?.detail || '请求失败')
          error.status = res.statusCode
          reject(error)
        } catch (error) {
          reject(errorFrom(error, '请求失败'))
        }
      },
      fail(error) { reject(errorFrom(error, '无法连接服务器')) }
    })
  })
}

export const bootstrap = (options = {}) => request('/api/bootstrap', options)

export function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${apiBase()}/api/uploads`, filePath, name: 'file',
      header: { Authorization: `Bearer ${token()}` },
      success(res) {
        try {
          let body
          try {
            body = JSON.parse(res.data || '{}')
          } catch {
            reject(new Error('上传响应格式不正确'))
            return
          }

          if (res.statusCode >= 200 && res.statusCode < 300) return resolve(body)
          if (res.statusCode === 401) redirectAfterUnauthorized()
          const error = new Error(body?.detail || '上传失败')
          error.status = res.statusCode
          reject(error)
        } catch (error) {
          reject(errorFrom(error, '上传失败'))
        }
      },
      fail(error) { reject(errorFrom(error, '无法连接服务器')) }
    })
  })
}

export async function run(action, success = '') {
  try {
    uni.showLoading({ title: '请稍候', mask: true })
    const result = await action()
    if (success) uni.showToast({ title: success, icon: 'success' })
    return result
  } catch (error) {
    try {
      uni.showToast({ title: error.message || '操作失败', icon: 'none' })
    } catch {}
    throw error
  } finally { uni.hideLoading() }
}
