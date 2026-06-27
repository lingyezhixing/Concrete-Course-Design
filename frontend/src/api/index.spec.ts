import { describe, it, expect, vi, beforeEach } from 'vitest'

const holders = vi.hoisted(() => ({
  requestInterceptor: null as ((c: any) => any) | null,
  responseError: null as ((e: any) => any) | null,
}))

vi.mock('axios', () => ({
  default: {
    create: () => ({
      get: vi.fn(),
      post: vi.fn(),
      interceptors: {
        request: { use: (fn: any) => { holders.requestInterceptor = fn } },
        response: { use: (_s: any, fn: any) => { holders.responseError = fn } },
      },
    }),
  },
}))

import './index'

describe('api interceptors', () => {
  beforeEach(() => {
    localStorage.clear()
    Object.defineProperty(window, 'location', {
      writable: true,
      value: { href: '', pathname: '/' },
    })
  })

  it('injects Bearer header when token present', () => {
    localStorage.setItem('ccd-token', 'abc')
    const cfg = holders.requestInterceptor!({ headers: {} })
    expect(cfg.headers.Authorization).toBe('Bearer abc')
  })

  it('omits Authorization when no token', () => {
    const cfg = holders.requestInterceptor!({ headers: {} })
    expect(cfg.headers.Authorization).toBeUndefined()
  })

  it('on 401 from non-auth endpoint clears session', async () => {
    localStorage.setItem('ccd-token', 'abc')
    localStorage.setItem('ccd-user', '{}')
    await expect(
      holders.responseError!({ response: { status: 401 }, config: { url: '/health' } }),
    ).rejects.toBeDefined()
    expect(localStorage.getItem('ccd-token')).toBeNull()
    expect(localStorage.getItem('ccd-user')).toBeNull()
  })

  it('on 401 from /auth/ endpoint does NOT clear', async () => {
    localStorage.setItem('ccd-token', 'abc')
    await expect(
      holders.responseError!({ response: { status: 401 }, config: { url: '/auth/login' } }),
    ).rejects.toBeDefined()
    expect(localStorage.getItem('ccd-token')).toBe('abc')
  })

  it('on 500 does not clear', async () => {
    localStorage.setItem('ccd-token', 'abc')
    await expect(
      holders.responseError!({ response: { status: 500 }, config: { url: '/health' } }),
    ).rejects.toBeDefined()
    expect(localStorage.getItem('ccd-token')).toBe('abc')
  })
})
