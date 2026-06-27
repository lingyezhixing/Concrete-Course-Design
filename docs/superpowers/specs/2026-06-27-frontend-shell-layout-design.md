# 混凝土课程设计计算平台 — 前端骨架与布局设计

- **日期**: 2026-06-27
- **状态**: 已批准，待实现
- **参考**: `E:\Programming\pycodes\Projects\LLM-Manager\frontend`（React + Tailwind 的应用外壳与视觉风格）
- **范围**: 仅前端骨架与布局；计算模块页面为"建设中"占位

---

## 1. 背景与目标

本项目是"水利水电工程 - 混凝土课程设计计算平台"，面向水利水电工程专业学生，辅助完成混凝土结构（板 / 次梁 / 主梁 / 柱）课程设计的计算工作。

本阶段目标：参考 LLM-Manager 项目的前端，搭建一致的**应用外壳（App Shell）与视觉框架**——即"顶栏 + 可折叠侧边栏 + 主内容区"的仪表盘式布局，配以暗 / 亮主题系统。各计算模块页面本阶段仅做"建设中"占位，后续逐步填充真实计算功能。

### 架构选型理由

LLM-Manager 采用 React + Tailwind（无组件库），原因是它是**监控仪表盘**——满屏自定义实时卡片、几乎无表单。混凝土计算平台形态相反，是**表单与表格密集型**应用（大量带校验的数值输入、等级下拉、结果表格）。对这类应用，成熟组件库（Element Plus）的表单 / 表格 / 校验能力远胜从零造轮子。因此本阶段选择 **Vue 3 + Element Plus**（即现有骨架），而非照搬 LLM-Manager 的 React + Tailwind。

LLM-Manager 迁移到本项目的是**外壳布局与视觉框架**（顶栏 + 可折叠侧边栏 + 主题），而非具体技术栈。

---

## 2. 范围

### 包含

- 替换现有 Vue 占位骨架为完整应用骨架
- App Shell：`el-container` 顶栏 + 可折叠侧边栏 + 主内容区
- 路由结构（混凝土模块导航）
- 主题系统（dark / light + localStorage 持久化）
- 顶栏健康指示灯（轮询 `/api/health`）
- "建设中"占位组件
- 概览页静态内容（项目信息 + 设计参数）

### 不含（后续阶段）

- 各计算模块的实际表单 / 结果 UI 与计算逻辑
- 后端计算接口
- 后端材料接口（`materials.py` 数据已存在但未暴露为 API）
- "warm" 暖色主题（需额外自定义 CSS，本阶段先不做）
- SSE 实时流（计算平台无需）

---

## 3. 技术栈

### 保留现有（不改动版本）

- Vue `^3.5`
- Element Plus `^2.9`
- vue-router `^4.5`
- axios `^1.7`
- Vite `^6.0`
- TypeScript `~5.7`
- vue-tsc `^2.2`

### 新增

- `@element-plus/icons-vue`（菜单与按钮图标）

### 明确不引入

Tailwind、React、Pinia、TanStack Query、@vueuse/core。本阶段状态管理需求极小（仅主题、侧边栏折叠、健康状态），用轻量 composable + 原生 `setInterval` + `localStorage` 即可，避免引入额外依赖。

---

## 4. 目录结构

