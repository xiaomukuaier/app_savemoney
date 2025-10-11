#!/usr/bin/env python3
"""
飞书表格访问详细测试
检查多维表格访问权限和表格结构
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
import lark_oapi.api.bitable.v1 as bitable_v1


def test_table_access():
    """测试表格访问权限"""
    print("=== 飞书多维表格访问详细测试 ===")

    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    table_id = os.getenv("FEISHU_TABLE_ID")
    node_token = os.getenv("FEISHU_NODE_TOKEN")

    print(f"App ID: {app_id}")
    print(f"Table ID: {table_id}")
    print(f"Node Token: {node_token}")

    if not all([app_id, app_secret]):
        print("❌ 环境变量配置不完整")
        return

    # 初始化客户端
    client = Client.builder() \
        .app_id(app_id) \
        .app_secret(app_secret) \
        .build()

    # 测试1: 使用节点token作为app_token
    print("\n1. 使用节点token作为app_token测试...")
    if node_token:
        test_app_token(node_token, "节点token", client, table_id)
    else:
        print("   ℹ️ 未配置节点token")

    # 测试2: 使用table_id作为app_token
    print("\n2. 使用table_id作为app_token测试...")
    if table_id:
        test_app_token(table_id, "table_id", client, table_id)
    else:
        print("   ℹ️ 未配置table_id")

    # 测试3: 尝试获取所有可访问的多维表格
    print("\n3. 尝试获取所有可访问的多维表格...")
    try:
        # 首先尝试获取应用下的多维表格列表
        request = bitable_v1.ListAppRequest.builder().build()
        response = client.bitable.v1.app.list(request)

        if response.success():
            apps = response.data.items
            print(f"   ✅ 获取到 {len(apps)} 个多维表格应用")
            for app in apps:
                print(f"     - {app.name} (Token: {app.app_token})")

                # 尝试获取该应用的表格列表
                table_request = (bitable_v1.ListAppTableRequest.builder()
                    .app_token(app.app_token)
                    .build())

                table_response = client.bitable.v1.app_table.list(table_request)
                if table_response.success():
                    tables = table_response.data.items
                    print(f"       包含 {len(tables)} 个表格:")
                    for table in tables:
                        print(f"         - {table.name} (ID: {table.table_id})")
                else:
                    print(f"       获取表格列表失败: {table_response.msg}")
        else:
            print(f"   ❌ 获取多维表格应用列表失败: {response.msg}")
            print(f"     错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"   ❌ 获取多维表格应用列表异常: {e}")

    print("\n=== 飞书多维表格访问详细测试完成 ===")


def test_app_token(app_token, token_name, client, table_id):
    """测试特定的app_token"""
    print(f"   使用 {token_name}: {app_token}")

    # 测试获取应用信息
    try:
        request = (bitable_v1.GetAppRequest.builder()
            .app_token(app_token)
            .build())

        response = client.bitable.v1.app.get(request)

        if response.success():
            app_info = response.data.app
            print(f"      ✅ 多维表格信息获取成功")
            print(f"        表格名称: {app_info.name}")
            print(f"        表格修订版本: {app_info.revision}")
            print(f"        是否为高级权限: {app_info.is_advanced}")
        else:
            print(f"      ❌ 多维表格信息获取失败: {response.msg}")
            print(f"        错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"      ❌ 多维表格信息获取异常: {e}")

    # 测试获取表格列表
    try:
        request = (bitable_v1.ListAppTableRequest.builder()
            .app_token(app_token)
            .build())

        response = client.bitable.v1.app_table.list(request)

        if response.success():
            tables = response.data.items
            print(f"      ✅ 获取到 {len(tables)} 个表格")
            for table in tables:
                print(f"        - {table.name} (ID: {table.table_id})")
        else:
            print(f"      ❌ 获取表格列表失败: {response.msg}")
            print(f"        错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"      ❌ 获取表格列表异常: {e}")

    # 测试获取字段列表
    try:
        request = (bitable_v1.ListAppTableFieldRequest.builder()
            .app_token(app_token)
            .table_id(table_id)
            .build())

        response = client.bitable.v1.app_table_field.list(request)

        if response.success():
            fields = response.data.items
            print(f"      ✅ 获取到 {len(fields)} 个字段")
            for field in fields[:5]:  # 只显示前5个字段
                print(f"        - {field.field_name} (类型: {field.type})")
        else:
            print(f"      ❌ 获取字段列表失败: {response.msg}")
            print(f"        错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"      ❌ 获取字段列表异常: {e}")


if __name__ == "__main__":
    test_table_access()