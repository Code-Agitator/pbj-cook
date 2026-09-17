import { afterEach, describe, expect, it, vi } from 'vitest'

function installUni({ request, uploadFile } = {}) {
  const storage = new Map()
  globalThis.uni = {
    getStorageSync: vi.fn((key) => storage.get(key)),
    setStorageSync: vi.fn((key, value) => storage.set(key, value)),
    removeStorageSync: vi.fn((key) => storage.delete(key)),
    reLaunch: vi.fn(),
    request: request || vi.fn(),
    uploadFile: uploadFile || vi.fn(),
    showLoading: vi.fn(),
    hideLoading: vi.fn(),
    showToast: vi.fn(),
  }
  return storage
}

async function loadClient(options) {
  vi.resetModules()
  const storage = installUni(options)
  return { storage, ...(await import('./client')) }
}

afterEach(() => {
  vi.unstubAllGlobals()
  delete globalThis.uni
})

describe('API client server configuration', () => {
  it('normalizes valid stored server addresses and falls back for invalid values', async () => {
    const { apiBase, setApiBase, storage } = await loadClient()
    storage.set('dacook_api_base', ' https://cook.example.test/api/ ')
    expect(apiBase()).toBe('https://cook.example.test/api')
    expect(setApiBase('http://127.0.0.1:8100/')).toBe(true)
    expect(storage.get('dacook_api_base')).toBe('http://127.0.0.1:8100')
    expect(setApiBase('ftp://invalid')).toBe(false)
    expect(storage.get('dacook_api_base')).toBe('http://127.0.0.1:8100')
    storage.set('dacook_api_base', 'not a server')
    expect(apiBase()).toBe('http://127.0.0.1:8000')
  })
})

describe('API client authorization lifecycle', () => {
  it('clears the session and redirects only once for unauthorized requests', async () => {
    const request = vi.fn(({ success }) => success({ statusCode: 401, data: { detail: '登录已过期' } }))
    const { clearSession, request: sendRequest, setSession } = await loadClient({ request })
    setSession({ token: 'old-token', user: { id: 'u1' } })

    await expect(sendRequest('/api/me')).rejects.toMatchObject({ message: '登录已过期', status: 401 })
    await expect(sendRequest('/api/me')).rejects.toMatchObject({ status: 401 })
    expect(uni.reLaunch).toHaveBeenCalledTimes(1)
    expect(uni.removeStorageSync).toHaveBeenCalledWith('dacook_token')
    clearSession()

    setSession({ token: 'new-token', user: { id: 'u1' } })
    await expect(sendRequest('/api/me')).rejects.toMatchObject({ status: 401 })
    expect(uni.reLaunch).toHaveBeenCalledTimes(2)
  })

  it('can reject an unauthorized public request without redirecting', async () => {
    const request = vi.fn(({ success }) => success({ statusCode: 401, data: { detail: '未授权' } }))
    const { request: sendRequest } = await loadClient({ request })
    await expect(sendRequest('/api/bootstrap', { redirectOnUnauthorized: false })).rejects.toMatchObject({ status: 401 })
    expect(uni.reLaunch).not.toHaveBeenCalled()
  })
})

describe('image uploads', () => {
  it('rejects malformed JSON with an Error instance', async () => {
    const uploadFile = vi.fn(({ success }) => success({ statusCode: 500, data: '{' }))
    const { uploadImage } = await loadClient({ uploadFile })
    await expect(uploadImage('/tmp/photo.jpg')).rejects.toThrow('上传响应格式不正确')
  })

  it('preserves an upload backend error message', async () => {
    const uploadFile = vi.fn(({ success }) => success({ statusCode: 413, data: '{"detail":"图片太大"}' }))
    const { uploadImage } = await loadClient({ uploadFile })
    await expect(uploadImage('/tmp/photo.jpg')).rejects.toMatchObject({ message: '图片太大', status: 413 })
  })
})

describe('run', () => {
  it('always clears the loading state after an action failure', async () => {
    const { run } = await loadClient()
    await expect(run(() => Promise.reject(new Error('保存失败')))).rejects.toThrow('保存失败')
    expect(uni.hideLoading).toHaveBeenCalledTimes(1)
  })
})
