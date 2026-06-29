# 水工钢筋混凝土课程设计 — 整体式单向板楼盖辅助计算平台

> [!IMPORTANT]
> 🌐 **在线体验（已通过Docker Compose部署，开箱即用）**：<https://school.u1068774.nyat.app:20597/>
> 网站持续开放至 **2026 年 7 月 20 日**，无需本地安装即可体验全部功能。

> 面向水利水电工程专业《水工钢筋混凝土结构》课程设计的 Web 计算平台。
> 覆盖 **板、次梁、主梁** 三构件的荷载计算、内力分析、正截面配筋、斜截面箍筋与构造措施，
> 支持 **多项目管理、历史快照、计算书自动生成（可一键打印 PDF）**，并提供用户登录与数据隔离。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-249%20passed-brightgreen.svg)
![Python](https://img.shields.io/badge/python-3.12-3776AB.svg)
![Vue](https://img.shields.io/badge/Vue-3-42b883.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688.svg)

- **开源地址**：<https://github.com/lingyezhixing/Concrete-Course-Design>
- **开源协议**：MIT（见 [LICENSE](LICENSE)）
- **详细文档**：见 [`docs/`](docs/) 目录（[文档索引](docs/README.md)）

---

## 目录

- [水工钢筋混凝土课程设计 — 整体式单向板楼盖辅助计算平台](#水工钢筋混凝土课程设计--整体式单向板楼盖辅助计算平台)
  - [目录](#目录)
  - [一、项目简介](#一项目简介)
  - [二、课程背景与设计目标](#二课程背景与设计目标)
  - [三、功能一览](#三功能一览)
  - [四、技术栈](#四技术栈)
    - [与教师示例平台（Streamlit）的对比](#与教师示例平台streamlit的对比)
  - [五、开发与代码统计](#五开发与代码统计)
    - [开发提交统计](#开发提交统计)
    - [代码量统计](#代码量统计)
  - [六、安装与运行](#六安装与运行)
    - [方式一：Windows 便携版（推荐，零环境配置）](#方式一windows-便携版推荐零环境配置)
    - [方式二：Windows 源码运行（开发 / 自定义）](#方式二windows-源码运行开发--自定义)
    - [方式三：Linux 源码运行](#方式三linux-源码运行)
    - [方式四：Linux Docker Compose 一键启动（推荐部署）](#方式四linux-docker-compose-一键启动推荐部署)
  - [七、计算方法速览](#七计算方法速览)
  - [八、测试](#八测试)
  - [九、开发启动方式](#九开发启动方式)
  - [十、目录结构](#十目录结构)
  - [十一、已知不足与改进方向](#十一已知不足与改进方向)
  - [十二、文档导航](#十二文档导航)
  - [许可证](#许可证)

---

## 一、项目简介

本平台将传统手算的整体式单向板肋形楼盖设计流程**数字化、参数化、可视化**。用户在网页上输入结构布置、材料、荷载等设计参数，平台自动完成 **板 → 次梁 → 主梁** 的全链计算，输出每一控制截面的荷载、跨度、内力、配筋面积与钢筋选型，并附带力学计算简图、弯矩图、剪力图与抵抗弯矩图。

平台核心特点：

- **全构件覆盖**：板、次梁、主梁三类构件的荷载 → 内力 → 正截面 → 斜截面全流程。
- **荷载自动传递**：板传次梁、次梁传主梁的集中力由程序自动推导（满足任务书「提高要求」）。
- **参数输入自动校验 + 实时建议**：参数页对每一项输入即时校验（缺项高亮、超筋 αs > 0.5 拦截、范围与单位约束），并实时给出跨数推荐区间、板厚与截面高跨比 / 宽高比的合理性提示，辅助初学者规避低级错误。
- **全程实时保存 + 结果完全可编辑**：所有输入与每一项计算得数（荷载、跨度、内力、配筋）的修改均经 800 ms 防抖**实时自动落库**，刷新或换设备登录等操作均不会丢失数据；同时**所有计算得数均可在表格中手动微调，计算书会随之实时自动更新**，便于与手算结果逐项对照后定稿。
- **计算书自动生成**：一键装配八章节计算书并打印为 PDF。
- **教师参考值逐位回归**：内置教师平台实测数据作为回归基准，三构件荷载 / 内力逐位吻合，杜绝回归。
- **工程化质量**：前后端共计 **249 个自动化测试用例全部通过**，分层架构、类型严格、参数化无硬编码。

---

## 二、课程背景与设计目标

本平台依据 **《2026 版水工钢筋混凝土课程设计任务书》** 开发，设计对象为**某水电站厂房整体式单向板肋形楼盖**。

任务书对「辅助计算程序」提出了分层要求，本项目对照完成情况如下（详见 [课程背景与设计目标](docs/课程背景与设计目标.md)）：

| 任务书要求层次 | 本项目完成情况 |
|----------------|----------------|
| **基本要求**：至少实现一个构件模块、输入输出、公式与计算书一致、算例复核 | ✅ 三构件全覆盖，公式与教材一致，教师算例逐位复核 |
| **提高要求**：覆盖两/三个构件、荷载自动传递、截面初估校核、配筋推荐与超配提示、弯矩剪力图、结果导出、友好界面 | ✅ 全部实现（三构件、荷载自动传递、截面合理性提示、配筋下拉选筋与状态、内力图、计算书 PDF 导出、Web 界面） |
| **加分要求**：最不利荷载组合 / 弯矩包络图 / 抵抗弯矩图 / 全流程自动计算 / 计算书自动生成 / 智能校核 | ✅ 主梁四工况包络、抵抗弯矩图、全流程级联计算、计算书自动生成、超筋与必填校核 |

本组选用平面尺寸 **30 m × 18 m**：30 m 方向平行于次梁，18 m 方向平行于主梁（亦为板的跨度方向）。混凝土 **C20**，板筋与箍筋用 **Ⅰ级钢（HPB300，fy = 270）**，梁纵筋用 **Ⅱ级钢（HRB335，fy = 300）**。

---

## 三、功能一览

| 模块 | 功能说明 |
|------|----------|
| **登录 / 注册** | JWT 认证（7 天有效期）、bcrypt 密码哈希；同一设备多用户数据完全隔离，互不可见 |
| **项目概览** | 项目卡片网格、新建 / 打开 / 删除项目，含未提交变更提示与加载骨架 |
| **设计参数** | 三段式表单（结构布置 / 荷载 / 材料常量展示），**一键填入和清空演示数值，输入自动校验 + 实时跨数推荐 / 截面合理性建议**，一键级联计算，**所有荷载自动传递** |
| **板计算** | 荷载（恒/活/折算）、计算跨度（边/中跨）、五控制截面弯矩剪力、按间距选筋（Φd@s）、计算简图与弯矩剪力图 |
| **次梁计算** | 板传来荷载 + 自重 + 粉刷、折算荷载、支座边缘弯矩调整、T 形（跨中）/ 矩形（支座）正截面、斜截面箍筋、抵抗弯矩图 |
| **主梁计算** | 次梁传来集中力（三等分）、四工况内力包络、支座边缘调整、T 形正截面、斜截面箍筋与吊筋、三跨连续梁计算简图 |
| **计算书** | 封面信息表单 + 八章节 A4 预览（基本资料 / 布置初估 / 板 / 次梁 / 主梁 / 配筋汇总 / 构造措施 / 抵抗弯矩图），浏览器原生打印为 PDF |
| **存档管理** | 项目历史快照的归档 / 恢复 / 派生（fork）/ 重命名 / 删除，支持回溯任意版本、多任务推进、多方案比较 |
| **系统设置** | 三主题切换（暗 / 亮 / 暖）、账户注销（二次确认，级联清除个人数据） |

---

## 四、技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Python 3.12 / FastAPI / Uvicorn |
| 数据存储 | SQLite（`users` / `projects` / `snapshots` 三表，参数化查询防注入） |
| 认证 | JWT（PyJWT）+ bcrypt |
| 前端框架 | Vue 3（Composition API）+ TypeScript（strict） |
| 构建工具 | Vite 6 |
| UI 组件 | Element Plus + Lucide 图标 |
| 主题系统 | 三主题设计令牌（暗 / 亮 / 暖），`color-mix` 桥接 Element Plus 变量 |
| 后端测试 | pytest（147 用例） |
| 前端测试 | Vitest + happy-dom（102 用例） |
| 容器化 | Docker Compose（前端 Nginx 多阶段构建反代后端） |
| 桌面打包 | PyInstaller（Windows 单文件便携版） |

### 与教师示例平台（Streamlit）的对比

教师提供的示例计算平台基于 **Streamlit**（Python 单体、服务端渲染，每次交互触发整页 rerun）。本项目采用 **Vue 3 + FastAPI 前后端分离 SPA** 架构，在交互体验与工程化方面优势明显：

| 维度 | 教师示例（Streamlit） | 本平台（Vue + FastAPI） |
|------|----------------------|------------------------|
| 架构模型 | Python 单体，服务端渲染，交互触发整页重跑 | 前后端分离 SPA，组件级局部更新 |
| 表格交互 | 编辑能力受限、状态管理弱 | 全部结果表格**逐格可编辑**、即时校验 |
| 自动保存 | 无（依赖 session_state，刷新易丢） | 800 ms 防抖自动落库，刷新 / 换设备等操作不会丢失数据 |
| 多用户 | 无内建鉴权与数据隔离 | JWT 登录 + 按用户项目 / 快照隔离 |
| 历史版本 | 无 | 多项目 + 快照归档 / 恢复 / 派生 |
| 计算书 / 打印 | 浏览器整页打印，分页不可控 | A4 专用打印样式，封面 / 表格 / 简图分页可控 |
| 可维护性 | 单文件脚本，难扩展测试 | 分层架构 + 249 个自动化测试 |
| 部署门槛 | 单进程易起 | 门槛较高但已提供exe 便携版 + Docker 一键，门槛已抹平 |

> Streamlit 的优势在于**纯 Python、开发快、部署简单**；本平台以较高的实现复杂度换取了**流畅的交互体验、多用户支持与工程化可维护性**，更接近一个可长期使用的产品，而非一次性脚本。

---

## 五、开发与代码统计

### 开发提交统计

| 指标 | 数值 |
|------|------|
| Git 提交总数 | **144** 次 |
| 开发者 | lingyezhixing（独立开发） |
| 开发周期 | 2026-06-24 → 2026-06-30（约 7 天） |
| 累计代码变更 | 524 次文件改动、+26,860 行、−9,211 行 |

提交时间分布（按日）：

```
2026-06-24  ███████                       7
2026-06-27  ██████████████████████       22
2026-06-28  ██████████████████████████████████  66
2026-06-29  ██████████████████████████████████  39
2026-06-30  ██████████                   10
```

### 代码量统计

> **已排除 `node_modules`、`dist`、`build`、`__pycache__`、虚拟环境等所有编译 / 开发 / 生成文件**。

| 类型 | 文件数 | 行数 |
|------|--------|------|
| 后端 Python（应用逻辑 `backend/app`） | 35 | 3,116 |
| 前端 Vue 组件 | 23 | 4,339 |
| 前端 TypeScript（源码） | 19 | 1,809 |
| 前端 CSS（三主题令牌 + 打印样式） | 2 | 418 |
| 前端 HTML（入口） | 1 | 27 |
| 构建 / 打包脚本（`build_win.py`、`run.py`） | 2 | 179 |
| **应用源码合计** | **82** | **9,888** |
| 后端测试（pytest） | 15 | 1,907 |
| 前端测试（Vitest spec） | 15 | 1,150 |
| **测试代码合计** | **30** | **3,057** |
| **项目总计（不含生成物）** | **112** | **12,945** |

---

## 六、安装与运行

本平台提供 **Windows** 与 **Linux** 两种平台、**源码运行**与**开箱即用**两类方式，共四种组合。详细步骤见 [安装与运行](docs/安装与运行.md)。

### 方式一：Windows 便携版（推荐，零环境配置）

无需安装任何环境，双击 exe 即可运行。获取 exe 有两种途径：

- **GitHub Releases（推荐）**：到 [Releases 页](https://github.com/lingyezhixing/Concrete-Course-Design/releases) 下载 `ConcreteCourseDesign.exe`，**始终为最新版本**；
- **仓库 `Portable/` 目录**：仓库根目录的 [`Portable/`](Portable/) 文件夹内置可直接运行的 exe，**但可能不是最新版本**（随不定期打包更新）。

运行说明：

- 双击 `ConcreteCourseDesign.exe`，程序自动在 exe 同级目录创建 `data/`（数据库）与 `logs/`（日志）；
- 自动打开浏览器访问 <http://localhost:8000>；
- 后端以 `SERVE_STATIC` 模式直接托管前端，**无需安装 Python / Node / 任何依赖**。

如需自行打包最新版：`pip install pyinstaller && python build_win.py`（构建后自动放入 `Portable/`）。

### 方式二：Windows 源码运行（开发 / 自定义）

```bash
# 1. 后端（建议在 conda 环境）
conda create -n concrete python=3.12 && conda activate concrete
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000

# 2. 前端（另开终端）
cd frontend
npm install
npm run dev      # 访问 http://localhost:3000
```

### 方式三：Linux 源码运行

```bash
# 后端
cd backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000

# 前端
cd frontend
npm install && npm run dev
```

### 方式四：Linux Docker Compose 一键启动（推荐部署）

> **在线体验**：本平台已用此方式部署于 <https://school.u1068774.nyat.app:20597/>，可直接访问（持续开放至 2026 年 7 月 20 日），无需自行部署。

```bash
cp docker-compose.yml.example docker-compose.yml
docker compose up -d --build
# 访问 http://localhost:8000
```

前端容器（Nginx）反代 `/api/` 至后端容器，对外仅需暴露 `8000` 端口，避免SQL注入攻击；数据通过 `./data`、`./logs` 卷挂载持久化。

> ⚠️ 生产部署请务必设置 `SECRET_KEY` 环境变量（JWT 签名密钥），默认值为开发占位值。其余可配置项见 `.env.example`。

---

## 七、计算方法速览

三构件统一遵循课程设计手算步骤：**参数派生 → 荷载计算 → 跨度确定 → 内力分析 → 正截面配筋 → 斜截面箍筋**。完整公式、系数表与推导见 [计算方法与公式](docs/计算方法与公式.md)。

**材料与系数（固定，单一来源 `backend/app/materials.py`）**：C20 混凝土 fc = 9.6、ft = 1.1 N/mm²；Ⅰ级钢 fy = 270；Ⅱ级钢 fy = 300 N/mm²；结构系数 γd = 1.2；恒载分项系数 γG = 1.05；活载分项系数 γQ = 1.2。

| 构件 | 荷载 | 内力方法 | 正截面 | 斜截面 |
|------|------|----------|--------|--------|
| **板** | 水磨石 + 板自重 + 抹灰 | 等跨连续梁系数表（2~5 跨，>5 跨按 5 跨简化），五控制截面弯矩剪力 | h₀ / αs / ξ / As，按 Φd@s 间距选筋 | —（板一般不验算） |
| **次梁** | 板传来 + 自重 + 粉刷，折算荷载 g′、q′ | 同上系数表 + 支座边缘调整 M′=|Mc|−b/2·V₀ | 跨中 T 形 / 支座矩形 | Vc = 0.7·ft·b·h₀/γd，箍筋 |
| **主梁** | 次梁传来集中力（三等分）+ 自重 + 粉刷 | 三跨集中力系数包络（4 种活载布置取最不利） | 全 T 形（课程简化） | Vc = 0.5·ft·b·h₀/γd，箍筋 + 吊筋 |

**有效高度统一约定** h₀ = h − c − d/2（c 为保护层，d 为估算纵筋直径）。

---

## 八、测试

| 测试范围 | 文件数 | 用例数 | 状态 |
|----------|--------|--------|------|
| 后端单元 + 集成（pytest） | 15 | **147** | ✅ 全部通过 |
| 前端单元（Vitest） | 15 | **102** | ✅ 全部通过 |
| **合计** | **30** | **249** | ✅ |

运行方式：

```bash
# 后端
cd backend && pytest -v            # 或 conda run -n concrete pytest -v

# 前端
cd frontend && npm run test:run    # 单次运行
cd frontend && npx vue-tsc --noEmit  # 类型检查
```

**测试亮点**：

- **教师参考值回归**：`test_teacher_validation.py` 以教师平台实测数据为期望值，对三构件荷载 / 跨度 / 内力**逐位断言**，防止任何回归。
- **求解器单元测试**：每个计算阶段（荷载 / 跨度 / 内力 / 配筋 / 抗剪）独立测试，并与手算参考值对比。
- **API 集成测试**：项目 CRUD、用户隔离、认证门禁、超筋检测（αs > 0.5 返回 400）全覆盖。
- **测试隔离**：`isolated_db` fixture 使用 `tmp_path + monkeypatch`，测试间互不干扰。

测试用例清单与手算对比见 [测试与验证](docs/测试与验证.md)。

---

## 九、开发启动方式

```bash
# 1. 克隆仓库
git clone https://github.com/lingyezhixing/Concrete-Course-Design.git
cd Concrete-Course-Design

# 2. 后端（conda 环境，热重载）
conda create -n concrete python=3.12 -y && conda activate concrete
cd backend && pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000     # API 文档: http://localhost:8000/docs

# 3. 前端（另开终端，Vite HMR）
cd frontend && npm install
npm run dev                                    # http://localhost:3000，/api 代理到 8000
```

常用脚本：

| 命令 | 说明 |
|------|------|
| `cd backend && pytest -v` | 后端测试 |
| `cd frontend && npm run dev` | 前端开发服务器（HMR） |
| `cd frontend && npm run build` | 前端生产构建（含 vue-tsc 类型检查） |
| `cd frontend && npm run test:run` | 前端测试 |
| `python build_win.py` | 构建 Windows 便携版 exe（需先 `pip install pyinstaller`） |

开发约定与环境细节见 [开发指南](docs/开发指南.md)。

---

## 十、目录结构

```
Concrete-Course-Design/
├── backend/                          # FastAPI 后端
│   ├── app/
│   │   ├── main.py                   # 入口：CORS、路由挂载、SPA 静态回落、启动建表
│   │   ├── config.py                 # 环境变量（SECRET_KEY / CORS / SERVE_STATIC）
│   │   ├── security.py               # bcrypt 密码哈希 + JWT 签发/验证
│   │   ├── logging_config.py         # 日志（控制台 + 文件轮转）
│   │   ├── materials.py              # 材料强度与分项系数（单一来源）
│   │   ├── api/
│   │   │   ├── health.py             # GET /api/health
│   │   │   ├── projects.py           # 项目 CRUD + POST /calculate
│   │   │   └── snapshots.py          # 快照归档/恢复/fork/删除
│   │   ├── auth/
│   │   │   ├── router.py             # 注册/登录/当前用户/删除账户
│   │   │   ├── dependencies.py       # get_current_user 依赖注入
│   │   │   └── repository.py         # 用户数据访问层
│   │   ├── models/                   # Pydantic 模型（各含 __init__.py）
│   │   │   ├── user.py               # UserCreate/UserLogin/UserPublic/Token
│   │   │   ├── project.py            # Project*/Snapshot*/CalculateRequest + REQUIRED 字段
│   │   │   └── slab.py / beam.py / main_beam.py
│   │   ├── solvers/                  # 计算引擎
│   │   │   ├── common.py             # 共享：h0/αs/ξ/As、抗剪、等跨连续梁系数表
│   │   │   ├── derive.py             # 扁平参数 → 各构件输入（荷载自动传递）
│   │   │   ├── slab/{solver,utils}.py        # 板：编排 + 按间距选筋
│   │   │   ├── beam/{solver,utils}.py        # 次梁：T形/矩形正截面、边缘调整
│   │   │   └── main_beam/{solver,utils}.py   # 主梁：集中力包络 + 吊筋
│   │   └── data/
│   │       ├── connection.py         # SQLite 连接 + 建表 DDL
│   │       └── project_repository.py # 项目/快照数据访问层
│   ├── tests/                        # 后端测试（15 文件，147 用例）
│   │   ├── conftest.py               # 共享 fixtures（isolated_db / client / auth）
│   │   ├── test_auth.py              # 认证流程 + 用户隔离
│   │   ├── test_common.py            # 共享公式与连续梁系数
│   │   ├── test_slab_*.py            # 板：配筋 / 工具 / 编排（3 文件）
│   │   ├── test_beam*.py             # 次梁：单元 + 编排（2 文件）
│   │   ├── test_main_beam.py         # 主梁单元测试
│   │   ├── test_project_repository.py
│   │   ├── test_projects_api.py      # 项目 API 集成
│   │   ├── test_calculate_api.py     # /calculate 集成 + 超筋检测
│   │   ├── test_snapshots_api.py
│   │   └── test_teacher_validation.py # 教师参考值逐位回归
│   ├── run.py                        # PyInstaller 便携版入口（SERVE_STATIC）
│   ├── requirements.txt / requirements-dev.txt
│   ├── pyproject.toml                # pytest 配置
│   └── Dockerfile / .dockerignore
├── frontend/                         # Vue 3 + TypeScript 前端
│   ├── src/
│   │   ├── main.ts                   # 入口：EP 注册、主题预设、全局样式
│   │   ├── App.vue                   # 根组件
│   │   ├── api/
│   │   │   ├── index.ts              # Axios 实例 + 拦截器（401 跳登录）
│   │   │   ├── auth.ts               # 认证 API
│   │   │   └── projects.ts           # 项目/快照/计算 API + 类型
│   │   ├── assets/styles/
│   │   │   ├── tokens.css            # 三主题设计令牌 + Element Plus 桥接
│   │   │   └── report-print.css      # 计算书打印样式（A4 分页）
│   │   ├── components/
│   │   │   ├── layout/               # AppLayout / AppHeader / AppSidebar / UserDropdown
│   │   │   ├── common/               # PageHeader / EmptyState / Skeleton
│   │   │   ├── diagrams/             # UniformLoadBeam / MainBeam / InternalForce / ResistingMoment / SectionRebar
│   │   │   └── report/ReportDocument.vue   # 计算书 A4 渲染
│   │   ├── composables/              # 组合式函数（模块级单例）
│   │   │   ├── useAuth / useProject / useTheme / useSidebar / useHealth
│   │   │   ├── useReportDocument / useResistingMoment / useBeamLayout / useInternalForce
│   │   │   └── useReinfStatus
│   │   ├── config/{nav.ts, rebarTable.ts}   # 导航配置 + 钢筋面积表
│   │   ├── report/{materials.ts, types.ts}  # 计算书材料常量 + 文档模型
│   │   ├── router/index.ts           # Vue Router + 导航守卫
│   │   └── views/                    # 9 个页面
│   │       ├── Login / Overview / Params
│   │       ├── Slab / SecondaryBeam / MainBeam
│   │       └── Archive / Settings / Report
│   ├── public/logo.ico
│   ├── index.html / env.d.ts
│   ├── package.json / package-lock.json
│   ├── vite.config.ts / vitest.config.ts / tsconfig.json
│   └── Dockerfile / nginx.conf / .dockerignore
├── docs/                             # 详细文档（见 §十二）
│   ├── README.md                     # 文档索引
│   ├── 课程背景与设计目标.md / 功能详解.md / 技术架构.md
│   ├── 计算方法与公式.md / 安装与运行.md / 测试与验证.md
│   └── 开发指南.md / 已知不足与改进方向.md
├── Portable/                         # Windows 便携版 exe（构建产物；最新版见 GitHub Releases）
├── assets/logo.ico                   # 应用图标
├── build_win.py                      # Windows 便携版打包脚本（产物 → Portable/）
├── docker-compose.yml.example        # Docker Compose 编排示例
├── .env.example                      # 环境变量模板
└── .gitignore / LICENSE              # MIT
```

---

## 十一、已知不足与改进方向

诚实披露以下局限（答辩可说明，详见 [已知不足与改进方向](docs/已知不足与改进方向.md)）：

1. **主梁仅支持 3 跨**：不同于板和次梁的完整支持，三等分集中力系数表（表 14-4）只覆盖三等跨，4/5 跨方案需补充系数表（本组方案 A 为 3 跨，已够用）。

2. **抵抗弯矩图**截断点以文字说明，未自动绘制纵筋详图（求解器尚无配筋构造详图引擎）。

---

## 十二、文档导航

所有细节文档位于 [`docs/`](docs/)，索引见 [docs/README.md](docs/README.md)：

| 文档 | 内容 |
|------|------|
| [课程背景与设计目标](docs/课程背景与设计目标.md) | 任务书对照、设计参数、本组方案 |
| [功能详解](docs/功能详解.md) | 每个页面的功能与交互详述 |
| [技术架构](docs/技术架构.md) | 前后端分层、数据库、鉴权、主题系统 |
| [计算方法与公式](docs/计算方法与公式.md) | ★ 板 / 次梁 / 主梁完整公式、系数表与推导 |
| [安装与运行](docs/安装与运行.md) | Windows / Linux 四种运行方式详解 |
| [测试与验证](docs/测试与验证.md) | 测试用例清单、教师值回归、手算对比 |
| [开发指南](docs/开发指南.md) | 开发环境、脚本、约定 |
| [已知不足与改进方向](docs/已知不足与改进方向.md) | 局限与后续改进 |

---

## 许可证

本项目基于 [MIT License](LICENSE) 开源，© 2026 lingyezhixing。欢迎学习参考，引用请注明来源。
