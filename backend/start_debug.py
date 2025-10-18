#!/usr/bin/env python3
"""
诊断启动脚本 - 用于调试Python应用启动问题
"""
import os
import sys
import traceback

def check_environment():
    """检查环境变量"""
    print("=== 环境变量检查 ===")
    required_vars = [
        'FEISHU_APP_ID',
        'FEISHU_APP_SECRET',
        'FEISHU_TABLE_ID',
        'OPENAI_API_KEY'
    ]

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 8)} (长度: {len(value)})")
        else:
            print(f"❌ {var}: 未设置")

def check_imports():
    """检查关键依赖导入"""
    print("\n=== 依赖导入检查 ===")

    packages = [
        ('fastapi', 'fastapi'),
        ('uvicorn', 'uvicorn'),
        ('langgraph', 'langgraph'),
        ('openai', 'openai'),
        ('lark_oapi', 'lark_oapi'),
        ('pydantic', 'pydantic'),
        ('httpx', 'httpx'),
        ('requests', 'requests'),
        ('python_dotenv', 'dotenv')
    ]

    for package_name, import_name in packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError as e:
            print(f"❌ {package_name}: {e}")

def check_app_import():
    """检查应用模块导入"""
    print("\n=== 应用模块导入检查 ===")

    # 添加当前目录到Python路径
    sys.path.insert(0, '/app')

    modules_to_check = [
        'app.main',
        'app.api.routes',
        'app.services.stt',
        'app.services.gpt_parser',
        'app.services.feishu_api',
        'app.langgraph.workflow'
    ]

    for module in modules_to_check:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module}: {e}")
            traceback.print_exc()

def check_fastapi_app():
    """检查FastAPI应用启动"""
    print("\n=== FastAPI应用检查 ===")
    try:
        from app.main import app
        print("✅ FastAPI应用导入成功")
        print(f"   标题: {app.title}")
        print(f"   版本: {app.version}")
        return True
    except Exception as e:
        print(f"❌ FastAPI应用导入失败: {e}")
        traceback.print_exc()
        return False

def main():
    print("🚀 SaveMoney后端诊断脚本启动...")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print(f"Python路径: {sys.path}")

    check_environment()
    check_imports()
    check_app_import()

    if check_fastapi_app():
        print("\n🎉 所有检查通过！应用应该可以正常启动。")
    else:
        print("\n💥 应用启动失败，请查看上面的错误信息。")

    print("\n📝 诊断完成")

if __name__ == "__main__":
    main()