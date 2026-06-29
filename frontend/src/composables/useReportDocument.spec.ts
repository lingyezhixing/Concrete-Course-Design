import { describe, it, expect } from 'vitest'
import {
  buildReportDoc, buildBasicInfo, buildSlab, buildBeam, buildMainBeam,
  buildReinfSummary, buildConstructionNotes, buildResistingMoment, num,
} from './useReportDocument'
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
  d.beam.result = {
    load: { from_slab_dead: 5.81, self_weight: 1.6, plaster: 0.163,
      dead_load_standard: 7.583, dead_load_design: 7.962,
      live_load_standard: 8, live_load_design: 9.6 },
    span: { middle_span: 6.0, edge_span: 5.88 },
    converted: { converted_dead: 10.362, converted_live: 7.2 },
    internal_forces: {
      moments: [{ name: 'M1', value: 52.874 }, { name: 'MB', value: -70.013 }],
      shears: [{ name: 'VA', value: 41.141 }, { name: 'VB左', value: -60.539 }],
    },
    reinforcement: {
      flexure: [{ name: '1', section_type: 'T形(第一类)', width_used: 1960, moment: 52.874,
        h0: 360, alpha_s: 0.026, xi: 0.0264, as_required: 661.5,
        selected_bar: { count: 3, diameter: 18 }, as_provided: 763, status: 'ok' }],
      shear: { max_shear: 60.539, vc: 55.44, asv_s: 0.177,
        recommended_spacing: 200, stirrup_ratio: 0.0014 },
    },
  }
  d.beam.initialized = true
  d.main_beam.result = {
    load: { from_beam_dead: 45.498, self_weight: 5.25, plaster: 0.4284,
      dead_load_standard: 51.1764, dead_load_design: 53.7352,
      live_load_standard: 48, live_load_design: 57.6 },
    internal_forces: { M1_max: 166.7, M2_max: 87.99, M_B_min: -178.3, M_C_min: 0,
      VA_max: 89.544, VBl_min: -143.259, VBr_max: 124.005 },
    reinforcement: {
      flexure: [{ name: '边跨中', section_type: 'T形(第一类)', width_used: 1977.5, moment: 166.7,
        h0: 460, alpha_s: 0.0498, xi: 0.0511, as_required: 1652.9,
        selected_bar: { count: 4, diameter: 25 }, as_provided: 1964, status: 'ok' }],
      shear: { max_shear: 143.259, vc: 88.55, asv_s: 0.001,
        recommended_spacing: 150, stirrup_ratio: 0.00268, hanger_area: 331 },
    },
  }
  d.main_beam.initialized = true
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
  it('含荷载逐项推导与折算公式', () => {
    const blocks = buildSlab(fixture())
    const formulas = blocks.filter((b) => b.kind === 'formula').map((b) => (b as { text: string }).text)
    expect(formulas.some((t) => t.includes('恒载标准值 gₖ ='))).toBe(true)
    expect(formulas.some((t) => t.includes('g = γG · gₖ'))).toBe(true)
    expect(formulas.some((t) => t.includes("g' = g + q/2"))).toBe(true)
    const tables = blocks.filter((b) => b.kind === 'table') as Array<{ headers: string[]; rows: (string | number)[][] }>
    expect(tables.some((t) => t.headers.includes('选筋'))).toBe(true)
  })
  it('含正截面公式代入与配筋率验算', () => {
    const blocks = buildSlab(fixture())
    const formulas = blocks.filter((b) => b.kind === 'formula').map((b) => (b as { text: string }).text)
    expect(formulas.some((t) => t.includes('配筋率验算：ρ ='))).toBe(true)
  })
  it('未计算时给出 warn 提示', () => {
    const d = fixture()
    d.slab.initialized = false
    const blocks = buildSlab(d)
    expect(blocks.some((b) => b.kind === 'note')).toBe(true)
  })
})

describe('buildBeam', () => {
  it('含荷载逐项推导、折算荷载 q/4 与斜截面公式', () => {
    const blocks = buildBeam(fixture())
    const formulas = blocks.filter((b) => b.kind === 'formula').map((b) => (b as { text: string }).text)
    expect(formulas.some((t) => t.includes("g' = g + q/4"))).toBe(true)
    expect(formulas.some((t) => t.includes('0.7·ft·b·h₀'))).toBe(true)
    expect(formulas.some((t) => t.includes('配筋率验算：ρ ='))).toBe(true)
  })
})

describe('buildMainBeam', () => {
  it('含荷载逐项推导、配筋验算与吊筋公式', () => {
    const blocks = buildMainBeam(fixture())
    const formulas = blocks.filter((b) => b.kind === 'formula').map((b) => (b as { text: string }).text)
    expect(formulas.some((t) => t.includes('G = γG · Gk'))).toBe(true)
    expect(formulas.some((t) => t.includes('吊筋 Asb'))).toBe(true)
    expect(formulas.some((t) => t.includes('配筋率验算：ρ ='))).toBe(true)
    const tables = blocks.filter((b) => b.kind === 'table') as Array<{ headers: string[] }>
    expect(tables.some((t) => t.headers.includes('M1 (kN·m)'))).toBe(true)
  })
})

describe('收尾三章', () => {
  it('配筋汇总合并三构件', () => {
    const blocks = buildReinfSummary(fixture())
    const tables = blocks.filter((b) => b.kind === 'table') as Array<{ rows: (string | number)[][] }>
    expect(tables[0].rows.some((r) => String(r[0]).startsWith('次梁·'))).toBe(true)
    expect(tables[0].rows.some((r) => String(r[0]).startsWith('主梁·'))).toBe(true)
    expect(tables[0].rows.some((r) => String(r[0]).startsWith('板·'))).toBe(true)
  })
  it('构造措施含箍筋直径', () => {
    const blocks = buildConstructionNotes(fixture())
    const formulas = blocks.filter((b) => b.kind === 'formula').map((b) => (b as { text: string }).text)
    expect(formulas.some((t) => t.includes('6 mm（次梁）'))).toBe(true)
  })
  it('抵抗弯矩章含 resistingMoment 图块', () => {
    const blocks = buildResistingMoment(fixture())
    expect(blocks.some((b) => b.kind === 'figure' && (b as { figure: string }).figure === 'resistingMoment')).toBe(true)
  })
  it('buildReportDoc 共 8 章', () => {
    expect(buildReportDoc(fixture()).sections.length).toBe(8)
  })
})
