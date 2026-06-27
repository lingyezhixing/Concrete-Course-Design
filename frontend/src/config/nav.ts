import { markRaw } from 'vue'
import type { Component } from 'vue'
import {
  DataBoard,
  Box,
  Grid,
  Operation,
  Memo,
  Document,
  Setting,
} from '@element-plus/icons-vue'

export interface NavItem {
  path: string
  title: string
  icon: Component
}

export const NAV_ITEMS: NavItem[] = [
  { path: '/', title: '概览', icon: markRaw(DataBoard) },
  { path: '/materials', title: '材料参数', icon: markRaw(Box) },
  { path: '/slab', title: '板计算', icon: markRaw(Grid) },
  { path: '/secondary-beam', title: '次梁计算', icon: markRaw(Operation) },
  { path: '/main-beam', title: '主梁计算', icon: markRaw(Memo) },
  { path: '/report', title: '计算书', icon: markRaw(Document) },
  { path: '/settings', title: '系统设置', icon: markRaw(Setting) },
]
