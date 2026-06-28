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

// 材料参数并入「参数」页（结构/材料/荷载三段）。
export const NAV_ITEMS: NavItem[] = [
  { path: '/', title: '开始', icon: markRaw(LayoutDashboard) },
  { path: '/params', title: '参数', icon: markRaw(Boxes) },
  { path: '/slab', title: '板计算', icon: markRaw(LayoutGrid) },
  { path: '/beam', title: '次梁计算', icon: markRaw(Columns3) },
  { path: '/main_beam', title: '主梁计算', icon: markRaw(Grid2x2) },
  { path: '/report', title: '计算书', icon: markRaw(FileText) },
  { path: '/archive', title: '存档与历史', icon: markRaw(Archive) },
  { path: '/settings', title: '系统设置', icon: markRaw(Settings) },
]
