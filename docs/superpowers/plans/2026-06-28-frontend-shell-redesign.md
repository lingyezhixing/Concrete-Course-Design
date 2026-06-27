# Frontend Shell & Theme Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the app shell and theme system to match LLM-Manager's restrained three-theme aesthetic on Vue + Element Plus, remove the column module, clear dead code, and reduce all pages to PageHeader-only frames.

**Architecture:** Keep Vue 3 + Element Plus. Add a single `tokens.css` design-system stylesheet: three `[data-theme]` palettes (dark/light/warm) of semantic tokens, plus an Element Plus bridge that drives EP's `--el-*` variables (including `color-mix()`-derived shade ramps) from those tokens so EP components follow the theme. Rebuild the shell (AppLayout/AppHeader/AppSidebar) as plain semantic markup styled by tokens, add a ThemeSwitcher and a reusable PageHeader, and rewrite `useTheme` as a 3-state module singleton.

**Tech Stack:** Vue 3.5 + TypeScript + Element Plus 2.9 + Vite 6 + Vitest 3 (frontend); Python 3.12 + FastAPI + Pydantic (backend).

**Spec:** `docs/superpowers/specs/2026-06-28-frontend-shell-redesign-design.md`

**Branch:** `frontend-shell-redesign` (already created and checked out)

---

## Verification commands (used throughout)

- Frontend unit tests: `cd frontend && npm run test:run`
- Frontend typecheck + build: `cd frontend && npm run build`
- Backend tests: `cd backend && python -m pytest tests/ -q`
- Frontend dev server (manual visual check): `cd frontend && npm run dev` → http://localhost:5173 (Vite default port; confirm from dev server output)

> **Note on the color-mix refinement:** The spec (§4.2) suggested pre-computing and hardcoding EP's `light-N`/`dark-2` shade values per theme. This plan instead derives them with CSS `color-mix(in srgb, var(--primary) N%, var(--card))` defined once. Because `--card` is pure white in the light/warm themes, this reproduces EP's exact shade math there; in the dark theme it yields correct dark tints automatically. One definition serves all three themes — DRY and drift-free. This fully satisfies the spec's intent (correct per-theme shade rendering).

---

## Task 1: Backend — delete dead empty files and the column/beam module scaffolding

**Why first:** Removes 0-byte dead files and the column module before touching anything live. The slab solver (the only real backend asset) is untouched.

**Files:**
- Delete: `backend/app/api/column.py`, `backend/app/api/beam.py`, `backend/app/api/slab.py` (all empty)
- Delete: `backend/app/models/column.py`, `backend/app/models/beam.py` (both empty)
- Delete: `backend/app/solvers/column/` (entire dir: `__init__.py`, `solver.py`, `utils.py` — all empty)
- Delete: `backend/app/solvers/beam/` (entire dir: `__init__.py`, `solver.py`, `utils.py` — all empty)

- [ ] **Step 1: Delete the files and directories**

Run from the repo root:
```bash
cd backend
rm app/api/column.py app/api/beam.py app/api/slab.py
rm app/models/column.py app/models/beam.py
rm -r app/solvers/column app/solvers/beam
```

- [ ] **Step 2: Verify nothing references the deleted modules**

Run: `cd backend && grep -rn "column\|solvers.beam\|models.beam\|api.beam\|api.column" app/ || echo "no references"`
Expected: `no references` (main.py only imports `health`; the deleted modules were never wired in).

- [ ] **Step 3: Verify backend tests still pass**

Run: `cd backend && python -m pytest tests/ -q`
Expected: `21 passed` (slab coefficient tests are unaffected — they test `solvers/slab/utils.py`, which still exists).

- [ ] **Step 4: Commit**

```bash
git add -A backend
git commit -m "refactor: remove dead empty files and column/beam scaffolding from backend"
```

---

## Task 2: Backend — remove the dead `structure_factor` field from SlabInput

**Why:** The structure factor was removed from the solver in commit `0c40c98`, but the `SlabInput.structure_factor` field (default `1.2`) was left behind, unused. It is dead.

**Files:**
- Modify: `backend/app/models/slab.py` (remove the `structure_factor` field, lines ~35-37)

- [ ] **Step 1: Remove the field**

In `backend/app/models/slab.py`, delete these two lines from the `# 分项系数` block:

```python
    structure_factor: float = Field(default=1.2, description="结构系数")
```

The `# 分项系数` section should now contain only:
```python
    # 分项系数
    dead_load_factor: float = Field(default=1.05, description="恒载分项系数")
    live_load_factor: float = Field(default=1.2, description="活载分项系数")
```

- [ ] **Step 2: Verify no code references `structure_factor`**

