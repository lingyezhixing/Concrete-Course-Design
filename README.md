# 水利水电工程 - 混凝土课程设计计算平台

## 技术栈

- **后端**: Python 3.12 + FastAPI + Uvicorn
- **前端**: Vue 3 + TypeScript + Element Plus + Vite

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

## 项目结构

```
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── main.py    # 应用入口
│   │   └── calc/      # 计算模块（纯函数）
│   └── requirements.txt
├── frontend/          # Vue 3 前端
│   └── src/
│       ├── api/       # API 请求
│       ├── views/     # 页面
│       └── router/    # 路由
└── README.md
```
