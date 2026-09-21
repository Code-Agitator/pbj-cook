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
 * 压缩等级预设
 */
const COMPRESS_PRESETS = {
  // 缩略图级别：~20-80 KB
  thumbnail: { maxSide: 400, quality: 60 },
  // 菜品展示图：~150-400 KB（最大宽度 1024px）
  dish: { maxSide: 1024, quality: 70 },
  // 头像：~30-80 KB
  avatar: { maxSide: 300, quality: 65 },
  // 高质量展示：~200-500 KB
  high: { maxSide: 1080, quality: 75 },
}

/**
 * 压缩图片 — 限制最长边 + 质量，降低上传大小
 * @param {string} src 原始图片路径
 * @param {number} maxSide 最长边 px（菜品图建议 600，头像建议 200）
 * @param {number} quality 压缩质量 0-100
 */
function compressImage(src, maxSide = 720, quality = 70) {
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
 * Canvas 压缩 — 跨平台通用方案，压缩率更高
 * @param {string} src 原始图片路径
 * @param {number} maxSide 最长边 px
 * @param {number} quality 压缩质量 0-100
 * @param {string} format 输出格式 'jpeg' | 'webp'
 */
function canvasCompress(src, maxSide = 720, quality = 70, format = 'jpeg') {
  return new Promise((resolve, reject) => {
    // #ifdef H5
    const img = new Image()
    img.crossOrigin = 'anonymous'
    img.onload = () => {
      const long = Math.max(img.width, img.height)
      const ratio = long > maxSide ? maxSide / long : 1
      const width = Math.round(img.width * ratio)
      const height = Math.round(img.height * ratio)

      const canvas = document.createElement('canvas')
      canvas.width = width
      canvas.height = height
      const ctx = canvas.getContext('2d')
      ctx.drawImage(img, 0, 0, width, height)

      const mimeType = format === 'webp' ? 'image/webp' : 'image/jpeg'
      const dataUrl = canvas.toDataURL(mimeType, quality / 100)
      resolve(dataUrl)
    }
    img.onerror = () => resolve(src)
    img.src = src
    // #endif
    // #ifndef H5
    // 非 H5 端使用原生压缩
    resolve(src)
    // #endif
  })
}

/**
 * 上传图片（自动压缩后上传）
 * @param {string} filePath 原始图片路径
 * @param {Object} opts 压缩参数
 * @param {number} opts.maxSide 最长边 px（默认 600）
 * @param {number} opts.quality 压缩质量 0-100（默认 60）
 * @param {string} opts.preset 预设等级 'thumbnail'|'dish'|'avatar'|'high'
 * @param {boolean} opts.useCanvas 是否使用 Canvas 压缩（H5 端更有效）
 */
export async function uploadImage(filePath, opts = {}) {
  const { preset, useCanvas = true, ...restOpts } = opts

  // 如果有预设，使用预设参数
  const compressOpts = preset && COMPRESS_PRESETS[preset]
    ? COMPRESS_PRESETS[preset]
    : { maxSide: 720, quality: 70, ...restOpts }

  let compressed = filePath

  // H5 端使用 Canvas 压缩（压缩率更高）
  // #ifdef H5
  if (useCanvas && typeof document !== 'undefined') {
    compressed = await canvasCompress(filePath, compressOpts.maxSide, compressOpts.quality)
  }
  // #endif

  // 非 H5 端使用原生压缩
  // #ifndef H5
  compressed = await compressImage(filePath, compressOpts.maxSide, compressOpts.quality)
  // #endif

  // 如果是 dataURL（Canvas 产出），转为 Blob 上传
  if (compressed.startsWith('data:')) {
    return uploadDataURL(compressed)
  }

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

/**
 * 上传 Canvas 生成的 DataURL
 * @param {string} dataURL base64 图片数据
 */
function uploadDataURL(dataURL) {
  return new Promise((resolve, reject) => {
    // 将 DataURL 转为 Blob
    const byteString = atob(dataURL.split(',')[1])
    const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0]
    const ab = new ArrayBuffer(byteString.length)
    const ia = new Uint8Array(ab)
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i)
    }
    const blob = new Blob([ab], { type: mimeString })

    // 创建 FormData 上传
    const formData = new FormData()
    formData.append('file', blob, 'image.jpg')

    // 使用 fetch API 发送，让浏览器自动处理 boundary
    fetch(`${apiBase()}/api/uploads`, {
      method: 'POST',
      body: formData,
      headers: {
        Authorization: `Bearer ${token()}`,
        // 不手动设置 content-type，让浏览器自动添加 boundary
      },
    })
      .then(async (response) => {
        let body
        try {
          body = await response.json()
        } catch {
          reject(new Error('上传响应格式不正确'))
          return
        }

        if (response.ok) return resolve(body)
        if (response.status === 401) redirectAfterUnauthorized()
        const error = new Error(body?.detail || '上传失败')
        error.status = response.status
        reject(error)
      })
      .catch((error) => reject(errorFrom(error, '无法连接服务器')))
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
