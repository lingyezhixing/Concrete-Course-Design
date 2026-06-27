import { describe, it, expect, beforeEach } from 'vitest'
import { useTheme } from './useTheme'

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('defaults to dark when nothing stored', () => {
    const { isDark } = useTheme()
    expect(isDark.value).toBe(true)
  })

  it('reads stored light theme', () => {
    localStorage.setItem('ccd-theme', 'light')
    const { isDark } = useTheme()
    expect(isDark.value).toBe(false)
  })

  it('applies html.dark class on init', () => {
    useTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('toggle flips value, persists, and toggles html class', () => {
    const { isDark, toggle } = useTheme()
    expect(isDark.value).toBe(true)

    toggle()
    expect(isDark.value).toBe(false)
    expect(localStorage.getItem('ccd-theme')).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    toggle()
    expect(isDark.value).toBe(true)
    expect(localStorage.getItem('ccd-theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
