# 水利水电工程 — 混凝土课程设计计算平台

**混凝土结构课程设计** Web 计算平台，涵盖 **板、次梁、主梁** 的内力计算与配筋设计，支持多项目存储、快照管理及教师参考值验证。

---

## 目录

- [课程背景](#课程背景)
- [快速启动](#快速启动)
- [功能模块](#功能模块)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [架构设计](#架构设计)
- [测试](#测试)
- [部署](#部署)

---

## 课程背景

本平台针对水利水电工程专业《水工钢筋混凝土结构》课程设计开发，依据 **2026 版水工钢筋混凝土课程设计任务书** 实现。设计任务涵盖：

- 某水电站厂房 **整体式单向板楼盖** 设计
- 三构件计算：**板**、**次梁**、**主梁**
- 完整计算流程：荷载计算 → 内力分析 → 配筋设计 → 截面复核

平台将传统手算流程数字化，自动完成查表、迭代选筋等重复性工作，输出可直接用于施工图绘制的配筋结果。

---

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

API 文档: http://localhost:8000/docs

> 可选：复制 `.env.example` 为 `.env` 以自定义 JWT 密钥、CORS 源等配置（默认值可直接用于本地开发）。

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端地址: http://localhost:3000

### 容器化部署（一键启动）

```bash
cp docker-compose.yml.example docker-compose.yml
docker compose up -d
```

前端: http://localhost:8000

---

## 功能模块

| 模块 | 功能说明 |
|------|----------|
| **登录/注册** | JWT 认证、用户数据隔离，同一设备可多用户独立使用 |
| **项目概览** | 项目列表展示、创建/删除/快捷操作，含未提交变更提示 |
| **设计参数** | 结构布置参数（跨度、柱网）、材料参数（混凝土等级、钢筋等级）、荷载参数（恒载/活载） |
| **板计算** | 板的内力分析与配筋，含荷载计算、跨度确定、内力包络图、配筋面积及钢筋选型 |
| **次梁计算** | 次梁内力与配筋，含 T 形/矩形截面判断、正截面抗弯、斜截面抗剪、箍筋计算 |
| **主梁计算** | 主梁内力与配筋，含集中荷载处理、吊筋计算、弯矩包络图 |
| **存档管理** | 项目快照保存/恢复/派生，支持回溯任意历史版本 |
| **设置** | 三主题切换（暗/亮/暖）、账户管理 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.12+ / FastAPI / Uvicorn |
| 数据库 | SQLite（3 表：users / projects / snapshots） |
| 认证 | JWT (PyJWT) + bcrypt（密码哈希） |
| 前端框架 | Vue 3 (Composition API) + TypeScript (strict) |
| 构建工具 | Vite |
| UI 组件 | Element Plus + Lucide icons |
| 主题系统 | 三主题令牌体系（暗/亮/暖），`color-mix` 桥接 Element Plus CSS 变量 |
| 后端测试 | pytest（13 文件，144 个测试） |
| 前端测试 | Vitest（9 spec 文件） |
| 容器化 | Docker Compose（多阶段构建，Nginx 反代 Uvicorn） |

---

## 项目结构

```
Concrete-Course-Design/
├── backend/                                    # FastAPI 后端服务
│   ├── app/
│   │   ├── main.py                             # 应用入口：CORS、路由挂载、SPA 静态文件回落
│   │   ├── config.py                           # 环境变量配置（SECRET_KEY、CORS、SERVE_STATIC 等）
│   │   ├── security.py                         # 密码哈希（bcrypt）与 JWT 签发/验证工具
│   │   ├── logging_config.py                   # 日志配置（控制台 + 文件轮转）
│   │   ├── api/
│   │   │   ├── health.py                       # GET /api/health 健康检查端点
│   │   │   ├── projects.py                     # 项目 CRUD + /api/projects/{id}/calculate
│   │   │   └── snapshots.py                    # 快照保存/恢复/派生端点
│   │   ├── auth/
│   │   │   ├── router.py                       # 注册/登录/获取当前用户/删除账户
│   │   │   ├── dependencies.py                 # get_current_user 依赖注入
│   │   │   └── repository.py                   # 用户数据访问层（注册、查询）
│   │   ├── models/                             # Pydantic 数据模型（输入校验 + 输出序列化）
│   │   │   ├── user.py                         # UserCreate / UserLogin / UserPublic / Token
│   │   │   ├── project.py                      # ProjectCreate / ProjectPublic / Snapshot* / CalculateRequest
│   │   │   ├── slab.py                         # SlabInput / SlabLoadOutput / SlabSpanOutput / 内力 / 配筋
│   │   │   ├── beam.py                         # BeamInput / BeamFlexureResult / BeamShearResult / 等
│   │   │   └── main_beam.py                    # MainBeamInput / MainBeamOutput / 集中力 / 吊筋
│   │   ├── solvers/                            # 结构计算引擎（核心业务逻辑）
│   │   │   ├── common.py                       # 共享公式：h0、αs、ξ、As、抗剪、等跨连续梁系数表
│   │   │   ├── derive.py                       # 扁平参数 → 构件输入（板/次梁/主梁的荷载、跨度、截面派生）
│   │   │   ├── slab/
│   │   │   │   ├── solver.py                   # 板计算编排：荷载 → 跨度 → 内力 → 配筋
│   │   │   │   └── utils.py                    # 板配筋辅助：φ@间距候选钢筋生成
│   │   │   ├── beam/
│   │   │   │   ├── solver.py                   # 次梁计算编排：荷载 → 跨度 → 内力 → 抗弯 → 抗剪
│   │   │   │   └── utils.py                    # 次梁辅助：T 形/矩形截面判断
│   │   │   └── main_beam/
│   │   │       ├── solver.py                   # 主梁计算编排：含集中力处理
│   │   │       └── utils.py                    # 主梁辅助：集中力下内力计算
│   │   └── data/
│   │       ├── connection.py                   # SQLite 连接管理 + 建表 DDL（users / projects / snapshots）
│   │       └── project_repository.py           # 项目/快照数据访问层
│   ├── tests/                                  # 后端测试（13 文件，144 测试）
│   │   ├── conftest.py                         # 共享 fixtures：isolated_db、client、auth tokens
│   │   ├── test_auth.py                        # 认证流程：密码哈希、JWT 编解码、注册/登录路由、用户隔离
│   │   ├── test_common.py                      # 共享公式：等跨系数、内力计算
│   │   ├── test_slab_reinforcement.py          # 板配筋单元测试（φ@间距、配筋面积、截面计算）
│   │   ├── test_slab_utils.py                  # 板工具函数测试
│   │   ├── test_slab_orchestration.py          # 板计算全流程编排测试
│   │   ├── test_beam.py                        # 次梁单元测试（抗弯/抗剪/荷载/跨度/内力）
│   │   ├── test_beam_orchestration.py          # 次梁全流程编排测试
│   │   ├── test_main_beam.py                   # 主梁计算测试
│   │   ├── test_project_repository.py          # 数据仓库层测试
│   │   ├── test_projects_api.py                # 项目 API 集成测试（CRUD、用户隔离、认证门禁）
│   │   ├── test_calculate_api.py               # 计算 API 集成测试（正常/异常/超筋检测）
│   │   ├── test_snapshots_api.py               # 快照 API 集成测试
│   │   └── test_teacher_validation.py          # 教师参考值回归测试
│   ├── run.py                                  # PyInstaller 便携版入口
│   ├── requirements.txt                        # 生产依赖
│   ├── requirements-dev.txt                    # 开发依赖
│   ├── Dockerfile
│   └── pyproject.toml                          # pytest 配置
├── frontend/                                   # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── main.ts                             # 入口：Element Plus 注册、主题启
│   │   ├── App.vue                             # 根组件
│   │   ├── env.d.ts                            # 环境类型声明（.vue 模块声明等）
│   │   ├── api/                                # Axios HTTP 接口层
│   │   │   ├── index.ts                        # Axios 实例（baseURL、请求/响应拦截器、401 自动跳转登录）
│   │   │   ├── auth.ts                         # 认证 API（register / login / me）
│   │   │   └── projects.ts                     # 项目/快照/计算 API
│   │   ├── assets/styles/
│   │   │   └── tokens.css                      # 三主题设计令牌（暗/亮/暖）+ 全局样式 + Element Plus 变量桥接
│   │   ├── components/
│   │   │   ├── layout/                         # 布局组件
│   │   │   │   ├── AppLayout.vue               # 整体页面布局框架
│   │   │   │   ├── AppHeader.vue               # 顶部导航栏
│   │   │   │   ├── AppSidebar.vue              # 侧边栏导航
│   │   │   │   └── UserDropdown.vue            # 用户下拉菜单
│   │   │   └── common/                         # 通用组件
│   │   │       └── PageHeader.vue              # 页面标题栏
│   │   ├── composables/                        # 组合式状态管理（模块级单例模式）
│   │   │   ├── useAuth.ts                      # 认证状态：登录/注册/登出、会话持久化
│   │   │   ├── useProject.ts                   # 项目状态：当前项目数据、防抖自动保存（800ms）
│   │   │   ├── useTheme.ts                     # 主题切换：暗/亮/暖，localStorage 持久化
│   │   │   ├── useSidebar.ts                   # 侧栏折叠状态
│   │   │   ├── useHealth.ts                    # 后端健康状态轮询
│   │   │   ├── useBeamLayout.ts                # 梁跨数与跨度配置逻辑
│   │   │   └── useInternalForce.ts             # 内力系数表数据处理
│   │   ├── config/
│   │   │   └── nav.ts                          # 导航配置（路由标题、图标映射、顺序）
│   │   ├── router/
│   │   │   └── index.ts                        # Vue Router（懒加载路由、导航守卫）
│   │   └── views/                              # 页面视图
│   │       ├── Login.vue                       # 登录/注册页
│   │       ├── Overview.vue                    # 项目概览页
│   │       ├── Params.vue                      # 设计参数配置页
│   │       ├── Slab.vue                        # 板计算页
│   │       ├── SecondaryBeam.vue               # 次梁计算页
│   │       ├── MainBeam.vue                    # 主梁计算页
│   │       ├── Archive.vue                     # 存档管理页
│   │       ├── Settings.vue                    # 设置页
│   │       └── Report.vue                      # 报表页（预留）
│   ├── src/__tests__/                          # 前端测试（9 spec 文件）
│   │   ├── composables/
│   │   │   ├── useAuth.spec.ts
│   │   │   ├── useProject.spec.ts
│   │   │   ├── useBeamLayout.spec.ts
│   │   │   ├── useHealth.spec.ts
│   │   │   ├── useInternalForce.spec.ts
│   │   │   ├── useTheme.spec.ts
│   │   │   └── useSidebar.spec.ts
│   │   └── api/
│   │       ├── auth.spec.ts
│   │       └── index.spec.ts
│   ├── Dockerfile                              # 多阶段构建（nginx 托管）
│   ├── nginx.conf                               # Nginx 配置（API 反代到后端）
│   ├── vite.config.ts                          # Vite 配置（开发代理到 localhost:8000）
│   ├── vitest.config.ts                        # Vitest 配置（happy-dom）
│   └── tsconfig.json                           # TypeScript strict 模式
├── docs/                                       # 课程设计文档
│   ├── 课设要求/                                # 课程设计任务书
│   │   ├── 2026版水工钢筋混凝土课程设计.md
│   │   └── 2026版_钢筋混凝土课程设计任务书_程序设计版.md
│   ├── 求解器问题记录.md                        # 计算引擎已知问题与修复记录
│   └── 想法记录.txt                             # 功能规划与改进思路
├── assets/
│   └── logo.ico                                # 应用程序图标
├── .env.example                                # 环境变量配置模板
├── .gitignore                                  # Git 忽略规则
├── build_win.py                                # Windows 便携版打包脚本（PyInstaller）
├── docker-compose.yml.example                  # Docker Compose 编排示例
└── LICENSE
```

---

## 架构设计

### 后端架构

采用 **分层架构**，从路由到数据访问职责清晰：

```
路由层 (api/) → 认证层 (auth/) → 业务逻辑层 (solvers/) → 数据访问层 (data/)
```

- **路由层**：接收 HTTP 请求，参数校验，调用业务逻辑，返回响应
- **认证层**：JWT 令牌验证，用户身份注入
- **业务逻辑层**：独立的计算引擎，每个构件（板/次梁/主梁）有独立的 solver 子包，共享公式提取至 `common.py`
- **数据访问层**：SQLite 原始 SQL，参数化查询防注入

### 前端架构

采用 **组合式 API + 模块级单例** 状态管理模式：

- **API 层**：Axios 封装，统一错误拦截，401 自动跳转登录
- **组合式函数**：模块级 `ref` 实现全局状态共享，替代 Pinia/Vuex
- **视图层**：每个构件一个视图页面，内含计算参数表格、结果展示、SVG 内力图与配筋示意图

### 计算引擎设计

计算流程遵循课程设计手算步骤：

```
参数派生 (derive.py) → 荷载计算 → 跨度确定 → 内力分析 → 配筋计算
```

每个阶段输出均为 Pydantic 模型，可独立测试。内力计算基于《水工钢筋混凝土结构》等跨连续梁系数表，>5 跨自动简化为 5 跨计算。

---

## 测试

### 测试概况

| 测试范围 | 文件数 | 测试数 |
|----------|--------|--------|
| 后端单元测试 | 9 | ~100 |
| 后端集成测试 | 4 | ~44 |
| 前端测试 | 9 spec | — |
| **合计** | **22** | **144+** |

### 运行测试

```bash
# 后端全部测试
cd backend && pytest -v

# 前端测试
cd frontend && npm run test:run

# 前端类型检查
cd frontend && npx vue-tsc --noEmit
```

### 测试覆盖亮点

- **计算引擎**：每个求解阶段（荷载/跨度/内力/配筋）均有独立单元测试，与手算参考值对比验证
- **教师参考值回归**：`test_teacher_validation.py` 内置标准工况的期望结果，防止回归
- **API 集成测试**：完整覆盖项目 CRUD、用户隔离、认证门禁、超筋检测
- **测试隔离**：`isolated_db` fixture 使用 `tmp_path + monkeypatch`，测试间互不干扰

---

## 部署

### 服务器（Docker Compose）

```bash
cp docker-compose.yml.example docker-compose.yml
docker compose up -d
```

Nginx 反代前端请求到 Uvicorn 后端，前端访问: http://localhost:8000

### Windows 便携版（单文件 exe）

```bash
pip install PyInstaller
python build_win.py
```

构建产物为 `build/ConcreteCourseDesign.exe`，运行后自动在 exe 同级创建 `data/`（SQLite 数据库）和 `logs/`（日志）。后端以 `SERVE_STATIC=1` 模式启动，直接托管前端静态文件，无需额外配置。
