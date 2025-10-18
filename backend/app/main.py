"""
SaveMoney 记账应用后端主入口
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

# 加载环境变量 - 支持本地开发和云环境
import os
env_path = Path(os.getcwd()).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # 云环境，从环境变量直接读取
    print("Running in cloud environment, using environment variables directly")

app = FastAPI(
    title="SaveMoney API",
    description="基于语音输入的智能记账应用",
    version="0.1.0"
)

# CORS配置 - 支持本地开发和云环境
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://*.zeabur.app"  # Zeabur部署域名
]

# 从环境变量读取额外允许的域名
extra_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
if extra_origins and extra_origins != [""]:
    allowed_origins.extend(extra_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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