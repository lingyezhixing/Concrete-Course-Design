import { describe, it, expect, beforeEach, vi } from 'vitest'

const { login, register, fetchMe } = vi.hoisted(() => ({
  login: vi.fn(),
  register: vi.fn(),
  fetchMe: vi.fn(),
}))
vi.mock('../api/auth', () => ({ login, register, fetchMe }))

const { loadThemeFor, loadSidebarFor } = vi.hoisted(() => ({
  loadThemeFor: vi.fn(),
  loadSidebarFor: vi.fn(),
}))
vi.mock('./useTheme', () => ({ useTheme: () => ({ loadThemeFor }) }))
vi.mock('./useSidebar', () => ({ useSidebar: () => ({ loadSidebarFor }) }))

describe('useAuth', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
    login.mockReset()
    register.mockReset()
    fetchMe.mockReset()
    loadThemeFor.mockReset()
    loadSidebarFor.mockReset()
  })

  it('starts unauthenticated', async () => {
    const { useAuth } = await import('./useAuth')
    const { isAuthenticated, currentUser } = useAuth()
    expect(isAuthenticated.value).toBe(false)
    expect(currentUser.value).toBeNull()
  })

  it('login stores token+user and loads prefs for user', async () => {
    login.mockResolvedValue({
      access_token: 'tok',
      token_type: 'bearer',
      expires_in: 604800,
      user: { id: 7, username: 'alice', created_at: 'now' },
    })
    const { useAuth } = await import('./useAuth')
    const { login: doLogin, currentUser, token } = useAuth()
    await doLogin('alice', 'secret1')
    expect(currentUser.value?.username).toBe('alice')
    expect(token.value).toBe('tok')
    expect(localStorage.getItem('ccd-token')).toBe('tok')
    expect(loadThemeFor).toHaveBeenCalledWith('7')
    expect(loadSidebarFor).toHaveBeenCalledWith('7')
  })

  it('register also establishes a session', async () => {
    register.mockResolvedValue({
      access_token: 'tok2',
      token_type: 'bearer',
      expires_in: 604800,
      user: { id: 8, username: 'bob', created_at: 'now' },
    })
    const { useAuth } = await import('./useAuth')
    const { register: doRegister, isAuthenticated } = useAuth()
    await doRegister('bob', 'secret1')
    expect(isAuthenticated.value).toBe(true)
    expect(localStorage.getItem('ccd-token')).toBe('tok2')
  })

  it('logout clears state and reverts prefs to global', async () => {
    const { useAuth } = await import('./useAuth')
    const { logout, token, currentUser } = useAuth()
    token.value = 'tok'
    currentUser.value = { id: 7, username: 'alice', created_at: 'now' }
    localStorage.setItem('ccd-token', 'tok')
    localStorage.setItem('ccd-user', JSON.stringify({ id: 7 }))
    logout()
    expect(token.value).toBeNull()
    expect(currentUser.value).toBeNull()
    expect(localStorage.getItem('ccd-token')).toBeNull()
    expect(loadThemeFor).toHaveBeenLastCalledWith(null)
    expect(loadSidebarFor).toHaveBeenLastCalledWith(null)
  })

  it('bootstrap with cached user restores session synchronously', async () => {
    localStorage.setItem('ccd-token', 'tok')
    localStorage.setItem(
      'ccd-user',
      JSON.stringify({ id: 7, username: 'alice', created_at: 'now' }),
    )
    fetchMe.mockResolvedValue({ id: 7, username: 'alice', created_at: 'now' })
    const { useAuth } = await import('./useAuth')
    const { bootstrap, currentUser } = useAuth()
    await bootstrap()
    expect(currentUser.value?.username).toBe('alice')
    expect(loadThemeFor).toHaveBeenCalledWith('7')
  })

  it('bootstrap with invalid token clears session', async () => {
    localStorage.setItem('ccd-token', 'stale')
    localStorage.setItem(
      'ccd-user',
      JSON.stringify({ id: 7, username: 'alice', created_at: 'now' }),
    )
    fetchMe.mockRejectedValue(new Error('401'))
    const { useAuth } = await import('./useAuth')
    const { bootstrap, isAuthenticated } = useAuth()
    await bootstrap()
    expect(isAuthenticated.value).toBe(false)
    expect(localStorage.getItem('ccd-token')).toBeNull()
  })
})
