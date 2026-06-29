// 计算书装配器（纯函数）：ProjectData → ReportDoc。
// 只读 data（含手改），不重算。公式推导用 Unicode 富文本。
// figure 用 figureKind + props，不引 .vue，保持可测。
// 结果字段名以后端 *FullResult 为准（见 Slab/SecondaryBeam/MainBeam.vue）。
//
// 类型与助手按章节任务增量引入（构件 result 类型 / table / note / *Of / figure
// 分别在板/次梁/主梁章节任务中加入），以通过 vue-tsc 的 noUnusedLocals。

import type {
  ReportBlock, ReportDoc, ReportSection, TableBlock, FigureBlock,
} from '../report/types'
import { GAMMA_G, GAMMA_Q } from '../report/materials'
import type { ProjectData } from '../api/projects'

// ── 选筋类型（被 slabBarText/beamBarText 引用；构件章节会复用） ──
interface SlabBar { diameter: number; spacing: number }
interface BeamBar { count: number; diameter: number }

// ── 板结果类型（镜像后端 SlabFullResult） ──
interface NamedValue { name: string; value: number }
interface SlabReinfSection {
  name: string; moment: number; h0: number; alpha_s: number; xi: number
  as_required: number; selected_bar: SlabBar | null; as_provided: number; status: string
}
interface SlabResult {
  load: { terrazzo: number; concrete: number; plaster: number
    dead_load_standard: number; dead_load_design: number
    live_load_standard: number; live_load_design: number }
  span: { middle_span: number; edge_span: number }
  converted: { converted_dead: number; converted_live: number }
  internal_forces: { moments: NamedValue[]; shears: NamedValue[] }
  reinforcement: { sections: SlabReinfSection[] }
}

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
const note = (text: string, tone: 'info' | 'warn' = 'info'): ReportBlock =>
  ({ kind: 'note', text, tone })
const table = (
  caption: string | undefined, headers: string[], rows: (string | number)[][],
): TableBlock => ({ kind: 'table', caption, headers, rows })
const figure = (
  caption: string, f: FigureBlock['figure'], props: Record<string, unknown>,
): FigureBlock => ({ kind: 'figure', caption, figure: f, props })

// ── 安全读取 result（未计算时给空对象） ──
function slabOf(d: ProjectData): SlabResult {
  return (d?.slab?.result ?? {}) as unknown as SlabResult
}

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

/** 三、板设计 */
export function buildSlab(d: ProjectData): ReportBlock[] {
  const s = d.structure
  const r = slabOf(d)
  const ld = r.load ?? ({} as SlabResult['load'])
  const cv = r.converted ?? ({} as SlabResult['converted'])
  const sp = r.span ?? ({} as SlabResult['span'])
  const out: ReportBlock[] = [h2('板设计')]
  if (!d.slab?.initialized) {
    out.push(note('板尚未计算，本章略。', 'warn'))
    return out
  }
  // 荷载
  out.push(h3('荷载计算（取 1 米板带）'))
  out.push(formula(`水磨石面层：${num(ld.terrazzo)} kN/m²；钢筋混凝土板：${num(ld.concrete)} kN/m²；板底抹灰：${num(ld.plaster)} kN/m²`))
  out.push(formula(`恒载标准值 gₖ = ${num(ld.dead_load_standard)} kN/m²；恒载设计值 g = γG·gₖ = ${GAMMA_G}×${num(ld.dead_load_standard)} = ${num(ld.dead_load_design)} kN/m²`))
  out.push(formula(`活载标准值 qₖ = ${num(ld.live_load_standard)} kN/m²；活载设计值 q = γQ·qₖ = ${GAMMA_Q}×${num(ld.live_load_standard)} = ${num(ld.live_load_design)} kN/m²`))
  out.push(formula(`折算荷载：g' = g + q/2 = ${num(cv.converted_dead)} kN/m；q' = q/2 = ${num(cv.converted_live)} kN/m`))
  // 计算跨度
  out.push(h3('计算跨度'))
  out.push(formula(`边跨 l₀ = ${num(sp.edge_span)} m；中间跨 l₀ = ${num(sp.middle_span)} m`))
  // 计算简图
  out.push(figure('图：板计算简图', 'uniformBeam', {
    rawSpans: s.slab_spans ?? 0, edgeSpan: sp.edge_span, midSpan: sp.middle_span,
    loadDead: cv.converted_dead, loadLive: cv.converted_live,
    sectionType: 'slab', sectionSize: { h: s.slab_thickness ?? 0 },
  }))
  // 内力表
  out.push(h3('内力计算'))
  out.push(table('表：板弯矩 M（kN·m/m）', ['截面', '弯矩值'],
    (r.internal_forces?.moments ?? []).map((m) => [m.name, num(m.value, 3)])))
  out.push(table('表：板剪力 V（kN/m）', ['截面', '剪力值'],
    (r.internal_forces?.shears ?? []).map((v) => [v.name, num(v.value, 3)])))
  out.push(figure('图：板弯矩图 / 剪力图', 'internalForce', {
    moments: r.internal_forces?.moments ?? [], shears: r.internal_forces?.shears ?? [],
    rawSpans: s.slab_spans ?? 0, edgeSpan: sp.edge_span, midSpan: sp.middle_span,
  }))
  // 配筋
  out.push(h3('截面强度及配筋计算'))
  out.push(table('表：板正截面强度及配筋计算',
    ['截面', 'M (kN·m/m)', 'h0 (mm)', 'αs', 'ξ', 'As需 (mm²)', '选筋', 'As实 (mm²)'],
    (r.reinforcement?.sections ?? []).map((c) => [
      c.name, num(c.moment, 3), num(c.h0, 0), num(c.alpha_s, 4), num(c.xi, 4),
      Math.round(c.as_required), slabBarText(c.selected_bar), Math.round(c.as_provided),
    ])))
  out.push(figure('图：板截面配筋简图', 'sectionRebar', {
    sections: (r.reinforcement?.sections ?? []).map((c) => ({
      name: c.name, shape: 'slab', b: 1000, h: s.slab_thickness ?? 0,
      bar: { diameter: c.selected_bar?.diameter ?? 0, spacing: c.selected_bar?.spacing ?? 0 },
    })),
  }))
  return out
}

// ── 装配入口（本任务含前三章；后续任务追加构件章节） ──
export function buildReportDoc(d: ProjectData): ReportDoc {
  const sections: ReportSection[] = [
    { id: 'basic', number: '一', title: '设计基本资料', blocks: buildBasicInfo(d) },
    { id: 'layout', number: '二', title: '结构平面布置及构件截面尺寸初估', blocks: buildLayoutAndSize(d) },
    { id: 'slab', number: '三', title: '板设计', blocks: buildSlab(d) },
  ]
  return { cover: d.report ?? {}, sections }
}
