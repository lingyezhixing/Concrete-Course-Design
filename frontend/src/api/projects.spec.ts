import { describe, it, expect } from 'vitest'
import { emptyProjectData } from './projects'

describe('emptyProjectData', () => {
  it('包含空封面对象 report', () => {
    const d = emptyProjectData()
    expect(d.report).toEqual({})
  })
  it('三构件状态默认未初始化', () => {
    const d = emptyProjectData()
    expect(d.slab.initialized).toBe(false)
    expect(d.beam.initialized).toBe(false)
    expect(d.main_beam.initialized).toBe(false)
  })
})
