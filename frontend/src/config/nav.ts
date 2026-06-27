import { markRaw } from 'vue'
import type { Component } from 'vue'
import {
  LayoutDashboard,
  Boxes,
  LayoutGrid,
  ChartLine,
  ChartSpline,
  FileText,
  Settings,
} from '@lucide/vue'

export interface NavItem {
  path: string
  title: string
  icon: Component
}

export const NAV_ITEMS: NavItem[] = [
  { path: '/', title: '开始', icon: markRaw(LayoutDashboard) },
  { path: '/materials', title: '材料参数', icon: markRaw(Boxes) },
  { path: '/slab', title: '板计算', icon: markRaw(LayoutGrid) },
  { path: '/secondary-beam', title: '次梁计算', icon: markRaw(ChartLine) },
  { path: '/main-beam', title: '主梁计算', icon: markRaw(ChartSpline) },
  { path: '/report', title: '计算书', icon: markRaw(FileText) },
  { path: '/settings', title: '系统设置', icon: markRaw(Settings) },
]
