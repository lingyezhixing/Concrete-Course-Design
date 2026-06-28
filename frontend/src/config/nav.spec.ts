import { describe, it, expect } from 'vitest'
import { NAV_ITEMS } from './nav'

describe('nav config', () => {
  it('has 6 items', () => {
    expect(NAV_ITEMS).toHaveLength(6)
  })

  it('every item has path, title, and icon', () => {
    for (const item of NAV_ITEMS) {
      expect(typeof item.path).toBe('string')
      expect(item.path.length).toBeGreaterThan(0)
      expect(typeof item.title).toBe('string')
      expect(item.title.length).toBeGreaterThan(0)
      expect(item.icon).toBeTruthy()
    }
  })

  it('paths are unique', () => {
    const paths = NAV_ITEMS.map((i) => i.path)
    expect(new Set(paths).size).toBe(paths.length)
  })

  it('contains overview at "/"', () => {
    expect(NAV_ITEMS.some((i) => i.path === '/')).toBe(true)
  })

  it('contains params and archive', () => {
    expect(NAV_ITEMS.some((i) => i.path === '/params')).toBe(true)
    expect(NAV_ITEMS.some((i) => i.path === '/archive')).toBe(true)
  })

  it('does not contain deferred beam pages or old materials', () => {
    expect(NAV_ITEMS.some((i) => i.path === '/secondary-beam')).toBe(false)
    expect(NAV_ITEMS.some((i) => i.path === '/main-beam')).toBe(false)
    expect(NAV_ITEMS.some((i) => i.path === '/materials')).toBe(false)
    expect(NAV_ITEMS.some((i) => i.path === '/column')).toBe(false)
  })
})
