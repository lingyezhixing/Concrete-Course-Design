/**
 * 计算简图（力学模型）的横向布局计算 —— 与渲染解耦的纯函数。
 *
 * 板 / 次梁为均布荷载多跨连续梁，跨数随参数变化（2~5 直接画，>5 按五跨等效）；
 * 主梁为三等分集中荷载连续梁（当前固定 3 跨）。本模块只负责把跨数 / 跨度映射为
 * SVG viewBox 横向坐标（支座、跨边界、集中力、均布荷载箭头）+ 等效逻辑标志，
 * 颜色 / 纵向坐标由组件自行决定，便于单测与三主题适配。
 *
 * 详见 docs/superpowers/specs/2026-06-29-calculation-diagrams-design.md。
 */

export interface LayoutOptions {
  /** 画布（viewBox）宽度，默认 600 */
  width?: number
  /** 两侧留白，默认 32 */
  pad?: number
}

export const DEFAULT_WIDTH = 600
export const DEFAULT_PAD = 32

/** 单个支座 */
export interface SupportMark {
  x: number
  index: number
}

/** 单跨（均布梁） */
export interface SpanMark {
  x0: number
  x1: number
  cx: number
  /** 该跨计算长度（m），仅用于标注 */
  length: number
  /** 是否为五跨等效时的中间等效跨 */
  isEquiv: boolean
  /** 跨度标注文字（l₀₁ / l₀₂ / 中间等效跨） */
  label: string
}

/** 均布荷载连续梁（板 / 次梁）布局结果 */
export interface UniformBeamLayout {
  /** 等效跨数（实际绘制的跨数，2~5） */
  eqSpans: number
  /** 是否触发了五跨等效（原始跨数 > 5） */
  isEquiv: boolean
  /** 中间等效跨代表的实际跨数（未等效时为 0） */
  equivRepresents: number
  /** 等效说明文字（未等效时为空串） */
  equivNote: string
  /** 支座（eqSpans + 1 个） */
  supports: SupportMark[]
  /** 各跨 */
  spans: SpanMark[]
  /** 均布荷载箭头 x 坐标 */
  loadArrows: number[]
}

/**
 * 计算均布荷载连续梁（板 / 次梁）的横向布局。
 *
 * - 跨数：`min(rawSpans, 5)`，钳制到 `[2, 5]`
 * - 逐跨长度：边跨 = `edgeSpan`，中间跨 = `midSpan`（等跨连续梁）
 * - 原始跨数 > 5 触发五跨等效：第 3 跨（索引 2）标记为等效跨
 *
 * @returns 输入非法（跨数 < 2 或跨度 ≤ 0）时返回 `null`
 */
export function layoutUniformBeam(
  rawSpans: number,
  edgeSpan: number,
  midSpan: number,
  opts: LayoutOptions = {},
): UniformBeamLayout | null {
  const width = opts.width ?? DEFAULT_WIDTH
  const pad = opts.pad ?? DEFAULT_PAD

  if (!Number.isFinite(rawSpans) || rawSpans < 2) return null
  if (!(edgeSpan > 0) || !(midSpan > 0)) return null

  const n = Math.trunc(rawSpans)
  const eqSpans = Math.min(Math.max(n, 2), 5)
  const isEquiv = n > 5
  const equivRepresents = isEquiv ? n - 4 : 0

  // 逐跨长度：两端为边跨，其余为中跨
  const lengths: number[] = []
  for (let i = 0; i < eqSpans; i++) {
    lengths.push(i === 0 || i === eqSpans - 1 ? edgeSpan : midSpan)
  }
  const totalLen = lengths.reduce((a, b) => a + b, 0)
  const usable = width - pad * 2

  // 支座 x：按累积长度比例映射到 [pad, width - pad]
  const supportXs: number[] = [pad]
  let acc = 0
  for (let i = 0; i < eqSpans; i++) {
    acc += lengths[i]
    supportXs.push(pad + (acc / totalLen) * usable)
  }

  const supports: SupportMark[] = supportXs.map((x, index) => ({ x, index }))

  const spans: SpanMark[] = []
  for (let i = 0; i < eqSpans; i++) {
    const x0 = supportXs[i]
    const x1 = supportXs[i + 1]
    const isEquivSpan = isEquiv && eqSpans === 5 && i === 2
    spans.push({
      x0,
      x1,
      cx: (x0 + x1) / 2,
      length: lengths[i],
      isEquiv: isEquivSpan,
      label: isEquivSpan
        ? '中间等效跨'
        : i === 0 || i === eqSpans - 1
          ? 'l₀₁'
          : 'l₀₂',
    })
  }

  return {
    eqSpans,
    isEquiv,
    equivRepresents,
    equivNote: isEquiv
      ? `第 3 跨代表原第 3 ~ ${n - 2} 跨（${equivRepresents} 跨等效为 1 跨）`
      : '',
    supports,
    spans,
    loadArrows: computeUniformArrows(pad, width - pad),
  }
}

/** 在 [from, to] 内按固定间距生成均布荷载箭头位置。 */
function computeUniformArrows(from: number, to: number, gap = 38): number[] {
  const arr: number[] = []
  if (!(to > from)) return arr
  for (let x = from + gap / 2; x < to; x += gap) {
    arr.push(x)
  }
  return arr
}

/** 集中力位置（主梁） */
export interface PointLoadMark {
  x: number
  /** 所属跨索引 */
  spanIndex: number
}

/** 主梁单跨标注 */
export interface MainBeamSpanMark {
  x0: number
  x1: number
  cx: number
  label: string
}

/** 主梁（三等分集中荷载连续梁）布局结果 */
export interface MainBeamLayout {
  spans: number
  supports: SupportMark[]
  pointLoads: PointLoadMark[]
  spanMarks: MainBeamSpanMark[]
}

/**
 * 计算主梁（三等分集中荷载连续梁）布局。
 *
 * 当前固定 3 等跨、每跨 2 个集中力（1/3、2/3 处）。`spans` 当前仅支持 3，
 * 传入其他值会被钳制到 3（与后端现状一致；未来参数化时再放开）。
 */
export function layoutMainBeam(
  opts: { spans?: number; width?: number; pad?: number } = {},
): MainBeamLayout {
  const width = opts.width ?? DEFAULT_WIDTH
  const pad = opts.pad ?? DEFAULT_PAD
  // 当前后端仅支持 3 跨；这里显式锚定为 3，避免误用。
  const spans = 3
  void opts.spans // 保留参数位以便未来参数化扩展

  const usable = width - pad * 2
  const spanW = usable / spans

  const supports: SupportMark[] = []
  for (let i = 0; i <= spans; i++) {
    supports.push({ x: pad + spanW * i, index: i })
  }

  const pointLoads: PointLoadMark[] = []
  const spanMarks: MainBeamSpanMark[] = []
  for (let i = 0; i < spans; i++) {
    const x0 = pad + spanW * i
    const x1 = pad + spanW * (i + 1)
    spanMarks.push({ x0, x1, cx: (x0 + x1) / 2, label: 'l₀' })
    pointLoads.push({ x: x0 + spanW / 3, spanIndex: i })
    pointLoads.push({ x: x0 + (spanW * 2) / 3, spanIndex: i })
  }

  return { spans, supports, pointLoads, spanMarks }
}