```
frontend/src/
├── api/
│   └── index.ts                  # axios 实例（baseURL '/api'）+ 类型化请求函数
├── assets/
│   └── styles/
│       ├── index.css             # 全局样式入口（滚动条、基础重置）
│       └── theme.css             # Element Plus 主色覆盖（dark/light）
├── components/
│   ├── layout/
│   │   ├── AppLayout.vue         # el-container 外壳（header + aside + main）
│   │   ├── AppHeader.vue         # 顶栏：折叠按钮 + Logo + 健康灯 + 主题开关
│   │   └── AppSidebar.vue        # el-menu(:collapse) 导航
│   └── common/
│       └── UnderConstruction.vue # "建设中"占位组件
├── composables/
│   ├── useTheme.ts               # 'dark'|'light' + localStorage("ccd-theme")
│   ├── useSidebar.ts             # 折叠状态 + localStorage
│   └── useHealth.ts              # 轮询 /api/health，暴露 isOnline
├── config/
│   └── nav.ts                    # NAV_ITEMS 导航单一数据源
├── router/
│   └── index.ts                  # 路由（AppLayout 嵌套 + 各模块 + 兜底）
├── views/
│   ├── Overview.vue              # 概览（静态：项目信息 + 设计参数）
│   ├── Materials.vue             # 材料参数（静态展示混凝土/钢筋强度表，非占位）
│   ├── Slab.vue                  # 板计算（建设中）
│   ├── SecondaryBeam.vue         # 次梁计算（建设中）
│   ├── MainBeam.vue              # 主梁计算（建设中）
│   ├── Column.vue                # 柱计算（建设中）
│   ├── Report.vue                # 计算书（建设中）
│   └── Settings.vue              # 系统设置（建设中）
├── App.vue
└── main.ts
```

**设计原则**：每个单元单一职责、接口清晰、可独立理解。`nav.ts` 作为导航单一数据源，路由路径与导航项路径一一对应，避免散落多处。

---

## 5. App Shell 布局

```
┌───────────────────────────────────────────────────────────┐
│ AppHeader  [≡] 混凝土课程设计计算平台      [●健康] [☾主题]  │  ← el-header, 56px
├─────────────┬─────────────────────────────────────────────┤
│             │                                             │
│ AppSidebar  │                                             │
│ (el-menu)   │           <router-view />                   │  ← el-main, 可滚动
│ 可折叠      │                                             │
│             │                                             │
└─────────────┴─────────────────────────────────────────────┘
```

### AppLayout.vue

- 根节点：`el-container`，全高 flex 列（`height: 100vh`）
- `el-header`（height 56px）承载 `AppHeader`
- 内层 `el-container`（横向）：`el-aside`（`AppSidebar`，宽度 210px 展开 / 64px 折叠）+ `el-main`（可滚动，承载 `<router-view />`）

### AppHeader.vue

- 左侧：折叠按钮（`el-icon`，`Fold` / `Expand` 切换，绑定 `useSidebar`）+ Logo 文字"混凝土课程设计计算平台"
- 右侧：健康灯（圆点，`ok` 绿色 / 离线灰色，绑定 `useHealth().isOnline`）+ 主题开关（图标按钮，`dark` / `light` 切换，绑定 `useTheme`）

### AppSidebar.vue

- `el-menu`，启用 `:collapse` 与 router 模式（`router` 属性，点击即跳转）
- 菜单项数据来自 `config/nav.ts` 的 `NAV_ITEMS`
- 折叠状态绑定 `useSidebar().isCollapsed`
- 激活项采用 Element Plus 默认高亮（`default-active` 绑定当前路由 path）

### 全局样式

- 细滚动条（宽 8px，hover 时加深），替换系统默认粗滚动条，样式写于 `assets/styles/index.css`

---

## 6. 导航与路由

### `config/nav.ts`（NAV_ITEMS 单一数据源）

| path            | title     | icon（@element-plus/icons-vue） | underConstruction |
|-----------------|-----------|---------------------------------|-------------------|
| `/`             | 概览      | `DataBoard`                     | 否                |
| `/materials`    | 材料参数  | `Box`                           | 否（静态展示）    |
| `/slab`         | 板计算    | `Grid`                          | 是                |
| `/secondary-beam` | 次梁计算 | `Operation`                    | 是                |
| `/main-beam`    | 主梁计算  | `Memo`                          | 是                |
| `/column`       | 柱计算    | `Coin`                          | 是                |
| `/report`       | 计算书    | `Document`                      | 是                |
| `/settings`     | 系统设置  | `Setting`                       | 是                |

