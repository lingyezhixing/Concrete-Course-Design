# 前端骨架与布局 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用 Vue 3 + Element Plus 搭建应用外壳（顶栏 + 可折叠侧边栏 + 主内容区）与暗/亮主题系统，路由覆盖混凝土课程设计各模块，计算页面为"建设中"占位。

**Architecture:** 在现有 Vue 3 + Element Plus 骨架上扩展。布局用 `el-container`/`el-header`/`el-aside`/`el-main` + `el-menu`（`:collapse`）；主题与侧边栏状态用轻量 composable + `localStorage`；健康状态用 `setInterval` 轮询 `/api/health`。逻辑单元（composables、nav 配置、api 函数）走 TDD；纯展示组件用类型检查 + 构建验证。

**Tech Stack:** Vue 3.5, Element Plus 2.9, vue-router 4.5, axios, Vite 6, TypeScript 5.7, @element-plus/icons-vue（新增）, vitest + happy-dom（新增，仅用于逻辑单测）。

**Spec:** [docs/superpowers/specs/2026-06-27-frontend-shell-layout-design.md](../specs/2026-06-27-frontend-shell-layout-design.md)

---

## 关键约定（执行前必读）

1. **相对路径导入**：项目未配置 `@/` 别名，且 spec 要求不改 `tsconfig.json` / `vite.config.ts`，故全部用相对路径导入（如 `'../api'`、`'../../composables/useTheme'`）。
2. **strict + noUnusedLocals/noUnusedParameters**：不得有未使用的 import 或变量。
3. **测试策略**：逻辑单元（`nav.ts`、三个 composable、`getHealth`）走 TDD（先写失败测试 → 实现 → 通过）；展示型 `.vue` 组件用 `npx vue-tsc --noEmit` 类型检查 + 最终 `npm run build` 验证。
4. **保留 `Home.vue` 直到 Task 12**（路由改写后才删除），保证每一步类型检查可通过。
5. **所有命令在 `frontend/` 目录下执行**。

---

## Task 1: 测试与图标依赖、vitest 配置

**Files:**
- Modify: `frontend/package.json`
- Create: `frontend/vitest.config.ts`

- [ ] **Step 1: 安装依赖**

Run（在 `frontend/` 下）:
```bash
npm install @element-plus/icons-vue
npm install -D vitest happy-dom
```
Expected: `package.json` 中新增 `@element-plus/icons-vue`（dependencies）、`vitest` 与 `happy-dom`（devDependencies）。

- [ ] **Step 2: 添加测试脚本**

修改 `frontend/package.json` 的 `scripts`，改为：
```json
"scripts": {
  "dev": "vite",
  "build": "vue-tsc -b && vite build",
  "preview": "vite preview",
  "test": "vitest",
  "test:run": "vitest run"
}
```

- [ ] **Step 3: 创建 vitest 配置**

Create `frontend/vitest.config.ts`:
```ts
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'happy-dom',
    include: ['src/**/*.spec.ts'],
  },
})
```

- [ ] **Step 4: 验证安装**

Run: `npx vitest --version`
Expected: 打印 vitest 版本号（确认安装成功）。

- [ ] **Step 5: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vitest.config.ts
git commit -m "chore: add element-plus icons, vitest and happy-dom"
```

---

## Task 2: 导航配置 `nav.ts`（TDD）

**Files:**
- Create: `frontend/src/config/nav.ts`
- Test: `frontend/src/config/nav.spec.ts`

- [ ] **Step 1: 写失败测试**

Create `frontend/src/config/nav.spec.ts`:
```ts
import { describe, it, expect } from 'vitest'
import { NAV_ITEMS } from './nav'

describe('nav config', () => {
  it('has 8 items', () => {
    expect(NAV_ITEMS).toHaveLength(8)
  })

  it('every item has path, title, and icon', () => {
    for (const item of NAV_ITEMS) {
      expect(typeof item.path).toBe('string')
      expect(item.path.length).toBeGreaterThan(0)
      expect(typeof item.title).toBe('string')
      expect(item.title.length).toBeGreaterThan(0)
      expect(item.icon).toBeTruthy()
      expect(typeof item.underConstruction).toBe('boolean')
    }
  })

  it('paths are unique', () => {
    const paths = NAV_ITEMS.map((i) => i.path)
    expect(new Set(paths).size).toBe(paths.length)
  })

  it('contains overview at "/"', () => {
    expect(NAV_ITEMS.some((i) => i.path === '/')).toBe(true)
  })
})
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `npx vitest run src/config/nav.spec.ts`
Expected: FAIL —— `Cannot find module './nav'`。

