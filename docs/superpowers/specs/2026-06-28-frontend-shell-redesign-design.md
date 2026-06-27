# 前端外壳与主题体系重构 — 设计文档

- **日期**: 2026-06-28
- **状态**: 已批准（待实现）
- **作者**: 设计协作（用户 + Claude）
- **关联项目**: 水利水电工程 - 混凝土课程设计计算平台

---

## 1. 背景与目标

当前前端外壳（`AppLayout` / `AppHeader` / `AppSidebar`）参考了 `E:\Programming\pycodes\Projects\LLM-Manager` 实现，但存在两个问题：

1. **视觉粗糙**：外壳是 Element Plus（EP）默认 `el-container/el-header/el-aside/el-main` 的裸拼装，加一个孤立的手动主色覆盖（`--el-color-primary`），没有完整的设计令牌体系，整体不协调、偏「毛坯」。
2. **参考栈漂移**：LLM-Manager 已重构为 **React 19 + Tailwind v4 + TanStack Query**，仅借鉴了其配色与外壳形态，底层栈（Vue + EP）与之不同，直接照搬代码不可行。

**目标**：在不放弃 Vue + EP（EP 的表单/表格组件是计算平台的核心资产）的前提下，复刻 LLM-Manager 那套「简洁、优雅、克制、耐看」的视觉气质——三主题（深 / 浅 / 暖）、语义设计令牌、真实组件镀铬、单一强调色、无多余动效。

同时完成三项目清理：**移除柱计算**、**清理前后端死代码**、**清空所有前端页面只保留外壳**。

### 非目标（YAGNI）

- 不切换到 React / Tailwind（会丢弃 EP 组件库，对表单+表格型应用得不偿失）。
- 不引入 SSE / 实时流 / 图表库（本项目是参数输入 + 结果表格 + 计算书，非实时看板）。
- 不实现任何计算页面的功能内容（本次只做外壳 + 空页面框架）。
- 不动板计算后端求解器与测试（核心资产）。

---

## 2. 架构决策

**保留 Vue 3 + TypeScript + Element Plus + Vite。新增一层「语义设计令牌 → EP CSS 变量」桥接。**

### 决策依据

| 选项 | 结论 |
|------|------|
| A. Vue + EP + 令牌桥接（**选定**） | 复用 EP 表单/表格；通过驱动 EP 的 `--el-*` 变量获得 LLM-Manager 视觉；工作量最小、风险最低、最契合「表单+表格」需求 |
| B. Vue + Tailwind，弃用 EP | 视觉控制力强，但要自建所有表单组件（校验等），工作量高 |
| C. 全面切到 React + Tailwind | 可直接搬运 LLM-Manager 代码，但等于前端重写 + 维护两套生态，且丢失 EP |

用户已明确：核心诉求是 **LLM-Manager 的视觉气质（三色 + 克制 + 耐看）**，而非栈本身，并授权「按你认为合适的来」。故选 A。

### 设计原则（照搬 LLM-Manager `index.css` 头部注释）

> 无渐变、无毛玻璃、无多余动效；单一强调色；真实的组件镀铬（边框 + 底色），不裸奔。

---

## 3. 三主题令牌体系

采用 LLM-Manager 同款**语义令牌模型**，用 `[data-theme="dark|light|warm"]` 驱动（**不再**使用 EP 的 `html.dark` 类）。

### 3.1 完整令牌与三套配色

| 令牌 | `dark`（默认） | `light` | `warm` |
|------|------|------|------|
| `--background` | `#0d1117` | `#f6f7f9` | `#f6f2ec` |
| `--foreground` | `#e6edf3` | `#16181d` | `#3b352b` |
| `--card` | `#161b22` | `#ffffff` | `#fffdf8` |
| `--card-foreground` | `#e6edf3` | `#16181d` | `#3b352b` |
| `--popover` | `#161b22` | `#ffffff` | `#fffdf8` |
| `--popover-foreground` | `#e6edf3` | `#16181d` | `#3b352b` |
| `--primary` | `#6b8cff` | `#4f46e5` | `#8a6d52` |
| `--primary-foreground` | `#ffffff` | `#ffffff` | `#ffffff` |
| `--secondary` | `#21262d` | `#eef0f3` | `#ece4d6` |
| `--secondary-foreground` | `#e6edf3` | `#16181d` | `#3b352b` |
| `--muted` | `#21262d` | `#eef0f3` | `#ece4d6` |
| `--muted-foreground` | `#8b949e` | `#6b7280` | `#9a8f7d` |
| `--accent` | `#21262d` | `#eef0f3` | `#ece4d6` |
| `--accent-foreground` | `#e6edf3` | `#16181d` | `#3b352b` |
| `--destructive` | `#f85149` | `#dc2626` | `#b5462f` |
| `--destructive-foreground` | `#ffffff` | `#ffffff` | `#ffffff` |
| `--success` | `#3fb950` | `#16a34a` | `#6f8f5a` |
| `--success-foreground` | `#0d1117` | `#ffffff` | `#ffffff` |
| `--warning` | `#d29922` | `#b45309` | `#a47a3b` |
| `--warning-foreground` | `#0d1117` | `#ffffff` | `#ffffff` |
| `--border` | `#262c36` | `#e7e8ec` | `#e8e0d3` |
| `--input` | `#262c36` | `#e7e8ec` | `#e8e0d3` |
| `--ring` | `#6b8cff` | `#4f46e5` | `#8a6d52` |
| `--radius` | `0.625rem` | `0.75rem` | `0.75rem` |

