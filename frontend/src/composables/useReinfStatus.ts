/**
 * 配筋状态展示助手（板 / 次梁 / 主梁计算页共用）。
 *
 * 后端求解器 status 词表统一为：推荐 / 建议复核 / 不足
 * （见 backend/app/solvers/common.py 的 flexure_status）。
 * 文案映射兼容历史英文状态值（pass/review/fail…），保持各页原有展示行为。
 */

/** 状态 → 中文文案。 */
export function reinfLabel(status: string): string {
  if (status === 'pass' || status === 'ok') return '满足'
  if (status === 'review') return '复核'
  if (status === 'fail' || status === 'insufficient') return '不足'
  return status
}

/** 状态 → el-tag 类型。 */
export function reinfTagType(status: string): 'success' | 'warning' | 'danger' {
  if (status === 'pass' || status === 'ok' || status === '推荐') return 'success'
  if (status === 'review' || status === '建议复核') return 'danger'
  return 'danger'
}
