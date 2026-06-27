from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import health
from app.data.connection import init_db
from app.logging_config import setup_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    # lifespan 在 uvicorn 的 dictConfig 之后执行，文件 handler 才不会被覆盖。
    setup_logging()
    init_db()
    yield


app = FastAPI(title="混凝土课程设计计算平台", version="0.1.0", lifespan=lifespan)


app.include_router(health.router, prefix="/api")
