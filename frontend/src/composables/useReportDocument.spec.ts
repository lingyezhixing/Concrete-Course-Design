import { describe, it, expect } from 'vitest'
import { buildReportDoc, buildBasicInfo, num } from './useReportDocument'
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
