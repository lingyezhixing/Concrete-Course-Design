import { describe, it, expect } from 'vitest'
import { FC, FT, FY_SLAB, FY_BEAM, FYV, GAMMA_D, GAMMA_G, GAMMA_Q } from './materials'

describe('materials constants', () => {
  it('镜像后端 materials.py 取值', () => {
    expect(FC).toBe(9.6)
    expect(FT).toBe(1.1)
    expect(FY_SLAB).toBe(270)
    expect(FY_BEAM).toBe(300)
    expect(FYV).toBe(270)
    expect(GAMMA_D).toBe(1.2)
    expect(GAMMA_G).toBe(1.05)
    expect(GAMMA_Q).toBe(1.2)
  })
})
