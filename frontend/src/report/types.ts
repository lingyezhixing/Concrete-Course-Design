// 计算书文档模型 —— 装配器(buildReportDoc)产出、渲染器(ReportDocument.vue)消费。
// figure 用 figureKind + props 解耦，避免装配器引入 .vue 组件，保持纯函数可测。

export type BlockKind = 'heading' | 'paragraph' | 'formula' | 'table' | 'figure' | 'note'

export interface HeadingBlock {
  kind: 'heading'
  level: 1 | 2 | 3
  text: string
}
export interface ParagraphBlock { kind: 'paragraph'; text: string }
export interface FormulaBlock { kind: 'formula'; text: string }

export interface TableBlock {
  kind: 'table'
  caption?: string
  headers: string[]
  rows: (string | number)[][]
}

export type FigureKind =
  | 'uniformBeam'     // 板/次梁 计算简图（均布荷载连续梁）
  | 'mainBeam'        // 主梁 计算简图（三等分集中力）
  | 'internalForce'   // 板/次梁 弯矩剪力图
  | 'sectionRebar'    // 截面配筋简图
  | 'resistingMoment' // 抵抗弯矩图（次梁）

export interface FigureBlock {
  kind: 'figure'
  caption: string
  figure: FigureKind
  props: Record<string, unknown>
}

export interface NoteBlock { kind: 'note'; text: string; tone?: 'info' | 'warn' }

export type ReportBlock =
  | HeadingBlock | ParagraphBlock | FormulaBlock
  | TableBlock | FigureBlock | NoteBlock

export interface ReportSection {
  id: string
  number: string      // '一'、'二'…；前置（封面/目录）为空串
  title: string
  blocks: ReportBlock[]
}

export interface CoverInfo {
  college?: string
  major?: string
  name?: string
  student_id?: string
  advisor?: string
  date?: string
}

export interface ReportDoc {
  cover: CoverInfo
  sections: ReportSection[]
}
