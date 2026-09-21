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

/**
 * 压缩图片 — 限制最长边 + 质量，降低上传大小
 * @param {string} src 原始图片路径
 * @param {number} maxSide 最长边 px（菜品图建议 1080，头像建议 512）
 * @param {number} quality 压缩质量 0-100
 */
function compressImage(src, maxSide = 1080, quality = 75) {
  return new Promise((resolve, reject) => {
    // uni.compressImage H5 端部分浏览器不支持，做能力检测
    if (typeof uni.compressImage !== 'function') return resolve(src)
    // #ifdef MP-WEIXIN || APP-PLUS
    uni.getImageInfo({
      src,
      success(info) {
        const long = Math.max(info.width, info.height)
        const ratio = long > maxSide ? maxSide / long : 1
        const targetWidth = Math.round(info.width * ratio)
        const targetHeight = Math.round(info.height * ratio)
        uni.compressImage({
          src,
          quality,
          width: targetWidth,
          height: targetHeight,
          success(res) { resolve(res.tempFilePath || src) },
          fail() { resolve(src) }
        })
      },
      fail() { resolve(src) }
    })
    // #endif
    // #ifdef H5
    // H5 端 quality 在 chooseImage 时已生效，compressImage 兼容性差，直接使用原图
    resolve(src)
    // #endif
  })
}

/**
 * 上传图片（自动压缩后上传）
 * @param {string} filePath 原始图片路径
 * @param {{maxSide?: number, quality?: number}} opts 压缩参数
 */
export async function uploadImage(filePath, opts = {}) {
  const { maxSide = 1080, quality = 75 } = opts
  const compressed = await compressImage(filePath, maxSide, quality)
  return new Promise((resolve, reject) => {
    uni.uploadFile({
      url: `${apiBase()}/api/uploads`, filePath: compressed, name: 'file',
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
