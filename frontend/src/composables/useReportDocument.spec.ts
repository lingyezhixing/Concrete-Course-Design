import { describe, it, expect } from 'vitest'
import { buildReportDoc, buildBasicInfo, buildSlab, num } from './useReportDocument'
import { emptyProjectData } from '../api/projects'
import type { ProjectData } from '../api/projects'

/** 构造带参数的最小 fixture（构件 result 在后续任务补） */
function fixture(): ProjectData {
  const d = emptyProjectData()
  Object.assign(d.structure, {
    L1: 18, L2: 30, slab_thickness: 80,
    beam_width: 200, beam_height: 400,
    main_beam_width: 250, main_beam_height: 500, column_width: 350,
    slab_spans: 9, beam_spans: 3, main_beam_spans: 3,
    beam_stirrup_diameter: 6, main_beam_stirrup_diameter: 8,
  })
  Object.assign(d.loads, {
    reinforced_concrete_weight: 25, terrazzo_surface: 0.65,
    plaster_thickness: 15, plaster_weight: 17, live_load: 4,
  })
  d.slab.result = {
    load: { terrazzo: 0.65, concrete: 2.0, plaster: 0.255,
      dead_load_standard: 2.905, dead_load_design: 3.0975,
      live_load_standard: 4, live_load_design: 4.8 },
    span: { middle_span: 2.0, edge_span: 1.92 },
    converted: { converted_dead: 5.4975, converted_live: 2.4 },
    internal_forces: {
      moments: [{ name: 'M1', value: 2.468 }, { name: 'MB', value: -3.315 }],
      shears: [{ name: 'VA', value: 5.765 }, { name: 'VB左', value: -8.579 }],
    },
    reinforcement: { sections: [{
      name: '1', moment: 2.468, h0: 55, alpha_s: 0.102, xi: 0.108,
      as_required: 210.8, selected_bar: { diameter: 8, spacing: 200 }, as_provided: 251, status: 'ok',
    }] },
  }
  d.slab.initialized = true
  d.report = { name: '张三' }
  return d
}

describe('num', () => {
  it('保留小数，空值返回 —', () => {
    expect(num(3.1415, 2)).toBe('3.14')
    expect(num(null)).toBe('—')
    expect(num(NaN)).toBe('—')
  })
})

describe('buildBasicInfo', () => {
  it('产出平面尺寸公式行', () => {
    const blocks = buildBasicInfo(fixture())
    const texts = blocks.map((b) => (b.kind === 'formula' ? b.text : ''))
    expect(texts.some((t) => t.includes('L1 = 18.00 m，L2 = 30.00 m'))).toBe(true)
  })
})

describe('buildReportDoc', () => {
  it('封面来自 data.report', () => {
    const doc = buildReportDoc(fixture())
    expect(doc.cover.name).toBe('张三')
  })
  it('现有项目缺 report 字段时封面为空对象', () => {
    const d = fixture()
    delete (d as Partial<ProjectData>).report
    expect(buildReportDoc(d).cover).toEqual({})
  })
  it('至少含基本资料、布置两章', () => {
    const doc = buildReportDoc(fixture())
    const titles = doc.sections.map((s) => s.title)
    expect(titles).toContain('设计基本资料')
    expect(titles).toContain('结构平面布置及构件截面尺寸初估')
  })
})

describe('buildSlab', () => {
  it('含荷载/折算/跨度公式与配筋表', () => {
    const blocks = buildSlab(fixture())
    const formulas = blocks.filter((b) => b.kind === 'formula').map((b) => (b as { text: string }).text)
    expect(formulas.some((t) => t.includes('g = γG·gₖ'))).toBe(true)
    expect(formulas.some((t) => t.includes("g' = g + q/2"))).toBe(true)
    const tables = blocks.filter((b) => b.kind === 'table') as Array<{ headers: string[]; rows: (string | number)[][] }>
    expect(tables.some((t) => t.headers.includes('选筋'))).toBe(true)
  })
  it('未计算时给出 warn 提示', () => {
    const d = fixture()
    d.slab.initialized = false
    const blocks = buildSlab(d)
    expect(blocks.some((b) => b.kind === 'note')).toBe(true)
  })
})