### 3.2 字体

`system-ui, -apple-system, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif`（与 LLM-Manager 一致）。

---

## 4. Element Plus 令牌桥接

EP 组件在运行时读取 `--el-*` CSS 变量。在**每个** `[data-theme]` 块内，把语义令牌映射到 EP 变量，使 EP 组件自动跟随主题。

### 4.1 基础映射

| EP 变量 | ← 语义令牌 |
|---------|-----------|
| `--el-color-primary` | `--primary` |
| `--el-bg-color` | `--card` |
| `--el-bg-color-page` | `--background` |
| `--el-bg-color-overlay` | `--popover` |
| `--el-text-color-primary` | `--foreground` |
| `--el-text-color-regular` | `--foreground` |
| `--el-text-color-secondary` | `--muted-foreground` |
| `--el-text-color-placeholder` | `--muted-foreground` |
| `--el-text-color-disabled` | `--muted-foreground`（适当降低对比） |
| `--el-border-color` | `--border` |
| `--el-border-color-light` / `lighter` / `extra-light` | `--border`（或略浅派生） |
| `--el-fill-color` / `light` / `lighter` / `blank` | `--muted` / `--card` |
| `--el-color-success` | `--success` |
| `--el-color-danger` | `--destructive` |
| `--el-color-warning` | `--warning` |
| `--el-border-radius-base` / `small` / `round` | 由 `--radius` 派生 |
| `--el-box-shadow` / `light` / `lighter` | 极淡 / `none`（靠边框分隔而非阴影） |
| `--el-disabled-bg-color` / `text-color` | 基于 `--muted` 派生 |

### 4.2 色阶变体（关键，必须处理）

EP 的按钮悬停、菜单激活填充、表格条纹等依赖 `--el-color-primary-light-3/5/7/8/9` 与 `--el-color-primary-dark-2`，以及 success/warning/danger 的同名色阶。**若不提供，换肤后这些状态会「破相」。**

**处理方式**：在三套主题块中，对 `primary` / `success` / `warning` / `destructive` 四个基色，分别预计算并硬编码：
- `light-3`、`light-5`、`light-7`、`light-8`、`light-9`
- `dark-2`

计算遵循 EP 的混色算法：`light-N = mix(white, 基色, N × 10%)`，`dark-2 = mix(black, 基色, 20%)`。具体十六进制值在实现阶段生成（可用一次性脚本计算后固化，或手算填入）。本任务接受这三套色阶在实现时确定最终值，但**必须在三个主题中完整提供**，不能只覆盖 `--el-color-primary`。

> 注：dark 主题下「light-N = 与白色混合」会得到偏淡的冷色，正符合 LLM-Manager 暗色按钮的悬停观感。

### 4.3 取消 EP 自带暗色

**删除** `main.ts` 中的 `import 'element-plus/theme-chalk/dark/css-vars.css'`。暗色完全由本令牌层接管，避免 EP 的 `html.dark` 逻辑与 `[data-theme]` 两套暗色打架。

---

## 5. 外壳架构

### 5.1 布局结构（照搬 LLM-Manager `app-shell.tsx`）

```
┌─────────────────────────────────────────────────────────┐
│ TopBar  [■ 混凝土课程设计计算平台] [«]        [深|浅|暖]  │  ← 56px, bg-card, border-b
├──────────┬──────────────────────────────────────────────┤
│ Sidebar  │  main (padding, overflow-auto)                │
│ 概览     │  ┌─ PageHeader: 标题 + 副标题 ─────────────┐  │
│ 材料参数  │  │                                        │  │
│ 板计算   │  │   （清空，待模块开发）                  │  │
│ 次梁     │  │                                        │  │
│ 主梁     │  └────────────────────────────────────────┘  │
│ 计算书   │                                              │
│ 系统设置 │                                              │
└──────────┴──────────────────────────────────────────────┘
```