Run: `cd backend && grep -rn "structure_factor" app/ tests/ || echo "no references"`
Expected: `no references` (the solver never used it).

- [ ] **Step 3: Verify backend tests still pass**

Run: `cd backend && python -m pytest tests/ -q`
Expected: `21 passed`.

- [ ] **Step 4: Commit**

```bash
git add backend/app/models/slab.py
git commit -m "refactor: remove dead structure_factor field from SlabInput"
```

---

## Task 3: Frontend — create the design-system stylesheet and rewire main.ts

**Why:** This is the foundation. Once `tokens.css` exists and `main.ts` imports it (and drops EP's dark css-vars + the old theme.css/index.css), the whole app runs on the new three-theme token system.

**Files:**
- Create: `frontend/src/assets/styles/tokens.css`
- Modify: `frontend/src/main.ts`
- Delete: `frontend/src/assets/styles/theme.css`, `frontend/src/assets/styles/index.css` (superseded by tokens.css)

- [ ] **Step 1: Create `tokens.css`**

Create `frontend/src/assets/styles/tokens.css` with this exact content:

```css
/* ============================================================
   设计令牌 + Element Plus 桥接（单一设计系统样式表）
   原则（参考 LLM-Manager）：无渐变、无毛玻璃、无多余动效；
   单一强调色；真实的组件镀铬（边框 + 底色），不裸奔。
   三主题由 [data-theme="dark|light|warm"] 驱动；EP 组件通过
   下面的 --el-* 变量自动跟随主题。
   ============================================================ */

/* ---- 语义令牌：深色（默认） ---- */
:root,
[data-theme='dark'] {
  --background: #0d1117;
  --foreground: #e6edf3;
  --card: #161b22;
  --card-foreground: #e6edf3;
  --popover: #161b22;
  --popover-foreground: #e6edf3;
  --primary: #6b8cff;
  --primary-foreground: #ffffff;
  --secondary: #21262d;
  --secondary-foreground: #e6edf3;
  --muted: #21262d;
  --muted-foreground: #8b949e;
  --accent: #21262d;
  --accent-foreground: #e6edf3;
  --destructive: #f85149;
  --destructive-foreground: #ffffff;
  --success: #3fb950;
  --success-foreground: #0d1117;
  --warning: #d29922;
  --warning-foreground: #0d1117;
  --border: #262c36;
  --input: #262c36;
  --ring: #6b8cff;
  --radius: 0.625rem;
}

/* ---- 语义令牌：浅色 ---- */
[data-theme='light'] {
  --background: #f6f7f9;
  --foreground: #16181d;
  --card: #ffffff;
  --card-foreground: #16181d;
  --popover: #ffffff;
  --popover-foreground: #16181d;
  --primary: #4f46e5;
  --primary-foreground: #ffffff;
  --secondary: #eef0f3;
  --secondary-foreground: #16181d;
  --muted: #eef0f3;
  --muted-foreground: #6b7280;
  --accent: #eef0f3;
  --accent-foreground: #16181d;
  --destructive: #dc2626;
  --destructive-foreground: #ffffff;
  --success: #16a34a;
  --success-foreground: #ffffff;
  --warning: #b45309;
  --warning-foreground: #ffffff;
  --border: #e7e8ec;
  --input: #e7e8ec;
  --ring: #4f46e5;
  --radius: 0.75rem;
}

/* ---- 语义令牌：暖灰 ---- */
[data-theme='warm'] {
  --background: #f6f2ec;
  --foreground: #3b352b;
  --card: #fffdf8;
  --card-foreground: #3b352b;
  --popover: #fffdf8;
  --popover-foreground: #3b352b;
  --primary: #8a6d52;
  --primary-foreground: #ffffff;
  --secondary: #ece4d6;
  --secondary-foreground: #3b352b;
  --muted: #ece4d6;
  --muted-foreground: #9a8f7d;
  --accent: #ece4d6;
  --accent-foreground: #3b352b;
  --destructive: #b5462f;
  --destructive-foreground: #ffffff;
  --success: #6f8f5a;
  --success-foreground: #ffffff;
  --warning: #a47a3b;
  --warning-foreground: #ffffff;
  --border: #e8e0d3;
  --input: #e8e0d3;
  --ring: #8a6d52;
  --radius: 0.75rem;
}

/* ---- Element Plus 桥接：定义在 :root，引用上面的语义令牌；
   data-theme 切换时 color-mix/var 自动重算，三个主题共用一套定义。 ---- */
:root {
  /* 主色 + 色阶（light/warm 混入 card=白=EP 原始算法；dark 混入深色 card 得暗色 tint） */
  --el-color-primary: var(--primary);
  --el-color-primary-light-3: color-mix(in srgb, var(--primary) 70%, var(--card));
  --el-color-primary-light-5: color-mix(in srgb, var(--primary) 50%, var(--card));
  --el-color-primary-light-7: color-mix(in srgb, var(--primary) 30%, var(--card));
  --el-color-primary-light-8: color-mix(in srgb, var(--primary) 20%, var(--card));
  --el-color-primary-light-9: color-mix(in srgb, var(--primary) 10%, var(--card));
  --el-color-primary-dark-2: color-mix(in srgb, var(--primary) 80%, #000);

  --el-color-success: var(--success);
  --el-color-success-light-3: color-mix(in srgb, var(--success) 70%, var(--card));
  --el-color-success-light-5: color-mix(in srgb, var(--success) 50%, var(--card));
  --el-color-success-light-7: color-mix(in srgb, var(--success) 30%, var(--card));
  --el-color-success-light-8: color-mix(in srgb, var(--success) 20%, var(--card));
  --el-color-success-light-9: color-mix(in srgb, var(--success) 10%, var(--card));

  --el-color-warning: var(--warning);
  --el-color-warning-light-3: color-mix(in srgb, var(--warning) 70%, var(--card));
  --el-color-warning-light-5: color-mix(in srgb, var(--warning) 50%, var(--card));
  --el-color-warning-light-7: color-mix(in srgb, var(--warning) 30%, var(--card));
  --el-color-warning-light-8: color-mix(in srgb, var(--warning) 20%, var(--card));
  --el-color-warning-light-9: color-mix(in srgb, var(--warning) 10%, var(--card));

  --el-color-danger: var(--destructive);
  --el-color-error: var(--destructive);
  --el-color-danger-light-3: color-mix(in srgb, var(--destructive) 70%, var(--card));
  --el-color-danger-light-5: color-mix(in srgb, var(--destructive) 50%, var(--card));
  --el-color-danger-light-7: color-mix(in srgb, var(--destructive) 30%, var(--card));
  --el-color-danger-light-8: color-mix(in srgb, var(--destructive) 20%, var(--card));
  --el-color-danger-light-9: color-mix(in srgb, var(--destructive) 10%, var(--card));
  --el-color-error-light-3: color-mix(in srgb, var(--destructive) 70%, var(--card));
  --el-color-error-light-5: color-mix(in srgb, var(--destructive) 50%, var(--card));
  --el-color-error-light-7: color-mix(in srgb, var(--destructive) 30%, var(--card));
  --el-color-error-light-8: color-mix(in srgb, var(--destructive) 20%, var(--card));
  --el-color-error-light-9: color-mix(in srgb, var(--destructive) 10%, var(--card));

  /* 背景 / 填充 */
  --el-bg-color: var(--card);
  --el-bg-color-page: var(--background);
  --el-bg-color-overlay: var(--popover);
  --el-fill-color: var(--muted);
  --el-fill-color-light: var(--muted);
  --el-fill-color-lighter: var(--muted);
  --el-fill-color-extra-light: var(--muted);
  --el-fill-color-blank: var(--card);
  --el-fill-color-dark: var(--secondary);

  /* 文本 */
  --el-text-color-primary: var(--foreground);
  --el-text-color-regular: var(--foreground);
  --el-text-color-secondary: var(--muted-foreground);
  --el-text-color-placeholder: var(--muted-foreground);
  --el-text-color-disabled: color-mix(in srgb, var(--muted-foreground) 60%, var(--card));

  /* 边框 */
  --el-border-color: var(--border);
  --el-border-color-light: var(--border);
  --el-border-color-lighter: var(--border);
  --el-border-color-extra-light: var(--border);
  --el-border-color-hover: var(--muted-foreground);
  --el-border-color-darker: var(--border);

  /* 圆角（克制） */
  --el-border-radius-base: var(--radius);
  --el-border-radius-small: calc(var(--radius) - 4px);
  --el-border-radius-round: calc(var(--radius) + 8px);
  --el-border-radius-circle: 50%;

  /* 阴影：极淡，靠边框分隔而非阴影 */
  --el-box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --el-box-shadow-light: 0 2px 4px 0 rgba(0, 0, 0, 0.05);
  --el-box-shadow-lighter: 0 1px 2px 0 rgba(0, 0, 0, 0.04);
  --el-box-shadow-dark: 0 2px 6px 0 rgba(0, 0, 0, 0.12);

  /* 禁用 / 遮罩 */
  --el-disabled-bg-color: var(--muted);
  --el-disabled-text-color: var(--muted-foreground);
  --el-disabled-border-color: var(--border);
  --el-mask-color: color-mix(in srgb, var(--background) 80%, transparent);
}

/* ---- 全局基底 ---- */
html,
body,
#app {
  height: 100%;
  margin: 0;
}
body {
  background: var(--background);
  color: var(--foreground);
  font-family: system-ui, -apple-system, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
}
* {
  box-sizing: border-box;
}

/* ---- 细滚动条（主题感知） ---- */
* {
  scrollbar-width: thin;
  scrollbar-color: var(--border) transparent;
}
*::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
*::-webkit-scrollbar-track {
  background: transparent;
}
*::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 9999px;
}
*::-webkit-scrollbar-thumb:hover {
  background: var(--muted-foreground);
}
```

- [ ] **Step 2: Sanity-check the stylesheet for duplicate declarations**

Run: `cd frontend && grep -c "color-primary-light-7" src/assets/styles/tokens.css`
Expected: `1` (each shade appears exactly once). If it prints more than 1, remove the duplicate line.

- [ ] **Step 3: Rewrite `main.ts`**

Replace the entire contents of `frontend/src/main.ts` with:

```ts
import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/tokens.css'
import App from './App.vue'
import router from './router'

// 挂载前应用初始主题，避免刷新闪烁
const storedTheme = localStorage.getItem('ccd-theme')
const theme = storedTheme === 'light' || storedTheme === 'warm' ? storedTheme : 'dark'
document.documentElement.dataset.theme = theme

const app = createApp(App)
app.use(ElementPlus)
app.use(router)
app.mount('#app')
```

This drops `element-plus/theme-chalk/dark/css-vars.css`, `theme.css`, and `index.css` — dark mode is now driven entirely by `tokens.css`.

- [ ] **Step 4: Delete the two superseded stylesheets**

Run:
```bash
rm frontend/src/assets/styles/theme.css frontend/src/assets/styles/index.css
```

- [ ] **Step 5: Verify no stale imports remain**

Run: `cd frontend && grep -rn "theme.css\|index.css\|dark/css-vars" src/ || echo "no stale imports"`
Expected: `no stale imports`.

- [ ] **Step 6: Verify the app builds**

Run: `cd frontend && npm run build`
Expected: build succeeds (`vue-tsc` typecheck + `vite build`), no errors. (The app is mid-refactor — pages still reference `UnderConstruction`, which still exists — so this should pass.)

- [ ] **Step 7: Commit**

```bash
git add -A frontend/src/assets/styles frontend/src/main.ts
git commit -m "feat: add three-theme design token system and rewire main.ts"
```

---

## Task 4: Frontend — rewrite `useTheme` as a 3-state singleton (TDD)

**Why:** The theme system moves from a dark/light boolean (`html.dark` class) to dark/light/warm three-state (`data-theme` attribute), matching LLM-Manager. TDD: rewrite the test first, watch it fail against the old impl, then implement.

**Files:**
- Modify (test first): `frontend/src/composables/useTheme.spec.ts`
- Modify (impl): `frontend/src/composables/useTheme.ts`

- [ ] **Step 1: Replace the test file**

Replace the entire contents of `frontend/src/composables/useTheme.spec.ts` with:

```ts
import { describe, it, expect, beforeEach, vi } from 'vitest'

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.removeAttribute('data-theme')
    vi.resetModules()
  })

  it('defaults to dark when nothing stored', async () => {
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('dark')
  })

  it('reads stored light theme', async () => {
    localStorage.setItem('ccd-theme', 'light')
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('light')
  })

  it('reads stored warm theme', async () => {
    localStorage.setItem('ccd-theme', 'warm')
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('warm')
  })

  it('falls back to dark when stored value is invalid', async () => {
    localStorage.setItem('ccd-theme', 'neon')
    const { useTheme } = await import('./useTheme')
    const { theme } = useTheme()
    expect(theme.value).toBe('dark')
  })

  it('applies data-theme on init', async () => {
    await import('./useTheme')
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')
  })

  it('setTheme updates value, persists, and applies data-theme', async () => {
    const { useTheme } = await import('./useTheme')
    const { theme, setTheme } = useTheme()
    setTheme('warm')
    expect(theme.value).toBe('warm')
    expect(localStorage.getItem('ccd-theme')).toBe('warm')
    expect(document.documentElement.getAttribute('data-theme')).toBe('warm')
  })

  it('shares one state across multiple useTheme() calls', async () => {
    const { useTheme } = await import('./useTheme')
    const a = useTheme()
    const b = useTheme()
    a.setTheme('light')
    expect(b.theme.value).toBe('light')
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npm run test:run -- useTheme`
Expected: FAIL — the old `useTheme` exports `{ isDark, toggle }`, not `{ theme, setTheme }`, so `theme` is `undefined` and the dark-state assertions break.

- [ ] **Step 3: Rewrite `useTheme.ts`**

Replace the entire contents of `frontend/src/composables/useTheme.ts` with:

```ts
import { ref } from 'vue'

export type Theme = 'dark' | 'light' | 'warm'

const STORAGE_KEY = 'ccd-theme'
const DEFAULT_THEME: Theme = 'dark'
const VALID: ReadonlySet<Theme> = new Set(['dark', 'light', 'warm'])

function readTheme(): Theme {
  const stored = localStorage.getItem(STORAGE_KEY)
  return stored && VALID.has(stored as Theme) ? (stored as Theme) : DEFAULT_THEME
}

function applyTheme(next: Theme): void {
  document.documentElement.dataset.theme = next
}

// 模块级单例：所有 useTheme() 调用共享同一主题状态
const theme = ref<Theme>(readTheme())
applyTheme(theme.value)

export function useTheme() {
  function setTheme(next: Theme): void {
    theme.value = next
    localStorage.setItem(STORAGE_KEY, next)
    applyTheme(next)
  }
  return { theme, setTheme }
}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd frontend && npm run test:run -- useTheme`
Expected: PASS — all 7 useTheme tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/composables/useTheme.ts frontend/src/composables/useTheme.spec.ts
git commit -m "feat: rewrite useTheme as a three-state (dark/light/warm) singleton"
```

---

## Task 5: Frontend — update nav config to 7 items, drop column and the underConstruction flag (TDD)

**Why:** Column is removed and `underConstruction` is no longer used (pages become PageHeader frames). Update the test first.

**Files:**
- Modify (test first): `frontend/src/config/nav.spec.ts`
- Modify (impl): `frontend/src/config/nav.ts`

- [ ] **Step 1: Replace the test file**

Replace the entire contents of `frontend/src/config/nav.spec.ts` with:

```ts
import { describe, it, expect } from 'vitest'
import { NAV_ITEMS } from './nav'

describe('nav config', () => {
  it('has 7 items', () => {
    expect(NAV_ITEMS).toHaveLength(7)
  })

  it('every item has path, title, and icon', () => {
    for (const item of NAV_ITEMS) {
      expect(typeof item.path).toBe('string')
      expect(item.path.length).toBeGreaterThan(0)
      expect(typeof item.title).toBe('string')
      expect(item.title.length).toBeGreaterThan(0)
      expect(item.icon).toBeTruthy()
    }
  })

  it('paths are unique', () => {
    const paths = NAV_ITEMS.map((i) => i.path)
    expect(new Set(paths).size).toBe(paths.length)
  })

  it('contains overview at "/"', () => {
    expect(NAV_ITEMS.some((i) => i.path === '/')).toBe(true)
  })

  it('does not contain column', () => {
    expect(NAV_ITEMS.some((i) => i.path === '/column')).toBe(false)
  })
})
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `cd frontend && npm run test:run -- nav`
Expected: FAIL — old nav has 8 items and each item has an `underConstruction` boolean (the new test no longer asserts that, but `has 7 items` fails since there are 8).

- [ ] **Step 3: Rewrite `nav.ts`**

Replace the entire contents of `frontend/src/config/nav.ts` with:

```ts
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd frontend && npm run test:run -- nav`
Expected: PASS — all 5 nav tests pass.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/config/nav.ts frontend/src/config/nav.spec.ts
git commit -m "feat: trim nav to 7 items, drop column and underConstruction flag"
```

---

## Task 6: Frontend — add the reusable PageHeader component

**Why:** A unified per-page header (title + optional muted subtitle + optional action slot) is part of the "frame." All cleared pages will use it.

**Files:**
- Create: `frontend/src/components/common/PageHeader.vue`

- [ ] **Step 1: Create the component**

Create `frontend/src/components/common/PageHeader.vue` with:

```vue
<template>
  <div class="page-header">
    <div class="titles">
      <h1 class="title">{{ title }}</h1>
      <p v-if="subtitle" class="subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.action" class="action">
      <slot name="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}
.title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--foreground);
}
.subtitle {
  margin: 4px 0 0;
  font-size: 13px;
  color: var(--muted-foreground);
}
.action {
  flex-shrink: 0;
}
</style>
```

- [ ] **Step 2: Verify the build**

Run: `cd frontend && npm run build`
Expected: build succeeds (the component is unused so far — that's fine; it has no type errors).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/common/PageHeader.vue
git commit -m "feat: add reusable PageHeader component"
```

