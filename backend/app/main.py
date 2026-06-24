from fastapi import FastAPI

app = FastAPI(
    title="混凝土课程设计计算平台",
    version="0.1.0",
)


@app.get("/api/health")
def health():
    return {"status": "ok"}
