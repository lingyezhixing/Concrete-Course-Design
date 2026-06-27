# 水利水电工程 — 混凝土课程设计计算平台

一个面向混凝土结构课程设计的 Web 计算平台，涵盖 **板、次梁、主梁** 等构件的内力计算与配筋设计。

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端** | Python 3.12 + FastAPI + Uvicorn |
| **ORM** | SQLModel + SQLite (via aiosqlite) |
| **前端** | Vue 3 + TypeScript + Vite |
| **UI** | Element Plus + Lucide icons |
| **主题** | 三主题令牌体系（暗/亮/暖），color-mix 桥接 EP |
| **容器化** | Docker Compose (Nginx + Uvicorn) |

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
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

- **Overview** — 项目概览
- **设计参数** — 混凝土、钢筋等材料参数配置
- **板计算** — 板的内力分析与配筋
- **次梁计算** — 次梁内力与配筋
- **主梁计算** — 主梁内力与配筋
- **报表** — 计算书生成
- **Settings** — 应用设置

## 项目结构

```
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── main.py             # 应用入口（CORS、生命周期、路由挂载）
│   │   ├── logging_config.py   # 文件/控制台分级日志（按尺寸轮转）
│   │   ├── api/
│   │   │   ├── health.py       # /api/health 健康检查（含数据库状态）
│   │   │   └── __init__.py
│   │   ├── models/
│   │   │   └── slab.py         # slab 数据模型（SQLModel）
│   │   ├── solvers/
│   │   │   └── slab/           # 板计算求解器（荷载转换、内力计算）
│   │   └── data/
│   │       └── connection.py   # 数据库连接引擎
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # Vue 3 + Element Plus 前端
│   ├── src/
│   │   ├── main.ts             # 入口：Element Plus + 主题注入
│   │   ├── App.vue             # 根组件
│   │   ├── api/                # axios 请求封装
│   │   ├── assets/styles/      # 三主题令牌 + 全局样式
│   │   ├── components/
│   │   │   ├── layout/         # AppLayout, AppHeader(TopBar), AppSidebar
│   │   │   └── common/         # PageHeader, ThemeSwitcher
│   │   ├── composables/        # useTheme / useSidebar / useHealth
│   │   ├── config/             # 导航配置
│   │   ├── router/             # Vue Router 路由表
│   │   └── views/              # 各模块页面
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── vite.config.ts
│   └── vitest.config.ts
├── docs/
├── docker-compose.yml.example
├── start-backend.bat
└── README.md
```

## 开发

```bash
# 安装依赖
cd backend && pip install -r requirements.txt
cd frontend && npm install

# 运行测试
cd backend && pytest
cd frontend && npm run test:run
```

## 部署

服务器部署流程参考 [`docs/`](docs/)，生产环境使用 Docker Compose 启动 Nginx + Uvicorn 双容器。