- [ ] **Step 3: 实现 `nav.ts`**

Create `frontend/src/config/nav.ts`:
```ts
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
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `npx vitest run src/config/nav.spec.ts`
Expected: PASS（4 个用例全过）。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/config/nav.ts frontend/src/config/nav.spec.ts
git commit -m "feat: add nav config with concrete course-design modules"
```

---

## Task 3: 主题 composable `useTheme`（TDD）

**Files:**
- Create: `frontend/src/composables/useTheme.ts`
- Test: `frontend/src/composables/useTheme.spec.ts`

- [ ] **Step 1: 写失败测试**

Create `frontend/src/composables/useTheme.spec.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useTheme } from './useTheme'

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove('dark')
  })

  it('defaults to dark when nothing stored', () => {
    const { isDark } = useTheme()
    expect(isDark.value).toBe(true)
  })

  it('reads stored light theme', () => {
    localStorage.setItem('ccd-theme', 'light')
    const { isDark } = useTheme()
    expect(isDark.value).toBe(false)
  })

  it('applies html.dark class on init', () => {
    useTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('toggle flips value, persists, and toggles html class', () => {
    const { isDark, toggle } = useTheme()
    expect(isDark.value).toBe(true)

    toggle()
    expect(isDark.value).toBe(false)
    expect(localStorage.getItem('ccd-theme')).toBe('light')
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    toggle()
    expect(isDark.value).toBe(true)
    expect(localStorage.getItem('ccd-theme')).toBe('dark')
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `npx vitest run src/composables/useTheme.spec.ts`
Expected: FAIL —— `Cannot find module './useTheme'`。

- [ ] **Step 3: 实现 `useTheme.ts`**

Create `frontend/src/composables/useTheme.ts`:
```ts
import { ref } from 'vue'

const STORAGE_KEY = 'ccd-theme'

function readIsDark(): boolean {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored === null ? true : stored === 'dark'
}

function applyClass(isDark: boolean): void {
  document.documentElement.classList.toggle('dark', isDark)
}

export function useTheme() {
  const isDark = ref(readIsDark())
  applyClass(isDark.value)

  function toggle() {
    isDark.value = !isDark.value
    localStorage.setItem(STORAGE_KEY, isDark.value ? 'dark' : 'light')
    applyClass(isDark.value)
  }

  return { isDark, toggle }
}
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `npx vitest run src/composables/useTheme.spec.ts`
Expected: PASS（4 个用例全过）。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/composables/useTheme.ts frontend/src/composables/useTheme.spec.ts
git commit -m "feat: add useTheme composable with dark/light + persistence"
```

---

## Task 4: 侧边栏 composable `useSidebar`（TDD）

**Files:**
- Create: `frontend/src/composables/useSidebar.ts`
- Test: `frontend/src/composables/useSidebar.spec.ts`

- [ ] **Step 1: 写失败测试**

Create `frontend/src/composables/useSidebar.spec.ts`:
```ts
import { describe, it, expect, beforeEach } from 'vitest'
import { useSidebar } from './useSidebar'

describe('useSidebar', () => {
  beforeEach(() => localStorage.clear())

  it('defaults to expanded', () => {
    const { isCollapsed } = useSidebar()
    expect(isCollapsed.value).toBe(false)
  })

  it('reads stored collapsed state', () => {
    localStorage.setItem('ccd-sidebar', 'collapsed')
    const { isCollapsed } = useSidebar()
    expect(isCollapsed.value).toBe(true)
  })

  it('toggle flips and persists', () => {
    const { isCollapsed, toggle } = useSidebar()
    toggle()
    expect(isCollapsed.value).toBe(true)
    expect(localStorage.getItem('ccd-sidebar')).toBe('collapsed')
    toggle()
    expect(isCollapsed.value).toBe(false)
    expect(localStorage.getItem('ccd-sidebar')).toBe('expanded')
  })
})
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `npx vitest run src/composables/useSidebar.spec.ts`
Expected: FAIL —— `Cannot find module './useSidebar'`。

