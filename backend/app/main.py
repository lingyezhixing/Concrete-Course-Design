import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException

from app.api import health, projects, snapshots
from app.auth.router import router as auth_router
from app.config import CORS_ORIGINS, SERVE_STATIC, STATIC_DIR
from app.data.connection import init_db
from app.logging_config import setup_logging


class _SPAStaticFiles(StaticFiles):
    """为 Vue SPA 提供 fallback：找不到文件时返回 index.html。"""

    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            raise


@asynccontextmanager
async def lifespan(_: FastAPI):
    # lifespan 在 uvicorn 的 dictConfig 之后执行，文件 handler 才不会被覆盖。
    setup_logging()
    init_db()
    yield


app = FastAPI(title="混凝土课程设计计算平台", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(projects.router, prefix="/api")
app.include_router(snapshots.router, prefix="/api")

# Windows 安装包/便携版：后端直接托管前端静态文件（仅 SERVE_STATIC=true 时启用）
# 必须在 API 路由之后挂载，避免抢 API 请求
if SERVE_STATIC:
    static_dir = STATIC_DIR or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist"
    )
    if os.path.isdir(static_dir):
        app.mount("/", _SPAStaticFiles(directory=static_dir, html=True), name="frontend")
