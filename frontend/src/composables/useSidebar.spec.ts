import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('useSidebar', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetModules()
  })

  it('defaults to expanded', async () => {
    const { useSidebar } = await import('./useSidebar')
    const { isCollapsed } = useSidebar()
    expect(isCollapsed.value).toBe(false)
  })

  it('reads stored collapsed state', async () => {
    localStorage.setItem('ccd-sidebar', 'collapsed')
    const { useSidebar } = await import('./useSidebar')
    const { isCollapsed } = useSidebar()
    expect(isCollapsed.value).toBe(true)
  })

  it('toggle flips and persists', async () => {
    const { useSidebar } = await import('./useSidebar')
    const { isCollapsed, toggle } = useSidebar()
    toggle()
    expect(isCollapsed.value).toBe(true)
    expect(localStorage.getItem('ccd-sidebar')).toBe('collapsed')
  })

  it('loadSidebarFor(userId) reads user-scoped key', async () => {
    localStorage.setItem('ccd-sidebar:7', 'collapsed')
    const { useSidebar } = await import('./useSidebar')
    const { isCollapsed, loadSidebarFor } = useSidebar()
    loadSidebarFor('7')
    expect(isCollapsed.value).toBe(true)
  })

  it('toggle after loadSidebarFor writes user-scoped key', async () => {
    const { useSidebar } = await import('./useSidebar')
    const { toggle, loadSidebarFor } = useSidebar()
    loadSidebarFor('7') // 无值 → expanded(false)
    toggle() // → collapsed(true)
    expect(localStorage.getItem('ccd-sidebar:7')).toBe('collapsed')
    expect(localStorage.getItem('ccd-sidebar')).toBeNull()
  })

  it('loadSidebarFor(null) falls back to global key', async () => {
    localStorage.setItem('ccd-sidebar', 'collapsed')
    const { useSidebar } = await import('./useSidebar')
    const { isCollapsed, loadSidebarFor } = useSidebar()
    loadSidebarFor('7')
    loadSidebarFor(null)
    expect(isCollapsed.value).toBe(true)
  })
})
