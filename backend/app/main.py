from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, projects, snapshots
from app.auth.router import router as auth_router
from app.config import CORS_ORIGINS
from app.data.connection import init_db
from app.logging_config import setup_logging


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
