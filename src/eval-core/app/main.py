"""FastAPI 入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import benchmarks, models, evaluations, results, reports

app = FastAPI(
    title="AI安全评测平台 API",
    description="Agent Security Evaluation Framework API",
    version="1.0.0",
)

# CORS（开发模式）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(benchmarks.router)
app.include_router(models.router)
app.include_router(evaluations.router)
app.include_router(results.router)
app.include_router(reports.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "eval-core"}
