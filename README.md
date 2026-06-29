# 水利水电工程 — 混凝土课程设计计算平台

面向混凝土结构课程设计的 Web 计算平台，涵盖 **板、次梁、主梁** 的内力计算与配筋设计，支持项目存储、快照管理及教师参考值验证。

---

## 目录

- [快速启动](#快速启动)
- [功能模块](#功能模块)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [开发](#开发)
- [部署](#部署)

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

| 模块 | 功能 |
|------|------|
| **登录/注册** | JWT 认证，用户数据隔离 |
| **项目概览** | 项目列表、快捷操作 |
| **设计参数** | 混凝土/钢筋材料参数配置（结构、材料、荷载） |
| **板计算** | 板的内力分析与配筋 |
| **次梁计算** | 次梁内力与配筋（含 T 形截面判断） |
| **主梁计算** | 主梁内力与配筋（含吊筋计算） |
| **存档管理** | 项目快照保存/恢复/派生 |
| **设置** | 主题切换（暗/亮/暖三主题）等 |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.12+ / FastAPI / Uvicorn |
| 数据库 | SQLite |
| 认证 | JWT (PyJWT) + bcrypt |
| 前端 | Vue 3 + TypeScript + Vite |
| UI | Element Plus + Lucide icons |
| 主题 | 三主题令牌体系（暗/亮/暖），`color-mix` 桥接 Element Plus 变量 |
| 测试 | 后端 pytest（13 文件），前端 Vitest（9 spec 文件） |
| 容器化 | Docker Compose（Nginx + Uvicorn） |

---

## 项目结构

```
Concrete-Course-Design/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── main.py                   # 入口（CORS、路由挂载）
│   │   ├── config.py                 # 环境配置
│   │   ├── security.py               # 密码哈希 & JWT
│   │   ├── api/                      # 路由层（health / projects / snapshots）
│   │   ├── auth/                     # 用户认证（注册、登录、依赖注入）
│   │   ├── models/                   # Pydantic 数据模型
│   │   ├── solvers/                  # 结构计算引擎（板/次梁/主梁）
│   │   └── data/                     # SQLite 连接与数据访问
│   ├── tests/                        # 13 个 pytest 测试文件
│   └── Dockerfile
├── frontend/                         # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── api/                      # Axios 接口层
│   │   ├── assets/styles/            # 全局样式与主题令牌
│   │   ├── components/               # 布局与通用组件
│   │   ├── composables/              # 组合式状态管理
│   │   ├── router/                   # 路由配置
│   │   └── views/                    # 页面视图（9 个页面）
│   ├── Dockerfile
│   └── nginx.conf
├── docs/                             # 课程需求与设计文档
├── build_win.py                      # Windows 便携版打包脚本
├── .env.example                      # 环境变量配置模板
└── docker-compose.yml.example
```

---

## 开发

### 运行测试

```bash
# 后端
cd backend && pytest -v

# 前端
cd frontend && npm run test:run
```

### 前端类型检查

```bash
cd frontend && npx vue-tsc --noEmit
```

### 测试覆盖

- **后端**: 13 个测试文件，涵盖认证、计算引擎（板/次梁/主梁）、项目 CRUD、快照管理、API 路由及教师参考值回归测试
- **前端**: 9 个 spec 文件，涵盖 composables、API 模块、导航配置
- **特性**: 数据库隔离（`tmp_path` + `monkeypatch`）、浮点近似断言（`pytest.approx`）、用户隔离验证

---

## 部署

### 服务器

使用 Docker Compose 启动 Nginx + Uvicorn 双容器（参考 `docs/` 目录）。

```bash
cp docker-compose.yml.example docker-compose.yml
docker compose up -d
```

### Windows 便携版（单文件 exe）

```bash
pip install PyInstaller
python build_win.py
```

构建产物为 `build/ConcreteCourseDesign.exe`，运行后自动在 exe 同级创建 `data/`（SQLite 数据库）和 `logs/`（日志）。后端以 `SERVE_STATIC=1` 模式启动，直接托管前端静态文件。
