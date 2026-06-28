import { markRaw } from 'vue'
import type { Component } from 'vue'
import {
  LayoutDashboard,
  Boxes,
  LayoutGrid,
  FileText,
  Archive,
  Settings,
} from '@lucide/vue'

export interface NavItem {
  path: string
  title: string
  icon: Component
}

// 次梁/主梁暂未接通（待深入调查），先从导航移除；材料参数并入「参数」页。
export const NAV_ITEMS: NavItem[] = [
  { path: '/', title: '开始', icon: markRaw(LayoutDashboard) },
  { path: '/params', title: '参数', icon: markRaw(Boxes) },
  { path: '/slab', title: '板计算', icon: markRaw(LayoutGrid) },
  { path: '/report', title: '计算书', icon: markRaw(FileText) },
  { path: '/archive', title: '存档与历史', icon: markRaw(Archive) },
  { path: '/settings', title: '系统设置', icon: markRaw(Settings) },
]