---

## Task 7: Frontend — add the ThemeSwitcher component

**Why:** The three-button deep/light/warm switcher (matching LLM-Manager) lives in the top bar.

**Files:**
- Create: `frontend/src/components/layout/ThemeSwitcher.vue`

- [ ] **Step 1: Create the component**

Create `frontend/src/components/layout/ThemeSwitcher.vue` with:

```vue
<template>
  <div class="theme-switcher">
    <button
      v-for="opt in OPTIONS"
      :key="opt.value"
      type="button"
      class="opt"
      :class="{ active: theme === opt.value }"
      :title="opt.label"
      @click="setTheme(opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useTheme, type Theme } from '../../composables/useTheme'

const OPTIONS: ReadonlyArray<{ value: Theme; label: string }> = [
  { value: 'dark', label: '深色' },
  { value: 'light', label: '浅色' },
  { value: 'warm', label: '暖灰' },
]

const { theme, setTheme } = useTheme()
</script>

<style scoped>
.theme-switcher {
  display: flex;
  gap: 4px;
}
.opt {
  height: 28px;
  padding: 0 10px;
  font-size: 13px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: transparent;
  color: var(--muted-foreground);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
}
.opt:hover {
  background: var(--muted);
  color: var(--foreground);
}
.opt.active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--primary-foreground);
}
</style>
```

