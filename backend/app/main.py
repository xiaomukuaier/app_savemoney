"""
SaveMoney 记账应用后端主入口
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

# 加载环境变量
import os
env_path = Path(os.getcwd()).parent / ".env"
load_dotenv(env_path)

app = FastAPI(
    title="SaveMoney API",
    description="基于语音输入的智能记账应用",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(router)


@app.get("/")
async def root():
    """健康检查"""
    return {"message": "SaveMoney API is running"}


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)