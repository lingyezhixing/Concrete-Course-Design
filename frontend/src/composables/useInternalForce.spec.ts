import { describe, expect, it } from 'vitest'

import { layoutInternalForce } from './useInternalForce'

/** 造 NamedValue 数组 */
const nv = (vals: number[]) => vals.map((v, i) => ({ name: `s${i}`, value: v }))

// 3 跨测试数据：moments 长度 5（2n−1）、shears 长度 6（2n）
const M3 = nv([10, -15, 8, -12, 9])
const V3 = nv([5, -6, 7, -5, 6, -4])
const args3 = { moments: M3, shears: V3, rawSpans: 3, edgeSpan: 2, midSpan: 2 }

describe('layoutInternalForce', () => {
  it('3 跨：eqSpans + 支座/跨数', () => {
    const r = layoutInternalForce(args3)
    expect(r?.eqSpans).toBe(3)
    expect(r?.supportXs.length).toBe(4) // eqSpans + 1
    expect(r?.moment.spans.length).toBe(3)
    expect(r?.shear.spans.length).toBe(3)
  })

  describe('弯矩解析', () => {
    it('端支座取 0、内部支座取正确值', () => {
      const s = layoutInternalForce(args3)!.moment.spans
      expect(s[0].left.m).toBe(0) // 端 A
      expect(s[0].mid.m).toBe(10) // 跨1中
      expect(s[0].right.m).toBe(-15) // 支座 B
      expect(s[1].left.m).toBe(-15) // 支座 B（同一支座两侧相等）
      expect(s[1].mid.m).toBe(8) // 跨2中
      expect(s[2].right.m).toBe(0) // 端 D
    })

    it('量程 mMax / mMin', () => {
      const r = layoutInternalForce(args3)!
      expect(r.moment.mMax).toBe(10)
      expect(r.moment.mMin).toBe(-15)
    })
  })

  describe('剪力解析', () => {
    it('每跨左右端取正确值', () => {
      const s = layoutInternalForce(args3)!.shear.spans
      expect(s[0].leftV).toBe(5) // VA
      expect(s[0].rightV).toBe(-6) // B 左
      expect(s[1].leftV).toBe(7) // B 右
      expect(s[1].rightV).toBe(-5) // C 左
      expect(s[2].rightV).toBe(-4) // 末端
    })

    it('量程 vMax / vMin', () => {
      const r = layoutInternalForce(args3)!
      expect(r.shear.vMax).toBe(7)
      expect(r.shear.vMin).toBe(-6)
    })
  })

  it('控制点 x 与支座 / 跨中对齐', () => {
    const r = layoutInternalForce(args3)!
    expect(r.moment.spans[0].left.x).toBeCloseTo(r.supportXs[0])
    expect(r.moment.spans[0].right.x).toBeCloseTo(r.supportXs[1])
    expect(r.shear.spans[0].leftX).toBeCloseTo(r.supportXs[0])
    expect(r.shear.spans[0].rightX).toBeCloseTo(r.supportXs[1])
  })

  it('>5 跨等效为 5（moments 9 / shears 10）', () => {
    const r = layoutInternalForce({
      moments: nv([1, 2, 3, 4, 5, 6, 7, 8, 9]),
      shears: nv([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
      rawSpans: 9,
      edgeSpan: 2,
      midSpan: 2,
    })
    expect(r?.eqSpans).toBe(5)
    expect(r?.moment.spans.length).toBe(5)
    expect(r?.shear.spans.length).toBe(5)
  })

  describe('非法输入返回 null', () => {
    it('跨数 < 2', () => {
      expect(layoutInternalForce({ ...args3, rawSpans: 1 })).toBeNull()
    })
    it('跨度 ≤ 0', () => {
      expect(layoutInternalForce({ ...args3, edgeSpan: 0 })).toBeNull()
      expect(layoutInternalForce({ ...args3, midSpan: -1 })).toBeNull()
    })
    it('moments / shears 为空', () => {
      expect(layoutInternalForce({ ...args3, moments: [] })).toBeNull()
      expect(layoutInternalForce({ ...args3, shears: [] })).toBeNull()
    })
  })
})