- [ ] **Step 2: Verify the build**

Run: `cd frontend && npm run build`
Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/layout/ThemeSwitcher.vue
git commit -m "feat: add three-button ThemeSwitcher"
```

---

## Task 8: Frontend — rebuild AppLayout with token-driven semantic markup

**Why:** Replace the EP `el-container/el-header/el-aside/el-main` shell with plain semantic markup styled by tokens, matching LLM-Manager's `app-shell.tsx` structure (TopBar over a [Sidebar | main] row).

**Files:**
- Modify: `frontend/src/components/layout/AppLayout.vue`

- [ ] **Step 1: Rewrite `AppLayout.vue`**

Replace the entire contents of `frontend/src/components/layout/AppLayout.vue` with:

```vue
<template>
  <div class="app-layout">
    <AppHeader :collapsed="isCollapsed" @toggle="toggle" />
    <div class="app-body">
      <AppSidebar :collapsed="isCollapsed" />
      <main class="app-main">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'
import { useSidebar } from '../../composables/useSidebar'

const { isCollapsed, toggle } = useSidebar()
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: var(--background);
  color: var(--foreground);
}
.app-body {
  display: flex;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.app-main {
  flex: 1;
  min-width: 0;
  overflow-y: auto;
  padding: 24px;
}
</style>
```

- [ ] **Step 2: Verify the build**

Run: `cd frontend && npm run build`
Expected: build succeeds. (`AppHeader`/`AppSidebar` still accept `collapsed`/emit `toggle`, so prop contracts hold.)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/layout/AppLayout.vue
git commit -m "feat: rebuild AppLayout as token-driven flex shell"
```

---

## Task 9: Frontend — rebuild AppSidebar with a custom router-link nav

**Why:** Drop `el-menu` (whose default styling fights the target look) for a custom `<router-link>` nav that reproduces LLM-Manager's active state exactly: 2px primary left-accent + muted background + foreground text. Uses the trimmed `NAV_ITEMS` from Task 5.

**Files:**
- Modify: `frontend/src/components/layout/AppSidebar.vue`

- [ ] **Step 1: Rewrite `AppSidebar.vue`**

Replace the entire contents of `frontend/src/components/layout/AppSidebar.vue` with:

```vue
<template>
  <aside class="sidebar" :class="{ collapsed }">
    <nav class="nav">
      <router-link
        v-for="item in NAV_ITEMS"
        :key="item.path"
        :to="item.path"
        class="nav-item"
        :class="{ collapsed }"
        :title="collapsed ? item.title : undefined"
      >
        <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
        <span v-if="!collapsed" class="nav-label">{{ item.title }}</span>
      </router-link>
    </nav>
  </aside>
</template>

<script setup lang="ts">
import { NAV_ITEMS } from '../../config/nav'

defineProps<{ collapsed: boolean }>()
</script>

<style scoped>
.sidebar {
  flex-shrink: 0;
  width: 208px;
  background: var(--card);
  border-right: 1px solid var(--border);
  transition: width 0.15s ease;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 56px;
}
.nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-left: 2px solid transparent;
  border-radius: var(--radius);
  font-size: 14px;
  color: var(--muted-foreground);
  text-decoration: none;
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
}
.nav-item:hover {
  background: var(--muted);
  color: var(--foreground);
}
/* exact-active so the "/" item is only highlighted on the overview page,
   not on every page (router-link-active would prefix-match "/"). */
.nav-item.router-link-exact-active {
  border-left-color: var(--primary);
  background: var(--muted);
  color: var(--foreground);
  font-weight: 500;
}
.nav-item.collapsed {
  justify-content: center;
  padding: 8px 0;
  border-left: none;
}
.nav-item.collapsed.router-link-exact-active {
  color: var(--primary);
}
.nav-icon {
  flex-shrink: 0;
  font-size: 16px;
}
.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
```

- [ ] **Step 2: Verify the build**

Run: `cd frontend && npm run build`
Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/layout/AppSidebar.vue
git commit -m "feat: rebuild AppSidebar as custom router-link nav with active accent"
```

---

## Task 10: Frontend — rebuild AppHeader as the TopBar (LED + collapse + ThemeSwitcher)

**Why:** Replace the simple health dot with the CSS-drawn health LED (green frame + dot when online, hollow red frame when offline — matching LLM-Manager so online/offline render at identical size), and host the ThemeSwitcher on the right.

**Files:**
- Modify: `frontend/src/components/layout/AppHeader.vue`

- [ ] **Step 1: Rewrite `AppHeader.vue`**

Replace the entire contents of `frontend/src/components/layout/AppHeader.vue` with:

```vue
<template>
  <header class="topbar">
    <div class="left">
      <span class="brand" :title="isOnline ? '后端已连接' : '后端连接中断'">
        <span class="led" :class="isOnline ? 'on' : 'off'">
          <span v-if="isOnline" class="led-dot" />
        </span>
        <span class="brand-text">混凝土课程设计计算平台</span>
      </span>
      <button
        type="button"
        class="collapse-btn"
        :aria-label="collapsed ? '展开侧栏' : '收起侧栏'"
        :title="collapsed ? '展开侧栏' : '收起侧栏'"
        @click="emit('toggle')"
      >
        <el-icon :size="16"><component :is="collapsed ? Expand : Fold" /></el-icon>
      </button>
    </div>
    <div class="right">
      <ThemeSwitcher />
    </div>
  </header>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { Fold, Expand } from '@element-plus/icons-vue'
import { useHealth } from '../../composables/useHealth'
import ThemeSwitcher from './ThemeSwitcher.vue'

defineProps<{ collapsed: boolean }>()
const emit = defineEmits<{ toggle: [] }>()

const { isOnline, start, stop } = useHealth()

onMounted(start)
onUnmounted(stop)
</script>

<style scoped>
.topbar {
  flex-shrink: 0;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
}
.left,
.right {
  display: flex;
  align-items: center;
}
.left {
  gap: 4px;
}
.brand {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 4px;
  color: var(--foreground);
}
.brand-text {
  font-size: 15px;
  font-weight: 600;
  letter-spacing: -0.01em;
}
.led {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 14px;
  height: 14px;
  border: 2px solid var(--success);
  border-radius: 2px;
}
.led.off {
  border-color: var(--destructive);
}
.led-dot {
  width: 6px;
  height: 6px;
  border-radius: 1px;
  background: var(--success);
}
.collapse-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: var(--radius);
  color: var(--muted-foreground);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
}
.collapse-btn:hover {
  background: var(--muted);
  color: var(--foreground);
}
</style>
```

- [ ] **Step 2: Verify the build**

Run: `cd frontend && npm run build`
Expected: build succeeds.

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/layout/AppHeader.vue
git commit -m "feat: rebuild AppHeader as TopBar with CSS health LED and ThemeSwitcher"
```

