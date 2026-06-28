# 水利水电工程 — 混凝土课程设计计算平台

一个面向混凝土结构课程设计的 Web 计算平台，涵盖 **板、次梁、主梁** 等构件的内力计算与配筋设计，支持用户项目存储、快照管理及教师参考值验证。

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.12+ / FastAPI / Uvicorn |
| **数据库** | SQLite (raw sqlite3) |
| **认证** | JWT (python-jose) + bcrypt 密码哈希 |
| **前端** | Vue 3 + TypeScript + Vite |
| **UI** | Element Plus + Lucide icons |
| **主题** | 三主题令牌体系（暗/亮/暖），color-mix 桥接 Element Plus 变量 |
| **测试** | 后端 pytest（16 测试文件），前端 Vitest（10 spec 文件） |
| **容器化** | Docker Compose (Nginx + Uvicorn) |

## 快速启动

### 后端

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

API 文档: http://localhost:8000/docs

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端地址: http://localhost:3000

测试: `npm run test:run`

### 容器化部署（一键启动）

```bash
cp docker-compose.yml.example docker-compose.yml
docker compose up -d
```

前端: http://localhost:8000

## 功能模块

- **登录/注册** — JWT 认证，用户隔离
- **Overview** — 项目概览与快捷操作
- **设计参数** — 混凝土、钢筋等材料参数配置（结构、材料、荷载）
- **板计算** — 板的内力分析与配筋
- **次梁计算** — 次梁内力与配筋（含 T 形截面判断）
- **主梁计算** — 主梁内力与配筋（含吊筋计算）
- **存档管理** — 项目快照（保存/恢复/派生）
- **Settings** — 应用设置（主题切换等）

## 项目结构

```
├── backend/                        # FastAPI 后端
│   ├── app/
│   │   ├── main.py                 # 应用入口（CORS、生命周期、路由挂载）
│   │   ├── config.py               # 配置（SECRET_KEY、CORS 等）
│   │   ├── logging_config.py       # 文件/控制台分级日志（按尺寸轮转）
│   │   ├── security.py             # 密码哈希与 JWT 工具函数
│   │   ├── checks.py               # 规范检查端点（休眠中）
│   │   ├── api/
│   │   │   ├── health.py           # GET /api/health 健康检查
│   │   │   ├── projects.py         # 项目 CRUD + 计算路由
│   │   │   └── snapshots.py        # 快照路由（保存/恢复/派生）
│   │   ├── auth/
│   │   │   ├── router.py           # 登录/注册路由
│   │   │   ├── dependencies.py     # 依赖注入（获取当前用户）
│   │   │   └── repository.py       # 用户数据访问
│   │   ├── models/
│   │   │   ├── slab.py             # 板 Pydantic 模型
│   │   │   ├── beam.py             # 次梁 Pydantic 模型
│   │   │   ├── main_beam.py        # 主梁 Pydantic 模型
│   │   │   ├── project.py          # 项目/快照数据模型
│   │   │   └── user.py             # 用户模型
│   │   ├── solvers/
│   │   │   ├── common.py           # 共享 RC 公式（有效高度、αs、ξ、As 等）
│   │   │   ├── derive.py           # 参数派生（前端扁平数据 → 构件输入）
│   │   │   ├── slab/               # 板计算求解器
│   │   │   ├── beam/               # 次梁计算求解器
│   │   │   └── main_beam/          # 主梁计算求解器
│   │   └── data/
│   │       ├── connection.py       # SQLite 连接
│   │       └── project_repository.py # 项目/快照数据访问
│   ├── tests/                      # 16 个 pytest 测试文件
│   │   ├── conftest.py             # 共享 fixture（DB 隔离、认证客户端）
│   │   ├── test_auth.py            # 认证全链路测试
│   │   ├── test_common.py          # 共享 RC 公式测试
│   │   ├── test_slab_*.py          # 板计算测试（工具函数/配筋/编排）
│   │   ├── test_beam*.py           # 次梁计算测试
│   │   ├── test_main_beam.py       # 主梁计算测试
│   │   ├── test_checks.py          # 规范检查测试
│   │   ├── test_project_repository.py # 仓库层测试
│   │   ├── test_projects_api.py    # 项目 API 测试
│   │   ├── test_snapshots_api.py   # 快照 API 测试
│   │   └── test_teacher_validation.py # 教师参考值回归测试
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/                       # Vue 3 + Element Plus 前端
│   ├── src/
│   │   ├── main.ts                 # 入口：Element Plus + 主题注入
│   │   ├── App.vue                 # 根组件
│   │   ├── api/                    # Axios 请求封装（含 401 拦截器）
│   │   │   ├── index.ts            # Axios 实例
│   │   │   ├── auth.ts             # 登录/注册 API
│   │   │   └── projects.ts         # 项目/快照/计算 API
│   │   ├── assets/styles/
│   │   │   └── tokens.css          # 三主题令牌 + 全局样式
│   │   ├── components/
│   │   │   ├── layout/             # AppLayout, AppHeader, AppSidebar, UserDropdown
│   │   │   └── common/             # PageHeader, ThemeSwitcher
│   │   ├── composables/            # 状态管理（模块级单例）
│   │   │   ├── useAuth.ts          # 认证状态
│   │   │   ├── useProject.ts       # 项目状态 + 防抖自动保存
│   │   │   ├── useTheme.ts         # 主题切换（localStorage 持久化）
│   │   │   ├── useSidebar.ts       # 侧栏折叠状态
│   │   │   └── useHealth.ts        # 后端健康轮询
│   │   ├── config/
│   │   │   └── nav.ts              # 导航配置
│   │   ├── router/
│   │   │   └── index.ts            # Vue Router（懒加载路由）
│   │   └── views/
│   │       ├── Login.vue           # 登录页
│   │       ├── Overview.vue        # 项目概览
│   │       ├── Params.vue          # 设计参数
│   │       ├── Slab.vue            # 板计算
│   │       ├── SecondaryBeam.vue   # 次梁计算
│   │       ├── MainBeam.vue        # 主梁计算
│   │       ├── Archive.vue         # 存档管理
│   │       ├── Settings.vue        # 应用设置
│   │       └── Report.vue          # 报表（待实现）
│   ├── Dockerfile
│   ├── nginx.conf
│   └── vite.config.ts
├── docs/
├── docker-compose.yml.example
├── start-backend.bat
└── README.md
```

## 开发

```bash
# 安装依赖
cd backend && pip install -e ".[dev]"
cd frontend && npm install

# 运行测试
cd backend && pytest -v
cd frontend && npm run test:run

# 前端类型检查
cd frontend && npx vue-tsc --noEmit
```

## 测试

项目具有较高的测试覆盖率：

- **后端**: 16 个测试文件，涵盖认证、计算引擎（板/次梁/主梁）、项目 CRUD、快照管理、API 路由、教师参考值回归测试
- **前端**: 10 个 spec 文件，涵盖 composables、API 模块、导航配置
- **测试特性**: 数据库隔离（`tmp_path` + `monkeypatch`）、浮点近似断言（`pytest.approx`）、认证门禁验证、用户隔离测试

## 部署

服务器部署流程参考 [`docs/`](docs/)，生产环境使用 Docker Compose 启动 Nginx + Uvicorn 双容器。