> 图标为初步映射，实现时可按可用图标微调。

### `router/index.ts`

- 根路由 `/` 使用 `AppLayout` 作为布局组件，各模块作为 `children`
- 各 `views/*.vue` 采用懒加载（`() => import(...)`）
- 兜底路由 `/:pathMatch(.*)*` 重定向到 `/`

---

## 7. 主题系统

- `useTheme` composable：管理 `'dark' | 'light'`，初始读取 `localStorage("ccd-theme")`，默认 `'dark'`
- 切换时：`document.documentElement.classList.toggle('dark', isDark)` 并写入 `localStorage`
- Element Plus 暗色变量：`main.ts` 中 `import 'element-plus/theme-chalk/dark/css-vars.css'`
- 主色覆盖：`assets/styles/theme.css` 覆盖 `--el-color-primary` 等（dark / light 分别设置），并通过 `html.dark` 选择器区分
- 初始化时机：在 `App.vue` 的 `setup` 中（挂载前）应用初始主题，避免刷新闪烁

---

## 8. API 与数据层

- `api/index.ts`：保留现有 axios 实例（`baseURL: '/api'`）
- 新增类型化函数：

  ```ts
  export interface HealthResponse { status: string }
  export function getHealth(): Promise<HealthResponse>
  ```

- `useHealth(intervalMs = 5000)` composable：`onMounted` 启动 `setInterval` 轮询 `getHealth()`，`onUnmounted` 清理；暴露响应式 `isOnline`（请求成功为 `true`，失败为 `false`）
- `AppHeader` 健康灯绑定 `isOnline`
- 不引入 SSE

---

## 9. 迁移与基础设施

### 保留不动

- `frontend/vite.config.ts`（dev 端口 3000，`/api` 代理到 `localhost:8000`）
- `frontend/tsconfig.json`、`frontend/index.html`、`frontend/env.d.ts`
- `frontend/Dockerfile`（node 构建 + nginx 服务，框架无关）
- `frontend/nginx.conf`（SPA 回退 + `/api` 代理到 `backend:8000`）
- `docker-compose.yml`、`tools-net`、端口 33018
- `backend/`（`/api/health` 返回 `{"status": "ok"}` 不变）

### 替换

- `frontend/src/` 全部内容（现有仅为 `Home.vue` 占位）
- `frontend/package.json`：新增 `@element-plus/icons-vue` 依赖

### 文档

- 更新 `README.md`：补充前端结构与启动方式说明

---

## 10. 验收标准

1. `npm run dev` 启动，访问 `localhost:3000` 显示完整 App Shell（顶栏 + 侧边栏 + 主内容区）
2. 侧边栏列出 8 个导航项；点击路由切换；激活项高亮
3. 侧边栏可折叠 / 展开；**刷新页面后折叠状态保持**
4. 主题开关可切换 dark / light；**刷新页面后主题保持**；切换无刷新闪烁
5. 概览页（`/`）展示项目信息与设计参数（柱网 18×30m、板厚 120mm、次梁 200×500、主梁 300×600、混凝土 C25–C40、钢筋 HPB300–HRB500）
6. `underConstruction` 为 true 的页面显示 `UnderConstruction` 占位组件
7. 后端运行时顶栏健康灯为绿色；后端关闭时为灰色
8. `npm run build` 通过（`vue-tsc -b && vite build` 无类型 / 构建错误）
9. 后端 `/api/health` 行为不变；nginx `/api` 代理不变
10. 不引入未在"技术栈"中列出的依赖

---

## 11. 后续（超出本阶段）

- 计算模块（板 / 次梁 / 主梁 / 柱）实现顺序与依赖拆分（各自独立子项目）
- 后端 `materials` 数据暴露为 API
- "warm" 暖色主题（如确需）
- 计算结果的可视化（图表）与计算书导出（PDF）