- [ ] **Step 3: 实现 `useSidebar.ts`**

Create `frontend/src/composables/useSidebar.ts`:
```ts
import { ref } from 'vue'

const STORAGE_KEY = 'ccd-sidebar'

export function useSidebar() {
  const isCollapsed = ref(localStorage.getItem(STORAGE_KEY) === 'collapsed')

  function toggle() {
    isCollapsed.value = !isCollapsed.value
    localStorage.setItem(STORAGE_KEY, isCollapsed.value ? 'collapsed' : 'expanded')
  }

  return { isCollapsed, toggle }
}
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `npx vitest run src/composables/useSidebar.spec.ts`
Expected: PASS（3 个用例全过）。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/composables/useSidebar.ts frontend/src/composables/useSidebar.spec.ts
git commit -m "feat: add useSidebar composable with collapse persistence"
```

---

## Task 5: API 健康检查函数 `getHealth`（TDD）

**Files:**
- Modify: `frontend/src/api/index.ts`
- Test: `frontend/src/api/health.spec.ts`

- [ ] **Step 1: 写失败测试**

Create `frontend/src/api/health.spec.ts`:
```ts
import { describe, it, expect, vi, beforeEach } from 'vitest'

const { get } = vi.hoisted(() => ({ get: vi.fn() }))
vi.mock('axios', () => ({ default: { create: () => ({ get }) } }))

import { getHealth } from './index'

describe('getHealth', () => {
  beforeEach(() => get.mockReset())

  it('calls /health and returns data', async () => {
    get.mockResolvedValue({ data: { status: 'ok' } })
    const result = await getHealth()
    expect(get).toHaveBeenCalledWith('/health')
    expect(result).toEqual({ status: 'ok' })
  })

  it('propagates errors', async () => {
    get.mockRejectedValue(new Error('network'))
    await expect(getHealth()).rejects.toThrow('network')
  })
})
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `npx vitest run src/api/health.spec.ts`
Expected: FAIL —— `getHealth is not a function`（尚未导出）。

- [ ] **Step 3: 修改 `api/index.ts` 追加 `getHealth`**

将 `frontend/src/api/index.ts` 全文替换为：
```ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
})

export default api

export interface HealthResponse {
  status: string
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await api.get<HealthResponse>('/health')
  return data
}
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `npx vitest run src/api/health.spec.ts`
Expected: PASS（2 个用例全过）。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/api/index.ts frontend/src/api/health.spec.ts
git commit -m "feat: add typed getHealth api function"
```

---

## Task 6: 健康轮询 composable `useHealth`（TDD）

**Files:**
- Create: `frontend/src/composables/useHealth.ts`
- Test: `frontend/src/composables/useHealth.spec.ts`

- [ ] **Step 1: 写失败测试**

Create `frontend/src/composables/useHealth.spec.ts`:
```ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

const { getHealth } = vi.hoisted(() => ({ getHealth: vi.fn() }))
vi.mock('../api', () => ({ getHealth }))

import { useHealth } from './useHealth'