---

## Task 11: Frontend — remove the column route from the router

**Why:** With column gone, its route must go too (otherwise navigating to `/column` would 404-redirect to `/`, and the lazy import would point at a deleted file).

**Files:**
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: Rewrite `router/index.ts`**

Replace the entire contents of `frontend/src/router/index.ts` with:

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

- [ ] **Step 2: Verify the build**

Run: `cd frontend && npm run build`
Expected: build succeeds. (Note: `Column.vue` still exists at this point but is no longer routed — it is deleted in Task 12.)

- [ ] **Step 3: Commit**

```bash
git add frontend/src/router/index.ts
git commit -m "refactor: remove column route from router"
```

---

## Task 12: Frontend — clear all pages to PageHeader-only frames; delete Column.vue and UnderConstruction.vue

**Why:** With the frame complete, reduce every page to just a `PageHeader` (title + subtitle, no functional content) and remove the now-unused `Column.vue` and `UnderConstruction.vue`.

**Files:**
- Modify: `frontend/src/views/Overview.vue`, `Materials.vue`, `Slab.vue`, `SecondaryBeam.vue`, `MainBeam.vue`, `Report.vue`, `Settings.vue`
- Delete: `frontend/src/views/Column.vue`, `frontend/src/components/common/UnderConstruction.vue`