- 整体：`flex h-screen flex-col`，背景 `--background`、文字 `--foreground`。
- TopBar：全宽、`bg-card`、`border-b`。
- 主体行：`flex flex-1 overflow-hidden` = Sidebar + main。
- Sidebar：展开 ~210px / 收起 ~56px，`bg-card`、`border-r`，宽度过渡 150ms。
- main：`flex-1 overflow-auto`，内边距（约 24px）。

### 5.2 组件清单

| 组件 | 动作 | 说明 |
|------|------|------|
| `components/layout/AppLayout.vue` | 重写 | 上述 flex 布局；持有 sidebar 折叠态（沿用 `useSidebar`） |
| `components/layout/AppHeader.vue` | 重写为 TopBar | 左：CSS 手绘健康度 LED（在线=绿框+实心点，离线=空心红框）+ 平台标题 + 折叠按钮；右：`ThemeSwitcher`。**替换**现有简陋小圆点 |
| `components/layout/AppSidebar.vue` | 重写 | **弃用 `el-menu`**，改自定义 `<router-link>` 导航，精确复刻激活态（见 5.3） |
| `components/layout/ThemeSwitcher.vue` | **新增** | 深 / 浅 / 暖 三按钮，激活态用 primary |
| `components/common/PageHeader.vue` | **新增** | H1 标题 + 可选 muted 副标题（左）+ 可选 action 插槽（右），底部留白 |

### 5.3 侧边栏激活态（照搬 `sidebar.tsx`）

- 激活项：`border-left: 2px solid var(--primary)` + `background: var(--muted)` + `color: var(--foreground)` + 字重 500。
- 非激活：左边框透明 + `color: var(--muted-foreground)` + hover `background: var(--muted)` / `color: var(--foreground)`。
- 收起态：仅图标、居中、无文字，hover 显示 title 提示。

### 5.4 健康度 LED（照搬 `top-bar.tsx`）

CSS 手绘，非 Unicode 字形（保证在线/离线尺寸一致）：
- 外框：`8px × 8px`、2px 边框、`border-radius: 2px`。在线 `border-color: var(--success)`，离线 `border-color: var(--destructive)`。
- 在线时内部一个 `3px × 3px` 实心点 `background: var(--success)`；离线留空。
- 复用现有 `useHealth`（轮询 `/api/health`）。

---

## 6. 主题机制

`composables/useTheme.ts` 从「dark/light 布尔」改为 **dark / light / warm 三态**：

- 状态：`theme: Ref<'dark'|'light'|'warm'>`，默认 `dark`。
- 持久化：localStorage key `ccd-theme`（沿用）。
- 应用：写 `document.documentElement.dataset.theme = theme`（替代 `classList.toggle('dark')`）。
- 暴露：`{ theme, setTheme }`（`setTheme(t)` 设定具体主题）。
- `main.ts` 挂载前预设 `data-theme`，避免刷新闪烁（沿用现有防闪烁思路，改为写 data-theme）。

`ThemeSwitcher` 调 `setTheme`，三按钮显示「深色 / 浅色 / 暖灰」。

---

## 7. 页面处理（清空，仅保留 PageHeader）

所有视图清空功能内容，**仅渲染一个 `PageHeader`**（标题 + 副标题，无表单/无结果），作为「框」的一部分，不毛坯、随时可填。

| 视图 | 标题 | 副标题 |
|------|------|--------|
| `Overview.vue` | 概览 | 项目与设计参数总览（待实现） |
| `Materials.vue` | 材料参数 | 混凝土与钢筋强度（待实现） |
| `Slab.vue` | 板计算 | 连续板荷载与内力计算（待实现） |
| `SecondaryBeam.vue` | 次梁计算 | 次梁内力与配筋（待实现） |
| `MainBeam.vue` | 主梁计算 | 主梁内力与配筋（待实现） |
| `Report.vue` | 计算书 | 自动生成设计计算书（待实现） |
| `Settings.vue` | 系统设置 | 系统与主题偏好（待实现） |

`Column.vue` **删除**。

---

## 8. 导航结构（最终）

`config/nav.ts` 移除 `underConstruction` 字段与柱计算项，保留 7 项（顺序不变）：

| path | 标题 | 图标 |
|------|------|------|
| `/` | 概览 | DataBoard |
| `/materials` | 材料参数 | Box |
| `/slab` | 板计算 | Grid |
| `/secondary-beam` | 次梁计算 | Operation |
| `/main-beam` | 主梁计算 | Memo |
| `/report` | 计算书 | Document |
| `/settings` | 系统设置 | Setting |