describe('useHealth', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    getHealth.mockReset()
  })
  afterEach(() => vi.useRealTimers())

  it('starts offline, becomes online after a successful check', async () => {
    getHealth.mockResolvedValue({ status: 'ok' })
    const { isOnline, start, stop } = useHealth()
    expect(isOnline.value).toBe(false)
    start()
    await vi.waitFor(() => expect(isOnline.value).toBe(true))
    stop()
  })

  it('becomes offline when check throws', async () => {
    getHealth.mockRejectedValue(new Error('down'))
    const { isOnline, start, stop } = useHealth()
    start()
    await vi.waitFor(() => expect(isOnline.value).toBe(false))
    stop()
  })

  it('polls at the given interval', async () => {
    getHealth.mockResolvedValue({ status: 'ok' })
    const { start, stop } = useHealth(1000)
    start()
    await vi.waitFor(() => expect(getHealth).toHaveBeenCalled())
    const before = getHealth.mock.calls.length
    await vi.advanceTimersByTimeAsync(1000)
    expect(getHealth.mock.calls.length).toBeGreaterThan(before)
    stop()
  })

  it('stop() clears the interval', async () => {
    getHealth.mockResolvedValue({ status: 'ok' })
    const { start, stop } = useHealth(1000)
    start()
    await vi.waitFor(() => expect(getHealth).toHaveBeenCalled())
    stop()
    const after = getHealth.mock.calls.length
    await vi.advanceTimersByTimeAsync(5000)
    expect(getHealth.mock.calls.length).toBe(after)
  })
})
```

- [ ] **Step 2: 运行测试，确认失败**

Run: `npx vitest run src/composables/useHealth.spec.ts`
Expected: FAIL —— `Cannot find module './useHealth'`。

- [ ] **Step 3: 实现 `useHealth.ts`**

Create `frontend/src/composables/useHealth.ts`:
```ts
import { ref } from 'vue'
import type { Ref } from 'vue'
import { getHealth } from '../api'

export function useHealth(intervalMs = 5000): {
  isOnline: Ref<boolean>
  start: () => void
  stop: () => void
} {
  const isOnline = ref(false)
  let timer: ReturnType<typeof setInterval> | null = null

  async function check(): Promise<void> {
    try {
      await getHealth()
      isOnline.value = true
    } catch {
      isOnline.value = false
    }
  }

  function start(): void {
    if (timer !== null) return
    void check()
    timer = setInterval(() => void check(), intervalMs)
  }

  function stop(): void {
    if (timer === null) return
    clearInterval(timer)
    timer = null
  }

  return { isOnline, start, stop }
}
```

- [ ] **Step 4: 运行测试，确认通过**

Run: `npx vitest run src/composables/useHealth.spec.ts`
Expected: PASS（4 个用例全过）。

- [ ] **Step 5: 全量测试回归**

Run: `npx vitest run`
Expected: 所有 spec 通过（nav / useTheme / useSidebar / health / useHealth）。

- [ ] **Step 6: Commit**

```bash
git add frontend/src/composables/useHealth.ts frontend/src/composables/useHealth.spec.ts
git commit -m "feat: add useHealth polling composable"
```

---

## Task 7: "建设中"占位组件 + 全局样式

**Files:**
- Create: `frontend/src/components/common/UnderConstruction.vue`
- Create: `frontend/src/assets/styles/theme.css`
- Create: `frontend/src/assets/styles/index.css`

- [ ] **Step 1: 创建 `UnderConstruction.vue`**

Create `frontend/src/components/common/UnderConstruction.vue`:
```vue
<template>
  <div class="uc">
    <el-empty :description="`${title} — 建设中`">
      <template #image>
        <el-icon :size="64" class="uc-icon"><Tools /></el-icon>
      </template>
    </el-empty>
  </div>
</template>

<script setup lang="ts">
import { Tools } from '@element-plus/icons-vue'

defineProps<{ title: string }>()
</script>

<style scoped>
.uc {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 400px;
  padding: 40px;
}
.uc-icon {
  color: var(--el-text-color-secondary);
}
</style>
```

- [ ] **Step 2: 创建主题覆盖 `theme.css`**

Create `frontend/src/assets/styles/theme.css`:
```css
/* 主色覆盖：亮色用靛蓝，暗色用浅蓝（参考 LLM-Manager 配色） */
:root {
  --el-color-primary: #4f46e5;
}
html.dark {
  --el-color-primary: #6b8cff;
}
```

- [ ] **Step 3: 创建全局基础样式 `index.css`**

Create `frontend/src/assets/styles/index.css`:
```css
html,
body,
#app {
  height: 100%;
  margin: 0;
}
* {
  box-sizing: border-box;
}