- [ ] **Step 1: Rewrite Overview.vue**

Replace the entire contents of `frontend/src/views/Overview.vue` with:

```vue
<template>
  <PageHeader title="概览" subtitle="项目与设计参数总览（待实现）" />
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
</script>
```

- [ ] **Step 2: Rewrite Materials.vue**

Replace the entire contents of `frontend/src/views/Materials.vue` with:

```vue
<template>
  <PageHeader title="材料参数" subtitle="混凝土与钢筋强度（待实现）" />
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
</script>
```

- [ ] **Step 3: Rewrite Slab.vue**

Replace the entire contents of `frontend/src/views/Slab.vue` with:

```vue
<template>
  <PageHeader title="板计算" subtitle="连续板荷载与内力计算（待实现）" />
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
</script>
```

- [ ] **Step 4: Rewrite SecondaryBeam.vue**

Replace the entire contents of `frontend/src/views/SecondaryBeam.vue` with:

```vue
<template>
  <PageHeader title="次梁计算" subtitle="次梁内力与配筋（待实现）" />
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
</script>
```

- [ ] **Step 5: Rewrite MainBeam.vue**

Replace the entire contents of `frontend/src/views/MainBeam.vue` with:

```vue
<template>
  <PageHeader title="主梁计算" subtitle="主梁内力与配筋（待实现）" />
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
</script>
```

