import { markRaw } from 'vue'
import type { Component } from 'vue'
import {
  DataBoard,
  Box,
  Grid,
  Operation,
  Memo,
  Coin,
  Document,
  Setting,
} from '@element-plus/icons-vue'

export interface NavItem {
  path: string
  title: string
  icon: Component
  underConstruction: boolean
}

export const NAV_ITEMS: NavItem[] = [
  { path: '/', title: '概览', icon: markRaw(DataBoard), underConstruction: false },
  { path: '/materials', title: '材料参数', icon: markRaw(Box), underConstruction: false },
  { path: '/slab', title: '板计算', icon: markRaw(Grid), underConstruction: true },
  { path: '/secondary-beam', title: '次梁计算', icon: markRaw(Operation), underConstruction: true },
  { path: '/main-beam', title: '主梁计算', icon: markRaw(Memo), underConstruction: true },
  { path: '/column', title: '柱计算', icon: markRaw(Coin), underConstruction: true },
  { path: '/report', title: '计算书', icon: markRaw(Document), underConstruction: true },
  { path: '/settings', title: '系统设置', icon: markRaw(Setting), underConstruction: true },
]