/* 细滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-thumb {
  background: var(--el-border-color);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--el-border-color-darker);
}
::-webkit-scrollbar-track {
  background: transparent;
}
```

- [ ] **Step 4: 类型检查**

Run: `npx vue-tsc --noEmit`
Expected: 无错误。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/common/UnderConstruction.vue frontend/src/assets/styles/
git commit -m "feat: add UnderConstruction component and global styles"
```

---

## Task 8: 应用外壳布局组件（AppLayout / AppHeader / AppSidebar）

**Files:**
- Create: `frontend/src/components/layout/AppLayout.vue`
- Create: `frontend/src/components/layout/AppHeader.vue`
- Create: `frontend/src/components/layout/AppSidebar.vue`

- [ ] **Step 1: 创建 `AppLayout.vue`**

Create `frontend/src/components/layout/AppLayout.vue`:
```vue
<template>
  <el-container class="app-layout">
    <el-header class="app-header">
      <AppHeader :collapsed="isCollapsed" @toggle="toggle" />
    </el-header>
    <el-container>
      <el-aside :width="isCollapsed ? '64px' : '210px'" class="app-aside">
        <AppSidebar :collapsed="isCollapsed" />
      </el-aside>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import { useSidebar } from '../../composables/useSidebar'

const { isCollapsed, toggle } = useSidebar()
</script>

<style scoped>
.app-layout {
  height: 100vh;
}
.app-header {
  padding: 0;
  height: 56px;
  border-bottom: 1px solid var(--el-border-color);
}
.app-aside {
  border-right: 1px solid var(--el-border-color);
  transition: width 0.2s;
  overflow: hidden;
}
.app-main {
  padding: 0;
  background: var(--el-bg-color-page);
  overflow-y: auto;
}
</style>
```

- [ ] **Step 2: 创建 `AppHeader.vue`**

Create `frontend/src/components/layout/AppHeader.vue`:
```vue
<template>
  <div class="header">
    <div class="header-left">
      <el-icon class="header-btn" :size="20" @click="emit('toggle')">
        <component :is="collapsed ? Expand : Fold" />
      </el-icon>
      <span class="title">混凝土课程设计计算平台</span>
    </div>
    <div class="header-right">
      <el-tooltip :content="isOnline ? '后端在线' : '后端离线'" placement="bottom">
        <span class="health-dot" :class="{ online: isOnline }" />
      </el-tooltip>
      <el-icon class="header-btn" :size="20" @click="toggleTheme">
        <component :is="isDark ? Moon : Sunny" />
      </el-icon>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { Fold, Expand, Moon, Sunny } from '@element-plus/icons-vue'
import { useTheme } from '../../composables/useTheme'
import { useHealth } from '../../composables/useHealth'

defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ toggle: [] }>()

const { isDark, toggle: toggleTheme } = useTheme()
const { isOnline, start, stop } = useHealth()

onMounted(start)
onUnmounted(stop)
</script>

<style scoped>
.header {
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.header-btn {
  cursor: pointer;
  color: var(--el-text-color-regular);
}
.title {
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}
.health-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--el-text-color-disabled);
}
.health-dot.online {
  background: var(--el-color-success);
}
</style>
```

- [ ] **Step 3: 创建 `AppSidebar.vue`**

Create `frontend/src/components/layout/AppSidebar.vue`:
```vue
<template>
  <el-menu
    :default-active="route.path"
    :collapse="collapsed"
    :router="true"
    class="app-menu"
  >
    <el-menu-item v-for="item in NAV_ITEMS" :key="item.path" :index="item.path">
      <el-icon><component :is="item.icon" /></el-icon>
      <template #title>{{ item.title }}</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { NAV_ITEMS } from '../../config/nav'

defineProps<{ collapsed: boolean }>()

const route = useRoute()
</script>

<style scoped>
.app-menu {
  border-right: none;
  height: 100%;
}
.app-menu:not(.el-menu--collapse) {
  width: 210px;
}
</style>
```

- [ ] **Step 4: 类型检查**

Run: `npx vue-tsc --noEmit`
Expected: 无错误。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/layout/
git commit -m "feat: add app shell layout (header, sidebar, container)"
```

---

## Task 9: 概览页 `Overview.vue`（静态内容）

**Files:**
- Create: `frontend/src/views/Overview.vue`

- [ ] **Step 1: 创建 `Overview.vue`**

Create `frontend/src/views/Overview.vue`:
```vue
<template>
  <div class="page">
    <h2 class="page-title">概览</h2>

    <el-row :gutter="16">
      <el-col :span="12">
        <el-card header="项目信息" class="card">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="项目名称">水利水电工程 - 混凝土课程设计计算平台</el-descriptions-item>
            <el-descriptions-item label="用途">辅助混凝土结构课程设计计算</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card header="柱网布置" class="card">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="总尺寸">L1 × L2 = 18 × 30 m</el-descriptions-item>
            <el-descriptions-item label="梁格尺寸">6 × 6 m</el-descriptions-item>
            <el-descriptions-item label="主梁">横向布置，跨度 6 m</el-descriptions-item>
            <el-descriptions-item label="次梁">纵向布置，跨度 6 m</el-descriptions-item>
            <el-descriptions-item label="柱数量">8 根</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <el-card header="构件截面初估" class="card">
      <el-table :data="sections" border>
        <el-table-column prop="member" label="构件" />
        <el-table-column prop="size" label="截面尺寸" />
      </el-table>
    </el-card>

    <el-card header="材料" class="card">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="混凝土">C25 – C40</el-descriptions-item>
        <el-descriptions-item label="钢筋">HPB300 – HRB500</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup lang="ts">
const sections = [
  { member: '板', size: '厚度 120 mm' },
  { member: '次梁', size: 'b × h = 200 × 500 mm' },
  { member: '主梁', size: 'b × h = 300 × 600 mm' },
]
</script>

<style scoped>
.page {
  padding: 20px;
}
.page-title {
  margin: 0 0 16px;
  font-size: 20px;
  color: var(--el-text-color-primary);
}
.card {
  margin-bottom: 16px;
}
</style>
```

- [ ] **Step 2: 类型检查**

Run: `npx vue-tsc --noEmit`
Expected: 无错误。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Overview.vue
git commit -m "feat: add Overview page with project info and design params"
```

---

## Task 10: 材料参数页 `Materials.vue`（静态展示）

**Files:**
- Create: `frontend/src/views/Materials.vue`

- [ ] **Step 1: 创建 `Materials.vue`**

Create `frontend/src/views/Materials.vue`:
```vue
<template>
  <div class="page">
    <h2 class="page-title">材料参数</h2>

    <el-card header="混凝土强度设计值 (MPa)" class="card">
      <el-table :data="concrete" border>
        <el-table-column prop="grade" label="等级" />
        <el-table-column prop="fc" label="fc（抗压）" />
        <el-table-column prop="ft" label="ft（抗拉）" />
        <el-table-column prop="ec" label="Ec（弹性模量）" />
      </el-table>
    </el-card>

    <el-card header="钢筋强度设计值 (MPa)" class="card">
      <el-table :data="steel" border>
        <el-table-column prop="grade" label="等级" />
        <el-table-column prop="fy" label="fy（屈服强度）" />
      </el-table>
    </el-card>

    <p class="hint">注：本页为静态展示，数据与后端 calc/materials.py 一致。</p>
  </div>
</template>

<script setup lang="ts">
const concrete = [
  { grade: 'C25', fc: 11.9, ft: 1.27, ec: 28000 },
  { grade: 'C30', fc: 14.3, ft: 1.43, ec: 30000 },
  { grade: 'C35', fc: 16.7, ft: 1.57, ec: 31500 },
  { grade: 'C40', fc: 19.1, ft: 1.71, ec: 32500 },
]
const steel = [
  { grade: 'HPB300', fy: 270 },
  { grade: 'HRB335', fy: 300 },
  { grade: 'HRB400', fy: 360 },
  { grade: 'HRB500', fy: 435 },
]
</script>

<style scoped>
.page {
  padding: 20px;
}
.page-title {
  margin: 0 0 16px;
  font-size: 20px;
  color: var(--el-text-color-primary);
}
.card {
  margin-bottom: 16px;
}
.hint {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}
</style>
```

- [ ] **Step 2: 类型检查**

Run: `npx vue-tsc --noEmit`
Expected: 无错误。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Materials.vue
git commit -m "feat: add Materials page with concrete/steel strength tables"
```

---

## Task 11: 六个"建设中"页面

**Files:**
- Create: `frontend/src/views/Slab.vue`
- Create: `frontend/src/views/SecondaryBeam.vue`
- Create: `frontend/src/views/MainBeam.vue`
- Create: `frontend/src/views/Column.vue`
- Create: `frontend/src/views/Report.vue`
- Create: `frontend/src/views/Settings.vue`

- [ ] **Step 1: 创建 6 个页面（均使用 UnderConstruction 组件，仅 title 不同）**

Create `frontend/src/views/Slab.vue`:
```vue
<template>
  <UnderConstruction title="板计算" />
</template>

<script setup lang="ts">
import UnderConstruction from '../components/common/UnderConstruction.vue'
</script>
```

Create `frontend/src/views/SecondaryBeam.vue`:
```vue
<template>
  <UnderConstruction title="次梁计算" />
</template>

<script setup lang="ts">
import UnderConstruction from '../components/common/UnderConstruction.vue'
</script>
```

Create `frontend/src/views/MainBeam.vue`:
```vue
<template>
  <UnderConstruction title="主梁计算" />
</template>

<script setup lang="ts">
import UnderConstruction from '../components/common/UnderConstruction.vue'
</script>
```

Create `frontend/src/views/Column.vue`:
```vue
<template>
  <UnderConstruction title="柱计算" />
</template>

<script setup lang="ts">
import UnderConstruction from '../components/common/UnderConstruction.vue'
</script>
```

Create `frontend/src/views/Report.vue`:
```vue
<template>
  <UnderConstruction title="计算书" />
</template>

<script setup lang="ts">
import UnderConstruction from '../components/common/UnderConstruction.vue'
</script>
```

Create `frontend/src/views/Settings.vue`:
```vue
<template>
  <UnderConstruction title="系统设置" />
</template>

<script setup lang="ts">
import UnderConstruction from '../components/common/UnderConstruction.vue'
</script>
```

- [ ] **Step 2: 类型检查**

Run: `npx vue-tsc --noEmit`
Expected: 无错误。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/views/Slab.vue frontend/src/views/SecondaryBeam.vue frontend/src/views/MainBeam.vue frontend/src/views/Column.vue frontend/src/views/Report.vue frontend/src/views/Settings.vue
git commit -m "feat: add under-construction pages for calc modules"
```

---

## Task 12: 路由改写（AppLayout 嵌套 + 各模块 + 兜底）

**Files:**
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 重写 `router/index.ts`**

将 `frontend/src/router/index.ts` 全文替换为：
```ts
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import AppLayout from '../components/layout/AppLayout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: AppLayout,
    children: [
      { path: '', name: 'overview', component: () => import('../views/Overview.vue') },
      { path: 'materials', name: 'materials', component: () => import('../views/Materials.vue') },
      { path: 'slab', name: 'slab', component: () => import('../views/Slab.vue') },
      { path: 'secondary-beam', name: 'secondary-beam', component: () => import('../views/SecondaryBeam.vue') },
      { path: 'main-beam', name: 'main-beam', component: () => import('../views/MainBeam.vue') },
      { path: 'column', name: 'column', component: () => import('../views/Column.vue') },
      { path: 'report', name: 'report', component: () => import('../views/Report.vue') },
      { path: 'settings', name: 'settings', component: () => import('../views/Settings.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
```

- [ ] **Step 2: 类型检查**

Run: `npx vue-tsc --noEmit`
Expected: 无错误。注意：此步后路由不再引用 `Home.vue`，但仍未删除它（Task 13 删除）。

- [ ] **Step 3: Commit**

```bash
git add frontend/src/router/index.ts
git commit -m "feat: wire app shell layout and all module routes"
```

---

## Task 13: 入口装配（主题预挂载、全局样式、删除 Home.vue）

**Files:**
- Modify: `frontend/src/main.ts`
- Delete: `frontend/src/views/Home.vue`

- [ ] **Step 1: 修改 `main.ts`**

将 `frontend/src/main.ts` 全文替换为：
```ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import './assets/styles/theme.css'
import './assets/styles/index.css'
import App from './App.vue'
import router from './router'

// 挂载前应用初始主题，避免刷新闪烁
const storedTheme = localStorage.getItem('ccd-theme')
const isDark = storedTheme === null ? true : storedTheme === 'dark'
document.documentElement.classList.toggle('dark', isDark)

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
```

- [ ] **Step 2: 删除 `Home.vue`**

Run: `git rm frontend/src/views/Home.vue`
Expected: 文件被删除并暂存。

- [ ] **Step 3: 类型检查 + 全量单测**

Run: `npx vue-tsc --noEmit`
Expected: 无错误。

Run: `npx vitest run`
Expected: 所有 spec 通过。

- [ ] **Step 4: Commit**

```bash
git add frontend/src/main.ts
git commit -m "feat: wire theme pre-mount and global styles; remove Home.vue"
```

（`Home.vue` 的删除已在 Step 2 由 `git rm` 暂存，一并提交。）

---

## Task 14: README 更新 + 最终构建 + 验收

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README 前端结构**

将 `README.md` 中"项目结构"代码块替换为：
```
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py    # 应用入口（/api/health）
│   │   └── calc/      # 计算模块（纯函数）
│   └── requirements.txt
├── frontend/          # Vue 3 + Element Plus 前端
│   └── src/
│       ├── api/           # axios 请求
│       ├── assets/styles/ # 全局样式与主题
│       ├── components/    # layout（外壳）/ common（通用）
│       ├── composables/   # useTheme/useSidebar/useHealth
│       ├── config/        # nav 导航配置
│       ├── router/        # 路由
│       └── views/         # 各模块页面
└── README.md
```

并在"快速启动 > 前端"小节末尾追加一行：
```
测试: npm run test:run
```

- [ ] **Step 2: 最终构建**

Run: `npm run build`
Expected: `vue-tsc -b` 与 `vite build` 均成功，产出 `frontend/dist/`。

- [ ] **Step 3: 手动验收（启动后端 + 前端）**

后端（另一终端，在 `backend/` 下）: `uvicorn app.main:app --reload --port 8000`
前端（在 `frontend/` 下）: `npm run dev`，访问 `http://localhost:3000`，逐条核对 spec 验收标准 1–9：
1. 显示完整 App Shell（顶栏 + 侧边栏 + 主内容区）
2. 侧边栏 8 项，点击切换路由，激活项高亮
3. 侧边栏可折叠/展开；**刷新后折叠状态保持**
4. 主题开关切换 dark/light；**刷新后保持**；无闪烁
5. `/` 概览展示项目信息与设计参数
6. 板/次梁/主梁/柱/计算书/设置 显示"建设中"占位
7. 后端运行时顶栏健康灯绿色；关闭后端则灰色
8. （已在 Step 2 验证）构建通过
9. 后端 `/api/health` 不变

- [ ] **Step 4: Commit**

```bash
git add README.md
git commit -m "docs: update README with frontend structure and test command"
```

---

## Self-Review（计划自检结果）

- **Spec 覆盖**：spec 每节均有对应 task —— 技术栈(Task1)、目录结构(Task2/3/4/5/6/7/8/9/10/11/12/13)、App Shell(Task8)、导航路由(Task2+Task12)、主题(Task3+Task7+Task13)、API/数据层(Task5+Task6)、迁移(Task13 删 Home、Task14 更新 README、其余保留配置)、验收(Task14)。
- **占位扫描**：无 TBD/TODO；每个步骤均含完整代码或确切命令。
- **类型一致性**：`useTheme()` 返回 `{ isDark, toggle }`、`useSidebar()` 返回 `{ isCollapsed, toggle }`、`useHealth()` 返回 `{ isOnline, start, stop }`、`getHealth()` 返回 `HealthResponse`，在组件与测试中引用一致；`NAV_ITEMS` 字段（path/title/icon/underConstruction）在 nav、AppSidebar、Overview 一致。
- **已知简化**（已写入 spec 第 11 节"后续"）：仅覆盖 `--el-color-primary` 主色，未生成完整色阶；无 warm 主题；无 SSE。
