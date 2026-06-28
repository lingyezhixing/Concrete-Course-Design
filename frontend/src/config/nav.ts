import { markRaw } from 'vue'
import type { Component } from 'vue'
import {
  LayoutDashboard,
  Boxes,
  LayoutGrid,
  Grid2x2,
  Columns3,
  FileText,
  Archive,
  Settings,
} from '@lucide/vue'

export interface NavItem {
  path: string
  title: string
  icon: Component
}

export interface NavGroup {
  label: string
  items: NavItem[]
}

// 材料参数并入「参数」页（结构/材料/荷载三段）。
// 分组仅作视觉组织，不影响路由；NAV_ITEMS 为其扁平视图（兼容旧用法与测试）。
export const NAV_GROUPS: NavGroup[] = [
  {
    label: '工作区',
    items: [
      { path: '/', title: '开始', icon: markRaw(LayoutDashboard) },
      { path: '/params', title: '参数', icon: markRaw(Boxes) },
    ],
  },
  {
    label: '构件计算',
    items: [
      { path: '/slab', title: '板计算', icon: markRaw(LayoutGrid) },
      { path: '/beam', title: '次梁计算', icon: markRaw(Columns3) },
      { path: '/main_beam', title: '主梁计算', icon: markRaw(Grid2x2) },
    ],
  },
  {
    label: '成果',
    items: [
      { path: '/report', title: '计算书', icon: markRaw(FileText) },
      { path: '/archive', title: '存档与历史', icon: markRaw(Archive) },
    ],
  },
  {
    label: '系统',
    items: [{ path: '/settings', title: '系统设置', icon: markRaw(Settings) }],
  },
]

export const NAV_ITEMS: NavItem[] = NAV_GROUPS.flatMap((g) => g.items)