- [ ] **Step 6: Rewrite Report.vue**

Replace the entire contents of `frontend/src/views/Report.vue` with:

```vue
<template>
  <PageHeader title="计算书" subtitle="自动生成设计计算书（待实现）" />
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
</script>
```

- [ ] **Step 7: Rewrite Settings.vue**

Replace the entire contents of `frontend/src/views/Settings.vue` with:

```vue
<template>
  <PageHeader title="系统设置" subtitle="系统与主题偏好（待实现）" />
</template>

<script setup lang="ts">
import PageHeader from '../components/common/PageHeader.vue'
</script>
```

- [ ] **Step 8: Delete Column.vue and UnderConstruction.vue**

Run:
```bash
rm frontend/src/views/Column.vue frontend/src/components/common/UnderConstruction.vue
```

- [ ] **Step 9: Verify nothing references the deleted files or `underConstruction`**

Run: `cd frontend && grep -rn "UnderConstruction\|Column.vue\|underConstruction" src/ || echo "no references"`
Expected: `no references`.

- [ ] **Step 10: Verify the build**

Run: `cd frontend && npm run build`
Expected: build succeeds.

- [ ] **Step 11: Commit**

```bash
git add -A frontend/src/views frontend/src/components/common
git commit -m "refactor: clear pages to PageHeader-only frames, remove Column and UnderConstruction"
```

