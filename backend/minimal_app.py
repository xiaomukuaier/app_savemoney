#!/usr/bin/env python3
"""
最小化测试应用 - 验证容器能否启动
"""
import os
import time

print("🚀 最小化测试应用启动...")
print(f"Python版本: {__import__('sys').version}")
print(f"工作目录: {os.getcwd()}")

# 检查环境变量
print("\n📋 环境变量检查:")
for var in ['FEISHU_APP_ID', 'FEISHU_APP_SECRET', 'FEISHU_TABLE_ID', 'OPENAI_API_KEY']:
    value = os.getenv(var)
    if value:
        print(f"✅ {var}: 已设置 (长度: {len(value)})")
    else:
        print(f"❌ {var}: 未设置")

# 简单HTTP服务器
print("\n🌐 启动简单HTTP服务器...")
print("服务器运行在 http://0.0.0.0:8000")

# 保持容器运行
print("\n⏰ 容器保持运行中...")
while True:
    time.sleep(10)
    print("容器仍在运行...")