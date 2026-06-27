import { describe, it, expect, beforeEach } from 'vitest'
import { useSidebar } from './useSidebar'

describe('useSidebar', () => {
  beforeEach(() => localStorage.clear())

  it('defaults to expanded', () => {
    const { isCollapsed } = useSidebar()
    expect(isCollapsed.value).toBe(false)
  })

  it('reads stored collapsed state', () => {
    localStorage.setItem('ccd-sidebar', 'collapsed')
    const { isCollapsed } = useSidebar()
    expect(isCollapsed.value).toBe(true)
  })

  it('toggle flips and persists', () => {
    const { isCollapsed, toggle } = useSidebar()
    toggle()
    expect(isCollapsed.value).toBe(true)
    expect(localStorage.getItem('ccd-sidebar')).toBe('collapsed')
    toggle()
    expect(isCollapsed.value).toBe(false)
    expect(localStorage.getItem('ccd-sidebar')).toBe('expanded')
  })
})
