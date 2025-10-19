#!/bin/bash

# SaveMoney Gradio应用开发脚本
# 使用uv进行本地开发

echo "🚀 启动SaveMoney Gradio应用..."

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装，请先安装uv: pip install uv"
    exit 1
fi

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ]; then
    echo "📦 使用uv运行应用..."
    uv run python gradio_app.py
else
    echo "🐍 在虚拟环境中运行应用..."
    python gradio_app.py
fi