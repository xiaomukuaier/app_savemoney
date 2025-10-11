#!/usr/bin/env python3
"""
验证飞书表格ID和权限的测试脚本
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lark_oapi import Client


def test_feishu_connection():
    """测试飞书连接和权限"""
    print("=== 飞书连接和权限验证测试 ===")

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    table_id = os.getenv("FEISHU_TABLE_ID")

    print(f"App ID: {app_id}")
    print(f"Table ID: {table_id}")

    if not all([app_id, app_secret, table_id]):
        print("❌ 环境变量配置不完整")
        return

    # 初始化客户端
    client = Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    # 测试1: 获取应用信息
    print("\n1. 测试获取应用信息...")
    try:
        from lark_oapi.api.application.v6 import GetApplicationRequest
        request = GetApplicationRequest.builder().build()
        response = client.application.v6.application.get(request)

        if response.success():
            print(f"   ✅ 应用信息获取成功: {response.data.app.name}")
        else:
            print(f"   ❌ 应用信息获取失败: {response.msg}")
            print(f"   错误代码: {response.code}")
    except Exception as e:
        print(f"   ❌ 应用信息获取异常: {e}")

    # 测试2: 获取多维表格基本信息
    print("\n2. 测试获取多维表格基本信息...")
    try:
        from lark_oapi.api.bitable.v1 import GetAppRequest
        request = GetAppRequest.builder().app_token(table_id).build()
        response = client.bitable.v1.app.get(request)

        if response.success():
            print(f"   ✅ 多维表格信息获取成功: {response.data.app.name}")
        else:
            print(f"   ❌ 多维表格信息获取失败: {response.msg}")
            print(f"   错误代码: {response.code}")
    except Exception as e:
        print(f"   ❌ 多维表格信息获取异常: {e}")

    # 测试3: 获取表格列表
    print("\n3. 测试获取表格列表...")
    try:
        from lark_oapi.api.bitable.v1 import ListAppTableRequest
        request = ListAppTableRequest.builder().app_token(table_id).build()
        response = client.bitable.v1.app_table.list(request)

        if response.success():
            tables = response.data.items
            print(f"   ✅ 获取到 {len(tables)} 个表格")
            for table in tables:
                print(f"     - {table.name} (ID: {table.table_id})")
        else:
            print(f"   ❌ 获取表格列表失败: {response.msg}")
            print(f"   错误代码: {response.code}")
    except Exception as e:
        print(f"   ❌ 获取表格列表异常: {e}")


if __name__ == "__main__":
    test_feishu_connection()