import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.resetModules()
  })

  it('defaults to dark when nothing stored', async () => {
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('dark')
  })

  it('reads stored light theme', async () => {
    localStorage.setItem('ccd-theme', 'light')
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('light')
  })

  it('reads stored warm theme', async () => {
    localStorage.setItem('ccd-theme', 'warm')
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('warm')
  })

  it('falls back to dark when stored value is invalid', async () => {
    localStorage.setItem('ccd-theme', 'neon')
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('dark')
  })

  it('applies data-theme on init', async () => {
    await import('./useTheme')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('setTheme updates value, persists, and applies data-theme', async () => {
    const { useTheme } = await import('./useTheme')
    const { theme, setTheme } = useTheme()
    setTheme('warm')
    expect(theme.value).toBe('warm')
    expect(localStorage.getItem('ccd-theme')).toBe('warm')
    expect(document.documentElement.getAttribute('data-theme')).toBe('warm')
  })

  it('shares one state across multiple useTheme() calls', async () => {
    const { useTheme } = await import('./useTheme')
    const a = useTheme()
    const b = useTheme()
    a.setTheme('light')
    expect(b.theme.value).toBe('light')
  })

  it('loadThemeFor(userId) reads from user-scoped key', async () => {
    localStorage.setItem('ccd-theme:7', 'warm')
    const { useTheme } = await import('./useTheme')
    const { theme, loadThemeFor } = useTheme()
    loadThemeFor('7')
    expect(theme.value).toBe('warm')
  })

  it('setTheme after loadThemeFor writes user-scoped key', async () => {
    const { useTheme } = await import('./useTheme')
    const { setTheme, loadThemeFor } = useTheme()
    loadThemeFor('7')
    setTheme('light')
    expect(localStorage.getItem('ccd-theme:7')).toBe('light')
    expect(localStorage.getItem('ccd-theme')).toBeNull()
  })

  it('loadThemeFor(null) falls back to global key', async () => {
    localStorage.setItem('ccd-theme', 'light')
    const { useTheme } = await import('./useTheme')
    const { theme, loadThemeFor } = useTheme()
    loadThemeFor('7') // 切到用户键（无值→默认 dark）
    loadThemeFor(null)
    expect(theme.value).toBe('light')
  })
})
