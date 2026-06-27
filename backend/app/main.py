from fastapi import FastAPI
from app.api import health
from app.data.connection import init_db

app = FastAPI(title="混凝土课程设计计算平台", version="0.1.0")


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(health.router, prefix="/api")
