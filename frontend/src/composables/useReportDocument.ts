// 计算书装配器（纯函数）：ProjectData → ReportDoc。
// 只读 data（含手改），不重算。公式推导用 Unicode 富文本。
// figure 用 figureKind + props，不引 .vue，保持可测。
// 结果字段名以后端 *FullResult 为准（见 Slab/SecondaryBeam/MainBeam.vue）。
//
// 类型与助手按章节任务增量引入（构件 result 类型 / table / note / *Of / figure
// 分别在板/次梁/主梁章节任务中加入），以通过 vue-tsc 的 noUnusedLocals。

import type {
  ReportBlock, ReportDoc, ReportSection,
} from '../report/types'
import { GAMMA_G, GAMMA_Q } from '../report/materials'
import type { ProjectData } from '../api/projects'

// ── 选筋类型（被 slabBarText/beamBarText 引用；构件章节会复用） ──
interface SlabBar { diameter: number; spacing: number }
interface BeamBar { count: number; diameter: number }

// ── 格式化助手 ──
/** 保留 d 位小数；空/非有限值返回 —。 */
export function num(n: number | null | undefined, d = 2): string {
  if (n == null || !Number.isFinite(n)) return '—'
  return Number(n).toFixed(d)
}
/** 板选筋文字。 */
export function slabBarText(b: SlabBar | null): string {
  return b ? `Φ${b.diameter}@${b.spacing}` : '—'
}
/** 梁选筋文字。 */
export function beamBarText(b: BeamBar | null): string {
  return b ? `${b.count}Φ${b.diameter}` : '—'
}

// ── 块构造捷径 ──
const h2 = (text: string): ReportBlock => ({ kind: 'heading', level: 2, text })
const h3 = (text: string): ReportBlock => ({ kind: 'heading', level: 3, text })
const para = (text: string): ReportBlock => ({ kind: 'paragraph', text })
const formula = (text: string): ReportBlock => ({ kind: 'formula', text })

// ══════════════════════════════════════════════
// 章节装配
// ══════════════════════════════════════════════

/** 一、设计基本资料 */
export function buildBasicInfo(d: ProjectData): ReportBlock[] {
  const s = d.structure, l = d.loads
  const out: ReportBlock[] = [h2('设计基本资料')]
  out.push(h3('楼层平面与构件尺寸'))
  out.push(formula(`L1 = ${num(s.L1)} m，L2 = ${num(s.L2)} m`))
  out.push(formula(`板厚 ${num(s.slab_thickness, 0)} mm；次梁 ${num(s.beam_width, 0)}×${num(s.beam_height, 0)} mm；主梁 ${num(s.main_beam_width, 0)}×${num(s.main_beam_height, 0)} mm；柱 ${num(s.column_width, 0)}×${num(s.column_width, 0)} mm`))
  out.push(formula(`板跨数 ${num(s.slab_spans, 0)}，次梁跨数 ${num(s.beam_spans, 0)}，主梁跨数 ${num(s.main_beam_spans, 0)}`))
  out.push(h3('工程条件'))
  out.push(para('建筑位于非地震区；结构安全级别为二级；结构环境类别为一类。'))
  out.push(h3('材料等级'))
  out.push(formula('混凝土：梁、板 C20（fc = 9.6 N/mm²，ft = 1.10 N/mm²）'))
  out.push(formula('板受力筋/箍筋/构造筋 HPB300（fy = 270 N/mm²）；梁纵筋 HRB335（fy = 300 N/mm²）'))
  out.push(formula(`结构系数 γd = 1.2；恒载分项系数 γG = ${GAMMA_G}；活载分项系数 γQ = ${GAMMA_Q}`))
  out.push(h3('荷载资料'))
  out.push(formula(`钢筋混凝土重度 ${num(l.reinforced_concrete_weight)} kN/m³；水磨石面层 ${num(l.terrazzo_surface)} kN/m²`))
  out.push(formula(`石灰砂浆抹面厚度 ${num(l.plaster_thickness, 0)} mm、重度 ${num(l.plaster_weight)} kN/m³；楼面活荷载 ${num(l.live_load)} kN/m²`))
  return out
}

/** 二、结构平面布置及构件截面尺寸初估 */
export function buildLayoutAndSize(d: ProjectData): ReportBlock[] {
  const s = d.structure
  const out: ReportBlock[] = [h2('结构平面布置及构件截面尺寸初估')]
  out.push(para('采用主梁纵向、次梁横向布置。板为单向板，荷载传递路径：板 → 次梁 → 主梁 → 柱。'))
  out.push(h3('构件截面尺寸初估'))
  out.push(formula(`板厚 h = ${num(s.slab_thickness, 0)} mm（搁置长度 120 mm）`))
  const beamLn = s.beam_spans ? (s.L1 ?? 0) / s.beam_spans : 0
  out.push(formula(`次梁：跨度 ${num(beamLn)} m，h = ${num(s.beam_height, 0)} mm，b = ${num(s.beam_width, 0)} mm（校核范围 h ≈ L/18~1/12）`))
  const mbLn = s.main_beam_spans ? (s.L2 ?? 0) / s.main_beam_spans : 0
  out.push(formula(`主梁：跨度 ${num(mbLn)} m，h = ${num(s.main_beam_height, 0)} mm，b = ${num(s.main_beam_width, 0)} mm（校核范围 h ≈ L/15~1/10）`))
  out.push(formula(`柱：${num(s.column_width, 0)}×${num(s.column_width, 0)} mm`))
  return out
}

// ── 装配入口（本任务只含前两章；后续任务追加构件章节） ──
export function buildReportDoc(d: ProjectData): ReportDoc {
  const sections: ReportSection[] = [
    { id: 'basic', number: '一', title: '设计基本资料', blocks: buildBasicInfo(d) },
    { id: 'layout', number: '二', title: '结构平面布置及构件截面尺寸初估', blocks: buildLayoutAndSize(d) },
  ]
  return { cover: d.report ?? {}, sections }
}
