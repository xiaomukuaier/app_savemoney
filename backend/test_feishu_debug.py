#!/usr/bin/env python3
"""
飞书API调试脚本 - 尝试多种方法访问多维表格
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
import lark_oapi.api.application.v6 as application_v6


def test_feishu_debug():
    """调试飞书API访问"""
    print("=== 飞书API调试测试 ===")

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

    # 测试1: 获取应用信息
    print("\n1. 测试获取应用信息...")
    try:
        request = application_v6.GetApplicationRequest.builder().build()
        response = client.application.v6.application.get(request)

        if response.success():
            print(f"   ✅ 应用信息获取成功: {response.data.app.name}")
        else:
            print(f"   ❌ 应用信息获取失败: {response.msg}")
            print(f"   错误代码: {response.code}")
    except Exception as e:
        print(f"   ❌ 应用信息获取异常: {e}")

    # 测试2: 尝试不同的app_token组合
    print("\n2. 测试不同的app_token组合...")

    app_tokens_to_test = [
        ("table_id", table_id),
        ("node_token", node_token),
        ("space_id", "gbdzlr03tm"),  # 从URL中提取的space_id
    ]

    for token_name, app_token in app_tokens_to_test:
        if not app_token:
            continue

        print(f"\n   尝试使用 {token_name} 作为app_token: {app_token}")

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
                break  # 找到正确的app_token
            else:
                print(f"      ❌ 获取表格列表失败: {response.msg}")
                print(f"       错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
        except Exception as e:
            print(f"      ❌ 获取表格列表异常: {e}")

    # 测试3: 尝试获取知识空间信息
    print("\n3. 测试获取知识空间信息...")
    try:
        import lark_oapi.api.wiki.v2 as wiki_v2

        # 尝试获取空间列表
        request = wiki_v2.ListSpaceRequest.builder().build()
        response = client.wiki.v2.space.list(request)

        if response.success():
            spaces = response.data.items
            print(f"   ✅ 获取到 {len(spaces)} 个知识空间")
            for space in spaces[:3]:  # 只显示前3个
                print(f"     - {space.name} (ID: {space.space_id})")
        else:
            print(f"   ❌ 获取空间列表失败: {response.msg}")
            print(f"   错误代码: {response.code if hasattr(response, 'code') else 'N/A'}")
    except Exception as e:
        print(f"   ❌ 获取知识空间信息异常: {e}")

    print("\n=== 飞书API调试测试完成 ===")


if __name__ == "__main__":
    test_feishu_debug()