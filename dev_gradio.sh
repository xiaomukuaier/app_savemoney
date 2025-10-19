#!/bin/bash

# SaveMoney Gradio应用开发脚本
# 使用后端虚拟环境进行本地开发

echo "🚀 启动SaveMoney Gradio应用..."

# 检查后端虚拟环境是否存在
if [ -d "backend/.venv" ]; then
    echo "📦 使用后端虚拟环境运行应用..."
    cd backend && uv run python ../gradio_app.py
else
    echo "❌ 后端虚拟环境不存在，请先在后端目录运行: uv sync"
    echo "或者在后端目录运行: cd backend && uv run python ../gradio_app.py"
    exit 1
fi