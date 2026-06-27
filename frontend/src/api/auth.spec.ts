import { describe, it, expect, vi, beforeEach } from 'vitest'

const { post, get } = vi.hoisted(() => ({ post: vi.fn(), get: vi.fn() }))
vi.mock('./index', () => ({ default: { post, get } }))

import { register, login, fetchMe } from './auth'

describe('auth api', () => {
  beforeEach(() => {
    post.mockReset()
    get.mockReset()
  })

  it('register posts /auth/register and returns data', async () => {
    post.mockResolvedValue({ data: { access_token: 't', user: { id: 1 } } })
    const res = await register('alice', 'secret1')
    expect(post).toHaveBeenCalledWith('/auth/register', {
      username: 'alice',
      password: 'secret1',
    })
    expect(res.access_token).toBe('t')
  })

  it('login posts /auth/login', async () => {
    post.mockResolvedValue({ data: { access_token: 't2' } })
    await login('bob', 'secret1')
    expect(post).toHaveBeenCalledWith('/auth/login', {
      username: 'bob',
      password: 'secret1',
    })
  })

  it('fetchMe gets /auth/me', async () => {
    get.mockResolvedValue({ data: { id: 1, username: 'alice' } })
    const res = await fetchMe()
    expect(get).toHaveBeenCalledWith('/auth/me')
    expect(res.username).toBe('alice')
  })
})