---

## Task 13: Final verification

**Why:** Confirm the whole change set hangs together — all unit tests pass, both projects build, and the three themes render correctly in the browser.

- [ ] **Step 1: Run all frontend unit tests**

Run: `cd frontend && npm run test:run`
Expected: all tests pass (useTheme ×7, nav ×5, useSidebar ×3, useHealth ×4, health ×1).

- [ ] **Step 2: Run the frontend production build**

Run: `cd frontend && npm run build`
Expected: `vue-tsc` typecheck passes, `vite build` produces `dist/` with no errors.

- [ ] **Step 3: Run all backend tests**

Run: `cd backend && python -m pytest tests/ -q`
Expected: `21 passed`.

- [ ] **Step 4: Manual visual verification in the browser**

Start the dev server: `cd frontend && npm run dev` (and the backend: `cd backend && uvicorn app.main:app --reload --port 8000`, or use the project's `start-backend.bat`).

Open the app URL shown by Vite. Confirm:
1. Default theme is dark; background `#0d1117`, card `#161b22`, primary accent `#6b8cff`.
2. Clicking 深色 / 浅色 / 暖灰 switches all chrome (top bar, sidebar, page header text) and persists across a hard refresh (no flash on reload).
3. Health LED: green filled frame while the backend is up; hollow red frame when the backend is stopped.
4. Sidebar active item shows the 2px primary left-accent + muted fill; the 概览 ("/") item is highlighted only on the overview page, not on other pages.
5. Collapse toggle («) shrinks the sidebar to an icon rail and back.
6. No `/column` item in the sidebar; visiting `/column` redirects to `/`.
7. Every page shows only its PageHeader (title + muted subtitle), no leftover content, no "建设中" placeholders.

- [ ] **Step 5: Commit any final tweaks (if made during visual verification)**

If small CSS value tweaks were made during visual verification, commit them:
```bash
git add -A frontend
git commit -m "style: final visual tweaks to shell and tokens"
```
(If no tweaks were needed, skip this step.)

---

## Done

When all tasks are complete:
- Three-theme token system drives Element Plus via `tokens.css`.
- Shell matches LLM-Manager's restrained aesthetic (LED, active accent, thin scrollbars, no gradients).
- Column is gone from frontend and backend; dead empty files and the `structure_factor` field are removed.
- All pages are clean PageHeader-only frames, ready for module implementation.
- All frontend tests pass; the production build succeeds; all 21 backend tests pass.