`NavItem` 接口精简为 `{ path, title, icon }`。

---

## 9. 清理清单（移除柱计算 + 死代码 + 清空页面）

### 9.1 后端删除（均为 0 行空文件 + 柱模块）

- `backend/app/api/column.py`（空）
- `backend/app/api/beam.py`（空）
- `backend/app/api/slab.py`（空）
- `backend/app/models/column.py`（空）
- `backend/app/models/beam.py`（空）
- `backend/app/solvers/column/`（`__init__.py` / `solver.py` / `utils.py` 全空）→ 删整个目录
- `backend/app/solvers/beam/`（全空）→ 删整个目录

### 9.2 后端修改

- `backend/app/models/slab.py`：删除 `SlabInput.structure_factor` 字段（死字段，结构系数已于 commit `0c40c98` 移除）。

### 9.3 前端删除

- `frontend/src/views/Column.vue`
- `frontend/src/components/common/UnderConstruction.vue`
- `frontend/src/assets/styles/theme.css`（内容并入新的 `tokens.css`，删除旧文件）

### 9.4 前端新增

- `frontend/src/assets/styles/tokens.css`：语义令牌（三主题）+ EP 桥接 + 字体 + 细滚动条。
- `frontend/src/components/layout/ThemeSwitcher.vue`
- `frontend/src/components/common/PageHeader.vue`

### 9.5 前端修改

- `frontend/src/main.ts`：移除 EP dark css-vars 导入；导入 `tokens.css`（替代 `theme.css`）；挂载前预设 `data-theme`。
- `frontend/src/assets/styles/index.css`：保留全局 reset；滚动条改用语义令牌（`--border` / `--muted-foreground`）。
- `frontend/src/App.vue`：不变（仍只 `<router-view />`）。
- `frontend/src/components/layout/AppLayout.vue` / `AppHeader.vue` / `AppSidebar.vue`：按 §5 重写。
- `frontend/src/composables/useTheme.ts`：按 §6 重写为三态。
- `frontend/src/config/nav.ts`：按 §8 精简。
- `frontend/src/router/index.ts`：移除 `/column` 路由。
- `frontend/src/views/{Overview,Materials,Slab,SecondaryBeam,MainBeam,Report,Settings}.vue`：按 §7 清空为 PageHeader。

### 9.6 保留（不动）

- 板计算后端求解器 `solvers/slab/` 及 `tests/test_slab_utils.py`（21 个测试，核心资产）。
- `data/connection.py`（DB 脚手架，后续持久化要用；`init_db` 当前为占位，本次不展开）。
- `api/health.py`、`useHealth`、`useSidebar` 及其测试。
- `api/index.ts`（axios，health 仍用）。

---

## 10. 测试

- **更新** `composables/useTheme.spec.ts`：从「dark/light 布尔」断言改为「dark/light/warm 三态 + `data-theme` 属性 + localStorage 持久化」。
- **更新** `config/nav.spec.ts`：断言 7 项、无 column、无 `underConstruction` 字段。
- **保留** `useHealth.spec.ts`、`useSidebar.spec.ts`、`api/health.spec.ts`（行为未变）。
- 后端：`test_slab_utils.py` 21 个测试必须仍全通过（验证移除 `structure_factor` 未破坏求解器——该字段本就未被求解器使用，预期无影响）。
- 手动验收：`npm run dev` 切换三主题，确认 TopBar / Sidebar / 健康度 LED / EP 组件（至少放一个 `el-button`、`el-input`、`el-card` 到某页或在 dev 工具里）在三个主题下颜色/边框/悬停态正确、无「破相」。

---

## 11. 验收标准

1. 三主题（深/浅/暖）可切换、刷新后保持、无闪烁。
2. EP 组件（按钮、输入框、卡片、表格）在三主题下渲染正确，悬停/激活态不破相（色阶变体已提供）。
3. 外壳视觉与 LLM-Manager 同源：CSS-drawn LED、`border-l-2` 激活态、细滚动条、无渐变/无毛玻璃、单一强调色。
4. 所有页面仅 PageHeader，无残留功能内容；柱计算从前端（路由/nav/视图）与后端（api/models/solvers）彻底移除。
5. 死代码（空文件、`structure_factor`、`UnderConstruction`、`underConstruction` 标志）清除。
6. 前端 `npm run test:run` 全通过；后端 `pytest` 21 个测试全通过。

---

## 12. 范围外 / 后续

- 各计算模块的功能实现（板配筋、裂缝、挠度；次梁/主梁；计算书）。
- `/api/slab` 等路由暴露、数据库持久化。
- README 中 `app/calc/` 旧目录描述的更正（可顺手在实现时修，非阻塞）。
