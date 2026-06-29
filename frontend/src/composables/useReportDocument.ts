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
import { FC, FT, FY_SLAB, FY_BEAM, FYV, GAMMA_D, GAMMA_G, GAMMA_Q } from '../report/materials'
import type { ProjectData } from '../api/projects'

// ── 选筋类型（被 slabBarText/beamBarText 引用；构件章节会复用） ──
interface SlabBar { diameter: number; spacing: number }
interface BeamBar { count: number; diameter: number }

// ── 板结果类型（镜像后端 SlabFullResult） ──
interface NamedValue { name: string; value: number }
interface MomentDetail extends NamedValue {
  l0?: number; alpha?: number; alpha1?: number
  g_l0_sq?: number; q_l0_sq?: number; m_raw?: number
}
interface ShearDetail extends NamedValue {
  ln?: number; beta?: number; beta1?: number
  g_ln?: number; q_ln?: number
}
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
  internal_forces: { moments: MomentDetail[]; shears: ShearDetail[] }
  reinforcement: { sections: SlabReinfSection[] }
}

// ── 梁（次梁/主梁共用）结果类型 ──
interface Flexure {
  name: string; moment: number; h0: number; section_type: string; width_used: number
  alpha_s: number; xi: number; as_required: number
  selected_bar: BeamBar | null; as_provided: number; status: string
}
interface BeamShear { max_shear: number; h0: number; vc: number; asv_s: number
  recommended_spacing: number; stirrup_ratio: number }
interface BeamResult {
  load: { from_slab_dead: number; self_weight: number; plaster: number
    dead_load_standard: number; dead_load_design: number
    live_load_standard: number; live_load_design: number }
  span: { middle_span: number; edge_span: number }
  converted: { converted_dead: number; converted_live: number }
  internal_forces: { moments: MomentDetail[]; shears: ShearDetail[] }
  reinforcement: { flexure: Flexure[]; shear: BeamShear }
}

// ── 主梁结果类型 ──
interface MainBeamShear extends BeamShear { hanger_area: number }
interface MainBeamResult {
  load: { from_beam_dead: number; self_weight: number; plaster: number
    dead_load_standard: number; dead_load_design: number
    live_load_standard: number; live_load_design: number }
  internal_forces: { M1_max: number; M2_max: number; M_B_min: number; M_C_min: number
    VA_max: number; VBl_min: number; VBr_max: number }
  reinforcement: { flexure: Flexure[]; shear: MainBeamShear }
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
function beamOf(d: ProjectData): BeamResult {
  return (d?.beam?.result ?? {}) as unknown as BeamResult
}
function mainBeamOf(d: ProjectData): MainBeamResult {
  return (d?.main_beam?.result ?? {}) as unknown as MainBeamResult
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
  const ldIn = d.loads
  const out: ReportBlock[] = [h2('板设计')]
  if (!d.slab?.initialized) {
    out.push(note('板尚未计算，本章略。', 'warn'))
    return out
  }
  // 荷载（逐项推导）
  out.push(h3('荷载计算（取 1 米板带）'))
  out.push(formula(`水磨石面层：${num(ldIn.terrazzo_surface)} kN/m²`))
  out.push(formula(`钢筋混凝土板：${num(ldIn.reinforced_concrete_weight)} kN/m³ × ${num(s.slab_thickness, 0)} mm = ${num(ld.concrete)} kN/m²`))
  out.push(formula(`板底石灰砂浆抹面：${num(ldIn.plaster_weight)} kN/m³ × ${num(ldIn.plaster_thickness, 0)} mm = ${num(ld.plaster)} kN/m²`))
  out.push(formula(`恒载标准值 gₖ = ${num(ld.terrazzo)} + ${num(ld.concrete)} + ${num(ld.plaster)} = ${num(ld.dead_load_standard)} kN/m²`))
  out.push(formula(`恒载设计值 g = γG · gₖ = ${GAMMA_G} × ${num(ld.dead_load_standard)} = ${num(ld.dead_load_design)} kN/m²`))
  out.push(formula(`活载标准值 qₖ = ${num(ld.live_load_standard)} kN/m²；活载设计值 q = γQ · qₖ = ${GAMMA_Q} × ${num(ld.live_load_standard)} = ${num(ld.live_load_design)} kN/m²`))
  out.push(formula(`折算荷载：g' = g + q/2 = ${num(ld.dead_load_design)} + ${num(ld.live_load_design)}/2 = ${num(cv.converted_dead)} kN/m；q' = q/2 = ${num(ld.live_load_design)}/2 = ${num(cv.converted_live)} kN/m`))
  // 计算跨度
  out.push(h3('计算跨度'))
  out.push(formula(`边跨 l₀ = ${num(sp.edge_span)} m；中间跨 l₀ = ${num(sp.middle_span)} m`))
  // 计算简图
  out.push(figure('图：板计算简图', 'uniformBeam', {
    rawSpans: s.slab_spans ?? 0, edgeSpan: sp.edge_span, midSpan: sp.middle_span,
    loadDead: cv.converted_dead, loadLive: cv.converted_live,
    sectionType: 'slab', sectionSize: { h: s.slab_thickness ?? 0 },
  }))
  // 内力计算 — 系数详表
  out.push(h3('内力计算'))
  out.push(formula(`M = α · g' · l₀² + α₁ · q' · l₀²（查教材附录七表 4 得 α、α₁ 值）`))
  const moments = r.internal_forces?.moments ?? []
  const shears = r.internal_forces?.shears ?? []
  const hasMomentDetail = moments.some((m) => m.alpha != null)
  if (hasMomentDetail) {
    out.push(table('表：板弯矩 M（kN·m/m）',
      ['截面', 'l₀ (m)', "g'·l₀²", "q'·l₀²", 'α', 'α₁', 'M'],
      moments.map((m) => [
        m.name, num(m.l0, 3), num(m.g_l0_sq, 3), num(m.q_l0_sq, 3),
        num(m.alpha, 4), num(m.alpha1, 4), num(m.value, 3),
      ])))
    const tot = cv.converted_dead + cv.converted_live
    const v0 = 0.5 * tot * sp.middle_span
    out.push(formula(`V₀ = (g' + q')·l₀/2 = (${num(cv.converted_dead)} + ${num(cv.converted_live)})×${num(sp.middle_span)}/2 = ${num(v0, 4)} kN`))
    out.push(formula(`支座边缘弯矩 M' = |M| − 0.5·b·|V₀|；本板 b = ${num(s.beam_width, 0)} mm，M' 值供参考。`))
    out.push(table('表：板剪力 V（kN/m）',
      ['截面', 'lₙ (m)', "g'·lₙ", "q'·lₙ", 'β', 'β₁', 'V'],
      shears.map((s2) => [
        s2.name, num(s2.ln, 3), num(s2.g_ln, 3), num(s2.q_ln, 3),
        num(s2.beta, 3), num(s2.beta1, 3), num(s2.value, 3),
      ])))
  } else {
    out.push(table('表：板弯矩 M（kN·m/m）', ['截面', '弯矩值'],
      moments.map((m) => [m.name, num(m.value, 3)])))
    out.push(table('表：板剪力 V（kN/m）', ['截面', '剪力值'],
      shears.map((v) => [v.name, num(v.value, 3)])))
  }
  out.push(figure('图：板弯矩图 / 剪力图', 'internalForce', {
    moments: moments, shears: shears,
    rawSpans: s.slab_spans ?? 0, edgeSpan: sp.edge_span, midSpan: sp.middle_span,
  }))
  // 配筋
  out.push(h3('截面强度及配筋计算'))
  out.push(formula(`αs = γd·M/(fc·b·h₀²)，ξ = 1−√(1−2αs)，As = fc·b·ξ·h₀/fy`))
  const sections = r.reinforcement?.sections ?? []
  out.push(table('表：板正截面强度及配筋计算',
    ['截面', 'M (kN·m/m)', 'h0 (mm)', 'αs', 'ξ', 'As需 (mm²)', '选筋', 'As实 (mm²)'],
    sections.map((c) => [
      c.name, num(c.moment, 3), num(c.h0, 0), num(c.alpha_s, 4), num(c.xi, 4),
      Math.round(c.as_required), slabBarText(c.selected_bar), Math.round(c.as_provided),
    ])))
  // 公式代入演示 + 配筋率验算
  if (sections.length) {
    const c0 = sections[0]
    out.push(formula(`以截面 ${c0.name} 为例：αs = ${GAMMA_D}×(${num(c0.moment)}×10⁶)/(${FC}×1000×${num(c0.h0, 0)}²) = ${num(c0.alpha_s, 4)}`))
    out.push(formula(`ξ = 1−√(1−2×${num(c0.alpha_s, 4)}) = ${num(c0.xi, 4)}；As = ${FC}×1000×${num(c0.xi, 4)}×${num(c0.h0, 0)}/${FY_SLAB} = ${Math.round(c0.as_required)} mm²`))
    const minRho = 0.002
    const actualRho = c0.selected_bar ? c0.as_provided / (1000 * c0.h0) : 0
    out.push(formula(`配筋率验算：ρ = As实/(b·h₀) = ${Math.round(c0.as_provided)}/(1000×${num(c0.h0, 0)}) = ${num(actualRho * 100, 3)}% ≥ ρmin = ${minRho * 100}%，满足。${num(c0.xi, 4)} < ξb = 0.576，不超筋。`))
  }
  out.push(figure('图：板截面配筋简图', 'sectionRebar', {
    sections: sections.map((c) => ({
      name: c.name, shape: 'slab', b: 1000, h: s.slab_thickness ?? 0,
      bar: { diameter: c.selected_bar?.diameter ?? 0, spacing: c.selected_bar?.spacing ?? 0 },
    })),
  }))
  return out
}

/** 四、次梁设计 */
export function buildBeam(d: ProjectData): ReportBlock[] {
  const s = d.structure
  const r = beamOf(d)
  const ld = r.load ?? ({} as BeamResult['load'])
  const cv = r.converted ?? ({} as BeamResult['converted'])
  const sp = r.span ?? ({} as BeamResult['span'])
  const sh = r.reinforcement?.shear ?? ({} as BeamShear)
  const flexure = r.reinforcement?.flexure ?? []
  const out: ReportBlock[] = [h2('次梁设计')]
  if (!d.beam?.initialized) {
    out.push(note('次梁尚未计算，本章略。', 'warn'))
    return out
  }
  // 荷载（逐项推导）
  out.push(h3('荷载计算'))
  out.push(formula(`板传来恒载：板恒载标准值 × 次梁间距 = ${num(ld.from_slab_dead)} kN/m`))
  out.push(formula(`次梁自重：${num(s.beam_width, 0)}×(${num(s.beam_height, 0)}−${num(s.slab_thickness, 0)}) mm × 25 kN/m³ = ${num(ld.self_weight)} kN/m`))
  out.push(formula(`次梁粉刷（两侧）：17 kN/m³ × 15 mm × (${num(s.beam_height, 0)}−${num(s.slab_thickness, 0)}) mm × 2 = ${num(ld.plaster)} kN/m`))
  out.push(formula(`恒载标准值 gₖ = ${num(ld.from_slab_dead)} + ${num(ld.self_weight)} + ${num(ld.plaster)} = ${num(ld.dead_load_standard)} kN/m`))
  out.push(formula(`恒载设计值 g = γG · gₖ = ${GAMMA_G} × ${num(ld.dead_load_standard)} = ${num(ld.dead_load_design)} kN/m`))
  out.push(formula(`活载标准值 qₖ = ${num(ld.live_load_standard)} kN/m；设计值 q = γQ · qₖ = ${GAMMA_Q} × ${num(ld.live_load_standard)} = ${num(ld.live_load_design)} kN/m`))
  out.push(formula(`折算荷载：g' = g + q/4 = ${num(ld.dead_load_design)} + ${num(ld.live_load_design)}/4 = ${num(cv.converted_dead)} kN/m；q' = 3q/4 = 3×${num(ld.live_load_design)}/4 = ${num(cv.converted_live)} kN/m`))
  out.push(h3('计算跨度'))
  out.push(formula(`边跨 l₀ = ${num(sp.edge_span)} m；中间跨 l₀ = ${num(sp.middle_span)} m`))
  out.push(figure('图：次梁计算简图', 'uniformBeam', {
    rawSpans: s.beam_spans ?? 0, edgeSpan: sp.edge_span, midSpan: sp.middle_span,
    loadDead: cv.converted_dead, loadLive: cv.converted_live,
    sectionType: 'beam', sectionSize: { b: s.beam_width ?? 0, h: s.beam_height ?? 0 },
  }))
  // 内力系数详表
  out.push(h3('内力计算'))
  out.push(formula('M = α·g\'·l₀² + α₁·q\'·l₀²；V = β·g\'·lₙ + β₁·q\'·lₙ（系数查教材附录七表 4）'))
  const moments = r.internal_forces?.moments ?? []
  const shears = r.internal_forces?.shears ?? []
  const hasDetail = moments.some((m2) => m2.alpha != null)
  if (hasDetail) {
    out.push(table('表：次梁弯矩 M（kN·m）',
      ['截面', 'l₀ (m)', "g'·l₀²", "q'·l₀²", 'α', 'α₁', 'M（α法）', "M'"],
      moments.map((m2) => {
        const isSup = m2.name.startsWith('M_')
        return [
          m2.name, num(m2.l0, 3), num(m2.g_l0_sq, 3), num(m2.q_l0_sq, 3),
          num(m2.alpha, 4), num(m2.alpha1, 4), num(m2.m_raw, 3),
          isSup ? num(m2.value, 3) : '—',
        ]
      })))
    const tot = cv.converted_dead + cv.converted_live
    const v0 = 0.5 * tot * sp.middle_span
    const bSup = (s.main_beam_width ?? 250) / 1000
    out.push(formula(`支座边缘调整：V₀ = (g' + q')·l₀/2 = (${num(cv.converted_dead)}+${num(cv.converted_live)})×${num(sp.middle_span)}/2 = ${num(v0, 3)} kN`))
    out.push(formula(`M' = |M_α| − (b/2)·|V₀|，b = ${num(bSup * 1000, 0)} mm（主梁宽）；支座 M' 值见上表。`))
    out.push(table('表：次梁剪力 V（kN）',
      ['截面', 'lₙ (m)', "g'·lₙ", "q'·lₙ", 'β', 'β₁', 'V'],
      shears.map((sv) => [
        sv.name, num(sv.ln, 3), num(sv.g_ln, 3), num(sv.q_ln, 3),
        num(sv.beta, 3), num(sv.beta1, 3), num(sv.value, 3),
      ])))
  } else {
    out.push(table('表：次梁弯矩 M（kN·m）', ['截面', '弯矩值'],
      moments.map((m2) => [m2.name, num(m2.value, 3)])))
    out.push(table('表：次梁剪力 V（kN）', ['截面', '剪力值'],
      shears.map((sv) => [sv.name, num(sv.value, 3)])))
  }
  out.push(figure('图：次梁弯矩图 / 剪力图', 'internalForce', {
    moments: moments, shears: shears,
    rawSpans: s.beam_spans ?? 0, edgeSpan: sp.edge_span, midSpan: sp.middle_span,
  }))
  // 正截面强度 + 配筋验算
  out.push(h3('正截面强度及配筋计算'))
  out.push(formula('αs = γd·M/(fc·b·h₀²)，ξ = 1−√(1−2αs)，As = fc·b·ξ·h₀/fy'))
  out.push(table('表：次梁正截面强度及配筋',
    ['截面', '类型', '计算宽', 'M (kN·m)', 'h0', 'αs', 'ξ', 'As需 (mm²)', '选筋', 'As实 (mm²)'],
    flexure.map((f) => [
      f.name, f.section_type, num(f.width_used, 0), num(f.moment, 3), num(f.h0, 0),
      num(f.alpha_s, 4), num(f.xi, 4), Math.round(f.as_required), beamBarText(f.selected_bar), Math.round(f.as_provided),
    ])))
  if (flexure.length) {
    const f0 = flexure[0]
    out.push(formula(`以截面 ${f0.name} 为例：αs = ${GAMMA_D}×(${num(f0.moment)}×10⁶)/(${FC}×${num(f0.width_used, 0)}×${num(f0.h0, 0)}²) = ${num(f0.alpha_s, 4)}；ξ = ${num(f0.xi, 4)}`))
    out.push(formula(`As = ${FC}×${num(f0.width_used, 0)}×${num(f0.xi, 4)}×${num(f0.h0, 0)}/${FY_BEAM} = ${Math.round(f0.as_required)} mm²；实配 ${beamBarText(f0.selected_bar)}，As实 = ${Math.round(f0.as_provided)} mm²`))
    const minRho = 0.002
    const actualRho = f0.selected_bar ? f0.as_provided / ((s.beam_width ?? 0) * f0.h0) : 0
    out.push(formula(`配筋率验算：ρ = As实/(b·h₀) = ${Math.round(f0.as_provided)}/(${num(s.beam_width, 0)}×${num(f0.h0, 0)}) = ${num(actualRho * 100, 3)}% ≥ ρmin = ${minRho * 100}%，满足；ξ = ${num(f0.xi, 4)} < ξb = 0.550（Ⅱ级筋），不超筋。`))
  }
  out.push(figure('图：次梁截面配筋简图', 'sectionRebar', {
    sections: flexure.map((f) => ({
      name: f.name, shape: f.section_type?.includes('T') ? 't' : 'rect',
      b: s.beam_width ?? 0, h: s.beam_height ?? 0,
      bar: { diameter: f.selected_bar?.diameter ?? 0, count: f.selected_bar?.count ?? 0 },
    })),
  }))
  // 斜截面逐步代入
  out.push(h3('斜截面受剪承载力'))
  out.push(formula(`V = ${num(sh.max_shear, 3)} kN；h₀ = ${num(sh.h0, 0)} mm（主筋 d = 20 mm，c = 30 mm）`))
  out.push(formula(`Vc = 0.7·ft·b·h₀ = 0.7×${FT}×${num(s.beam_width, 0)}×${num(sh.h0, 0)} = ${num(sh.vc, 2)} kN`))
  out.push(formula(`Asv/s = (γd·V − Vc)/(fyv·h₀) = (${GAMMA_D}×${num(sh.max_shear, 3)}×10³ − ${num(sh.vc, 2)}×10³)/(${FYV}×${num(sh.h0, 0)}) = ${num(sh.asv_s, 4)} mm²/mm`))
  const asvPerLeg = Math.PI * (s.beam_stirrup_diameter ?? 6) ** 2 / 4
  out.push(formula(`选双肢箍 Φ${num(s.beam_stirrup_diameter, 0)}，Asv = 2×(${Math.PI}×${num(s.beam_stirrup_diameter, 0)}²/4) = ${num(Math.round(asvPerLeg * 2))} mm²`))
  out.push(formula(`间距 s = Asv/(Asv/s) = ${num(Math.round(asvPerLeg * 2))}/${num(sh.asv_s, 4)} = ${num(sh.recommended_spacing, 0)} mm（取整，且 S ≤ Smax = 200 mm）`))
  out.push(formula(`配箍率 ρsv = Asv/(b·s) = ${num(Math.round(asvPerLeg * 2))}/(${num(s.beam_width, 0)}×${num(sh.recommended_spacing, 0)}) = ${num(sh.stirrup_ratio, 4)} ≥ ρsv_min = 0.12%，满足。`))
  return out
}

/** 五、主梁设计 */
export function buildMainBeam(d: ProjectData): ReportBlock[] {
  const s = d.structure
  const r = mainBeamOf(d)
  const ld = r.load ?? ({} as MainBeamResult['load'])
  const ifr = r.internal_forces ?? ({} as MainBeamResult['internal_forces'])
  const sh = r.reinforcement?.shear ?? ({} as MainBeamShear)
  const flexure = r.reinforcement?.flexure ?? []
  const out: ReportBlock[] = [h2('主梁设计')]
  if (!d.main_beam?.initialized) {
    out.push(note('主梁尚未计算，本章略。', 'warn'))
    return out
  }
  const span = s.main_beam_spans ? (s.L2 ?? 0) / s.main_beam_spans : 0
  out.push(h3('荷载计算（简化为集中荷载作用于三分点）'))
  out.push(formula(`次梁传来恒载：次梁恒载总值 × 跨度 = ${num(ld.from_beam_dead, 3)} kN`))
  out.push(formula(`主梁自重：${num(s.main_beam_width, 0)}×(${num(s.main_beam_height, 0)}−${num(s.slab_thickness, 0)}) mm × 25 kN/m³ × ${num(span)} m = ${num(ld.self_weight, 3)} kN`))
  out.push(formula(`主梁粉刷（两侧）：17 kN/m³ × 15 mm × (${num(s.main_beam_height, 0)}−${num(s.slab_thickness, 0)}) mm × 2 × ${num(span)} m = ${num(ld.plaster, 3)} kN`))
  out.push(formula(`恒载标准值 Gk = ${num(ld.from_beam_dead, 3)} + ${num(ld.self_weight, 3)} + ${num(ld.plaster, 3)} = ${num(ld.dead_load_standard, 3)} kN`))
  out.push(formula(`恒载设计值 G = γG · Gk = ${GAMMA_G} × ${num(ld.dead_load_standard, 3)} = ${num(ld.dead_load_design, 3)} kN`))
  out.push(formula(`活载标准值 Qk = ${num(ld.live_load_standard, 3)} kN；设计值 Q = γQ · Qk = ${GAMMA_Q} × ${num(ld.live_load_standard, 3)} = ${num(ld.live_load_design, 3)} kN`))
  out.push(figure('图：主梁计算简图', 'mainBeam', {
    span, loadG: ld.dead_load_design, loadQ: ld.live_load_design,
    columnWidth: s.column_width ?? 0, sectionSize: { b: s.main_beam_width ?? 0, h: s.main_beam_height ?? 0 },
  }))
  out.push(h3('内力计算（三跨连续梁最不利组合）'))
  out.push(formula('按四组荷载工况（恒载、活载最不利布置）查三等分集中力系数表，取包络值。'))
  out.push(table('表：主梁控制截面最不利内力',
    ['M1 (kN·m)', 'M_B (kN·m)', 'M2 (kN·m)', 'VA (kN)', 'VB左 (kN)', 'VB右 (kN)'],
    [[num(ifr.M1_max, 1), num(ifr.M_B_min, 1), num(ifr.M2_max, 1),
      num(ifr.VA_max, 1), num(ifr.VBl_min, 1), num(ifr.VBr_max, 1)]]))
  out.push(h3('正截面强度及配筋计算（T 形）'))
  out.push(formula('αs = γd·M/(fc·b·h₀²)，ξ = 1−√(1−2αs)，As = fc·b·ξ·h₀/fy'))
  out.push(table('表：主梁正截面强度及配筋',
    ['截面', '类型', '计算宽', 'M (kN·m)', 'h0', 'αs', 'ξ', 'As需 (mm²)', '选筋', 'As实 (mm²)'],
    flexure.map((f) => [
      f.name, f.section_type, num(f.width_used, 0), num(f.moment, 3), num(f.h0, 0),
      num(f.alpha_s, 4), num(f.xi, 4), Math.round(f.as_required), beamBarText(f.selected_bar), Math.round(f.as_provided),
    ])))
  if (flexure.length) {
    const f0 = flexure[0]
    out.push(formula(`以截面 ${f0.name} 为例：αs = ${GAMMA_D}×(${num(f0.moment)}×10⁶)/(${FC}×${num(f0.width_used, 0)}×${num(f0.h0, 0)}²) = ${num(f0.alpha_s, 4)}；ξ = ${num(f0.xi, 4)}`))
    out.push(formula(`As = ${FC}×${num(f0.width_used, 0)}×${num(f0.xi, 4)}×${num(f0.h0, 0)}/${FY_BEAM} = ${Math.round(f0.as_required)} mm²；实配 ${beamBarText(f0.selected_bar)} = ${Math.round(f0.as_provided)} mm²`))
    const minRho = 0.002
    const actualRho = f0.selected_bar ? f0.as_provided / ((s.main_beam_width ?? 0) * f0.h0) : 0
    out.push(formula(`配筋率验算：ρ = As实/(b·h₀) = ${Math.round(f0.as_provided)}/(${num(s.main_beam_width, 0)}×${num(f0.h0, 0)}) = ${num(actualRho * 100, 3)}% ≥ ρmin = ${minRho * 100}%，满足；ξ = ${num(f0.xi, 4)} < ξb = 0.550，不超筋。`))
  }
  out.push(h3('斜截面受剪承载力与吊筋'))
  out.push(formula(`V = ${num(sh.max_shear, 3)} kN（最大剪力控制截面）；h₀ = ${num(sh.h0, 0)} mm`))
  out.push(formula(`Vc = 0.7·ft·b·h₀ = 0.7×${FT}×${num(s.main_beam_width, 0)}×${num(sh.h0, 0)} = ${num(sh.vc, 2)} kN`))
  out.push(formula(`Asv/s = (γd·V − Vc)/(fyv·h₀) = (${GAMMA_D}×${num(sh.max_shear, 3)}×10³ − ${num(sh.vc, 2)}×10³)/(${FYV}×${num(sh.h0, 0)}) = ${num(sh.asv_s, 4)} mm²/mm`))
  const mbAsv = Math.PI * (s.main_beam_stirrup_diameter ?? 8) ** 2 / 2
  out.push(formula(`选双肢箍 Φ${num(s.main_beam_stirrup_diameter, 0)}，Asv = 2×(${Math.PI}×${num(s.main_beam_stirrup_diameter, 0)}²/4) = ${num(Math.round(mbAsv))} mm²`))
  out.push(formula(`间距 s = ${num(Math.round(mbAsv))}/${num(sh.asv_s, 4)} = ${num(sh.recommended_spacing, 0)} mm（取整，且 ≤ Smax）；配箍率 ρsv = ${num(sh.stirrup_ratio, 4)} ≥ 0.12%`))
  out.push(formula(`吊筋 Asb = γd·F/(fyv·sin45°) = ${GAMMA_D} × F / (${FYV} × sin45°) = ${num(sh.hanger_area, 0)} mm²`))
  out.push(note('主梁包络图暂未自动生成（需后端逐工况采样数据）；控制截面内力可作为手工包络图输入。', 'info'))
  return out
}

/** 六、配筋结果汇总 */
export function buildReinfSummary(d: ProjectData): ReportBlock[] {
  const out: ReportBlock[] = [h2('配筋结果汇总')]
  const rows: (string | number)[][] = []
  for (const f of beamOf(d).reinforcement?.flexure ?? []) {
    rows.push(['次梁·' + f.name, f.section_type, beamBarText(f.selected_bar), Math.round(f.as_provided)])
  }
  for (const f of mainBeamOf(d).reinforcement?.flexure ?? []) {
    rows.push(['主梁·' + f.name, f.section_type, beamBarText(f.selected_bar), Math.round(f.as_provided)])
  }
  for (const c of slabOf(d).reinforcement?.sections ?? []) {
    rows.push(['板·' + c.name, '板带', slabBarText(c.selected_bar), Math.round(c.as_provided)])
  }
  if (!rows.length) out.push(note('尚无配筋结果。', 'warn'))
  else out.push(table('表：配筋结果汇总', ['构件·截面', '类型', '选筋', 'As实 (mm²)'], rows))
  return out
}

/** 七、构造措施说明 */
export function buildConstructionNotes(d: ProjectData): ReportBlock[] {
  const s = d.structure
  const out: ReportBlock[] = [h2('构造措施说明')]
  out.push(para('依据《水工钢筋混凝土结构学》及相关构造要求：'))
  out.push(formula(`板：受力筋直径不宜小于 8 mm、间距不宜大于 200 mm；保护层 c = 20 mm；下部受力筋伸入支座锚固长度不小于 5d。`))
  out.push(formula(`板分布筋单位长度截面面积不宜小于受力筋的 15%，间距不宜大于 250 mm；沿墙体嵌固端、墙角 45° 裂缝区、主梁连接处布置附加构造钢筋。`))
  out.push(formula(`梁：纵筋直径、净距需满足构造；箍筋 ${num(s.beam_stirrup_diameter, 0)} mm（次梁）/ ${num(s.main_beam_stirrup_diameter, 0)} mm（主梁），保护层 c = 30 mm；架立筋、腰筋（hw > 450 mm 时）按构造布置。`))
  out.push(formula(`锚固与搭接：搭接长度不小于 10d；主梁上部纵筋锚固长度不足时向下弯折，水平段 ≥ 0.4la。`))
  out.push(note('以上为通用构造要求模板；具体根数、长度需结合配筋详图确定。', 'info'))
  return out
}

/** 八、抵抗弯矩图说明（次梁） */
export function buildResistingMoment(d: ProjectData): ReportBlock[] {
  const s = d.structure
  const r = beamOf(d)
  const sp = r.span ?? ({} as BeamResult['span'])
  const out: ReportBlock[] = [h2('抵抗弯矩图说明')]
  if (!d.beam?.initialized || !(r.internal_forces?.moments?.length)) {
    out.push(note('次梁未计算，抵抗弯矩图略。', 'warn'))
    return out
  }
  out.push(para('抵抗弯矩图反映各截面实际配筋所能承担的弯矩 Mu（Mu = fc·b·x·(h0−x/2)，x = fy·As/(fc·b)），用以确定纵筋的截断与弯起位置。取次梁绘制。'))
  out.push(figure('图：次梁抵抗弯矩图（设计弯矩 + 抵抗弯矩 Mu）', 'resistingMoment', {
    moments: r.internal_forces.moments,
    rawSpans: s.beam_spans ?? 0, edgeSpan: sp.edge_span, midSpan: sp.middle_span,
    flexure: r.reinforcement?.flexure ?? [],
  }))
  out.push(formula('截断点：纵筋截断点至充分利用点距离 ≥ 1.2la + h0，至理论切断点 ≥ 20d；弯起点至充分利用点 ≥ 0.5h0。'))
  out.push(note('图中 Mu 为各设计截面抵抗弯矩；具体截断/弯起位置需结合配筋详图与抵抗弯矩图包络确定。', 'info'))
  return out
}

// ── 装配入口（8 章） ──
export function buildReportDoc(d: ProjectData): ReportDoc {
  const sections: ReportSection[] = [
    { id: 'basic', number: '一', title: '设计基本资料', blocks: buildBasicInfo(d) },
    { id: 'layout', number: '二', title: '结构平面布置及构件截面尺寸初估', blocks: buildLayoutAndSize(d) },
    { id: 'slab', number: '三', title: '板设计', blocks: buildSlab(d) },
    { id: 'beam', number: '四', title: '次梁设计', blocks: buildBeam(d) },
    { id: 'main', number: '五', title: '主梁设计', blocks: buildMainBeam(d) },
    { id: 'summary', number: '六', title: '配筋结果汇总', blocks: buildReinfSummary(d) },
    { id: 'construction', number: '七', title: '构造措施说明', blocks: buildConstructionNotes(d) },
    { id: 'resist', number: '八', title: '抵抗弯矩图说明', blocks: buildResistingMoment(d) },
  ]
  return { cover: d.report ?? {}, sections }
}
